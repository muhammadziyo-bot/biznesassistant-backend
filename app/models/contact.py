from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class ContactType(enum.Enum):
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    PARTNER = "partner"
    OTHER = "other"

class Contact(Base):
    __tablename__ = "biznes.contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    tax_id = Column(String, nullable=True)  # INN for Uzbekistan
    bank_name = Column(String, nullable=True)
    bank_account = Column(String, nullable=True)
    mfo = Column(String, nullable=True)
    website = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    type = Column(Enum(ContactType), default=ContactType.CUSTOMER)
    is_active = Column(Boolean, default=True)
    
    # Social media
    telegram = Column(String, nullable=True)
    instagram = Column(String, nullable=True)
    facebook = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    
    # Foreign keys
    assigned_user_id = Column(Integer, ForeignKey("biznes.app_users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("biznes.companies.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("biznes.tenants.id"), nullable=False)  # Multi-tenant support
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="contacts")
    assigned_user = relationship("User")
    tenant = relationship("Tenant", back_populates="contacts")
    transactions = relationship("Transaction", back_populates="contact")
    invoices = relationship("Invoice", back_populates="contact")
    leads = relationship("Lead", back_populates="contact")
    deals = relationship("Deal", back_populates="contact")
