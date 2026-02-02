from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.invoice import Invoice
from app.schemas.template import TemplateCreate, TemplateResponse, TemplateApply
from app.utils.auth import get_current_active_user, get_current_tenant

router = APIRouter()

@router.post("/", response_model=TemplateResponse)
async def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Create a new template."""
    # Validate template data based on type
    if template.type == "transaction":
        required_fields = ["amount", "category", "type"]
        for field in required_fields:
            if field not in template.data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    db_template = {
        "name": template.name,
        "type": template.type,
        "description": template.description,
        "is_recurring": template.is_recurring,
        "recurring_interval": template.recurring_interval,
        "recurring_day": template.recurring_day,
        "data": template.data,
        "created_by": current_user.id,
        "tenant_id": tenant_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # For now, store in a simple way (in production, use proper Template model)
    # This is a placeholder implementation
    return TemplateResponse(**db_template, id=1)

@router.get("/", response_model=List[TemplateResponse])
async def get_templates(
    template_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Get templates for the current tenant."""
    # Placeholder implementation - in production, query from database
    templates = []
    
    if template_type == "transaction":
        templates = [
            TemplateResponse(
                id=1,
                name="Monthly Rent",
                type="transaction",
                description="Monthly rent payment",
                is_recurring=True,
                recurring_interval="monthly",
                recurring_day=1,
                data={
                    "amount": 1000.00,
                    "type": "expense",
                    "category": "rent",
                    "vat_included": True
                },
                created_by=current_user.id,
                tenant_id=tenant_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
    
    return templates

@router.post("/{template_id}/apply")
async def apply_template(
    template_id: int,
    apply_data: TemplateApply,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Apply a template to create a new transaction or invoice."""
    # Get template (placeholder)
    template = await get_templates(template_type="transaction")
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template_data = template[0].data
    
    # Merge with custom data
    if apply_data.custom_data:
        template_data.update(apply_data.custom_data)
    
    # Create transaction based on template
    if template[0].type == "transaction":
        transaction = Transaction(
            amount=template_data.get("amount", 0),
            type=template_data.get("type", "expense"),
            category=template_data.get("category", "other"),
            description=template_data.get("description", f"From template: {template[0].name}"),
            date=apply_data.custom_data.get("date", datetime.utcnow().date()),
            vat_amount=template_data.get("vat_amount", 0),
            tax_amount=template_data.get("tax_amount", 0),
            user_id=current_user.id,
            company_id=current_user.company_id or 1,
            tenant_id=tenant_id
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return {"message": "Template applied successfully", "transaction_id": transaction.id}
    
    return {"message": "Template applied successfully"}

@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    tenant_id: int = Depends(get_current_tenant)
):
    """Delete a template."""
    # Placeholder implementation
    return {"message": "Template deleted successfully"}
