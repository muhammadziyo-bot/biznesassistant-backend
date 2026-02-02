"""
Check user tenant information
"""

from sqlalchemy import create_engine, text
from app.config import settings

def check_user_tenant():
    """Check user tenant_id in database"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check the test user
        result = conn.execute(text("SELECT id, email, company_id, tenant_id FROM users WHERE email = 'test2@admin.com'"))
        user = result.fetchone()
        
        if user:
            print(f"User ID: {user[0]}")
            print(f"Email: {user[1]}")
            print(f"Company ID: {user[2]}")
            print(f"Tenant ID: {user[3]}")
        else:
            print("User not found")
        
        # Check all users
        result = conn.execute(text("SELECT id, email, company_id, tenant_id FROM users ORDER BY id DESC LIMIT 5"))
        users = result.fetchall()
        
        print("\nRecent users:")
        for user in users:
            print(f"ID: {user[0]}, Email: {user[1]}, Company: {user[2]}, Tenant: {user[3]}")

if __name__ == "__main__":
    check_user_tenant()
