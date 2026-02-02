from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import json
import statistics
from decimal import Decimal

from app.models.kpi import KPI, KPITrend, KPIAlert, KPICategory, KPIPeriod
from app.models.transaction import Transaction, TransactionType
from app.models.invoice import Invoice, InvoiceStatus
from app.models.contact import Contact
from app.models.lead import Lead, LeadStatus
from app.models.deal import Deal, DealStatus
from app.models.user import User, UserRole
from app.schemas.kpi import KPIResponse, KPITrendResponse, ForecastResponse

class KPIService:
    
    def __init__(self, db: Session, tenant_id: int = None):
        self.db = db
        self.tenant_id = tenant_id
    
    def _apply_tenant_filter(self, query, model_class):
        """Apply tenant filtering if tenant_id is set."""
        if self.tenant_id and hasattr(model_class, 'tenant_id'):
            return query.filter(model_class.tenant_id == self.tenant_id)
        return query
    
    def calculate_kpis(self, company_id: int, period: KPIPeriod = KPIPeriod.MONTHLY) -> List[KPIResponse]:
        """Calculate KPIs for a given company and period."""
        today = datetime.utcnow().date()
        
        # Calculate date ranges based on period
        if period == KPIPeriod.DAILY:
            start_date = today
            end_date = today
        elif period == KPIPeriod.WEEKLY:
            start_date = today - timedelta(days=7)
            end_date = today
        elif period == KPIPeriod.MONTHLY:
            start_date = today.replace(day=1)
            end_date = today
        elif period == KPIPeriod.QUARTERLY:
            quarter = (today.month - 1) // 3 + 1
            start_date = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            end_date = today
        else:  # YEARLY
            start_date = today.replace(month=1, day=1)
            end_date = today
        
        kpis = []
        
        # Revenue KPI
        revenue = self._calculate_revenue(company_id, start_date, end_date)
        previous_revenue = self._calculate_revenue(company_id, start_date - timedelta(days=30), start_date - timedelta(days=1))
        kpis.append(self._create_kpi(
            company_id, KPICategory.REVENUE, period, revenue, previous_revenue, start_date
        ))
        
        # Expenses KPI
        expenses = self._calculate_expenses(company_id, start_date, end_date)
        previous_expenses = self._calculate_expenses(company_id, start_date - timedelta(days=30), start_date - timedelta(days=1))
        kpis.append(self._create_kpi(
            company_id, KPICategory.EXPENSES, period, expenses, previous_expenses, start_date
        ))
        
        # Profit KPI
        profit = float(revenue) - float(expenses)
        previous_profit = float(previous_revenue) - float(previous_expenses)
        kpis.append(self._create_kpi(
            company_id, KPICategory.PROFIT, period, profit, previous_profit, start_date
        ))
        
        # Customers KPI
        customers = self._calculate_customers(company_id, start_date, end_date)
        previous_customers = self._calculate_customers(company_id, start_date - timedelta(days=30), start_date - timedelta(days=1))
        kpis.append(self._create_kpi(
            company_id, KPICategory.CUSTOMERS, period, customers, previous_customers, start_date
        ))
        
        # Invoices KPI
        invoices = self._calculate_invoices(company_id, start_date, end_date)
        previous_invoices = self._calculate_invoices(company_id, start_date - timedelta(days=30), start_date - timedelta(days=1))
        kpis.append(self._create_kpi(
            company_id, KPICategory.INVOICES, period, invoices, previous_invoices, start_date
        ))
        
        # Leads KPI
        leads = self._calculate_leads(company_id, start_date, end_date)
        previous_leads = self._calculate_leads(company_id, start_date - timedelta(days=30), start_date - timedelta(days=1))
        kpis.append(self._create_kpi(
            company_id, KPICategory.LEADS, period, leads, previous_leads, start_date
        ))
        
        # Deals KPI
        deals = self._calculate_deals(company_id, start_date, end_date)
        previous_deals = self._calculate_deals(company_id, start_date - timedelta(days=30), start_date - timedelta(days=1))
        kpis.append(self._create_kpi(
            company_id, KPICategory.DEALS, period, deals, previous_deals, start_date
        ))
        
        return kpis
    
    def _calculate_revenue(self, company_id: int, start_date: datetime.date, end_date: datetime.date) -> float:
        """Calculate total revenue for date range."""
        query = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.company_id == company_id,
                Transaction.type == TransactionType.INCOME,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        )
        query = self._apply_tenant_filter(query, Transaction)
        result = query.scalar()
        return float(result) if result is not None else 0.0
    
    def _calculate_expenses(self, company_id: int, start_date: datetime.date, end_date: datetime.date) -> float:
        """Calculate total expenses for date range."""
        query = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.company_id == company_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        )
        query = self._apply_tenant_filter(query, Transaction)
        result = query.scalar()
        return float(result) if result is not None else 0.0
    
    def _calculate_customers(self, company_id: int, start_date: datetime.date, end_date: datetime.date) -> float:
        """Calculate new customers for date range."""
        query = self.db.query(func.count(Contact.id)).filter(
            and_(
                Contact.company_id == company_id,
                Contact.created_at >= start_date,
                Contact.created_at <= end_date
            )
        )
        query = self._apply_tenant_filter(query, Contact)
        return query.scalar() or 0.0
    
    def _calculate_invoices(self, company_id: int, start_date: datetime.date, end_date: datetime.date) -> float:
        """Calculate total invoices for date range."""
        query = self.db.query(func.count(Invoice.id)).filter(
            and_(
                Invoice.company_id == company_id,
                Invoice.created_at >= start_date,
                Invoice.created_at <= end_date
            )
        )
        query = self._apply_tenant_filter(query, Invoice)
        return query.scalar() or 0.0
    
    def _calculate_leads(self, company_id: int, start_date: datetime.date, end_date: datetime.date) -> float:
        """Calculate new leads for date range."""
        query = self.db.query(func.count(Lead.id)).filter(
            and_(
                Lead.company_id == company_id,
                Lead.created_at >= start_date,
                Lead.created_at <= end_date
            )
        )
        query = self._apply_tenant_filter(query, Lead)
        return query.scalar() or 0.0
    
    def _calculate_deals(self, company_id: int, start_date: datetime.date, end_date: datetime.date) -> float:
        """Calculate total deals for date range."""
        query = self.db.query(func.count(Deal.id)).filter(
            and_(
                Deal.company_id == company_id,
                Deal.created_at >= start_date,
                Deal.created_at <= end_date
            )
        )
        query = self._apply_tenant_filter(query, Deal)
        return query.scalar() or 0.0
    
    def _create_kpi(self, company_id: int, category: KPICategory, period: KPIPeriod, 
                   value: float, previous_value: float, date: datetime.date) -> KPIResponse:
        """Create or update KPI record."""
        # Convert date to datetime for database storage
        date_datetime = datetime.combine(date, datetime.min.time())
        
        # Check if KPI already exists for this period
        existing_kpi = self.db.query(KPI).filter(
            and_(
                KPI.company_id == company_id,
                KPI.category == category,
                KPI.period == period,
                KPI.date == date_datetime
            )
        ).first()
        
        if existing_kpi:
            existing_kpi.value = value
            existing_kpi.previous_value = previous_value
            existing_kpi.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_kpi)
            return KPIResponse.model_validate(existing_kpi)
        else:
            kpi = KPI(
                company_id=company_id,
                category=category,
                period=period,
                value=value,
                previous_value=previous_value,
                date=date_datetime
            )
            self.db.add(kpi)
            self.db.commit()
            self.db.refresh(kpi)
            return KPIResponse.model_validate(kpi)
    
    def generate_trend_data(self, company_id: int, category: KPICategory, 
                           period_type: KPIPeriod, months: int = 12) -> List[Dict]:
        """Generate trend data for a KPI category."""
        trend_data = []
        current_date = datetime.utcnow().date()
        
        for i in range(months):
            if period_type == KPIPeriod.MONTHLY:
                month_start = (current_date.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
                month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                
                if category == KPICategory.REVENUE:
                    value = self._calculate_revenue(company_id, month_start, month_end)
                elif category == KPICategory.EXPENSES:
                    value = self._calculate_expenses(company_id, month_start, month_end)
                elif category == KPICategory.PROFIT:
                    revenue = self._calculate_revenue(company_id, month_start, month_end)
                    expenses = self._calculate_expenses(company_id, month_start, month_end)
                    value = revenue - expenses
                elif category == KPICategory.CUSTOMERS:
                    value = self._calculate_customers(company_id, month_start, month_end)
                elif category == KPICategory.INVOICES:
                    value = self._calculate_invoices(company_id, month_start, month_end)
                elif category == KPICategory.LEADS:
                    value = self._calculate_leads(company_id, month_start, month_end)
                elif category == KPICategory.DEALS:
                    value = self._calculate_deals(company_id, month_start, month_end)
                else:
                    value = 0.0
                
                trend_data.append({
                    "date": month_start.isoformat(),
                    "value": value,
                    "forecast": False
                })
        
        return list(reversed(trend_data))
    
    def generate_forecast(self, company_id: int, category: KPICategory, 
                         period_type: KPIPeriod, forecast_periods: int = 3) -> Dict[str, Any]:
        """Generate basic forecast using linear regression."""
        # Get historical data
        historical_data = self.generate_trend_data(company_id, category, period_type, 12)
        
        if len(historical_data) < 3:
            return {"error": "Insufficient historical data for forecasting"}
        
        # Simple linear regression
        values = [float(point["value"]) for point in historical_data]
        x_values = list(range(len(values)))
        
        # Check if all values are the same (including all zeros)
        if len(set(values)) <= 1:
            return {"error": "Insufficient data variation for forecasting"}
        
        # Calculate trend
        n = len(values)
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope and intercept
        denominator = (n * sum_x2 - sum_x * sum_x)
        if denominator == 0:
            return {"error": "Unable to calculate forecast trend"}
            
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        
        # Generate forecast
        forecast_data = []
        last_date = datetime.fromisoformat(historical_data[-1]["date"])
        
        for i in range(1, forecast_periods + 1):
            next_value = slope * (len(values) + i) + intercept
            next_date = last_date + timedelta(days=30 * i)
            
            forecast_data.append({
                "date": next_date.isoformat(),
                "value": max(0, next_value),  # Ensure non-negative values
                "forecast": True
            })
        
        # Calculate confidence score (simplified)
        mean_value = statistics.mean(values)
        variance = statistics.variance(values) if len(values) > 1 else 0
        confidence_score = max(0, min(100, 100 - (variance / mean_value * 100) if mean_value > 0 else 50))
        
        return {
            "historical_data": historical_data,
            "forecast_data": forecast_data,
            "confidence_score": round(confidence_score, 2),
            "model_used": "linear_regression"
        }
    
    def get_role_based_dashboard(self, company_id: int, user_role: UserRole) -> Dict[str, Any]:
        """Get dashboard data based on user role."""
        role_configurations = {
            UserRole.ADMIN: {
                "widgets": ["revenue_chart", "expense_chart", "profit_chart", "team_performance", "kpi_summary"],
                "permissions": {"view_all": True, "edit_all": True, "manage_users": True}
            },
            UserRole.ACCOUNTANT: {
                "widgets": ["revenue_chart", "expense_chart", "profit_chart", "invoice_summary", "tax_calculations"],
                "permissions": {"view_financial": True, "edit_financial": True, "view_reports": True}
            },
            UserRole.MANAGER: {
                "widgets": ["revenue_chart", "customer_chart", "task_summary", "team_performance", "lead_conversion"],
                "permissions": {"view_team": True, "manage_tasks": True, "view_reports": True}
            },
            UserRole.EMPLOYEE: {
                "widgets": ["task_summary", "customer_chart"],
                "permissions": {"view_own_tasks": True, "view_assigned_customers": True}
            }
        }
        
        config = role_configurations.get(user_role, role_configurations[UserRole.MANAGER])
        
        # Get relevant KPIs for this role
        kpis = self.calculate_kpis(company_id, KPIPeriod.MONTHLY)
        
        # Get real data for widgets
        widget_data = self._get_widget_data(company_id, user_role, config["widgets"])
        
        return {
            "role": user_role.value,
            "widgets": config["widgets"],
            "permissions": config["permissions"],
            "kpis": [kpi for kpi in kpis if self._is_kpi_relevant_for_role(kpi.category, user_role)],
            "widget_data": widget_data
        }
    
    def _get_widget_data(self, company_id: int, user_role: UserRole, widgets: list) -> Dict[str, Any]:
        """Get real data for dashboard widgets."""
        widget_data = {}
        
        # Get current month KPIs
        kpis = self.calculate_kpis(company_id, KPIPeriod.MONTHLY)
        kpi_dict = {kpi.category.value: kpi for kpi in kpis}
        
        # Revenue chart data
        if "revenue_chart" in widgets:
            widget_data["revenue_chart"] = {
                "totalRevenue": kpi_dict.get("revenue", {}).value or 0,
                "growth": kpi_dict.get("revenue", {}).growth_percentage or 0,
                "trend": self.generate_trend_data(company_id, KPICategory.REVENUE, KPIPeriod.MONTHLY, 6)
            }
        
        # Expense chart data
        if "expense_chart" in widgets:
            widget_data["expense_chart"] = {
                "totalExpenses": kpi_dict.get("expenses", {}).value or 0,
                "growth": kpi_dict.get("expenses", {}).growth_percentage or 0,
                "trend": self.generate_trend_data(company_id, KPICategory.EXPENSES, KPIPeriod.MONTHLY, 6)
            }
        
        # Profit chart data
        if "profit_chart" in widgets:
            widget_data["profit_chart"] = {
                "netProfit": kpi_dict.get("profit", {}).value or 0,
                "margin": self._calculate_profit_margin(kpis),
                "growth": kpi_dict.get("profit", {}).growth_percentage or 0
            }
        
        # Customer chart data
        if "customer_chart" in widgets:
            widget_data["customer_chart"] = {
                "totalCustomers": kpi_dict.get("customers", {}).value or 0,
                "newCustomers": kpi_dict.get("customers", {}).get("new_customers", 0),
                "segments": [
                    {"name": "New", "percentage": 25},
                    {"name": "Active", "percentage": 60},
                    {"name": "Inactive", "percentage": 15}
                ]
            }
        
        # Task summary data
        if "task_summary" in widgets:
            widget_data["task_summary"] = self._get_task_summary(company_id)
        
        # Team performance data
        if "team_performance" in widgets:
            widget_data["team_performance"] = self._get_team_performance(company_id)
        
        # Lead conversion data
        if "lead_conversion" in widgets:
            widget_data["lead_conversion"] = self._get_lead_conversion(company_id)
        
        # Invoice summary data
        if "invoice_summary" in widgets:
            widget_data["invoice_summary"] = self._get_invoice_summary(company_id)
        
        # Tax calculations data
        if "tax_calculations" in widgets:
            widget_data["tax_calculations"] = self._get_tax_calculations(kpis)
        
        # KPI summary data
        if "kpi_summary" in widgets:
            widget_data["kpi_summary"] = {
                "totalUsers": self._get_user_count(company_id),
                "activeUsers": self._get_active_user_count(company_id),
                "systemHealth": "Good",
                "pendingTasks": self._get_pending_task_count(company_id)
            }
        
        return widget_data
    
    def _calculate_profit_margin(self, kpis) -> float:
        """Calculate profit margin from KPIs."""
        revenue_kpi = next((kpi for kpi in kpis if kpi.category == KPICategory.REVENUE), None)
        expense_kpi = next((kpi for kpi in kpis if kpi.category == KPICategory.EXPENSES), None)
        
        if revenue_kpi and revenue_kpi.value > 0:
            expenses = expense_kpi.value if expense_kpi else 0
            margin = ((revenue_kpi.value - expenses) / revenue_kpi.value) * 100
            return round(margin, 2)
        return 0.0
    
    def _get_task_summary(self, company_id: int) -> Dict[str, Any]:
        """Get task summary data."""
        # Mock data - in real implementation, query from tasks table
        return {
            "totalTasks": 45,
            "completedTasks": 32,
            "pendingTasks": 8,
            "overdueTasks": 5,
            "completionRate": 71.1
        }
    
    def _get_team_performance(self, company_id: int) -> Dict[str, Any]:
        """Get team performance data."""
        # Mock data - in real implementation, query from users and tasks tables
        return {
            "teamMembers": 8,
            "tasksCompleted": 156,
            "avgCompletionTime": 2.3,  # days
            "productivity": 87.5  # percentage
        }
    
    def _get_lead_conversion(self, company_id: int) -> Dict[str, Any]:
        """Get lead conversion data."""
        # Mock data - in real implementation, query from leads and deals tables
        return {
            "totalLeads": 124,
            "convertedLeads": 43,
            "conversionRate": 34.7,
            "pipelineValue": 2850000  # UZS
        }
    
    def _get_invoice_summary(self, company_id: int) -> Dict[str, Any]:
        """Get invoice summary data."""
        # Mock data - in real implementation, query from invoices table
        return {
            "totalInvoices": 67,
            "paidInvoices": 52,
            "unpaidInvoices": 12,
            "overdueInvoices": 3,
            "totalAmount": 15400000  # UZS
        }
    
    def _get_tax_calculations(self, kpis) -> Dict[str, Any]:
        """Get tax calculations."""
        revenue_kpi = next((kpi for kpi in kpis if kpi.category == KPICategory.REVENUE), None)
        expense_kpi = next((kpi for kpi in kpis if kpi.category == KPICategory.EXPENSES), None)
        
        revenue = revenue_kpi.value if revenue_kpi else 0
        expenses = expense_kpi.value if expense_kpi else 0
        profit = revenue - expenses
        
        # Simplified tax calculation (Uzbekistan rates)
        income_tax = profit * 0.12 if profit > 0 else 0  # 12% income tax
        vat = revenue * 0.15  # 15% VAT
        
        return {
            "incomeTax": income_tax,
            "vat": vat,
            "totalTax": income_tax + vat,
            "taxableIncome": profit
        }
    
    def _get_user_count(self, company_id: int) -> int:
        """Get total user count for company."""
        # Mock data - in real implementation, query from users table
        return 8
    
    def _get_active_user_count(self, company_id: int) -> int:
        """Get active user count for company."""
        # Mock data - in real implementation, query from users table
        return 6
    
    def _get_pending_task_count(self, company_id: int) -> int:
        """Get pending task count for company."""
        # Mock data - in real implementation, query from tasks table
        return 13
    
    def _is_kpi_relevant_for_role(self, category: KPICategory, role: UserRole) -> bool:
        """Check if KPI category is relevant for user role."""
        role_kpi_mapping = {
            UserRole.ADMIN: list(KPICategory),
            UserRole.ACCOUNTANT: [KPICategory.REVENUE, KPICategory.EXPENSES, KPICategory.PROFIT, KPICategory.INVOICES],
            UserRole.MANAGER: [KPICategory.REVENUE, KPICategory.CUSTOMERS, KPICategory.LEADS, KPICategory.DEALS]
        }
        
        return category in role_kpi_mapping.get(role, [])
