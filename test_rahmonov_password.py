"""
Test connection with the exact password provided
"""

import psycopg2
import sys

print("Testing connection with password: Rahmonov")

configs_to_test = [
    {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "Rahmonov",
        "database": "postgres"
    },
    {
        "host": "127.0.0.1",  # Try IPv4 instead of IPv6
        "port": 5432,
        "user": "postgres",
        "password": "Rahmonov",
        "database": "postgres"
    }
]

for i, config in enumerate(configs_to_test, 1):
    try:
        print(f"\nTest {i}: Connecting to {config['host']}:{config['port']} as {config['user']}")
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        cur.execute("SELECT version()")
        version = cur.fetchone()
        print(f"SUCCESS! PostgreSQL version: {version[0][:60]}...")
        
        # List databases
        cur.execute("SELECT datname FROM pg_database WHERE NOT datistemplate")
        databases = cur.fetchall()
        print(f"Databases: {[db[0] for db in databases]}")
        
        cur.close()
        conn.close()
        
        print("Connection successful!")
        break
        
    except Exception as e:
        print(f"FAILED: {e}")
        continue

# If still fails, let's try to help troubleshoot
print("\n" + "="*50)
print("TROUBLESHOOTING HELP:")
print("1. Make sure PostgreSQL service is running")
print("2. Check if password has special characters")
print("3. Try connecting via pgAdmin to verify credentials")
print("4. Check PostgreSQL configuration (pg_hba.conf)")

# Try to get more info about the PostgreSQL server
try:
    # Try to connect without password to see what happens
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="",
        database="postgres"
    )
    print("Empty password works - maybe your password is actually empty?")
    conn.close()
except:
    print("Empty password doesn't work either")

try:
    # Try with postgres as password
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres"
    )
    print("Password 'postgres' works!")
    conn.close()
except:
    print("Password 'postgres' doesn't work")
