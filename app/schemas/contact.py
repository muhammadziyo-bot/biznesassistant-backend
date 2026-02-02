from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.contact import ContactType

class ContactBase(BaseModel):
    name: str
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    mfo: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    type: ContactType = ContactType.CUSTOMER
    telegram: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    linkedin: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    mfo: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    type: Optional[ContactType] = None
    is_active: Optional[bool] = None
    telegram: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    linkedin: Optional[str] = None

class ContactResponse(ContactBase):
    id: int
    is_active: bool
    assigned_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
