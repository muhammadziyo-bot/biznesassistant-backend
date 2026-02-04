from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class LeadStatus(enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"

class LeadSource(enum.Enum):
    WEBSITE = "website"
    SOCIAL_MEDIA = "social_media"
    REFERRAL = "referral"
    COLD_CALL = "cold_call"
    EMAIL = "email"
    ADVERTISEMENT = "advertisement"
    OTHER = "other"

class Lead(Base):
    __tablename__ = "app.leads"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    source = Column(Enum(LeadSource), nullable=True)
    
    # Lead value and probability
    estimated_value = Column(Numeric(15, 2), nullable=True)
    probability = Column(Numeric(5, 2), default=0)  # percentage
    
    # Contact information
    contact_name = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    
    # Address
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    region = Column(String, nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # comma-separated tags
    
    # Important dates
    follow_up_date = Column(DateTime(timezone=True), nullable=True)
    converted_date = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    assigned_user_id = Column(Integer, ForeignKey("app.app_users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("app.companies.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("app.tenants.id"), nullable=True)  # Multi-tenant support
    contact_id = Column(Integer, ForeignKey("app.contacts.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="leads")
    assigned_user = relationship("User")
    tenant = relationship("Tenant", back_populates="leads")
    contact = relationship("Contact", back_populates="leads")
    deals = relationship("Deal", back_populates="lead")
