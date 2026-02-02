"""
Simple ML API Routes
High-value ML features for Uzbek SMEs
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services.simple_ml import SimpleMLService
from app.utils.auth import get_current_active_user, get_current_tenant
from app.models.user import User

router = APIRouter()

@router.get("/suggest-category")
async def suggest_category(
    description: str = Query(..., description="Transaction description"),
    amount: float = Query(..., description="Transaction amount"),
    transaction_type: str = Query(..., description="Transaction type (income/expense)"),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Suggest transaction category based on description and amount
    Supports Uzbek and Russian keywords
    """
    try:
        ml_service = SimpleMLService(db, tenant_id)
        suggestion = ml_service.suggest_category(description, amount, transaction_type)
        return {
            "success": True,
            "suggestion": suggestion,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating category suggestion: {str(e)}"
        )

@router.get("/customer-reliability/{customer_id}")
async def get_customer_reliability(
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get customer payment reliability score
    Helps businesses assess payment risk
    """
    try:
        ml_service = SimpleMLService(db, tenant_id)
        reliability = ml_service.get_customer_reliability(customer_id)
        return {
            "success": True,
            "customer_id": customer_id,
            "reliability": reliability,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating customer reliability: {str(e)}"
        )

@router.get("/business-insights")
async def get_business_insights(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    """
    Get general business insights and patterns
    Helps owners understand their business performance
    """
    try:
        ml_service = SimpleMLService(db, tenant_id)
        insights = ml_service.get_business_insights(days)
        return {
            "success": True,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating business insights: {str(e)}"
        )

@router.get("/health")
async def ml_health_check():
    """
    Health check for ML service
    """
    return {
        "status": "healthy",
        "service": "SimpleML",
        "features": [
            "category_suggestion",
            "customer_reliability",
            "business_insights"
        ],
        "supported_languages": ["uz", "ru", "en"]
    }
