"""
Add tenant_id columns to existing tables
"""

from sqlalchemy import create_engine, text
from app.config import settings

def add_tenant_columns():
    """Add tenant_id columns to all existing tables"""
    engine = create_engine(settings.DATABASE_URL)
    
    print("Adding tenant_id columns to existing tables...")
    
    with engine.connect() as conn:
        # Add tenant_id columns to existing tables
        tables = [
            "users",
            "companies", 
            "transactions",
            "invoices",
            "contacts",
            "leads",
            "deals",
            "kpis"
        ]
        
        for table in tables:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN tenant_id INTEGER REFERENCES tenants(id)"))
                print(f"Added tenant_id to {table}")
            except Exception as e:
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print(f"tenant_id already exists in {table}")
                else:
                    print(f"Error adding tenant_id to {table}: {e}")
        
        conn.commit()
    
    print("Done!")

if __name__ == "__main__":
    add_tenant_columns()
