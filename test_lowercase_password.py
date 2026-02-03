"""
Test connection with lowercase password: rahmonov
"""

import psycopg2
import sys

print("Testing connection with password: rahmonov (lowercase)")

configs_to_test = [
    {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "rahmonov",
        "database": "postgres"
    },
    {
        "host": "127.0.0.1",
        "port": 5432,
        "user": "postgres",
        "password": "rahmonov",
        "database": "postgres"
    }
]

for i, config in enumerate(configs_to_test, 1):
    try:
        print(f"\nTest {i}: Connecting to {config['host']}:{config['port']} as {config['user']} with password '{config['password']}'")
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
        
        print("Connection successful with lowercase 'rahmonov'!")
        break
        
    except Exception as e:
        print(f"FAILED: {e}")
        continue

print("\nIf this works, I'll update all the configuration files...")
