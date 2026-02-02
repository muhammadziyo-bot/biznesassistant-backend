"""
Email verification routes for BiznesAssistant
Handles email verification and account activation
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.services.email_service import email_service

router = APIRouter()

class EmailVerificationRequest(BaseModel):
    email: str

class EmailVerificationResponse(BaseModel):
    message: str
    success: bool

@router.post("/resend-verification", response_model=EmailVerificationResponse)
async def resend_verification_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """Resend verification email to user"""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already verified
        if user.is_verified:
            return EmailVerificationResponse(
                message="Email already verified",
                success=True
            )
        
        # Get tenant info
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Generate new verification token
        verification_token = email_service.generate_verification_token()
        
        # Store token (you might want to add a verification_tokens table)
        user.email_verification_token = verification_token
        user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
        db.commit()
        
        # Send verification email
        email_sent = email_service.send_verification_email(
            user.email,
            verification_token,
            tenant.name
        )
        
        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email"
            )
        
        return EmailVerificationResponse(
            message="Verification email sent successfully",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resend verification email: {str(e)}"
        )

@router.get("/verify", response_model=EmailVerificationResponse)
async def verify_email(
    token: str = Query(..., description="Verification token"),
    db: Session = Depends(get_db)
):
    """Verify email using token"""
    try:
        # Find user by verification token
        user = db.query(User).filter(
            User.email_verification_token == token,
            User.email_verification_expires > datetime.utcnow()
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Check if already verified
        if user.is_verified:
            return EmailVerificationResponse(
                message="Email already verified",
                success=True
            )
        
        # Mark user as verified
        user.is_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None
        user.email_verified_at = datetime.utcnow()
        
        # Also mark tenant as verified
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if tenant:
            tenant.is_verified = True
        
        db.commit()
        
        # Send welcome email
        tenant_name = tenant.name if tenant else "Your Business"
        email_service.send_welcome_email(
            user.email,
            tenant_name,
            user.full_name
        )
        
        return EmailVerificationResponse(
            message="Email verified successfully! You can now login to your account.",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify email: {str(e)}"
        )

@router.get("/check-verification", response_model=EmailVerificationResponse)
async def check_verification_status(
    email: str = Query(..., description="Email to check"),
    db: Session = Depends(get_db)
):
    """Check if email is verified"""
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified:
            return EmailVerificationResponse(
                message="Email is verified",
                success=True
            )
        else:
            return EmailVerificationResponse(
                message="Email not verified. Please check your inbox for verification email.",
                success=False
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check verification status: {str(e)}"
        )
