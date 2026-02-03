"""
Test different PostgreSQL connection configurations
"""

import psycopg2
import sys

# Try different common PostgreSQL configurations
configs = [
    {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "password",
        "database": "postgres"  # Default database
    },
    {
        "host": "localhost", 
        "port": 5432,
        "user": "postgres",
        "password": "",  # Empty password
        "database": "postgres"
    },
    {
        "host": "localhost",
        "port": 5432,
        "user": "postgres", 
        "password": "postgres",
        "database": "postgres"
    },
    {
        "host": "localhost",
        "port": 5432,
        "user": "admin",
        "password": "password",
        "database": "postgres"
    }
]

print("Testing PostgreSQL connections...")

for i, config in enumerate(configs, 1):
    try:
        print(f"\nTest {i}: {config['user']}@{config['host']}:{config['port']} with password '{config['password']}'")
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()
        print(f"SUCCESS! Connected to PostgreSQL: {version[0][:50]}...")
        
        # List existing databases
        cur.execute("SELECT datname FROM pg_database WHERE NOT datistemplate")
        databases = cur.fetchall()
        print(f"Existing databases: {[db[0] for db in databases]}")
        
        cur.close()
        conn.close()
        
        print(f"✅ Working configuration found!")
        print(f"Update your DATABASE_URL to: postgresql://{config['user']}:{config['password']}@localhost:5432/biznes_assistant")
        break
        
    except Exception as e:
        print(f"FAILED: {e}")
        continue

print("\nIf none of these worked, you may need to:")
print("1. Check your PostgreSQL installation")
print("2. Reset the postgres user password")
print("3. Create a new user with appropriate permissions")
