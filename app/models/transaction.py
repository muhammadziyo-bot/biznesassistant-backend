from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionCategory(enum.Enum):
    # Income categories
    SALES = "sales"
    SERVICES = "services"
    INVESTMENT = "investment"
    OTHER_INCOME = "other_income"
    
    # Expense categories
    SALARIES = "salaries"
    RENT = "rent"
    UTILITIES = "utilities"
    MARKETING = "marketing"
    SUPPLIES = "supplies"
    TAXES = "taxes"
    OTHER_EXPENSE = "other_expense"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    category = Column(Enum(TransactionCategory), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(DateTime(timezone=True), nullable=False)
    vat_included = Column(String, default=True)
    vat_amount = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    reference_number = Column(String, nullable=True)
    attachment_url = Column(String, nullable=True)
    is_reconciled = Column(String, default=False)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)  # Multi-tenant support
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    company = relationship("Company", back_populates="transactions")
    tenant = relationship("Tenant", back_populates="transactions")
    contact = relationship("Contact", back_populates="transactions")
    invoice = relationship("Invoice", back_populates="transactions")
