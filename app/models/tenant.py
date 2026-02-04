from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Tenant(Base):
    """Multi-tenant model for business isolation"""
    __tablename__ = "app.tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    tax_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    industry = Column(String(100), nullable=True)
    employee_count = Column(Integer, nullable=True)
    
    # Subscription and billing
    subscription_tier = Column(String(50), default="basic")  # basic, professional, enterprise
    subscription_status = Column(String(50), default="trial")  # trial, active, cancelled, expired
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    subscription_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # System fields
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    companies = relationship("Company", back_populates="tenant")
    transactions = relationship("Transaction", back_populates="tenant")
    invoices = relationship("Invoice", back_populates="tenant")
    contacts = relationship("Contact", back_populates="tenant")
    leads = relationship("Lead", back_populates="tenant")
    deals = relationship("Deal", back_populates="tenant")
    kpis = relationship("KPI", back_populates="tenant")
    
    # New model relationships
    tasks = relationship("Task", back_populates="tenant")
    templates = relationship("Template", back_populates="tenant")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name='{self.name}', tax_id='{self.tax_id}')>"
