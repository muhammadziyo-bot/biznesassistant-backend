"""
Migration script to convert single-tenant to multi-tenant architecture
This script:
1. Creates the tenants table
2. Adds tenant_id columns to all existing tables
3. Creates a default tenant for existing data
4. Updates all existing records to belong to the default tenant
"""

from sqlalchemy import create_engine, text
from app.config import settings
from app.models import Base, Tenant
from sqlalchemy.orm import sessionmaker

def migrate_to_multi_tenant():
    """Migrate existing database to multi-tenant architecture"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    print("Starting multi-tenant migration...")
    
    # Create all tables including the new tenants table
    print("Creating tenants table...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if default tenant already exists
        default_tenant = db.query(Tenant).filter(Tenant.tax_id == "DEFAULT_TENANT").first()
        
        if not default_tenant:
            print("Creating default tenant...")
            default_tenant = Tenant(
                name="Default Demo Company",
                tax_id="DEFAULT_TENANT",
                email="demo@default.com",
                subscription_tier="enterprise",
                subscription_status="active",
                is_active=True,
                is_verified=True
            )
            db.add(default_tenant)
            db.commit()
            db.refresh(default_tenant)
            print(f"Created default tenant with ID: {default_tenant.id}")
        else:
            print(f"Default tenant already exists with ID: {default_tenant.id}")
        
        tenant_id = default_tenant.id
        
        # Update all existing records to belong to the default tenant
        print("\nMigrating existing data to default tenant...")
        
        # Update users
        result = db.execute(text(f"UPDATE users SET tenant_id = {tenant_id} WHERE tenant_id IS NULL"))
        print(f"Updated {result.rowcount} users")
        
        # Update companies
        result = db.execute(text(f"UPDATE companies SET tenant_id = {tenant_id} WHERE tenant_id IS NULL"))
        print(f"Updated {result.rowcount} companies")
        
        # Update transactions
        result = db.execute(text(f"UPDATE transactions SET tenant_id = {tenant_id} WHERE tenant_id IS NULL"))
        print(f"Updated {result.rowcount} transactions")
        
        # Update invoices
        result = db.execute(text(f"UPDATE invoices SET tenant_id = {tenant_id} WHERE tenant_id IS NULL"))
        print(f"Updated {result.rowcount} invoices")
        
        # Update contacts
        result = db.execute(text(f"UPDATE contacts SET tenant_id = {tenant_id} WHERE tenant_id IS NULL"))
        print(f"Updated {result.rowcount} contacts")
        
        # Update leads
        result = db.execute(text(f"UPDATE leads SET tenant_id = {tenant_id} WHERE tenant_id IS NULL"))
        print(f"Updated {result.rowcount} leads")
        
        # Update deals
        result = db.execute(text(f"UPDATE deals SET tenant_id = {tenant_id} WHERE tenant_id IS NULL"))
        print(f"Updated {result.rowcount} deals")
        
        # Update KPIs
        result = db.execute(text(f"UPDATE kpis SET tenant_id = {tenant_id} WHERE tenant_id IS NULL"))
        print(f"Updated {result.rowcount} KPIs")
        
        db.commit()
        
        print("\nMigration completed successfully!")
        print(f"All existing data now belongs to tenant: {default_tenant.name} (ID: {tenant_id})")
        print("\nNext steps:")
        print("1. Update authentication to include tenant_id in JWT")
        print("2. Add tenant isolation middleware")
        print("3. Create business registration system")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_to_multi_tenant()
