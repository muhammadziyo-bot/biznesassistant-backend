"""
Test connection with 'Rahmonov' password with detailed debugging
"""

import psycopg2
import sys

print("Testing connection with password: 'Rahmonov' (exact case)")
print("="*60)

# Test with exact password 'Rahmonov'
config = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "Rahmonov",
    "database": "postgres"
}

print(f"Connection details:")
print(f"  Host: {config['host']}")
print(f"  Port: {config['port']}")
print(f"  User: {config['user']}")
print(f"  Password: '{config['password']}'")
print(f"  Database: {config['database']}")
print()

try:
    print("Attempting to connect...")
    conn = psycopg2.connect(**config)
    cur = conn.cursor()
    
    print("SUCCESS! Connected to PostgreSQL!")
    
    cur.execute("SELECT version()")
    version = cur.fetchone()
    print(f"PostgreSQL version: {version[0][:80]}...")
    
    # List databases
    cur.execute("SELECT datname FROM pg_database WHERE NOT datistemplate ORDER BY datname")
    databases = cur.fetchall()
    print(f"Available databases:")
    for db in databases:
        print(f"  - {db[0]}")
    
    # Check if biznes_assistant exists
    db_exists = any('biznes_assistant' in db[0] for db in databases)
    if db_exists:
        print("✅ Database 'biznes_assistant' already exists!")
    else:
        print("❌ Database 'biznes_assistant' does not exist - will create it")
    
    cur.close()
    conn.close()
    
    print("\n🎉 CONNECTION SUCCESSFUL WITH PASSWORD 'Rahmonov'!")
    print("Ready to set up the database!")
    
except Exception as e:
    print(f"CONNECTION FAILED: {e}")
    print()
    print("Possible issues:")
    print("1. Password might be different")
    print("2. PostgreSQL might not be running")
    print("3. User 'postgres' might not exist")
    print("4. Authentication method might be different")
    print()
    print("Let's try some alternative passwords...")

# Try some common alternatives
alternative_passwords = [
    "rahmonov",  # lowercase
    "postgres",  # default
    "password",  # common
    "admin",     # common
    "",          # empty
    "123456",    # numeric
    "Rahmonov123", # with numbers
]

print("\n" + "="*60)
print("Testing alternative passwords:")

for alt_pwd in alternative_passwords:
    try:
        test_config = config.copy()
        test_config["password"] = alt_pwd
        
        conn = psycopg2.connect(**test_config)
        conn.close()
        print(f"SUCCESS with password: '{alt_pwd}'")
        break
        
    except Exception:
        print(f"Failed with password: '{alt_pwd}'")
        continue
