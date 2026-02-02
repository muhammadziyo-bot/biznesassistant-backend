from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.lead import LeadStatus, LeadSource

class LeadBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: LeadStatus = LeadStatus.NEW
    source: Optional[LeadSource] = None
    estimated_value: Optional[Decimal] = None
    probability: Optional[Decimal] = 0
    contact_name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    follow_up_date: Optional[datetime] = None

class LeadCreate(LeadBase):
    contact_id: Optional[int] = None

class LeadUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    estimated_value: Optional[Decimal] = None
    probability: Optional[Decimal] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    contact_id: Optional[int] = None

class LeadResponse(LeadBase):
    id: int
    company_id: int
    assigned_user_id: int
    contact_id: Optional[int] = None
    converted_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
