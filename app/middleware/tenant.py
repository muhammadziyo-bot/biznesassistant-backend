"""
Tenant isolation middleware for multi-tenant architecture
"""

from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tenant import Tenant
from functools import wraps
import inspect

def tenant_required(func):
    """Decorator to ensure tenant isolation for database operations."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get the request from args/kwargs
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            # Check kwargs
            for key, value in kwargs.items():
                if isinstance(value, Request):
                    request = value
                    break
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not determine request context"
            )
        
        # Get tenant_id from request state (set by authentication)
        tenant_id = getattr(request.state, 'tenant_id', None)
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant context not found"
            )
        
        # Add tenant_id to kwargs for the function
        kwargs['tenant_id'] = tenant_id
        
        return await func(*args, **kwargs)
    
    return wrapper

def get_tenant_from_request(request: Request) -> int:
    """Extract tenant_id from authenticated request."""
    tenant_id = getattr(request.state, 'tenant_id', None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant context not found"
        )
    return tenant_id

def validate_tenant_access(db: Session, tenant_id: int) -> Tenant:
    """Validate that tenant exists and is active."""
    tenant = db.query(Tenant).filter(
        Tenant.id == tenant_id,
        Tenant.is_active == True
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found or inactive"
        )
    
    return tenant

def apply_tenant_filter(query, tenant_id: int, model_class):
    """Apply tenant filtering to a SQLAlchemy query."""
    if hasattr(model_class, 'tenant_id'):
        return query.filter(model_class.tenant_id == tenant_id)
    return query

class TenantContext:
    """Helper class for tenant context management."""
    
    def __init__(self, tenant_id: int, db: Session):
        self.tenant_id = tenant_id
        self.db = db
        self._tenant = None
    
    @property
    def tenant(self) -> Tenant:
        """Lazy load tenant information."""
        if not self._tenant:
            self._tenant = validate_tenant_access(self.db, self.tenant_id)
        return self._tenant
    
    def filter_query(self, query, model_class):
        """Apply tenant filtering to query."""
        return apply_tenant_filter(query, self.tenant_id, model_class)
    
    def validate_ownership(self, model_instance) -> bool:
        """Validate that a model instance belongs to the current tenant."""
        if hasattr(model_instance, 'tenant_id'):
            return model_instance.tenant_id == self.tenant_id
        return True  # Models without tenant_id are considered global
