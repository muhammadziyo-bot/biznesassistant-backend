"""
Task model for BiznesAssistant
Supports task management, assignment, and tracking
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class TaskStatus(enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(Base):
    __tablename__ = "app.tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Task metadata
    status = Column(String(20), default=TaskStatus.TODO.value, nullable=False)
    priority = Column(String(20), default=TaskPriority.MEDIUM.value, nullable=False)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("app.app_users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("app.app_users.id"), nullable=False)
    
    # Dates
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Multi-tenant support
    tenant_id = Column(Integer, ForeignKey("app.tenants.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("app.companies.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tasks")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tasks")
    tenant = relationship("Tenant", back_populates="tasks")
    company = relationship("Company", back_populates="tasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}', assigned_to={self.assigned_to})>"

class TaskComment(Base):
    """Comments and updates on tasks"""
    __tablename__ = "app.task_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("app.tasks.id"), nullable=False)
    content = Column(Text, nullable=False)
    
    # Comment metadata
    created_by = Column(Integer, ForeignKey("app.app_users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="task_comments")
    
    def __repr__(self):
        return f"<TaskComment(id={self.id}, task_id={self.task_id}, author_id={self.created_by})>"
