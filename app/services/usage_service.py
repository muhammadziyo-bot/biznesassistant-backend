"""
Usage tracking and limit enforcement service
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.user import User
from app.models.company import Company
from app.models.transaction import Transaction
from app.models.invoice import Invoice
from app.models.task import Task
from app.models.tenant import Tenant

class UsageService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_current_usage(self, company_id: int) -> Dict[str, int]:
        """Get current monthly usage for a company."""
        today = datetime.utcnow().date()
        start_of_month = today.replace(day=1)
        
        # Count transactions this month
        transaction_count = self.db.query(func.count(Transaction.id)).filter(
            and_(
                Transaction.company_id == company_id,
                Transaction.date >= start_of_month,
                Transaction.date <= today
            )
        ).scalar() or 0
        
        # Count invoices this month
        invoice_count = self.db.query(func.count(Invoice.id)).filter(
            and_(
                Invoice.company_id == company_id,
                Invoice.created_at >= start_of_month,
                Invoice.created_at <= today
            )
        ).scalar() or 0
        
        # Count tasks this month
        task_count = self.db.query(func.count(Task.id)).filter(
            and_(
                Task.company_id == company_id,
                Task.created_at >= start_of_month,
                Task.created_at <= today
            )
        ).scalar() or 0
        
        return {
            "transactions": transaction_count,
            "invoices": invoice_count,
            "tasks": task_count
        }
    
    def get_plan_limits(self, subscription_tier: str) -> Dict[str, int]:
        """Get usage limits for a subscription tier."""
        limits = {
            "freemium": {
                "transactions": 30,
                "invoices": 15,
                "tasks": 25
            },
            "professional": {
                "transactions": -1,  # Unlimited
                "invoices": -1,
                "tasks": -1
            },
            "enterprise": {
                "transactions": -1,
                "invoices": -1,
                "tasks": -1
            },
            "premium": {
                "transactions": -1,
                "invoices": -1,
                "tasks": -1
            }
        }
        return limits.get(subscription_tier, limits["freemium"])
    
    def check_limits(self, company_id: int, subscription_tier: str) -> Dict[str, any]:
        """Check if company has exceeded their limits."""
        current_usage = self.get_current_usage(company_id)
        plan_limits = self.get_plan_limits(subscription_tier)
        
        status = {
            "can_create_transaction": True,
            "can_create_invoice": True,
            "can_create_task": True,
            "usage": current_usage,
            "limits": plan_limits,
            "needs_upgrade": False
        }
        
        # Check each limit (only for limited plans)
        if plan_limits["transactions"] != -1:
            if current_usage["transactions"] >= plan_limits["transactions"]:
                status["can_create_transaction"] = False
                status["needs_upgrade"] = True
        
        if plan_limits["invoices"] != -1:
            if current_usage["invoices"] >= plan_limits["invoices"]:
                status["can_create_invoice"] = False
                status["needs_upgrade"] = True
        
        if plan_limits["tasks"] != -1:
            if current_usage["tasks"] >= plan_limits["tasks"]:
                status["can_create_task"] = False
                status["needs_upgrade"] = True
        
        return status
    
    def get_usage_percentage(self, current: int, limit: int) -> float:
        """Get usage as percentage of limit."""
        if limit == -1:  # Unlimited
            return 0.0
        return (current / limit) * 100 if limit > 0 else 100.0
