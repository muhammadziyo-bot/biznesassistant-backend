"""
Setup Supabase database with exact local database structure
"""

import psycopg2
import sys
from datetime import datetime

# Local database connection
LOCAL_CONN = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "rakhmonov",
    "database": "biznes_assistant"
}

def get_local_database_structure():
    """Get the exact structure of local database"""
    
    try:
        conn = psycopg2.connect(**LOCAL_CONN)
        cur = conn.cursor()
        
        print("Analyzing local database structure...")
        
        # Get all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        print(f"Found {len(tables)} tables: {tables}")
        
        database_structure = {}
        
        for table in tables:
            # Get table columns
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table,))
            
            columns = cur.fetchall()
            
            # Get primary key
            cur.execute("""
                SELECT column_name 
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = %s AND tc.constraint_type = 'PRIMARY KEY'
            """, (table,))
            
            primary_keys = [row[0] for row in cur.fetchall()]
            
            # Get foreign keys
            cur.execute("""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = %s
            """, (table,))
            
            foreign_keys = cur.fetchall()
            
            database_structure[table] = {
                'columns': columns,
                'primary_keys': primary_keys,
                'foreign_keys': foreign_keys
            }
        
        cur.close()
        conn.close()
        
        return database_structure
        
    except Exception as e:
        print(f"Error getting local database structure: {e}")
        return None

def generate_supabase_sql(structure):
    """Generate SQL for Supabase setup"""
    
    sql_statements = []
    sql_statements.append("-- Supabase Database Setup")
    sql_statements.append("-- Generated from local database structure")
    sql_statements.append(f"-- Generated on: {datetime.now()}")
    sql_statements.append("")
    
    for table_name, table_info in structure.items():
        sql_statements.append(f"-- Table: {table_name}")
        
        # Create table statement
        columns_sql = []
        for col_name, data_type, is_nullable, default in table_info['columns']:
            # Convert data types to Supabase/PostgreSQL format
            pg_type = convert_data_type(data_type)
            
            nullable = "NOT NULL" if is_nullable == "NO" else ""
            default_sql = f"DEFAULT {default}" if default else ""
            
            column_sql = f"    {col_name} {pg_type} {nullable} {default_sql}"
            columns_sql.append(column_sql.strip())
        
        # Add primary key
        if table_info['primary_keys']:
            pk_sql = f"    PRIMARY KEY ({', '.join(table_info['primary_keys'])})"
            columns_sql.append(pk_sql)
        
        # Add foreign keys
        for fk_col, fk_table, fk_column in table_info['foreign_keys']:
            fk_sql = f"    FOREIGN KEY ({fk_col}) REFERENCES {fk_table}({fk_column})"
            columns_sql.append(fk_sql)
        
        # Create table
        create_sql = f"CREATE TABLE {table_name} (\n"
        create_sql += ",\n".join(columns_sql)
        create_sql += "\n);"
        
        sql_statements.append(create_sql)
        sql_statements.append("")
    
    return "\n".join(sql_statements)

def convert_data_type(data_type):
    """Convert data types to PostgreSQL format"""
    
    type_mapping = {
        'integer': 'INTEGER',
        'bigint': 'BIGINT',
        'smallint': 'SMALLINT',
        'numeric': 'NUMERIC',
        'decimal': 'DECIMAL',
        'real': 'REAL',
        'double precision': 'DOUBLE PRECISION',
        'character varying': 'VARCHAR',
        'varchar': 'VARCHAR',
        'text': 'TEXT',
        'boolean': 'BOOLEAN',
        'date': 'DATE',
        'timestamp without time zone': 'TIMESTAMP',
        'timestamp with time zone': 'TIMESTAMPTZ',
        'time without time zone': 'TIME',
        'time with time zone': 'TIMETZ',
        'json': 'JSONB',
        'uuid': 'UUID',
        'bytea': 'BYTEA'
    }
    
    # Handle precision/scale
    if 'numeric(' in data_type:
        return data_type.replace('numeric', 'NUMERIC')
    elif 'character varying(' in data_type:
        return data_type.replace('character varying', 'VARCHAR')
    elif 'timestamp(' in data_type:
        return data_type.replace('timestamp', 'TIMESTAMP')
    
    return type_mapping.get(data_type.lower(), data_type.upper())

