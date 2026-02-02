from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionType, TransactionCategory
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.utils.auth import get_current_active_user, get_current_tenant

router = APIRouter()

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Create a new transaction."""
    db_transaction = Transaction(
        **transaction.dict(),
        user_id=current_user.id,
        company_id=current_user.company_id or 1,  # Fallback to company ID 1 if None
        tenant_id=tenant_id
    )
    
    # Calculate VAT and tax amounts
    if db_transaction.vat_included:
        db_transaction.vat_amount = float(db_transaction.amount) * 0.12  # 12% VAT
        net_amount = float(db_transaction.amount) - db_transaction.vat_amount
    else:
        db_transaction.vat_amount = 0
        net_amount = float(db_transaction.amount)
    
    # Calculate tax amount (simplified for SMEs)
    if db_transaction.type == TransactionType.INCOME:
        db_transaction.tax_amount = net_amount * 0.15  # 15% income tax
    else:
        db_transaction.tax_amount = 0
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    transaction_type: Optional[TransactionType] = None,
    category: Optional[TransactionCategory] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get transactions with filters."""
    query = db.query(Transaction).filter(
        and_(
            Transaction.company_id == (current_user.company_id or 1),
            Transaction.tenant_id == tenant_id
        )
    )
    
    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)
    
    if category:
        query = query.filter(Transaction.category == category)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    transactions = query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
    return transactions

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get transaction by ID."""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.company_id == (current_user.company_id or 1),
            Transaction.tenant_id == tenant_id
        )
    ).first()
    
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    
    return transaction

@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Update transaction."""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.company_id == (current_user.company_id or 1),
            Transaction.tenant_id == tenant_id
        )
    ).first()
    
    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )
    
    update_data = transaction_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    # Recalculate VAT and tax amounts if amount changed
    if 'amount' in update_data:
        if transaction.vat_included:
            transaction.vat_amount = float(transaction.amount) * 0.12
            net_amount = float(transaction.amount) - transaction.vat_amount
        else:
            transaction.vat_amount = 0
            net_amount = float(transaction.amount)
        
        if transaction.type == TransactionType.INCOME:
            transaction.tax_amount = net_amount * 0.15
        else:
            transaction.tax_amount = 0
    
    db.commit()
    db.refresh(transaction)
    return transaction

@router.get("/summary")
async def get_accounting_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get accounting summary for dashboard."""
    query = db.query(Transaction).filter(
        and_(
            Transaction.company_id == (current_user.company_id or 1),
            Transaction.tenant_id == tenant_id
        )
    )
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    # Calculate totals
    income_total = query.filter(Transaction.type == TransactionType.INCOME).with_entities(
        func.sum(Transaction.amount)
    ).scalar() or 0
    
    expense_total = query.filter(Transaction.type == TransactionType.EXPENSE).with_entities(
        func.sum(Transaction.amount)
    ).scalar() or 0
    
    vat_total = query.with_entities(func.sum(Transaction.vat_amount)).scalar() or 0
    tax_total = query.with_entities(func.sum(Transaction.tax_amount)).scalar() or 0
    
    # Transaction counts by category
    income_by_category = query.filter(Transaction.type == TransactionType.INCOME).with_entities(
        Transaction.category,
        func.count(Transaction.id),
        func.sum(Transaction.amount)
    ).group_by(Transaction.category).all()
    
    expense_by_category = query.filter(Transaction.type == TransactionType.EXPENSE).with_entities(
        Transaction.category,
        func.count(Transaction.id),
        func.sum(Transaction.amount)
    ).group_by(Transaction.category).all()
    
    return {
        "total_income": float(income_total),
        "total_expense": float(expense_total),
        "net_profit": float(income_total - expense_total),
        "total_vat": float(vat_total),
        "total_tax": float(tax_total),
        "income_by_category": [
            {
                "category": cat[0].value,
                "count": cat[1],
                "total": float(cat[2])
            } for cat in income_by_category
        ],
        "expense_by_category": [
            {
                "category": cat[0].value,
                "count": cat[1],
                "total": float(cat[2])
            } for cat in expense_by_category
        ]
    }
