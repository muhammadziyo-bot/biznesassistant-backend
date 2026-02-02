"""
KPI Data Populator for BiznesAssistant
Populates KPI table with real business data from transactions, invoices, and CRM
"""

from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta, date
from app.models.transaction import Transaction, TransactionType
from app.models.invoice import Invoice, InvoiceStatus
from app.models.contact import Contact
from app.models.lead import Lead, LeadStatus
from app.models.deal import Deal, DealStatus
from app.models.kpi import KPI, KPICategory, KPIPeriod
from app.models.user import User

class KPIPopulator:
    """Service to populate KPI data from business operations"""
    
    def __init__(self, db: Session, tenant_id: int, company_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.company_id = company_id
    
    def populate_all_kpis(self, period: KPIPeriod = KPIPeriod.MONTHLY):
        """Populate all KPI categories for the given period"""
        today = datetime.utcnow().date()
        
        # Calculate date range based on period
        start_date, end_date = self._get_date_range(today, period)
        
        # Clear existing KPIs for this period
        self._clear_existing_kpis(period, start_date, end_date)
        
        # Populate each KPI category
        kpi_data = {}
        
        # Revenue KPIs
        kpi_data.update(self._calculate_revenue_kpis(start_date, end_date, period))
        
        # Expense KPIs
        kpi_data.update(self._calculate_expense_kpis(start_date, end_date, period))
        
        # Profit KPIs
        kpi_data.update(self._calculate_profit_kpis(start_date, end_date, period))
        
        # Customer KPIs
        kpi_data.update(self._calculate_customer_kpis(start_date, end_date, period))
        
        # Invoice KPIs
        kpi_data.update(self._calculate_invoice_kpis(start_date, end_date, period))
        
        # Lead KPIs
        kpi_data.update(self._calculate_lead_kpis(start_date, end_date, period))
        
        # Deal KPIs
        kpi_data.update(self._calculate_deal_kpis(start_date, end_date, period))
        
        # Save all KPIs
        self._save_kpis(kpi_data, period, start_date, end_date)
        
        return kpi_data
    
    def _get_date_range(self, today: date, period: KPIPeriod) -> tuple[date, date]:
        """Get start and end date for the given period"""
        if period == KPIPeriod.DAILY:
            start_date = today
            end_date = today
        elif period == KPIPeriod.WEEKLY:
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == KPIPeriod.MONTHLY:
            start_date = today.replace(day=1)
            # Get last day of month
            next_month = start_date.replace(month=start_date.month % 12 + 1, day=1)
            end_date = next_month - timedelta(days=1)
        elif period == KPIPeriod.QUARTERLY:
            quarter = (today.month - 1) // 3 + 1
            start_date = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            end_date = start_date.replace(month=start_date.month + 2, day=31)
        else:  # YEARLY
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        
        return start_date, end_date
    
    def _clear_existing_kpis(self, period: KPIPeriod, start_date: date, end_date: date):
        """Clear existing KPIs for the given period"""
        self.db.query(KPI).filter(
            KPI.tenant_id == self.tenant_id,
            KPI.company_id == self.company_id,
            KPI.period == period.value,
            KPI.date.between(start_date, end_date)
        ).delete()
        self.db.commit()
    
    def _calculate_revenue_kpis(self, start_date: date, end_date: date, period: KPIPeriod) -> Dict[str, Any]:
        """Calculate revenue-related KPIs"""
        # Total revenue from income transactions
        revenue_query = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.tenant_id == self.tenant_id,
            Transaction.company_id == self.company_id,
            Transaction.type == TransactionType.INCOME,
            func.date(Transaction.created_at).between(start_date, end_date)
        )
        
        total_revenue = revenue_query.scalar() or 0
        
        # Revenue from paid invoices
        invoice_revenue_query = self.db.query(func.sum(Invoice.total_amount)).filter(
            Invoice.tenant_id == self.tenant_id,
            Invoice.company_id == self.company_id,
            Invoice.status == InvoiceStatus.PAID,
            func.date(Invoice.created_at).between(start_date, end_date)
        )
        
        invoice_revenue = invoice_revenue_query.scalar() or 0
        
        return {
            "revenue": {
                "value": float(total_revenue + invoice_revenue),
                "previous_value": self._get_previous_period_value(KPICategory.REVENUE, period),
                "target_value": self._get_target_value(KPICategory.REVENUE, period)
            }
        }
    
    def _calculate_expense_kpis(self, start_date: date, end_date: date, period: KPIPeriod) -> Dict[str, Any]:
        """Calculate expense-related KPIs"""
        expense_query = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.tenant_id == self.tenant_id,
            Transaction.company_id == self.company_id,
            Transaction.type == TransactionType.EXPENSE,
            func.date(Transaction.created_at).between(start_date, end_date)
        )
        
        total_expenses = expense_query.scalar() or 0
        
        return {
            "expenses": {
                "value": float(total_expenses),
                "previous_value": self._get_previous_period_value(KPICategory.EXPENSES, period),
                "target_value": self._get_target_value(KPICategory.EXPENSES, period)
            }
        }
    
    def _calculate_profit_kpis(self, start_date: date, end_date: date, period: KPIPeriod) -> Dict[str, Any]:
        """Calculate profit-related KPIs"""
        # Get revenue and expenses for profit calculation
        revenue_query = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.tenant_id == self.tenant_id,
            Transaction.company_id == self.company_id,
            Transaction.type == TransactionType.INCOME,
            func.date(Transaction.created_at).between(start_date, end_date)
        )
        
        expense_query = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.tenant_id == self.tenant_id,
            Transaction.company_id == self.company_id,
            Transaction.type == TransactionType.EXPENSE,
            func.date(Transaction.created_at).between(start_date, end_date)
        )
        
        total_revenue = revenue_query.scalar() or 0
        total_expenses = expense_query.scalar() or 0
        net_profit = total_revenue - total_expenses
        
        return {
            "profit": {
                "value": float(net_profit),
                "previous_value": self._get_previous_period_value(KPICategory.PROFIT, period),
                "target_value": self._get_target_value(KPICategory.PROFIT, period)
            }
        }
    
    def _calculate_customer_kpis(self, start_date: date, end_date: date, period: KPIPeriod) -> Dict[str, Any]:
        """Calculate customer-related KPIs"""
        # Total customers
        customer_count = self.db.query(func.count(Contact.id)).filter(
            Contact.tenant_id == self.tenant_id,
            Contact.company_id == self.company_id,
            func.date(Contact.created_at).between(start_date, end_date)
        ).scalar() or 0
        
        # New customers this period
        new_customers = self.db.query(func.count(Contact.id)).filter(
            Contact.tenant_id == self.tenant_id,
            Contact.company_id == self.company_id,
            func.date(Contact.created_at).between(start_date, end_date)
        ).scalar() or 0
        
        return {
            "customers": {
                "value": customer_count,
                "previous_value": self._get_previous_period_value(KPICategory.CUSTOMERS, period),
                "target_value": self._get_target_value(KPICategory.CUSTOMERS, period),
                "new_customers": new_customers
            }
        }
    
    def _calculate_invoice_kpis(self, start_date: date, end_date: date, period: KPIPeriod) -> Dict[str, Any]:
        """Calculate invoice-related KPIs"""
        # Total invoices
        total_invoices = self.db.query(func.count(Invoice.id)).filter(
            Invoice.tenant_id == self.tenant_id,
            Invoice.company_id == self.company_id,
            func.date(Invoice.created_at).between(start_date, end_date)
        ).scalar() or 0
        
        # Paid invoices
        paid_invoices = self.db.query(func.count(Invoice.id)).filter(
            Invoice.tenant_id == self.tenant_id,
            Invoice.company_id == self.company_id,
            Invoice.status == InvoiceStatus.PAID,
            func.date(Invoice.created_at).between(start_date, end_date)
        ).scalar() or 0
        
        # Overdue invoices
        overdue_invoices = self.db.query(func.count(Invoice.id)).filter(
            Invoice.tenant_id == self.tenant_id,
            Invoice.company_id == self.company_id,
            Invoice.status == InvoiceStatus.SENT,
            Invoice.due_date < datetime.utcnow().date()
        ).scalar() or 0
        
        return {
            "invoices": {
                "value": total_invoices,
                "previous_value": self._get_previous_period_value(KPICategory.INVOICES, period),
                "target_value": self._get_target_value(KPICategory.INVOICES, period),
                "paid_count": paid_invoices,
                "overdue_count": overdue_invoices
            }
        }
    
    def _calculate_lead_kpis(self, start_date: date, end_date: date, period: KPIPeriod) -> Dict[str, Any]:
        """Calculate lead-related KPIs"""
        # Total leads
        total_leads = self.db.query(func.count(Lead.id)).filter(
            Lead.tenant_id == self.tenant_id,
            Lead.company_id == self.company_id,
            func.date(Lead.created_at).between(start_date, end_date)
        ).scalar() or 0
        
        # Converted leads
        converted_leads = self.db.query(func.count(Lead.id)).filter(
            Lead.tenant_id == self.tenant_id,
            Lead.company_id == self.company_id,
            Lead.status == LeadStatus.CONVERTED,
            func.date(Lead.created_at).between(start_date, end_date)
        ).scalar() or 0
        
        return {
            "leads": {
                "value": total_leads,
                "previous_value": self._get_previous_period_value(KPICategory.LEADS, period),
                "target_value": self._get_target_value(KPICategory.LEADS, period),
                "converted_count": converted_leads
            }
        }
    
    def _calculate_deal_kpis(self, start_date: date, end_date: date, period: KPIPeriod) -> Dict[str, Any]:
        """Calculate deal-related KPIs"""
        # Total deals
        total_deals = self.db.query(func.count(Deal.id)).filter(
            Deal.tenant_id == self.tenant_id,
            Deal.company_id == self.company_id,
            func.date(Deal.created_at).between(start_date, end_date)
        ).scalar() or 0
        
        # Won deals
        won_deals = self.db.query(func.count(Deal.id)).filter(
            Deal.tenant_id == self.tenant_id,
            Deal.company_id == self.company_id,
            Deal.status == DealStatus.WON,
            func.date(Deal.created_at).between(start_date, end_date)
        ).scalar() or 0
        
        return {
            "deals": {
                "value": total_deals,
                "previous_value": self._get_previous_period_value(KPICategory.DEALS, period),
                "target_value": self._get_target_value(KPICategory.DEALS, period),
                "won_count": won_deals
            }
        }
    
    def _get_previous_period_value(self, category: KPICategory, period: KPIPeriod) -> float:
        """Get KPI value from previous period for comparison"""
        today = datetime.utcnow().date()
        
        # Calculate previous period date range
        if period == KPIPeriod.DAILY:
            previous_start = today - timedelta(days=1)
            previous_end = previous_start
        elif period == KPIPeriod.WEEKLY:
            previous_start = today - timedelta(days=7)
            previous_end = previous_start + timedelta(days=6)
        elif period == KPIPeriod.MONTHLY:
            previous_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            previous_end = previous_start.replace(month=previous_start.month % 12 + 1, day=1) - timedelta(days=1)
        elif period == KPIPeriod.QUARTERLY:
            current_quarter = (today.month - 1) // 3 + 1
            if current_quarter == 1:
                previous_start = today.replace(year=today.year - 1, month=10, day=1)
                previous_end = today.replace(year=today.year - 1, month=12, day=31)
            else:
                previous_start = today.replace(month=(current_quarter - 2) * 3 + 1, day=1)
                previous_end = previous_start.replace(month=previous_start.month + 2, day=31)
        else:  # YEARLY
            previous_start = today.replace(year=today.year - 1, month=1, day=1)
            previous_end = today.replace(year=today.year - 1, month=12, day=31)
        
        previous_kpi = self.db.query(KPI).filter(
            KPI.tenant_id == self.tenant_id,
            KPI.company_id == self.company_id,
            KPI.category == category.value,
            KPI.period == period.value,
            KPI.date.between(previous_start, previous_end)
        ).first()
        
        return float(previous_kpi.value) if previous_kpi else 0.0
    
    def _get_target_value(self, category: KPICategory, period: KPIPeriod) -> float:
        """Get target value for KPI (could be user-defined or calculated)"""
        # For now, return a simple target based on previous period + 10%
        previous_value = self._get_previous_period_value(category, period)
        return previous_value * 1.1 if previous_value > 0 else 1000.0
    
    def _save_kpis(self, kpi_data: Dict[str, Any], period: KPIPeriod, start_date: date, end_date: date):
        """Save all KPIs to database"""
        for category_name, data in kpi_data.items():
            kpi = KPI(
                tenant_id=self.tenant_id,
                company_id=self.company_id,
                category=KPICategory(category_name),
                period=period,
                date=start_date,
                value=data["value"],
                previous_value=data.get("previous_value", 0),
                target_value=data.get("target_value", 0)
            )
            
            self.db.add(kpi)
        
        self.db.commit()
