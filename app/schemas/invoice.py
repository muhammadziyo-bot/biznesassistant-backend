from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.models.invoice import InvoiceStatus

class InvoiceItemBase(BaseModel):
    description: str
    quantity: Decimal
    unit_price: Decimal
    discount: Optional[Decimal] = 0
    vat_rate: Optional[Decimal] = 12

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemUpdate(BaseModel):
    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    vat_rate: Optional[Decimal] = None

class InvoiceItemResponse(InvoiceItemBase):
    id: int
    invoice_id: int
    line_total: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class InvoiceBase(BaseModel):
    customer_name: str
    customer_tax_id: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    template_name: str = "default"
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    paid_amount: Optional[Decimal] = None
    is_recurring: bool = False
    recurring_interval: Optional[str] = None
    recurring_end_date: Optional[datetime] = None
    issue_date: datetime
    due_date: datetime
    items: List[InvoiceItemCreate]
    
    # Calculated fields (will be computed by backend)
    subtotal: Optional[Decimal] = None
    vat_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    remaining_amount: Optional[Decimal] = None
    status: Optional[InvoiceStatus] = None

class InvoiceCreate(InvoiceBase):
    contact_id: Optional[int] = None

class InvoiceUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_tax_id: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    template_name: Optional[str] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_interval: Optional[str] = None
    recurring_end_date: Optional[datetime] = None
    status: Optional[InvoiceStatus] = None
    issue_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    contact_id: Optional[int] = None

class InvoiceResponse(InvoiceBase):
    id: int
    invoice_number: str
    status: InvoiceStatus
    subtotal: Decimal
    vat_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    paid_date: Optional[datetime] = None
    created_by_id: int
    company_id: int
    contact_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[InvoiceItemResponse]
    
    class Config:
        from_attributes = True
