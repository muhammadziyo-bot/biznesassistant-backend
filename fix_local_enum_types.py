"""
Fix local database ENUM types for transactions
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
    
    # Check current column types
    cur.execute("""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns 
        WHERE table_name = 'transactions' AND column_name IN ('type', 'category')
    """)
    
    columns = cur.fetchall()
    print("\nCurrent transactions column types:")
    for col in columns:
        print(f"  {col[0]}: {col[1]} ({col[2]})")
    
    # Drop existing ENUM types and recreate with both cases
    print("\nDropping and recreating ENUM types...")
    
    # First, convert columns back to VARCHAR
    try:
        cur.execute("ALTER TABLE transactions ALTER COLUMN type TYPE VARCHAR(20)")
        cur.execute("ALTER TABLE transactions ALTER COLUMN category TYPE VARCHAR(50)")
        conn.commit()
        print("Converted columns to VARCHAR")
    except Exception as e:
        print(f"Error converting to VARCHAR: {e}")
    
    # Drop existing ENUM types
    try:
        cur.execute("DROP TYPE IF EXISTS transaction_type")
        cur.execute("DROP TYPE IF EXISTS transaction_category")
        conn.commit()
        print("Dropped existing ENUM types")
    except Exception as e:
        print(f"Error dropping ENUM types: {e}")
    
    # Create new ENUM types with both cases
    try:
        cur.execute("CREATE TYPE transaction_type AS ENUM ('income', 'expense', 'INCOME', 'EXPENSE')")
        conn.commit()
        print("Created transaction_type ENUM with both cases")
    except Exception as e:
        print(f"Error creating transaction_type ENUM: {e}")
    
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
        print("Created transaction_category ENUM with both cases")
    except Exception as e:
        print(f"Error creating transaction_category ENUM: {e}")
    
    # Update existing data to lowercase
    try:
        cur.execute("UPDATE transactions SET type = LOWER(type) WHERE type IS NOT NULL")
        cur.execute("UPDATE transactions SET category = LOWER(category) WHERE category IS NOT NULL")
        conn.commit()
        print("Updated existing data to lowercase")
    except Exception as e:
        print(f"Error updating data: {e}")
    
    # Convert columns back to ENUM
    try:
        cur.execute("ALTER TABLE transactions ALTER COLUMN type TYPE transaction_type USING type::transaction_type")
        cur.execute("ALTER TABLE transactions ALTER COLUMN category TYPE transaction_category USING category::transaction_category")
        conn.commit()
        print("Converted columns to ENUM types")
    except Exception as e:
        print(f"Error converting to ENUM: {e}")
    
    # Test transaction creation with both cases
    print("\nTesting transaction creation...")
    
    # Test with lowercase
    try:
        cur.execute("""
            INSERT INTO transactions (amount, type, category, description, date, vat_included, vat_amount, tax_amount, user_id, company_id, tenant_id)
            VALUES (100.00, 'income', 'sales', 'Test lowercase', CURRENT_TIMESTAMP, true, 12.00, 15.00, 1, 1, 1)
        """)
        conn.commit()
        print("Test with lowercase successful!")
        
        # Clean up
        cur.execute("DELETE FROM transactions WHERE description = 'Test lowercase'")
        conn.commit()
        
    except Exception as e:
        print(f"Test with lowercase failed: {e}")
    
    # Test with uppercase
    try:
        cur.execute("""
            INSERT INTO transactions (amount, type, category, description, date, vat_included, vat_amount, tax_amount, user_id, company_id, tenant_id)
            VALUES (200.00, 'INCOME', 'SALES', 'Test uppercase', CURRENT_TIMESTAMP, true, 24.00, 30.00, 1, 1, 1)
        """)
        conn.commit()
        print("Test with uppercase successful!")
        
        # Clean up
        cur.execute("DELETE FROM transactions WHERE description = 'Test uppercase'")
        conn.commit()
        
    except Exception as e:
        print(f"Test with uppercase failed: {e}")
    
    # Verify final column types
    cur.execute("""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns 
        WHERE table_name = 'transactions' AND column_name IN ('type', 'category')
    """)
    
    columns = cur.fetchall()
    print("\nFinal transactions column types:")
    for col in columns:
        print(f"  {col[0]}: {col[1]} ({col[2]})")
    
    cur.close()
    conn.close()
    print("\nLocal ENUM types fix completed!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
