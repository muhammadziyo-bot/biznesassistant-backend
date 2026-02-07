from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, nullable=False, index=True)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Customer information
    customer_name = Column(String, nullable=False)
    customer_tax_id = Column(String, nullable=True)
    customer_address = Column(Text, nullable=True)
    customer_phone = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    
    # Financial details
    subtotal = Column(Numeric(15, 2), nullable=False)
    vat_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    paid_amount = Column(Numeric(15, 2), default=0, nullable=True)
    remaining_amount = Column(Numeric(15, 2), nullable=False)
    
    # Dates
    issue_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    paid_date = Column(DateTime(timezone=True), nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    template_name = Column(String, default="default")
    
    # Payment information
    payment_method = Column(String, nullable=True)  # cash, click, payme, bank_transfer
    payment_reference = Column(String, nullable=True)
    
    # Recurring invoice settings
    is_recurring = Column(Boolean, default=False)
    recurring_interval = Column(String, nullable=True)  # daily, weekly, monthly, yearly
    recurring_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    created_by_id = Column(Integer, ForeignKey("app_users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)  # Multi-tenant support
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by = relationship("User", back_populates="invoices")
    company = relationship("Company", back_populates="invoices")
    tenant = relationship("Tenant", back_populates="invoices")
    contact = relationship("Contact", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    quantity = Column(Numeric(15, 2), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    discount = Column(Numeric(5, 2), default=0)  # percentage
    vat_rate = Column(Numeric(5, 2), default=12)  # percentage
    line_total = Column(Numeric(15, 2), nullable=False)
    total_price = Column(Numeric(15, 2), nullable=True)  # Frontend compatibility field
    
    # Foreign keys
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")
