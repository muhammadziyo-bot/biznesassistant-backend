"""
Script to set up the local PostgreSQL database with all tables and initial data.
Run this script once to create your local database structure.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

# Local database connection (without specifying database initially)
conn_params = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "rakhmonov"
}

try:
    # Connect to PostgreSQL server (not to a specific database)
    conn = psycopg2.connect(**conn_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    print("Connected to PostgreSQL server!")
    
    # Create the database if it doesn't exist
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'biznes_assistant'")
    db_exists = cur.fetchone()
    
    if not db_exists:
        print("Creating database 'biznes_assistant'...")
        cur.execute("CREATE DATABASE biznes_assistant")
        print("Database created successfully!")
    else:
        print("Database 'biznes_assistant' already exists!")
    
    cur.close()
    conn.close()
    
    # Now connect to the specific database
    db_conn_params = conn_params.copy()
    db_conn_params["database"] = "biznes_assistant"
    
    conn = psycopg2.connect(**db_conn_params)
    cur = conn.cursor()
    
    print("Connected to 'biznes_assistant' database!")
    
    # Create all tables using SQLAlchemy
    print("Creating tables with SQLAlchemy...")
    
    # Import and create tables
    from app.database import create_tables
    create_tables()
    
    print("All tables created successfully!")
    
    # Create initial admin user
    print("Creating initial admin user...")
    from app.models.user import User, UserRole
    from app.utils.auth import get_password_hash
    from app.database import SessionLocal
    
    db = SessionLocal()
    
    # Check if admin user exists
    admin_user = db.query(User).filter(User.email == "admin@bizcore.uz").first()
    
    if not admin_user:
        admin_user = User(
            email="admin@bizcore.uz",
            username="admin",
            full_name="Admin User",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created: admin@bizcore.uz / admin123")
    else:
        print("Admin user already exists!")
    
    # Create initial company
    from app.models.company import Company
    from app.models.tenant import Tenant
    
    # Check if tenant exists
    tenant = db.query(Tenant).filter(Tenant.name == "Default Tenant").first()
    
    if not tenant:
        tenant = Tenant(
            name="Default Tenant",
            is_active=True
        )
        db.add(tenant)
        db.commit()
        print("Default tenant created!")
    else:
        print("Default tenant already exists!")
    
    # Check if company exists
    company = db.query(Company).filter(Company.name == "Demo Company").first()
    
    if not company:
        company = Company(
            name="Demo Company",
            tax_id="123456789",
            company_code="DEMO001",
            address="Tashkent, Uzbekistan",
            phone="+998901234567",
            email="info@demo.com",
            is_active=True,
            tenant_id=tenant.id
        )
        db.add(company)
        db.commit()
        print("Demo company created!")
    else:
        print("Demo company already exists!")
    
    # Update admin user with company and tenant
    admin_user.company_id = company.id
    admin_user.tenant_id = tenant.id
    db.commit()
    
    db.close()
    cur.close()
    conn.close()
    
    print("\n✅ Local database setup completed successfully!")
    print("📊 Database: biznes_assistant")
    print("👤 Admin user: admin@bizcore.uz / admin123")
    print("🏢 Company: Demo Company")
    print("🏠 Tenant: Default Tenant")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
