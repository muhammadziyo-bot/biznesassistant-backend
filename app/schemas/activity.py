from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.activity import ActivityType, ActivityStatus

class ActivityBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: ActivityType
    status: ActivityStatus = ActivityStatus.PENDING
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    outcome: Optional[str] = None
    priority: str = "medium"
    reminder_date: Optional[datetime] = None
    notes: Optional[str] = None

class ActivityCreate(ActivityBase):
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None
    deal_id: Optional[int] = None

class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[ActivityType] = None
    status: Optional[ActivityStatus] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    outcome: Optional[str] = None
    priority: Optional[str] = None
    reminder_date: Optional[datetime] = None
    notes: Optional[str] = None
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None
    deal_id: Optional[int] = None

class ActivityResponse(ActivityBase):
    id: int
    user_id: int
    company_id: int
    contact_id: Optional[int] = None
    lead_id: Optional[int] = None
    deal_id: Optional[int] = None
    completed_date: Optional[datetime] = None
    reminder_sent: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
