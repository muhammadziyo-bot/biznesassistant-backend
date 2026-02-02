from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.models.user import User, UserRole
from app.models.transaction import Transaction, TransactionType
from app.models.invoice import Invoice, InvoiceStatus
from app.models.contact import Contact
from app.models.lead import Lead, LeadStatus
from app.models.deal import Deal, DealStatus
from app.models.kpi import KPICategory, KPIPeriod
from app.utils.auth import get_current_active_user, get_current_tenant
from app.services.kpi_service import KPIService
from app.schemas.kpi import (
    KPIResponse, KPITrendResponse, ForecastRequest, ForecastResponse,
    RoleBasedDashboardResponse
)

router = APIRouter()

# Enhanced KPI endpoints

@router.get("/kpis", response_model=list[KPIResponse])
async def get_kpis(
    period: KPIPeriod = KPIPeriod.MONTHLY,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get KPIs for the current user's company."""
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company"
        )
    
    kpi_service = KPIService(db, tenant_id)
    return kpi_service.calculate_kpis(current_user.company_id, period)

@router.get("/kpi/trend/{category}")
async def get_kpi_trend(
    category: KPICategory,
    period_type: KPIPeriod = KPIPeriod.MONTHLY,
    months: int = 12,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get trend data for a specific KPI category."""
    kpi_service = KPIService(db, tenant_id)
    trend_data = kpi_service.generate_trend_data(
        current_user.company_id, category, period_type, months
    )
    
    return {
        "category": category.value,
        "period_type": period_type.value,
        "trend_data": trend_data
    }

@router.post("/kpi/forecast", response_model=ForecastResponse)
async def generate_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Generate forecast for a KPI category."""
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company"
        )
    
    kpi_service = KPIService(db, tenant_id)
    
    # Convert string values to enums properly
    try:
        if isinstance(request.kpi_category, str):
            category = KPICategory(request.kpi_category)
        else:
            category = KPICategory(request.kpi_category.value)
        
        if isinstance(request.period_type, str):
            period = KPIPeriod(request.period_type)
        else:
            period = KPIPeriod(request.period_type.value)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid enum value: {str(e)}"
        )
    
    forecast_result = kpi_service.generate_forecast(
        current_user.company_id, 
        category, 
        period, 
        request.forecast_periods
    )
    
    if "error" in forecast_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=forecast_result["error"]
        )
    
    # Convert date strings to datetime objects for proper schema validation
    historical_data = [
        {
            "date": datetime.fromisoformat(point["date"]),
            "value": point["value"],
            "forecast": point.get("forecast", False)
        }
        for point in forecast_result["historical_data"]
    ]
    forecast_data = [
        {
            "date": datetime.fromisoformat(point["date"]),
            "value": point["value"],
            "forecast": point.get("forecast", False)
        }
        for point in forecast_result["forecast_data"]
    ]
    
    return ForecastResponse(
        kpi_category=request.kpi_category,
        period_type=request.period_type,
        historical_data=historical_data,
        forecast_data=forecast_data,
        confidence_score=forecast_result["confidence_score"],
        model_used=forecast_result["model_used"]
    )

@router.get("/dashboard/role-based")
async def get_role_based_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get role-based dashboard configuration and data."""
    kpi_service = KPIService(db, tenant_id)
    dashboard_data = kpi_service.get_role_based_dashboard(
        current_user.company_id, 
        current_user.role
    )
    
    return dashboard_data

@router.get("/summary")
async def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get comprehensive analytics summary for the dashboard."""
    kpi_service = KPIService(db, tenant_id)
    
    # Get current month KPIs
    current_kpis = kpi_service.calculate_kpis(current_user.company_id, KPIPeriod.MONTHLY)
    
    # Get trend data for key metrics
    revenue_trend = kpi_service.generate_trend_data(
        current_user.company_id, KPICategory.REVENUE, KPIPeriod.MONTHLY, 6
    )
    expense_trend = kpi_service.generate_trend_data(
        current_user.company_id, KPICategory.EXPENSES, KPIPeriod.MONTHLY, 6
    )
    
    # Generate forecasts
    revenue_forecast = kpi_service.generate_forecast(
        current_user.company_id, KPICategory.REVENUE, KPIPeriod.MONTHLY, 3
    )
    
    # Calculate growth rates
    revenue_kpi = next((kpi for kpi in current_kpis if kpi.category == KPICategory.REVENUE), None)
    revenue_growth = 0
    if revenue_kpi and revenue_kpi.previous_value and revenue_kpi.previous_value > 0:
        revenue_growth = ((revenue_kpi.value - revenue_kpi.previous_value) / revenue_kpi.previous_value) * 100
    
    return {
        "current_kpis": [kpi for kpi in current_kpis],
        "trends": {
            "revenue": revenue_trend,
            "expenses": expense_trend
        },
        "forecasts": {
            "revenue": revenue_forecast.get("forecast_data", [])[:3] if "forecast_data" in revenue_forecast else []
        },
        "insights": {
            "revenue_growth": round(revenue_growth, 2),
            "profit_margin": _calculate_profit_margin(current_kpis),
            "trend_direction": _get_trend_direction(revenue_trend)
        }
    }

def _calculate_profit_margin(kpis):
    """Calculate profit margin from KPIs."""
    revenue_kpi = next((kpi for kpi in kpis if kpi.category == KPICategory.REVENUE), None)
    profit_kpi = next((kpi for kpi in kpis if kpi.category == KPICategory.PROFIT), None)
    
    if revenue_kpi and profit_kpi and revenue_kpi.value > 0:
        return round((profit_kpi.value / revenue_kpi.value) * 100, 2)
    return 0

def _get_trend_direction(trend_data):
    """Determine trend direction from trend data."""
    if len(trend_data) < 2:
        return "stable"
    
    recent_values = [float(point["value"]) for point in trend_data[-3:]]
    if len(recent_values) < 2:
        return "stable"
    
    avg_recent = sum(recent_values) / len(recent_values)
    previous_values = [float(point["value"]) for point in trend_data[-6:-3]] if len(trend_data) >= 6 else recent_values
    avg_previous = sum(previous_values) / len(previous_values)
    
    if avg_recent > avg_previous * 1.05:
        return "increasing"
    elif avg_recent < avg_previous * 0.95:
        return "decreasing"
    else:
        return "stable"
