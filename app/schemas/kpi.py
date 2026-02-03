from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# Import enums from models to ensure consistency
from app.models.kpi import KPICategory, KPIPeriod

class KPIBase(BaseModel):
    category: KPICategory
    period: KPIPeriod
    value: float
    previous_value: Optional[float] = None
    target_value: Optional[float] = None
    date: datetime

class KPICreate(KPIBase):
    company_id: int

class KPIResponse(KPIBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class KPITrendPoint(BaseModel):
    date: datetime
    value: float
    forecast: Optional[bool] = False

class KPITrendResponse(BaseModel):
    id: int
    company_id: int
    kpi_category: KPICategory
    period_type: KPIPeriod
    trend_data: List[KPITrendPoint]
    forecast_data: Optional[List[KPITrendPoint]] = None
    last_updated: datetime
    
    class Config:
        from_attributes = True

class KPIAlertResponse(BaseModel):
    id: int
    company_id: int
    kpi_category: KPICategory
    alert_type: str
    condition: str
    threshold_value: Optional[float] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class KPIDashboardResponse(BaseModel):
    kpis: List[KPIResponse]
    trends: List[KPITrendResponse]
    alerts: List[KPIAlertResponse]
    summary: Dict[str, Any]

class RoleBasedDashboardResponse(BaseModel):
    role: str
    widgets: List[Dict[str, Any]]
    permissions: Dict[str, bool]
    kpis: List[KPIResponse]

class ForecastRequest(BaseModel):
    kpi_category: KPICategory
    period_type: KPIPeriod
    forecast_periods: int = Field(default=3, ge=1, le=12)

class ForecastResponse(BaseModel):
    kpi_category: KPICategory
    period_type: KPIPeriod
    historical_data: List[KPITrendPoint]
    forecast_data: List[KPITrendPoint]
    confidence_score: float
    model_used: str
