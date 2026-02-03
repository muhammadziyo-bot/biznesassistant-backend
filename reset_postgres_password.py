"""
Script to help reset PostgreSQL password or create a new user
"""

import os
import sys

print("PostgreSQL Password Reset Helper")
print("="*50)
print()
print("Since none of the passwords work, let's try these solutions:")
print()
print("OPTION 1: Reset postgres password via command line")
print("1. Open Command Prompt as Administrator")
print("2. Navigate to PostgreSQL bin folder:")
print("   cd \"C:\\Program Files\\PostgreSQL\\16\\bin\"")
print("3. Run: psql -U postgres")
print("4. If it asks for password, try pressing Enter (empty password)")
print("5. If you get in, run: ALTER USER postgres PASSWORD 'Rahmonov';")
print("6. Type \\q to exit")
print()
print("OPTION 2: Use pgAdmin")
print("1. Open pgAdmin")
print("2. Right-click on your PostgreSQL server")
print("3. Select Properties")
print("4. Look at the connection details")
print("5. Note the actual username and password")
print("6. Or right-click on Login Roles -> postgres -> Properties")
print("7. Set password to 'Rahmonov'")
print()
print("OPTION 3: Check PostgreSQL service")
print("1. Open services.msc")
print("2. Find PostgreSQL service")
print("3. Make sure it's running")
print()
print("OPTION 4: Create a new database user")
print("If you can access postgres with any password, run this SQL:")
print("""
CREATE USER bizcore_user WITH PASSWORD 'bizcore123';
GRANT ALL PRIVILEGES ON DATABASE biznes_assistant TO bizcore_user;
ALTER USER bizcore_user SUPERUSER;
""")
print()
print("OPTION 5: Check pg_hba.conf")
print("1. Find PostgreSQL data directory")
print("2. Open pg_hba.conf file")
print("3. Look for authentication method")
print("4. It might be set to 'peer' or 'ident' instead of 'md5'")
print()
print("After you fix the password, run this script again to set up the database.")
print()
print("For now, let's try to see if we can connect without authentication...")

# Try to connect without authentication
try:
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        database="postgres"
    )
    print("SUCCESS: Connected without password!")
    conn.close()
except Exception as e:
    print(f"No-auth connection failed: {e}")

# Try Windows authentication
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres"
    )
    print("SUCCESS: Connected with Windows authentication!")
    conn.close()
except Exception as e:
    print(f"Windows auth failed: {e}")

print()
print("Please try one of the options above and let me know when you're ready!")
