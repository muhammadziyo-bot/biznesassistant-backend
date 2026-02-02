"""
Database setup script for BiznesAssistant
This will create tables and check database connectivity
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.database import create_tables, engine
from app.config import settings

def setup_database():
    print("🗄️  DATABASE SETUP FOR BIZNESASSISTANT")
    print("=" * 50)
    
    # Check database configuration
    print(f"📋 Database URL: {settings.DATABASE_URL}")
    
    if "postgresql://" in settings.DATABASE_URL:
        print("🐘 Configured for PostgreSQL")
        
        # Test PostgreSQL connection
        try:
            import psycopg2
            
            # Extract connection details
            db_url = settings.DATABASE_URL
            print(f"🔗 Testing connection to: {db_url.split('@')[1] if '@' in db_url else 'database'}")
            
            # Try to connect
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"✅ PostgreSQL connected: {version.split(',')[0]}")
            
            # Create tables
            print("🏗️  Creating tables...")
            create_tables()
            print("✅ Tables created successfully!")
            
            # Check tables
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print(f"📋 Found {len(tables)} tables:")
            
            main_tables = ['users', 'tenants', 'companies', 'transactions', 'contacts', 'leads', 'deals', 'invoices']
            
            for table in [t[0] for t in tables]:
                status = "✅" if table in main_tables else "📋"
                print(f"  {status} {table}")
                
                if table in main_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"     {count} records")
            
            conn.close()
            
        except ImportError:
            print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
            return False
        except Exception as e:
            print(f"❌ PostgreSQL error: {e}")
            print("\n💡 SOLUTIONS:")
            print("1. Make sure PostgreSQL is running")
            print("2. Check database credentials in config.py")
            print("3. Create database: CREATE DATABASE biznes_assistant;")
            print("4. Update password in DATABASE_URL")
            return False
            
    elif "sqlite:///" in settings.DATABASE_URL:
        print("🗄️  Configured for SQLite")
        
        # Test SQLite connection
        try:
            import sqlite3
            
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
            print(f"📁 SQLite file: {db_path}")
            
            # Create tables
            print("🏗️  Creating tables...")
            create_tables()
            print("✅ Tables created successfully!")
            
            # Check tables
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"📋 Found {len(tables)} tables:")
            
            main_tables = ['users', 'tenants', 'companies', 'transactions', 'contacts', 'leads', 'deals', 'invoices']
            
            for table in [t[0] for t in tables]:
                status = "✅" if table in main_tables else "📋"
                print(f"  {status} {table}")
                
                if table in main_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"     {count} records")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ SQLite error: {e}")
            return False
    else:
        print("❌ Unknown database configuration")
        return False
    
    print("\n🎉 DATABASE SETUP COMPLETE!")
    print("✅ Your backend is ready to save data!")
    return True

if __name__ == "__main__":
    success = setup_database()
    
    if success:
        print("\n🚀 NEXT STEPS:")
        print("1. Start your backend: uvicorn app.main:app --reload")
        print("2. Test API endpoints")
        print("3. Your data will be automatically saved!")
    else:
        print("\n❌ Please fix database issues before starting backend")
