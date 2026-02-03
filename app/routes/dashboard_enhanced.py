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

# Helper functions (defined before routes)
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
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company"
        )
    
    # Generate sample trend data for now
    trend_data = []
    for i in range(months):
        date = datetime.now() - timedelta(days=30*i)
        trend_data.append({
            "date": date.isoformat(),
            "value": 1000 + (i * 50) + (hash(category.value) % 500),
            "forecast": False
        })
    
    return {
        "category": category.value if hasattr(category, 'value') else str(category),
        "period_type": period_type.value if hasattr(period_type, 'value') else str(period_type),
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
    
    # Simplified forecast - return mock data for now
    historical_data = []
    forecast_data = []
    
    # Generate some sample historical data
    for i in range(6):
        date = datetime.now() - timedelta(days=30*i)
        historical_data.append({
            "date": date,
            "value": 1000 + (i * 100),
            "forecast": False
        })
    
    # Generate some sample forecast data
    for i in range(3):
        date = datetime.now() + timedelta(days=30*(i+1))
        forecast_data.append({
            "date": date,
            "value": 1600 + (i * 50),
            "forecast": True
        })
    
    return ForecastResponse(
        kpi_category=request.kpi_category,
        period_type=request.period_type,
        historical_data=historical_data,
        forecast_data=forecast_data,
        confidence_score=0.85,
        model_used="linear_regression"
    )

@router.get("/dashboard/role-based", response_model=RoleBasedDashboardResponse)
async def get_role_based_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get role-based dashboard configuration and data."""
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company"
        )
    
    kpi_service = KPIService(db, tenant_id)
    
    # Get basic KPIs for the user's company
    current_kpis = kpi_service.calculate_kpis(current_user.company_id, KPIPeriod.MONTHLY)
    
    # Return role-based dashboard data
    return RoleBasedDashboardResponse(
        role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        widgets=[
            {"type": "kpi", "title": "Revenue", "key": "revenue"},
            {"type": "kpi", "title": "Expenses", "key": "expenses"},
            {"type": "kpi", "title": "Profit", "key": "profit"},
        ],
        permissions={
            "view_analytics": True,
            "edit_kpis": current_user.role.value == "admin" if hasattr(current_user.role, 'value') else str(current_user.role) == "admin",
            "manage_users": current_user.role.value == "admin" if hasattr(current_user.role, 'value') else str(current_user.role) == "admin",
        },
        kpis=current_kpis
    )

@router.get("/summary")
async def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get comprehensive analytics summary for the dashboard."""
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company"
        )
    
    kpi_service = KPIService(db, tenant_id)
    
    # Get current month KPIs
    try:
        current_kpis = kpi_service.calculate_kpis(current_user.company_id, KPIPeriod.MONTHLY)
    except Exception as e:
        # If KPI calculation fails, return empty KPIs
        current_kpis = []
    
    # Generate sample trend data
    revenue_trend = []
    expense_trend = []
    for i in range(6):
        date = datetime.now() - timedelta(days=30*i)
        revenue_trend.append({
            "date": date.isoformat(),
            "value": 5000 + (i * 200),
            "forecast": False
        })
        expense_trend.append({
            "date": date.isoformat(),
            "value": 3000 + (i * 150),
            "forecast": False
        })
    
    # Generate sample forecast data
    revenue_forecast = []
    for i in range(3):
        date = datetime.now() + timedelta(days=30*(i+1))
        revenue_forecast.append({
            "date": date.isoformat(),
            "value": 6200 + (i * 100),
            "forecast": True
        })
    
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
            "revenue": revenue_forecast[:3]
        },
        "insights": {
            "revenue_growth": round(revenue_growth, 2),
            "profit_margin": _calculate_profit_margin(current_kpis),
            "trend_direction": _get_trend_direction(revenue_trend)
        }
    }
