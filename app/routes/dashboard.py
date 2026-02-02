from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.models.user import User, UserRole
from app.models.transaction import Transaction, TransactionType
from app.models.invoice import Invoice, InvoiceStatus
from app.models.contact import Contact
from app.models.lead import Lead, LeadStatus
from app.models.deal import Deal, DealStatus
from app.models.kpi import KPICategory, KPIPeriod
from app.utils.auth import get_current_active_user
from app.services.kpi_service import KPIService
from app.schemas.kpi import (
    KPIResponse, KPITrendResponse, ForecastRequest, ForecastResponse,
    RoleBasedDashboardResponse
)

router = APIRouter()

@router.get("/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard overview data."""
    company_id = current_user.company_id or 1
    
    # Date ranges
    today = datetime.utcnow().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    this_year_start = today.replace(month=1, day=1)
    
    # Accounting metrics
    # This month income
    this_month_income = db.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.company_id == company_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= this_month_start
        )
    ).scalar() or 0
    
    # This month expenses
    this_month_expenses = db.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.company_id == company_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= this_month_start
        )
    ).scalar() or 0
    
    # Last month income for comparison
    last_month_income = db.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.company_id == company_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= last_month_start,
            Transaction.date < this_month_start
        )
    ).scalar() or 0
    
    # Invoice metrics
    total_invoices = db.query(func.count(Invoice.id)).filter(
        Invoice.company_id == company_id
    ).scalar() or 0
    
    overdue_invoices = db.query(func.count(Invoice.id)).filter(
        and_(
            Invoice.company_id == company_id,
            Invoice.due_date < today,
            Invoice.status != InvoiceStatus.PAID
        )
    ).scalar() or 0
    
    # Outstanding amount
    outstanding_amount = db.query(func.sum(Invoice.remaining_amount)).filter(
        and_(
            Invoice.company_id == company_id,
            Invoice.status != InvoiceStatus.PAID
        )
    ).scalar() or 0
    
    # CRM metrics
    total_contacts = db.query(func.count(Contact.id)).filter(
        Contact.company_id == company_id
    ).scalar() or 0
    
    active_leads = db.query(func.count(Lead.id)).filter(
        and_(
            Lead.company_id == company_id,
            Lead.status.in_([LeadStatus.NEW, LeadStatus.CONTACTED, LeadStatus.QUALIFIED])
        )
    ).scalar() or 0
    
    active_deals = db.query(func.count(Deal.id)).filter(
        and_(
            Deal.company_id == company_id,
            Deal.status.in_([DealStatus.PROSPECTING, DealStatus.QUALIFICATION, DealStatus.PROPOSAL, DealStatus.NEGOTIATION])
        )
    ).scalar() or 0
    
    # Calculate growth percentages
    income_growth = ((this_month_income - last_month_income) / last_month_income * 100) if last_month_income > 0 else 0
    
    return {
        "accounting": {
            "this_month_income": float(this_month_income),
            "this_month_expenses": float(this_month_expenses),
            "net_profit": float(this_month_income - this_month_expenses),
            "income_growth_percentage": round(income_growth, 2)
        },
        "invoices": {
            "total_invoices": total_invoices,
            "overdue_invoices": overdue_invoices,
            "outstanding_amount": float(outstanding_amount)
        },
        "crm": {
            "total_contacts": total_contacts,
            "active_leads": active_leads,
            "active_deals": active_deals
        }
    }

@router.get("/cash-flow")
async def get_cash_flow(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get cash flow data for the last N months."""
    company_id = current_user.company_id or 1
    
    # Generate date ranges for each month
    cash_flow_data = []
    current_date = datetime.utcnow().date()
    
    for i in range(months):
        # Calculate month start and end
        month_start = (current_date.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        # Get income for this month
        income = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.company_id == company_id,
                Transaction.type == TransactionType.INCOME,
                Transaction.date >= month_start,
                Transaction.date <= month_end
            )
        ).scalar() or 0
        
        # Get expenses for this month
        expenses = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.company_id == company_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= month_start,
                Transaction.date <= month_end
            )
        ).scalar() or 0
        
        cash_flow_data.append({
            "month": month_start.strftime("%Y-%m"),
            "income": float(income),
            "expenses": float(expenses),
            "net_cash_flow": float(income - expenses)
        })
    
    return {"cash_flow": list(reversed(cash_flow_data))}

@router.get("/top-clients")
async def get_top_clients(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get top clients by total invoice amount."""
    company_id = current_user.company_id or 1
    
    top_clients = db.query(
        Invoice.customer_name,
        func.count(Invoice.id).label('invoice_count'),
        func.sum(Invoice.total_amount).label('total_amount')
    ).filter(
        Invoice.company_id == company_id
    ).group_by(
        Invoice.customer_name
    ).order_by(
        func.sum(Invoice.total_amount).desc()
    ).limit(limit).all()
    
    return {
        "top_clients": [
            {
                "customer_name": client[0],
                "invoice_count": client[1],
                "total_amount": float(client[2])
            }
            for client in top_clients
        ]
    }

@router.get("/recent-activities")
async def get_recent_activities(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get recent activities across all modules."""
    company_id = current_user.company_id or 1
    
    # Recent transactions
    recent_transactions = db.query(Transaction).filter(
        Transaction.company_id == company_id
    ).order_by(Transaction.created_at.desc()).limit(5).all()
    
    # Recent invoices
    recent_invoices = db.query(Invoice).filter(
        Invoice.company_id == company_id
    ).order_by(Invoice.created_at.desc()).limit(5).all()
    
    activities = []
    
    # Add transaction activities
    for transaction in recent_transactions:
        activities.append({
            "type": "transaction",
            "description": f"{transaction.type.value.title()}: {transaction.description or 'No description'}",
            "amount": float(transaction.amount),
            "date": transaction.created_at.isoformat(),
            "id": transaction.id
        })
    
    # Add invoice activities
    for invoice in recent_invoices:
        activities.append({
            "type": "invoice",
            "description": f"Invoice {invoice.invoice_number} for {invoice.customer_name}",
            "amount": float(invoice.total_amount),
            "date": invoice.created_at.isoformat(),
            "id": invoice.id
        })
    
    # Sort by date and limit
    activities.sort(key=lambda x: x["date"], reverse=True)
    
    return {"recent_activities": activities[:limit]}

@router.get("/sales-insights")
async def get_sales_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sales insights and analytics."""
    company_id = current_user.company_id or 1
    
    # This year's performance
    this_year_start = datetime.utcnow().date().replace(month=1, day=1)
    
    # Monthly sales trend
    monthly_sales = db.query(
        func.date_trunc('month', Transaction.date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        and_(
            Transaction.company_id == company_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= this_year_start
        )
    ).group_by(
        func.date_trunc('month', Transaction.date)
    ).order_by('month').all()
    
    # Income by category
    income_by_category = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        and_(
            Transaction.company_id == company_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= this_year_start
        )
    ).group_by(Transaction.category).all()
    
    return {
        "monthly_sales": [
            {
                "month": sale[0].strftime("%Y-%m") if sale[0] else None,
                "total": float(sale[1]) if sale[1] else 0
            }
            for sale in monthly_sales
        ],
        "income_by_category": [
            {
                "category": cat[0].value if cat[0] else "unknown",
                "total": float(cat[1]) if cat[1] else 0
            }
            for cat in income_by_category
        ]
    }
