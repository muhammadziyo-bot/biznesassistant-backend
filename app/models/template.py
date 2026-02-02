"""
Template model for BiznesAssistant
Supports transaction and invoice templates with recurring functionality
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class TemplateType(enum.Enum):
    TRANSACTION = "transaction"
    INVOICE = "invoice"

class RecurringInterval(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # 'transaction' or 'invoice'
    description = Column(Text, nullable=True)
    
    # Template data (JSON structure for transaction or invoice data)
    data = Column(JSON, nullable=False)
    
    # Recurring functionality
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurring_interval = Column(String(20), nullable=True)  # 'daily', 'weekly', 'monthly', 'yearly'
    recurring_day = Column(Integer, nullable=True)  # Day of month/week for recurring
    
    # Relationships
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="templates")
    tenant = relationship("Tenant", back_populates="templates")
    company = relationship("Company", back_populates="templates")
    schedules = relationship("RecurringSchedule", back_populates="template", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', type='{self.type}', tenant_id={self.tenant_id})>"

class RecurringSchedule(Base):
    """Track when recurring templates should be executed"""
    __tablename__ = "recurring_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    next_execution_date = Column(DateTime(timezone=True), nullable=False)
    last_execution_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    template = relationship("Template", back_populates="schedules")
    
    def __repr__(self):
        return f"<RecurringSchedule(id={self.id}, template_id={self.template_id}, next_execution={self.next_execution_date})>"
