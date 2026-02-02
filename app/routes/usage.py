"""
Usage tracking and limit enforcement routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.services.usage_service import UsageService
from app.utils.auth import get_current_active_user

router = APIRouter()

@router.get("/current-usage")
async def get_current_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current usage for the user's company."""
    usage_service = UsageService(db)
    
    # Get tenant info for subscription tier
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Get current usage and limits
    usage_status = usage_service.check_limits(
        current_user.company_id, 
        tenant.subscription_tier
    )
    
    # Add subscription info
    usage_status["subscription_tier"] = tenant.subscription_tier
    usage_status["subscription_status"] = tenant.subscription_status
    
    return usage_status

@router.get("/usage-stats")
async def get_usage_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed usage statistics for dashboard."""
    usage_service = UsageService(db)
    
    # Get tenant info
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Get current usage
    current_usage = usage_service.get_current_usage(current_user.company_id)
    plan_limits = usage_service.get_plan_limits(tenant.subscription_tier)
    
    # Calculate percentages
    stats = {
        "current_usage": current_usage,
        "plan_limits": plan_limits,
        "usage_percentages": {
            "transactions": usage_service.get_usage_percentage(
                current_usage["transactions"], 
                plan_limits["transactions"]
            ),
            "invoices": usage_service.get_usage_percentage(
                current_usage["invoices"], 
                plan_limits["invoices"]
            ),
            "tasks": usage_service.get_usage_percentage(
                current_usage["tasks"], 
                plan_limits["tasks"]
            )
        },
        "subscription_info": {
            "tier": tenant.subscription_tier,
            "status": tenant.subscription_status,
            "trial_ends_at": tenant.trial_ends_at
        }
    }
    
    return stats
