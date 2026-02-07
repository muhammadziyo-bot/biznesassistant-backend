from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.database import get_db
from app.models.user import User
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceItemCreate
from app.utils.auth import get_current_active_user, get_current_tenant

router = APIRouter()

def generate_invoice_number(db: Session, company_id: int, tenant_id: int) -> str:
    """Generate unique invoice number with tenant ID for guaranteed uniqueness."""
    current_year = datetime.now().year
    # New format: INV-TENANT{tenant_id}-YEAR-{6-digit number}
    prefix = f"INV-T{tenant_id}-{current_year}-"
    
    # Get last invoice number for this specific tenant and year
    last_invoice = db.query(Invoice).filter(
        and_(
            Invoice.company_id == company_id,
            Invoice.tenant_id == tenant_id,
            Invoice.invoice_number.like(f"{prefix}%")
        )
    ).order_by(Invoice.invoice_number.desc()).first()
    
    if last_invoice:
        # Extract number part and increment
        try:
            last_num = int(last_invoice.invoice_number.split("-")[-1])
            new_num = last_num + 1
        except (ValueError, IndexError):
            new_num = 1
    else:
        new_num = 1
    
    return f"{prefix}{new_num:06d}"

@router.post("/", response_model=InvoiceResponse)
async def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Create a new invoice."""
    # Use company_id with fallback, same as other endpoints for consistency
    company_id = current_user.company_id or 1
    
    try:
        # Debug: Print incoming data
        print(f"DEBUG: Invoice data: {invoice.dict()}")
        print(f"DEBUG: Company ID: {company_id}, Tenant ID: {tenant_id}")
        
        # Generate invoice number with the correct company_id and tenant_id
        invoice_number = generate_invoice_number(db, company_id, tenant_id)
        print(f"DEBUG: Generated invoice number: {invoice_number}")
        
        # Create invoice
        invoice_data = invoice.dict(exclude={"items"})
        print(f"DEBUG: Invoice data for creation: {invoice_data}")
        
        db_invoice = Invoice(
            **invoice_data,
            invoice_number=invoice_number,
            created_by_id=current_user.id,
            company_id=company_id,
            tenant_id=tenant_id
        )
        print(f"DEBUG: Invoice object created successfully")
        
        # Calculate totals from items
        subtotal = Decimal('0')
        for item_data in invoice.items:
            line_total = Decimal(str(item_data.quantity)) * Decimal(str(item_data.unit_price))
            if item_data.discount:
                line_total *= (Decimal('1') - Decimal(str(item_data.discount)) / Decimal('100'))
            
            item_vat = line_total * Decimal(str(item_data.vat_rate)) / Decimal('100')
            subtotal += line_total
        
        db_invoice.subtotal = subtotal
        db_invoice.vat_amount = subtotal * Decimal('0.12')  # 12% VAT
        db_invoice.total_amount = subtotal + db_invoice.vat_amount
        db_invoice.remaining_amount = db_invoice.total_amount
        
        db.add(db_invoice)
        db.flush()  # Get the ID without committing
        
        print(f"DEBUG: Invoice saved with ID: {db_invoice.id}")
        
        # Create invoice items
        for item_data in invoice.items:
            # Use provided line_total or calculate if not provided
            if hasattr(item_data, 'line_total') and item_data.line_total is not None:
                line_total = Decimal(str(item_data.line_total))
            else:
                line_total = Decimal(str(item_data.quantity)) * Decimal(str(item_data.unit_price))
                if item_data.discount:
                    line_total *= (Decimal('1') - Decimal(str(item_data.discount)) / Decimal('100'))
            
            db_item = InvoiceItem(
                invoice_id=db_invoice.id,
                description=item_data.description,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                discount=item_data.discount,
                vat_rate=item_data.vat_rate,
                line_total=line_total
            )
            db.add(db_item)
        
        db.commit()
        db.refresh(db_invoice)
        return db_invoice
    
    except Exception as e:
        db.rollback()
        print(f"DEBUG: Error creating invoice: {str(e)}")
        print(f"DEBUG: Error type: {type(e)}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        
        # Check if it's a duplicate key error
        if "duplicate key" in str(e) and "invoice_number" in str(e):
            raise HTTPException(
                status_code=500,
                detail="Unable to generate unique invoice number. Please try again."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create invoice: {str(e)}"
            )

# Legacy route for frontend compatibility
@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice_legacy(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Legacy route for frontend compatibility - redirects to main create_invoice."""
    return create_invoice(invoice, db, current_user, tenant_id)

