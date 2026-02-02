"""
Simple ML Service for BiznesAssistant
Focus on practical, high-value ML features for Uzbek SMEs
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
import re

from app.models.transaction import Transaction, TransactionType
from app.models.invoice import Invoice, InvoiceStatus
from app.models.contact import Contact

class SimpleMLService:
    """Simple, high-value ML service for Uzbek businesses"""
    
    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id
        
        # Uzbek business patterns for categorization
        self.category_patterns = {
            # Digital payments
            "digital_payments": [
                "click", "payme", "uzum", "anor", "paynet", "to'lov", "pul", "transfer",
                "клик", "пайме", "узум", "анор", "платеж", "деньги", "перевод"
            ],
            
            # Salaries
            "salaries": [
                "salary", "maosh", "oylik", "ish haqi", "zarplata", "зарплата",
                "оклад", "доход", "payment", "to'lov"
            ],
            
            # Rent
            "rent": [
                "rent", "ijara", "arenda", "kvartira", "office", "ofis", "joy",
                "аренда", "квартира", "офис", "помещение"
            ],
            
            # Utilities
            "utilities": [
                "electricity", "suv", "gaz", "internet", "telefon", "komunal",
                "электричество", "вода", "газ", "телефон", "коммунальные"
            ],
            
            # Supplies
            "supplies": [
                "material", "xom ashyo", "taminot", "supply", "inventory", "zakup",
                "сырье", "материал", "закупка", "инвентарь", "товар"
            ],
            
            # Marketing
            "marketing": [
                "reklama", "marketing", "advertisement", "promo", "kampaniya",
                "реклама", "маркетинг", "продвижение", "кампания"
            ],
            
            # Taxes
            "taxes": [
                "tax", "soliq", "nds", "vat", "nalog", "налог", "ндс"
            ],
            
            # Transportation
            "transportation": [
                "taxi", "transport", "yuk", "delivery", "yetkazish", "avto",
                "такси", "транспорт", "груз", "доставка", "авто"
            ]
        }
    
    def suggest_category(self, description: str, amount: float, transaction_type: str) -> Dict[str, Any]:
        """
        Suggest transaction category based on description and amount
        Uses pattern matching + business logic
        """
        description_lower = description.lower()
        
        # Pattern matching
        for category, keywords in self.category_patterns.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    confidence = self._calculate_confidence(description, keyword, amount)
                    return {
                        "category": category,
                        "confidence": confidence,
                        "method": "pattern",
                        "matched_keyword": keyword
                    }
        
        # Amount-based heuristics
        amount_suggestion = self._suggest_by_amount(amount, transaction_type)
        if amount_suggestion:
            return amount_suggestion
        
        # Default category
        default_category = "other_income" if transaction_type == "income" else "other_expense"
        return {
            "category": default_category,
            "confidence": 0.5,
            "method": "default"
        }
    
    def _calculate_confidence(self, description: str, keyword: str, amount: float) -> float:
        """Calculate confidence score for pattern match"""
        base_confidence = 0.85
        
        # Higher confidence for exact matches
        if keyword.lower() in description.lower():
            base_confidence += 0.10
        
        # Adjust based on context
        if len(description.split()) <= 3:  # Short descriptions
            base_confidence += 0.05
        
        return min(0.95, base_confidence)
    
    def _suggest_by_amount(self, amount: float, transaction_type: str) -> Optional[Dict[str, Any]]:
        """Suggest category based on amount patterns"""
        # Common salary ranges (UZS)
        if transaction_type == "expense" and 1000000 <= amount <= 10000000:
            return {
                "category": "salaries",
                "confidence": 0.7,
                "method": "amount_pattern"
            }
        
        # Common utility ranges
        if transaction_type == "expense" and 50000 <= amount <= 500000:
            return {
                "category": "utilities",
                "confidence": 0.6,
                "method": "amount_pattern"
            }
        
        return None
    
    def get_customer_reliability(self, customer_id: int) -> Dict[str, Any]:
        """
        Calculate customer payment reliability score
        Based on payment history and patterns
        """
        # Get customer's invoice history (match by customer_name since no customer_id field)
        customer = self.db.query(Contact).filter(
            and_(
                Contact.id == customer_id,
                Contact.tenant_id == self.tenant_id
            )
        ).first()
        
        if not customer:
            return {
                "score": 70,
                "class": "medium",
                "avg_days": 15,
                "last_payment": "Mijoz topilmadi",
                "total_invoices": 0,
                "paid_invoices": 0
            }
        
        invoices = self.db.query(Invoice).filter(
            and_(
                Invoice.customer_name == customer.name,
                Invoice.tenant_id == self.tenant_id
            )
        ).all()
        
        if not invoices:
            return {
                "score": 70,  # Neutral score for new customers
                "class": "medium",
                "avg_days": 15,
                "last_payment": "Yangi mijoz",
                "total_invoices": 0,
                "paid_invoices": 0
            }
        
        # Calculate payment metrics
        total_invoices = len(invoices)
        paid_invoices = len([inv for inv in invoices if inv.status == "paid"])
        overdue_invoices = len([inv for inv in invoices if inv.status == "overdue"])
        
        # Calculate reliability score
        if total_invoices == 0:
            base_score = 70
        else:
            payment_rate = paid_invoices / total_invoices
            base_score = payment_rate * 100
            
            # Penalty for overdue invoices
            if overdue_invoices > 0:
                base_score -= (overdue_invoices / total_invoices) * 30
        
        score = max(0, min(95, base_score))
        
        # Determine reliability class
        if score >= 80:
            reliability_class = "high"
        elif score >= 60:
            reliability_class = "medium"
        else:
            reliability_class = "low"
        
        # Calculate average payment days
        avg_days = self._calculate_avg_payment_days(invoices)
        
        # Get last payment info
        last_payment_info = self._get_last_payment_info(invoices)
        
        return {
            "score": round(score),
            "class": reliability_class,
            "avg_days": avg_days,
            "last_payment": last_payment_info,
            "total_invoices": total_invoices,
            "paid_invoices": paid_invoices,
            "overdue_invoices": overdue_invoices
        }
    
    def _calculate_avg_payment_days(self, invoices: List[Invoice]) -> int:
        """Calculate average days to payment"""
        paid_invoices = [inv for inv in invoices if inv.status == "paid" and inv.paid_date]
        
        if not paid_invoices:
            return 15  # Default estimate
        
        total_days = 0
        for invoice in paid_invoices:
            if invoice.issue_date and invoice.paid_date:
                days = (invoice.paid_date - invoice.issue_date).days
                total_days += days
        
        return round(total_days / len(paid_invoices)) if paid_invoices else 15
    
    def _get_last_payment_info(self, invoices: List[Invoice]) -> str:
        """Get information about last payment"""
        paid_invoices = [inv for inv in invoices if inv.status == "paid" and inv.paid_date]
        
        if not paid_invoices:
            return "To'lovlar yo'q"
        
        last_invoice = max(paid_invoices, key=lambda x: x.paid_date)
        days_ago = (datetime.now().date() - last_invoice.paid_date).days
        
        if days_ago == 0:
            return "Bugun"
        elif days_ago == 1:
            return "Kecha"
        elif days_ago <= 7:
            return f"{days_ago} kun oldin"
        elif days_ago <= 30:
            return f"{days_ago} kun oldin"
        else:
            return f"{days_ago // 30} oy oldin"
    
    def get_business_insights(self, days: int = 30) -> Dict[str, Any]:
        """
        Get general business insights for the tenant
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get transactions in period
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.tenant_id == self.tenant_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).all()
        
        # Calculate insights
        total_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
        total_expenses = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
        net_profit = total_income - total_expenses
        
        # Top expense categories
        expense_by_category = {}
        for t in transactions:
            if t.type == TransactionType.EXPENSE:
                expense_by_category[t.category] = expense_by_category.get(t.category, 0) + t.amount
        
        top_expenses = sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "period_days": days,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_profit": net_profit,
            "profit_margin": (net_profit / total_income * 100) if total_income > 0 else 0,
            "transaction_count": len(transactions),
            "top_expense_categories": top_expenses,
            "avg_daily_expense": total_expenses / days if days > 0 else 0
        }
