from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.transaction import TransactionType, TransactionCategory

class TransactionBase(BaseModel):
    amount: Decimal
    type: TransactionType
    category: TransactionCategory
    description: Optional[str] = None
    date: datetime
    vat_included: bool = True
    reference_number: Optional[str] = None
    attachment_url: Optional[str] = None
    contact_id: Optional[int] = None
    invoice_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    vat_included: Optional[bool] = None
    reference_number: Optional[str] = None
    attachment_url: Optional[str] = None
    is_reconciled: Optional[bool] = None
    contact_id: Optional[int] = None
    invoice_id: Optional[int] = None

class TransactionResponse(TransactionBase):
    id: int
    vat_amount: Decimal
    tax_amount: Decimal
    is_reconciled: bool
    user_id: int
    company_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
