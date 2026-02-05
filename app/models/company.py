from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    tax_id = Column(String, unique=True, nullable=False)  # INN in Uzbekistan
    company_code = Column(String, unique=True, nullable=False, index=True)  # Unique company identifier
    address = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    bank_account = Column(String, nullable=True)
    mfo = Column(String, nullable=True)  # MFO code for Uzbek banks
    description = Column(Text, nullable=True)
    logo_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)  # Multi-tenant support
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="companies")
    users = relationship("User", back_populates="company")
    transactions = relationship("Transaction", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")
    contacts = relationship("Contact", back_populates="company")
    leads = relationship("Lead", back_populates="company")
    deals = relationship("Deal", back_populates="company")
    kpis = relationship("KPI", back_populates="company")
    kpi_trends = relationship("KPITrend", back_populates="company")
    kpi_alerts = relationship("KPIAlert", back_populates="company")
    
    # New model relationships
    tasks = relationship("Task", back_populates="company")
    templates = relationship("Template", back_populates="company")
