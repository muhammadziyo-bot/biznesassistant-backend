"""
Business registration routes for multi-tenant SaaS
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import secrets
import string

from app.database import get_db
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.models.company import Company
from app.utils.auth import get_password_hash, create_access_token
from app.config import settings
from app.services.email_service import email_service

router = APIRouter()

# Pydantic models for registration
class BusinessRegistration(BaseModel):
    # Business Information
    business_name: str
    tax_id: str
    business_email: EmailStr
    business_phone: Optional[str] = None
    business_address: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    
    # Admin User Information
    admin_name: str
    admin_email: EmailStr
    admin_password: str
    admin_phone: Optional[str] = None
    
    # Subscription
    subscription_tier: str = "basic"  # basic, professional, enterprise

class RegistrationResponse(BaseModel):
    message: str
    tenant_id: int
    user_id: int
    company_id: int
    company_code: str
    access_token: str
    trial_ends_at: datetime

@router.post("/register-business", response_model=RegistrationResponse)
async def register_business(
    registration_data: BusinessRegistration,
    db: Session = Depends(get_db)
):
    """Register a new business and create admin user."""
    try:
        # Check if business with this tax_id already exists
        existing_tenant = db.query(Tenant).filter(Tenant.tax_id == registration_data.tax_id).first()
        if existing_tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business with this tax ID already registered"
            )
        
        # Check if admin email already exists
        existing_user = db.query(User).filter(User.email == registration_data.admin_email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create tenant
        trial_ends_at = datetime.utcnow() + timedelta(days=30)  # 30-day trial
        
        tenant = Tenant(
            name=registration_data.business_name,
            tax_id=registration_data.tax_id,
            email=registration_data.business_email,
            phone=registration_data.business_phone,
            address=registration_data.business_address,
            industry=registration_data.industry,
            employee_count=registration_data.employee_count,
            subscription_tier=registration_data.subscription_tier,
            subscription_status="trial",
            trial_ends_at=trial_ends_at,
            is_active=True,
            is_verified=False  # Will be verified after email confirmation
        )
        
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        # Generate unique company code
        def generate_company_code():
            """Generate a unique 6-character company code."""
            while True:
                code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                # Check if code already exists
                existing = db.query(Company).filter(Company.company_code == code).first()
                if not existing:
                    return code
        
        company_code = generate_company_code()
        
        # Create company
        company = Company(
            name=registration_data.business_name,
            tax_id=registration_data.tax_id,
            company_code=company_code,
            email=registration_data.business_email,
            phone=registration_data.business_phone,
            address=registration_data.business_address,
            tenant_id=tenant.id,
            is_active=True
        )
        
        db.add(company)
        db.commit()
        db.refresh(company)
        
        # Create admin user
        hashed_password = get_password_hash(registration_data.admin_password)
        admin_user = User(
            email=registration_data.admin_email,
            username=f"admin_{tenant.id}",  # Ensure unique username
            full_name=registration_data.admin_name,
            hashed_password=hashed_password,
            phone=registration_data.admin_phone,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=False,  # Must verify email first
            company_id=company.id,
            tenant_id=tenant.id
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Generate verification token
        verification_token = email_service.generate_verification_token()
        verification_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Store verification token in user record
        admin_user.email_verification_token = verification_token
        admin_user.email_verification_expires = verification_expires
        
        db.commit()
        
        # Send verification email
        email_sent = email_service.send_verification_email(
            admin_user.email,
            verification_token,
            registration_data.business_name
        )
        
        if not email_sent:
            # Still allow registration but warn about email
            print(f"Warning: Failed to send verification email to {admin_user.email}")
        
        # Create access token (but don't auto-login - user must verify email first)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": admin_user.email,
                "tenant_id": tenant.id
            },
            expires_delta=access_token_expires
        )
        
        return RegistrationResponse(
            message="Business registered successfully! Please check your email to verify your account.",
            tenant_id=tenant.id,
            user_id=admin_user.id,
            company_id=company.id,
            company_code=company_code,
            access_token=access_token,
            trial_ends_at=trial_ends_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during business registration: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.get("/subscription-tiers")
async def get_subscription_tiers():
    """Get available subscription tiers and their features."""
    tiers = {
        "freemium": {
            "name": "Bepul (Free)",
            "price": "0 UZS",
            "duration": "Cheksiz",
            "features": [
                "30 ta tranzaksiya oyiga",
                "15 ta invoice oyiga", 
                "25 ta vazifa oyiga",
                "Asosiy dashboard",
                "Email yordam"
            ],
            "limits": {
                "transactions": 30,
                "invoices": 15,
                "tasks": 25,
                "users": 3
            }
        },
        "professional": {
            "name": "Professional",
            "price": "60,000 UZS/oy",
            "duration": "Oylik to'lov",
            "features": [
                "Cheksiz tranzaksiyalar",
                "Cheksiz invoice'lar",
                "Cheksiz vazifalar",
                "Kengaytirilgan hisobotlar",
                "Prioritet yordam"
            ],
            "limits": {
                "transactions": -1,  # Unlimited
                "invoices": -1,
                "tasks": -1,
                "users": 10
            }
        },
        "enterprise": {
            "name": "Enterprise",
            "price": "120,000 UZS/oy",
            "duration": "Oylik to'lov",
            "features": [
                "Professionalning barcha imkoniyatlari",
                "Jamoa hamkorligi",
                "Kengaytirilgan analitika",
                "API kirish",
                "Tezkor yordam"
            ],
            "limits": {
                "transactions": -1,
                "invoices": -1,
                "tasks": -1,
                "users": 25
            }
        },
        "premium": {
            "name": "Premium",
            "price": "200,000 UZS/oy",
            "duration": "Oylik to'lov",
            "features": [
                "Enterprise'ning barcha imkoniyatlari",
                "Maxsus xususiyatlar",
                "Shaxsiy yordam",
                "Oq yorliq variantlari",
                "O'zbekiston bo'yicha trening"
            ],
            "limits": {
                "transactions": -1,
                "invoices": -1,
                "tasks": -1,
                "users": -1  # Unlimited
            }
        }
    }
    
    return {"tiers": tiers}

@router.post("/validate-tax-id")
async def validate_tax_id(tax_id: str, db: Session = Depends(get_db)):
    """Check if tax ID is available for registration."""
    existing = db.query(Tenant).filter(Tenant.tax_id == tax_id).first()
    return {
        "available": existing is None,
        "message": "Tax ID is available" if existing is None else "Tax ID already registered"
    }
