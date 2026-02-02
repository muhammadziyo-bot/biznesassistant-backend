from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class TemplateBase(BaseModel):
    name: str
    type: str  # 'transaction' or 'invoice'
    description: Optional[str] = None
    is_recurring: bool = False
    recurring_interval: Optional[str] = None  # 'daily', 'weekly', 'monthly', 'yearly'
    recurring_day: Optional[int] = None
    data: Dict[str, Any]

class TemplateCreate(TemplateBase):
    pass

class TemplateResponse(TemplateBase):
    id: int
    created_by: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TemplateApply(BaseModel):
    custom_data: Optional[Dict[str, Any]] = None