def generate_migration_script(structure):
    """Generate migration script for Supabase"""
    
    migration_sql = []
    migration_sql.append("-- Migration Script for Supabase")
    migration_sql.append("-- Run this in Supabase SQL Editor")
    migration_sql.append("")
    
    # Drop existing tables if they exist (for clean setup)
    for table_name in reversed(list(structure.keys())):
        migration_sql.append(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
    
    migration_sql.append("")
    migration_sql.append("-- Create tables")
    
    # Add the SQL for creating tables
    sql_statements = generate_supabase_sql(structure)
    migration_sql.append(sql_statements)
    
    # Add indexes for performance
    migration_sql.append("")
    migration_sql.append("-- Create indexes for better performance")
    
    for table_name, table_info in structure.items():
        # Add indexes for foreign keys
        for fk_col, _, _ in table_info['foreign_keys']:
            migration_sql.append(f"CREATE INDEX idx_{table_name}_{fk_col} ON {table_name}({fk_col});")
        
        # Add indexes for common query columns
        common_columns = ['company_id', 'tenant_id', 'user_id', 'created_at', 'email', 'status']
        for col_name, _, _, _ in table_info['columns']:
            if col_name in common_columns:
                migration_sql.append(f"CREATE INDEX idx_{table_name}_{col_name} ON {table_name}({col_name});")
    
    return "\n".join(migration_sql)

def create_supabase_setup_guide():
    """Create setup guide for Supabase"""
    
    guide_content = '''# SUPABASE SETUP GUIDE

## 🎯 EXACT DATABASE STRUCTURE SETUP

### 📋 STEPS:

1. **CREATE SUPABASE ACCOUNT**
   - Go to: https://supabase.com
   - Sign up with GitHub/Google
   - Create new organization

2. **CREATE NEW PROJECT**
   - Project name: "biznes-assistant"
   - Database password: Generate strong password
   - Region: Choose closest to you

3. **RUN THE MIGRATION**
   - Open Supabase SQL Editor
   - Copy and paste the migration script from "supabase_migration.sql"
   - Run the script

4. **UPDATE RENDER CONFIG**
   - Get connection string from Supabase Settings
   - Update Render DATABASE_URL environment variable

5. **SYNC YOUR DATA**
   - Run the data sync script to copy data from local to Supabase

## 🔗 CONNECTION STRING FORMAT:
```
postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

## 📦 FILES CREATED:
- `supabase_migration.sql` - Database structure
- `sync_to_supabase.py` - Data sync script
- `supabase_config.py` - Configuration helper

## 🚀 DEPLOYMENT:
1. Update Render environment variables
2. Deploy to Render
3. Test all features
4. Monitor performance

## ✅ BENEFITS:
- Free forever (500MB)
- PostgreSQL compatible
- Professional dashboard
- Auto-backups
- Real-time features
- No security risks
'''
    
    with open('SUPABASE_SETUP.md', 'w') as f:
        f.write(guide_content)
    
    print("Created SUPABASE_SETUP.md")

def main():
    print("Setting up Supabase with exact local database structure...")
    print("=" * 60)
    
    # Get local database structure
    structure = get_local_database_structure()
    
    if not structure:
        print("Failed to get local database structure!")
        return
    
    print(f"Analyzed {len(structure)} tables")
    
    # Generate migration script
    migration_sql = generate_migration_script(structure)
    
    # Save migration script
    with open('supabase_migration.sql', 'w') as f:
        f.write(migration_sql)
    
    print("Created supabase_migration.sql")
    
    # Create setup guide
    create_supabase_setup_guide()
    
    # Create data sync script
    create_sync_script()
    
    print("\n" + "=" * 60)
    print("SUPABASE SETUP COMPLETE!")
    print("\nFiles created:")
    print("- supabase_migration.sql (run this in Supabase)")
    print("- SUPABASE_SETUP.md (follow this guide)")
    print("- sync_to_supabase.py (sync your data)")
    print("\nNext steps:")
    print("1. Create Supabase account")
    print("2. Run the migration script")
    print("3. Sync your data")
    print("4. Update Render config")
    print("5. Deploy!")

def create_sync_script():
    """Create data sync script"""
    
    sync_script = '''"""
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
'''
    
    with open('sync_to_supabase.py', 'w') as f:
        f.write(sync_script)
    
    print("Created sync_to_supabase.py")

if __name__ == "__main__":
    main()