@router.get("/", response_model=List[InvoiceResponse])
async def get_invoices(
    skip: int = 0,
    limit: int = 100,
    status: Optional[InvoiceStatus] = None,
    customer_name: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get invoices with filters."""
    # Use company_id with fallback, same as in create_invoice
    company_id = current_user.company_id or 1
    query = db.query(Invoice).filter(
        and_(
            Invoice.company_id == company_id,
            Invoice.tenant_id == tenant_id
        )
    )
    
    if status:
        query = query.filter(Invoice.status == status)
    
    if customer_name:
        query = query.filter(Invoice.customer_name.ilike(f"%{customer_name}%"))
    
    if start_date:
        query = query.filter(Invoice.issue_date >= start_date)
    
    if end_date:
        query = query.filter(Invoice.issue_date <= end_date)
    
    invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
    return invoices

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get invoice by ID."""
    company_id = current_user.company_id or 1
    invoice = db.query(Invoice).filter(
        and_(
            Invoice.id == invoice_id,
            Invoice.company_id == company_id,
            Invoice.tenant_id == tenant_id
        )
    ).first()
    
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return invoice

# Legacy route for frontend compatibility
@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices_legacy(
    skip: int = 0,
    limit: int = 100,
    status: Optional[InvoiceStatus] = None,
    customer_name: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Legacy route for frontend compatibility - redirects to main get_invoices."""
    return get_invoices(skip, limit, status, customer_name, start_date, end_date, db, current_user, tenant_id)

# Legacy route for frontend compatibility
@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice_legacy(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Legacy route for frontend compatibility - redirects to main get_invoice."""
    return get_invoice(invoice_id, db, current_user, tenant_id)

@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Update invoice."""
    company_id = current_user.company_id or 1
    invoice = db.query(Invoice).filter(
        and_(
            Invoice.id == invoice_id,
            Invoice.company_id == company_id,
            Invoice.tenant_id == tenant_id
        )
    ).first()
    
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    update_data = invoice_update.dict(exclude_unset=True)
    
    # Handle items update if provided
    if 'items' in update_data and update_data['items']:
        # Delete existing items
        db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()
        
        # Recalculate totals
        subtotal = Decimal('0')
        
        # Create new items
        for item_data in update_data['items']:
            # Use provided line_total or calculate if not provided
            if hasattr(item_data, 'line_total') and item_data.line_total is not None:
                line_total = Decimal(str(item_data.line_total))
            else:
                line_total = Decimal(str(item_data.quantity)) * Decimal(str(item_data.unit_price))
                if item_data.discount:
                    line_total *= (Decimal('1') - Decimal(str(item_data.discount)) / Decimal('100'))
            
            db_item = InvoiceItem(
                invoice_id=invoice_id,
                description=item_data.description,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                discount=item_data.discount,
                vat_rate=item_data.vat_rate,
                line_total=line_total
            )
            db.add(db_item)
            subtotal += line_total
        
        # Update invoice totals
        invoice.subtotal = subtotal
        invoice.vat_amount = subtotal * Decimal('0.12')  # 12% VAT
        invoice.total_amount = subtotal + invoice.vat_amount
        invoice.remaining_amount = invoice.total_amount - invoice.paid_amount
        
        # Remove items from update_data to avoid conflicts
        del update_data['items']
    
    # Update other fields
    for field, value in update_data.items():
        setattr(invoice, field, value)
    
    db.commit()
    db.refresh(invoice)
    return invoice

# Legacy route for frontend compatibility
@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice_legacy(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Legacy route for frontend compatibility - redirects to main update_invoice."""
    return update_invoice(invoice_id, invoice_update, db, current_user, tenant_id)

@router.post("/{invoice_id}/send")
async def send_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Mark invoice as sent."""
    company_id = current_user.company_id or 1
    invoice = db.query(Invoice).filter(
        and_(
            Invoice.id == invoice_id,
            Invoice.company_id == company_id,
            Invoice.tenant_id == tenant_id
        )
    ).first()
    
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice.status = InvoiceStatus.SENT
    db.commit()
    return {"message": "Invoice sent successfully"}

# Legacy route for frontend compatibility
@router.post("/invoices/{invoice_id}/send")
async def send_invoice_legacy(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Legacy route for frontend compatibility - redirects to main send_invoice."""
    return send_invoice(invoice_id, db, current_user, tenant_id)

@router.post("/{invoice_id}/mark-paid")
async def mark_invoice_paid(
    invoice_id: int,
    paid_amount: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Mark invoice as paid."""
    company_id = current_user.company_id or 1
    invoice = db.query(Invoice).filter(
        and_(
            Invoice.id == invoice_id,
            Invoice.company_id == company_id,
            Invoice.tenant_id == tenant_id
        )
    ).first()
    
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Convert float to Decimal to avoid type mismatch
    paid_amount_decimal = Decimal(str(paid_amount))
    invoice.paid_amount += paid_amount_decimal
    invoice.remaining_amount = invoice.total_amount - invoice.paid_amount
    
    if invoice.remaining_amount <= 0:
        invoice.status = InvoiceStatus.PAID
        invoice.paid_date = datetime.utcnow()
        invoice.remaining_amount = 0
    else:
        invoice.status = InvoiceStatus.SENT
    
    db.commit()
    return {"message": "Payment recorded successfully"}

# Legacy route for frontend compatibility
@router.post("/invoices/{invoice_id}/mark-paid")
async def mark_invoice_paid_legacy(
    invoice_id: int,
    paid_amount: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Legacy route for frontend compatibility - redirects to main mark_invoice_paid."""
    return mark_invoice_paid(invoice_id, paid_amount, db, current_user, tenant_id)

@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Delete invoice."""
    company_id = current_user.company_id or 1
    invoice = db.query(Invoice).filter(
        and_(
            Invoice.id == invoice_id,
            Invoice.company_id == company_id,
            Invoice.tenant_id == tenant_id
        )
    ).first()
    
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Delete invoice items first
    db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()
    
    # Delete invoice
    db.delete(invoice)
    db.commit()
    return {"message": "Invoice deleted successfully"}

# Legacy route for frontend compatibility
@router.delete("/invoices/{invoice_id}")
async def delete_invoice_legacy(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Legacy route for frontend compatibility - redirects to main delete_invoice."""
    return delete_invoice(invoice_id, db, current_user, tenant_id)

@router.get("/summary")
async def get_invoices_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get invoices summary for dashboard."""
    company_id = current_user.company_id or 1
    query = db.query(Invoice).filter(
        and_(
            Invoice.company_id == company_id,
            Invoice.tenant_id == tenant_id
        )
    )
    
    if start_date:
        query = query.filter(Invoice.issue_date >= start_date)
    
    if end_date:
        query = query.filter(Invoice.issue_date <= end_date)
    
    # Count invoices by status
    invoices_by_status = query.with_entities(
        Invoice.status,
        func.count(Invoice.id)
    ).group_by(Invoice.status).all()
    
    # Calculate totals
    total_invoiced = query.with_entities(func.sum(Invoice.total_amount)).scalar() or 0
    total_paid = query.with_entities(func.sum(Invoice.paid_amount)).scalar() or 0
    total_outstanding = query.filter(Invoice.status != InvoiceStatus.PAID).with_entities(
        func.sum(Invoice.remaining_amount)
    ).scalar() or 0
    
    # Overdue invoices
    overdue_invoices = query.filter(
        and_(
            Invoice.due_date < datetime.utcnow().date(),
            Invoice.status != InvoiceStatus.PAID
        )
    ).count()
    
    return {
        "invoices_by_status": [
            {"status": status[0].value, "count": status[1]} for status in invoices_by_status
        ],
        "total_invoiced": float(total_invoiced),
        "total_paid": float(total_paid),
        "total_outstanding": float(total_outstanding),
        "overdue_invoices": overdue_invoices
    }

# Legacy route for frontend compatibility
@router.get("/invoices/summary")
async def get_invoices_summary_legacy(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Legacy route for frontend compatibility - redirects to main get_invoices_summary."""
    return get_invoices_summary(start_date, end_date, db, current_user, tenant_id)