from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class ActivityType(enum.Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    TASK = "task"
    NOTE = "note"
    SMS = "sms"
    TELEGRAM = "telegram"
    OTHER = "other"

class ActivityStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(ActivityType), nullable=False)
    status = Column(Enum(ActivityStatus), default=ActivityStatus.PENDING)
    
    # Date and time
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    completed_date = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)  # for calls, meetings
    
    # Location and details
    location = Column(String, nullable=True)
    outcome = Column(Text, nullable=True)
    
    # Priority
    priority = Column(String, default="medium")  # low, medium, high, urgent
    
    # Reminder settings
    reminder_date = Column(DateTime(timezone=True), nullable=True)
    reminder_sent = Column(String, default=False)
    
    # Additional information
    notes = Column(Text, nullable=True)
    
    # Foreign keys (polymorphic relationships)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Related entities (can be null)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    company = relationship("Company")
    contact = relationship("Contact")
    lead = relationship("Lead")
    deal = relationship("Deal")
