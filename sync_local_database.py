"""
Sync local database with current Python models
"""

import psycopg2
import sys

# Local database connection
conn_params = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "rakhmonov",
    "database": "biznes_assistant"
}

try:
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    print("Connected to local database!")
    
    # Check current table structure
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    
    tables = [row[0] for row in cur.fetchall()]
    print(f"\nCurrent tables: {tables}")
    
    # Check for missing columns in critical tables
    critical_tables = {
        'transactions': ['vat_amount', 'tax_amount', 'reference_number', 'attachment_url', 'is_reconciled', 'contact_id', 'invoice_id'],
        'leads': ['title', 'description', 'contact_name', 'contact_email', 'contact_phone', 'estimated_value', 'probability', 'assigned_user_id'],
        'deals': ['deal_value', 'primary_contact', 'contact_email', 'contact_phone', 'assigned_user_id'],
        'invoices': ['subtotal', 'vat_amount', 'paid_amount', 'remaining_amount', 'created_by_id', 'contact_id'],
        'contacts': ['type', 'assigned_user_id'],
        'tasks': ['assigned_to', 'created_by']
    }
    
    print("\nChecking for missing columns...")
    missing_columns = {}
    
    for table_name, expected_columns in critical_tables.items():
        if table_name in tables:
            # Get actual columns
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY column_name
            """, (table_name,))
            
            actual_columns = [row[0] for row in cur.fetchall()]
            
            # Find missing columns
            missing = [col for col in expected_columns if col not in actual_columns]
            if missing:
                missing_columns[table_name] = missing
                print(f"{table_name}: Missing columns -> {missing}")
            else:
                print(f"{table_name}: All expected columns present")
        else:
            print(f"{table_name}: Table doesn't exist")
    
    # Add missing columns
    if missing_columns:
        print(f"\nAdding missing columns...")
        
        for table_name, columns in missing_columns.items():
            print(f"Fixing {table_name} table...")
            
            for column in columns:
                # Determine column type based on name and table
                column_type = "VARCHAR(255)"
                default_value = "NULL"
                
                if column in ['id', 'user_id', 'company_id', 'tenant_id', 'assigned_user_id', 'assigned_to', 'created_by', 'created_by_id', 'contact_id', 'invoice_id', 'lead_id']:
                    column_type = "INTEGER"
                elif column in ['amount', 'subtotal', 'vat_amount', 'tax_amount', 'total_amount', 'paid_amount', 'remaining_amount', 'estimated_value', 'deal_value']:
                    column_type = "DECIMAL(15,2)"
                    default_value = "0"
                elif column in ['probability']:
                    column_type = "DECIMAL(5,2)"
                    default_value = "0"
                elif column in ['is_active', 'is_verified', 'vat_included', 'is_reconciled']:
                    column_type = "BOOLEAN"
                    default_value = "true" if 'active' in column else "false"
                elif column in ['created_at', 'updated_at', 'issue_date', 'due_date', 'date', 'follow_up_date', 'converted_date', 'expected_close_date', 'actual_close_date', 'completed_at']:
                    column_type = "TIMESTAMP"
                    default_value = "CURRENT_TIMESTAMP" if 'created' in column else "NULL"
                elif column in ['description', 'notes', 'address', 'products_services', 'next_steps', 'lost_reason', 'tags']:
                    column_type = "TEXT"
                elif column in ['role', 'status', 'priority', 'source', 'type', 'category']:
                    column_type = "VARCHAR(50)"
                    default_value = "'manager'" if column == 'role' else "'new'" if column == 'status' else "'medium'" if column == 'priority' else "NULL"
                elif column in ['email', 'username', 'full_name', 'phone', 'name', 'customer_name', 'contact_name', 'contact_email', 'contact_phone', 'company_name', 'primary_contact', 'invoice_number', 'reference_number', 'attachment_url', 'receipt_url']:
                    column_type = "VARCHAR(255)"
                
                # Add the column
                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column} {column_type} DEFAULT {default_value}"
                
                try:
                    cur.execute(alter_sql)
                    print(f"  + Added {column} ({column_type})")
                except Exception as e:
                    print(f"  - Error adding {column}: {e}")
        
        conn.commit()
        print("All missing columns added!")
    
    # Check ENUM types
    print("\nChecking ENUM types...")
    cur.execute("""
        SELECT typname 
        FROM pg_type 
        WHERE typname IN ('transaction_type', 'transaction_category')
    """)
    
    enum_types = [row[0] for row in cur.fetchall()]
    print(f"Existing ENUM types: {enum_types}")
    
    # Create ENUM types if needed
    if 'transaction_type' not in enum_types:
        print("Creating transaction_type ENUM...")
        try:
            cur.execute("CREATE TYPE transaction_type AS ENUM ('income', 'expense', 'INCOME', 'EXPENSE')")
            conn.commit()
            print("Created transaction_type ENUM")
        except Exception as e:
            print(f"Error creating transaction_type ENUM: {e}")
    
    if 'transaction_category' not in enum_types:
        print("Creating transaction_category ENUM...")
        try:
            cur.execute("""
                CREATE TYPE transaction_category AS ENUM (
                    'sales', 'services', 'investment', 'other_income',
                    'salaries', 'rent', 'utilities', 'marketing', 'supplies', 'taxes', 'other_expense',
                    'SALES', 'SERVICES', 'INVESTMENT', 'OTHER_INCOME',
                    'SALARIES', 'RENT', 'UTILITIES', 'MARKETING', 'SUPPLIES', 'TAXES', 'OTHER_EXPENSE'
                )
            """)
            conn.commit()
            print("Created transaction_category ENUM")
        except Exception as e:
            print(f"Error creating transaction_category ENUM: {e}")
    
    # Update transactions table to use ENUM types
    print("\nUpdating transactions table to use ENUM types...")
    try:
        cur.execute("UPDATE transactions SET type = LOWER(type) WHERE type IS NOT NULL")
        cur.execute("UPDATE transactions SET category = LOWER(category) WHERE category IS NOT NULL")
        conn.commit()
        print("Updated data to lowercase")
        
        # Check if columns are already ENUM type
        cur.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'transactions' AND column_name = 'type'
        """)
        type_data_type = cur.fetchone()
        
        if type_data_type and 'user-defined' not in type_data_type[0]:
            cur.execute("ALTER TABLE transactions ALTER COLUMN type TYPE transaction_type USING type::transaction_type")
            conn.commit()
            print("Updated type column to use transaction_type ENUM")
        
        cur.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'transactions' AND column_name = 'category'
        """)
        category_data_type = cur.fetchone()
        
        if category_data_type and 'user-defined' not in category_data_type[0]:
            cur.execute("ALTER TABLE transactions ALTER COLUMN category TYPE transaction_category USING category::transaction_category")
            conn.commit()
            print("Updated category column to use transaction_category ENUM")
        
    except Exception as e:
        print(f"Error updating to ENUM types: {e}")
    
    # Test a transaction insert
    print("\nTesting transaction creation...")
    try:
        cur.execute("""
            INSERT INTO transactions (amount, type, category, description, date, vat_included, vat_amount, tax_amount, user_id, company_id, tenant_id)
            VALUES (100.00, 'income', 'sales', 'Test transaction', CURRENT_TIMESTAMP, true, 12.00, 15.00, 1, 1, 1)
        """)
        conn.commit()
        print("Test transaction created successfully!")
        
        # Clean up
        cur.execute("DELETE FROM transactions WHERE description = 'Test transaction'")
        conn.commit()
        print("Test transaction cleaned up")
        
    except Exception as e:
        print(f"Test transaction failed: {e}")
    
    cur.close()
    conn.close()
    print("\nLocal database sync completed!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
