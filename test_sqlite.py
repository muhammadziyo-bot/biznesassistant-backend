import sqlite3
import os

def check_sqlite():
    # Check if SQLite database file exists
    db_path = 'biznes_assistant.db'
    if os.path.exists(db_path):
        print(f'✅ SQLite database found: {db_path}')
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f'Found {len(tables)} tables:')
            
            # Check main tables
            main_tables = ['users', 'tenants', 'companies', 'transactions', 'contacts', 'leads', 'deals', 'invoices']
            
            for table_name in [t[0] for t in tables]:
                print(f'  📋 {table_name}')
                
                if table_name in main_tables:
                    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                    count = cursor.fetchone()[0]
                    print(f'    ✅ {count} records')
            
            conn.close()
            
        except Exception as e:
            print(f'❌ Error reading SQLite: {e}')
    else:
        print(f'❌ No SQLite database found at: {db_path}')
        
        # Check if backend is configured for PostgreSQL
        with open('app/config.py', 'r') as f:
            config = f.read()
            if 'postgresql://' in config:
                print('📄 Backend is configured for PostgreSQL')
                print('❌ PostgreSQL connection failed - need to check credentials')
            else:
                print('❌ Backend not configured for any database')

if __name__ == "__main__":
    check_sqlite()
