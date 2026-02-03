"""
Sync data from local PostgreSQL to Supabase
"""

import psycopg2
import sys
from datetime import datetime

# Local database
LOCAL_CONN = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "rakhmonov",
    "database": "biznes_assistant"
}

# Supabase database (update with your actual credentials)
SUPABASE_CONN = {
    "host": "YOUR_SUPABASE_HOST",
    "port": 5432,
    "user": "postgres",
    "password": "YOUR_SUPABASE_PASSWORD",
    "database": "postgres"
}

def sync_all_data():
    """Sync all data from local to Supabase"""
    
    tables_to_sync = [
        'tenants', 'companies', 'users', 'contacts', 'leads', 'deals',
        'transactions', 'invoices', 'invoice_items', 'tasks', 'task_comments',
        'kpis', 'kpi_trends', 'kpi_alerts', 'templates', 'activities',
        'recurring_schedules'
    ]
    
    print("Starting data sync from local to Supabase...")
    
    try:
        # Connect to local database
        local_conn = psycopg2.connect(**LOCAL_CONN)
        local_cur = local_conn.cursor()
        
        # Connect to Supabase
        supabase_conn = psycopg2.connect(**SUPABASE_CONN)
        supabase_cur = supabase_conn.cursor()
        
        for table in tables_to_sync:
            print(f"Syncing {table}...")
            
            try:
                # Get data from local
                local_cur.execute(f"SELECT * FROM {table}")
                data = local_cur.fetchall()
                
                # Get column names
                local_cur.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns = [row[0] for row in local_cur.fetchall()]
                
                if data:
                    # Clear Supabase table
                    supabase_cur.execute(f"DELETE FROM {table}")
                    
                    # Insert data
                    placeholders = ', '.join(['%s'] * len(columns))
                    insert_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                    supabase_cur.executemany(insert_query, data)
                    
                    print(f"  Synced {len(data)} rows")
                else:
                    print(f"  No data to sync")
                
                supabase_conn.commit()
                
            except Exception as e:
                print(f"  Error syncing {table}: {e}")
                continue
        
        local_cur.close()
        local_conn.close()
        supabase_cur.close()
        supabase_conn.close()
        
        print("Data sync completed!")
        
    except Exception as e:
        print(f"Sync failed: {e}")

if __name__ == "__main__":
    sync_all_data()
