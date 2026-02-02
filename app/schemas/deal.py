from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.deal import DealStatus, DealPriority

class DealBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: DealStatus = DealStatus.PROSPECTING
    priority: DealPriority = DealPriority.MEDIUM
    deal_value: Optional[Decimal] = None
    expected_close_date: Optional[datetime] = None
    probability: Optional[Decimal] = 0
    confidence_level: Optional[Decimal] = 0
    primary_contact: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    company_name: Optional[str] = None
    products_services: Optional[str] = None
    next_steps: Optional[str] = None
    lost_reason: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None

class DealCreate(DealBase):
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None

class DealUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DealStatus] = None
    priority: Optional[DealPriority] = None
    deal_value: Optional[Decimal] = None
    expected_close_date: Optional[datetime] = None
    probability: Optional[Decimal] = None
    confidence_level: Optional[Decimal] = None
    primary_contact: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    company_name: Optional[str] = None
    products_services: Optional[str] = None
    next_steps: Optional[str] = None
    lost_reason: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None

class DealResponse(DealBase):
    id: int
    company_id: int
    assigned_user_id: int
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None
    actual_close_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
