"""
KPI Population Routes for BiznesAssistant
Endpoints to trigger KPI data population and management
"""

from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.kpi import KPIPeriod
from app.services.kpi_populator import KPIPopulator
from app.utils.auth import get_current_active_user, get_current_tenant

router = APIRouter()

@router.post("/populate")
async def populate_kpis(
    period: KPIPeriod = KPIPeriod.MONTHLY,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Trigger KPI population for the given period."""
    company_id = current_user.company_id or 1
    
    # Create KPI populator
    populator = KPIPopulator(db, tenant_id, company_id)
    
    try:
        # Populate KPIs
        kpi_data = populator.populate_all_kpis(period)
        
        return {
            "message": f"KPIs populated successfully for {period.value}",
            "period": period.value,
            "categories_populated": list(kpi_data.keys()),
            "total_categories": len(kpi_data),
            "populated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to populate KPIs: {str(e)}"
        )

@router.post("/populate-all-periods")
async def populate_all_periods(
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Trigger KPI population for all periods."""
    company_id = current_user.company_id or 1
    
    # Create KPI populator
    populator = KPIPopulator(db, tenant_id, company_id)
    
    results = {}
    
    try:
        # Populate for all periods
        for period in KPIPeriod:
            kpi_data = populator.populate_all_kpis(period)
            results[period.value] = {
                "categories_populated": list(kpi_data.keys()),
                "total_categories": len(kpi_data)
            }
        
        return {
            "message": "KPIs populated for all periods",
            "results": results,
            "populated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to populate KPIs: {str(e)}"
        )

@router.get("/status")
async def get_population_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get KPI population status."""
    company_id = current_user.company_id or 1
    
    from app.models.kpi import KPI, KPICategory
    
    # Count KPIs by category and period
    kpi_counts = {}
    for category in KPICategory:
        category_counts = {}
        for period in KPIPeriod:
            count = db.query(KPI).filter(
                KPI.tenant_id == tenant_id,
                KPI.company_id == company_id,
                KPI.category == category,
                KPI.period == period
            ).count()
            category_counts[period.value] = count
        
        kpi_counts[category.value] = category_counts
    
    # Get latest population date
    latest_kpi = db.query(KPI).filter(
        KPI.tenant_id == tenant_id,
        KPI.company_id == company_id
    ).order_by(KPI.created_at.desc()).first()
    
    return {
        "kpi_counts": kpi_counts,
        "latest_population": latest_kpi.created_at.isoformat() if latest_kpi else None,
        "total_kpis": sum(counts.get("monthly", 0) for counts in kpi_counts.values())
    }
