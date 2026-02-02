"""
Tenant dependencies for FastAPI
"""

from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from app.middleware.tenant import validate_tenant_access

async def get_tenant_context(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Tenant:
    """Get and validate tenant context for the current request."""
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any tenant"
        )
    
    # Set tenant_id in request state for middleware access
    request.state.tenant_id = current_user.tenant_id
    
    # Validate tenant exists and is active
    tenant = validate_tenant_access(db, current_user.tenant_id)
    
    return tenant

def get_tenant_id(
    tenant: Tenant = Depends(get_tenant_context)
) -> int:
    """Get tenant ID from tenant context."""
    return tenant.id

class TenantFilterMixin:
    """Mixin for adding tenant filtering to database operations."""
    
    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id
    
    def apply_tenant_filter(self, query, model_class):
        """Apply tenant filtering to a query."""
        if hasattr(model_class, 'tenant_id'):
            return query.filter(model_class.tenant_id == self.tenant_id)
        return query
    
    def validate_tenant_ownership(self, instance):
        """Validate that an instance belongs to the current tenant."""
        if hasattr(instance, 'tenant_id'):
            if instance.tenant_id != self.tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: resource belongs to different tenant"
                )
        return True
