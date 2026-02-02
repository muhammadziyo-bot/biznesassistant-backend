"""
Fix demo users to have proper tenant_id
"""

from sqlalchemy import create_engine, text
from app.config import settings

def fix_demo_users():
    """Ensure demo users have proper tenant_id"""
    engine = create_engine(settings.DATABASE_URL)
    
    print("Fixing demo users tenant_id...")
    
    with engine.connect() as conn:
        # Check if users have tenant_id
        result = conn.execute(text("SELECT id, email, tenant_id FROM users WHERE email LIKE '%demo%' OR email LIKE '%admin%'"))
        users = result.fetchall()
        
        print(f"Found {len(users)} demo users:")
        for user in users:
            print(f"  ID: {user[0]}, Email: {user[1]}, Tenant ID: {user[2]}")
        
        # Get the default tenant
        result = conn.execute(text("SELECT id FROM tenants WHERE tax_id = 'DEFAULT_TENANT'"))
        tenant = result.fetchone()
        
        if tenant:
            tenant_id = tenant[0]
            print(f"\nUpdating users to tenant_id: {tenant_id}")
            
            # Update users without tenant_id
            result = conn.execute(text(f"UPDATE users SET tenant_id = {tenant_id} WHERE tenant_id IS NULL"))
            print(f"Updated {result.rowcount} users")
            
            conn.commit()
            print("✅ Demo users fixed!")
        else:
            print("❌ Default tenant not found!")
    
    print("Done!")

if __name__ == "__main__":
    fix_demo_users()
