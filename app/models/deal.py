from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class DealStatus(enum.Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class DealPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Deal(Base):
    __tablename__ = "app.deals"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(DealStatus), default=DealStatus.PROSPECTING)
    priority = Column(Enum(DealPriority), default=DealPriority.MEDIUM)
    
    # Financial information
    deal_value = Column(Numeric(15, 2), nullable=True)
    expected_close_date = Column(DateTime(timezone=True), nullable=True)
    actual_close_date = Column(DateTime(timezone=True), nullable=True)
    
    # Probability and confidence
    probability = Column(Numeric(5, 2), default=0)  # percentage
    confidence_level = Column(Numeric(5, 2), default=0)  # percentage
    
    # Contact information
    primary_contact = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    
    # Company information
    company_name = Column(String, nullable=True)
    
    # Deal details
    products_services = Column(Text, nullable=True)
    next_steps = Column(Text, nullable=True)
    lost_reason = Column(Text, nullable=True)
    
    # Tags and notes
    tags = Column(Text, nullable=True)  # comma-separated tags
    notes = Column(Text, nullable=True)
    
    # Foreign keys
    assigned_user_id = Column(Integer, ForeignKey("app.app_users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("app.companies.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("app.tenants.id"), nullable=True)  # Multi-tenant support
    contact_id = Column(Integer, ForeignKey("app.contacts.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("app.leads.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="deals")
    assigned_user = relationship("User")
    tenant = relationship("Tenant", back_populates="deals")
    contact = relationship("Contact", back_populates="deals")
    lead = relationship("Lead", back_populates="deals")
