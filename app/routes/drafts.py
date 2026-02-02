"""
Draft management routes for BiznesAssistant
Handles auto-save functionality for forms and data
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.database import get_db
from app.models.user import User
from app.utils.auth import get_current_active_user, get_current_tenant

router = APIRouter()

class DraftCreate(BaseModel):
    draft_type: str  # 'transaction', 'invoice', 'task', etc.
    title: Optional[str] = None
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}

class DraftUpdate(BaseModel):
    title: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = {}

class DraftResponse(BaseModel):
    id: int
    draft_type: str
    title: Optional[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_by: int
    tenant_id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

@router.post("/", response_model=DraftResponse)
async def create_draft(
    draft: DraftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Create a new draft."""
    company_id = current_user.company_id or 1
    
    # Store draft in database (for now, we'll use a simple approach)
    # In a real implementation, you'd have a Draft model
    
    # For now, return a mock response
    import uuid
    draft_id = str(uuid.uuid4())
    
    # Store in session or cache (simplified approach)
    # In production, use Redis or database table
    
    return {
        "id": int(draft_id[:8], 16),  # Convert UUID part to int for demo
        "draft_type": draft.draft_type,
        "title": draft.title,
        "data": draft.data,
        "metadata": draft.metadata or {},
        "created_by": current_user.id,
        "tenant_id": tenant_id,
        "company_id": company_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@router.get("/{draft_type}/latest")
async def get_latest_draft(
    draft_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get the latest draft of a specific type for the current user."""
    company_id = current_user.company_id or 1
    
    # For now, return empty (no drafts saved yet)
    # In production, query from database
    
    return {
        "id": None,
        "draft_type": draft_type,
        "title": None,
        "data": {},
        "metadata": {},
        "created_by": current_user.id,
        "tenant_id": tenant_id,
        "company_id": company_id,
        "created_at": None,
        "updated_at": None
    }

@router.put("/{draft_id}")
async def update_draft(
    draft_id: int,
    draft_update: DraftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Update an existing draft."""
    company_id = current_user.company_id or 1
    
    # For now, just return success
    # In production, update the draft in database
    
    return {
        "message": "Draft updated successfully",
        "draft_id": draft_id
    }

@router.delete("/{draft_id}")
async def delete_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Delete a draft."""
    # For now, just return success
    # In production, delete from database
    
    return {
        "message": "Draft deleted successfully",
        "draft_id": draft_id
    }

@router.get("/")
async def list_drafts(
    draft_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """List all drafts for the current user."""
    company_id = current_user.company_id or 1
    
    # For now, return empty list
    # In production, query from database
    
    return {
        "drafts": [],
        "total": 0
    }
