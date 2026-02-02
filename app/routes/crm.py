from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models.user import User
from app.models.contact import Contact, ContactType
from app.models.lead import Lead, LeadStatus, LeadSource
from app.models.deal import Deal, DealStatus, DealPriority
from app.models.activity import Activity, ActivityType
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from app.schemas.deal import DealCreate, DealUpdate, DealResponse
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse
from app.utils.auth import get_current_active_user

router = APIRouter()

# Contacts endpoints
@router.post("/contacts", response_model=ContactResponse)
async def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new contact."""
    db_contact = Contact(
        **contact.dict(),
        company_id=current_user.company_id or 1,
        assigned_user_id=current_user.id
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@router.get("/contacts", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = 0,
    limit: int = 100,
    contact_type: Optional[ContactType] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get contacts with filters."""
    company_id = current_user.company_id or 1
    query = db.query(Contact).filter(Contact.company_id == company_id)
    
    if contact_type:
        query = query.filter(Contact.type == contact_type)
    
    if search:
        query = query.filter(
            Contact.name.ilike(f"%{search}%") |
            Contact.email.ilike(f"%{search}%") |
            Contact.phone.ilike(f"%{search}%") |
            Contact.company_name.ilike(f"%{search}%")
        )
    
    contacts = query.offset(skip).limit(limit).all()
    return contacts

@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get contact by ID."""
    company_id = current_user.company_id or 1
    contact = db.query(Contact).filter(
        and_(
            Contact.id == contact_id,
            Contact.company_id == company_id
        )
    ).first()
    
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return contact

@router.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update contact."""
    company_id = current_user.company_id or 1
    contact = db.query(Contact).filter(
        and_(
            Contact.id == contact_id,
            Contact.company_id == company_id
        )
    ).first()
    
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    update_data = contact_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    db.commit()
    db.refresh(contact)
    return contact

# Leads endpoints
@router.post("/leads", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new lead."""
    db_lead = Lead(
        **lead.dict(),
        company_id=current_user.company_id or 1,
        assigned_user_id=current_user.id
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.get("/leads", response_model=List[LeadResponse])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get leads with filters."""
    company_id = current_user.company_id or 1
    query = db.query(Lead).filter(Lead.company_id == company_id)
    
    if status:
        query = query.filter(Lead.status == status)
    
    if source:
        query = query.filter(Lead.source == source)
    
    leads = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()
    return leads

@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get lead by ID."""
    company_id = current_user.company_id or 1
    lead = db.query(Lead).filter(
        and_(
            Lead.id == lead_id,
            Lead.company_id == company_id
        )
    ).first()
    
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return lead

@router.put("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update lead."""
    company_id = current_user.company_id or 1
    lead = db.query(Lead).filter(
        and_(
            Lead.id == lead_id,
            Lead.company_id == company_id
        )
    ).first()
    
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = lead_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    # Set converted date if status changed to converted
    if lead.status == LeadStatus.CONVERTED and not lead.converted_date:
        lead.converted_date = datetime.utcnow()
    
    db.commit()
    db.refresh(lead)
    return lead

# Deals endpoints
@router.post("/deals", response_model=DealResponse)
async def create_deal(
    deal: DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new deal."""
    db_deal = Deal(
        **deal.dict(),
        company_id=current_user.company_id or 1,
        assigned_user_id=current_user.id
    )
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal

@router.get("/deals", response_model=List[DealResponse])
async def get_deals(
    skip: int = 0,
    limit: int = 100,
    status: Optional[DealStatus] = None,
    priority: Optional[DealPriority] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get deals with filters."""
    company_id = current_user.company_id or 1
    query = db.query(Deal).filter(Deal.company_id == company_id)
    
    if status:
        query = query.filter(Deal.status == status)
    
    if priority:
        query = query.filter(Deal.priority == priority)
    
    deals = query.order_by(Deal.created_at.desc()).offset(skip).limit(limit).all()
    return deals

@router.get("/deals/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get deal by ID."""
    company_id = current_user.company_id or 1
    deal = db.query(Deal).filter(
        and_(
            Deal.id == deal_id,
            Deal.company_id == company_id
        )
    ).first()
    
    if deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return deal

@router.put("/deals/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: int,
    deal_update: DealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update deal."""
    company_id = current_user.company_id or 1
    deal = db.query(Deal).filter(
        and_(
            Deal.id == deal_id,
            Deal.company_id == company_id
        )
    ).first()
    
    if deal is None:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    update_data = deal_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deal, field, value)
    
    # Set actual close date if deal is closed
    if deal.status in [DealStatus.CLOSED_WON, DealStatus.CLOSED_LOST] and not deal.actual_close_date:
        deal.actual_close_date = datetime.utcnow()
    
    db.commit()
    db.refresh(deal)
    return deal

# Activities endpoints
@router.post("/activities", response_model=ActivityResponse)
async def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new activity."""
    db_activity = Activity(
        **activity.dict(),
        user_id=current_user.id,
        company_id=current_user.company_id or 1
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.get("/activities", response_model=List[ActivityResponse])
async def get_activities(
    skip: int = 0,
    limit: int = 100,
    activity_type: Optional[ActivityType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get activities with filters."""
    company_id = current_user.company_id or 1
    query = db.query(Activity).filter(Activity.company_id == company_id)
    
    if activity_type:
        query = query.filter(Activity.type == activity_type)
    
    activities = query.order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()
    return activities

@router.get("/crm-summary")
async def get_crm_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get CRM summary for dashboard."""
    company_id = current_user.company_id or 1
    # Count contacts by type
    contacts_by_type = db.query(Contact.type, db.func.count(Contact.id)).filter(
        Contact.company_id == company_id
    ).group_by(Contact.type).all()
    
    # Count leads by status
    leads_by_status = db.query(Lead.status, db.func.count(Lead.id)).filter(
        Lead.company_id == company_id
    ).group_by(Lead.status).all()
    
    # Count deals by status
    deals_by_status = db.query(Deal.status, db.func.count(Deal.id)).filter(
        Deal.company_id == company_id
    ).group_by(Deal.status).all()
    
    # Calculate total deal value
    total_deal_value = db.query(db.func.sum(Deal.deal_value)).filter(
        and_(
            Deal.company_id == company_id,
            Deal.deal_value.isnot(None)
        )
    ).scalar() or 0
    
    # Recent activities count
    recent_activities = db.query(db.func.count(Activity.id)).filter(
        and_(
            Activity.company_id == company_id,
            Activity.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        )
    ).scalar() or 0
    
    return {
        "contacts_by_type": [
            {"type": ct[0].value, "count": ct[1]} for ct in contacts_by_type
        ],
        "leads_by_status": [
            {"status": ls[0].value, "count": ls[1]} for ls in leads_by_status
        ],
        "deals_by_status": [
            {"status": ds[0].value, "count": ds[1]} for ds in deals_by_status
        ],
        "total_deal_value": float(total_deal_value),
        "recent_activities": recent_activities
    }
