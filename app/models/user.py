from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class User(Base):
    """Application user - completely independent from Supabase auth"""
    __tablename__ = "app_users"
    
    id = Column(Integer, primary_key=True, index=True)
    supabase_auth_id = Column(UUID, nullable=True)  # Optional link to Supabase auth
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)  # Our own password management
    phone = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    language = Column(String, default="uz")  # uz, ru, en
    email_verification_token = Column(String, nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)  # Multi-tenant support
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="users")
    tenant = relationship("Tenant", back_populates="users")
    transactions = relationship("Transaction", back_populates="user")
    invoices = relationship("Invoice", back_populates="created_by")
    
    # Task relationships
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    created_tasks = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    task_comments = relationship("TaskComment", back_populates="author")
    
    # Template relationships
    templates = relationship("Template", back_populates="creator")
