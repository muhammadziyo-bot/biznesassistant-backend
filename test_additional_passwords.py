"""
Test additional password variations
"""

import psycopg2
import sys

print("Testing additional password variations:")
print("="*50)

passwords_to_test = [
    "Rakhmonov",
    "Muhammadziyo", 
    "rakhmonov",
    "muhammadziyo",
    "Rakhmonov123",
    "Muhammadziyo123",
    "rakhmonov123",
    "muhammadziyo123"
]

config_base = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "database": "postgres"
}

for password in passwords_to_test:
    try:
        config = config_base.copy()
        config["password"] = password
        
        print(f"Testing password: '{password}'")
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        cur.execute("SELECT version()")
        version = cur.fetchone()
        print(f"SUCCESS! Connected with password: '{password}'")
        print(f"PostgreSQL version: {version[0][:60]}...")
        
        # List databases
        cur.execute("SELECT datname FROM pg_database WHERE NOT datistemplate ORDER BY datname")
        databases = cur.fetchall()
        print(f"Available databases: {[db[0] for db in databases]}")
        
        cur.close()
        conn.close()
        
        print("🎉 FOUND WORKING PASSWORD!")
        print(f"Update your DATABASE_URL to: postgresql://postgres:{password}@localhost:5432/biznes_assistant")
        break
        
    except Exception as e:
        print(f"Failed with '{password}': {e}")
        print()

print("If none worked, let's try some other combinations...")

# Try some combinations
combinations = [
    "Rakhmonov_Muhammadziyo",
    "Muhammadziyo_Rakhmonov",
    "RakhmonovMuhammadziyo",
    "MuhammadziyoRakhmonov"
]

print("\nTrying combinations:")
for password in combinations:
    try:
        config = config_base.copy()
        config["password"] = password
        
        conn = psycopg2.connect(**config)
        conn.close()
        print(f"SUCCESS with combination: '{password}'")
        break
        
    except Exception:
        print(f"Failed with combination: '{password}'")
        continue
