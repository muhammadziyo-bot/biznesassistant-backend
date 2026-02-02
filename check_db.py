import psycopg2

def check_database():
    try:
        # Try common PostgreSQL passwords
        passwords = ['password', 'postgres', 'admin', '123456', '']
        
        for pwd in passwords:
            try:
                conn = psycopg2.connect(f'postgresql://postgres:{pwd}@localhost:5432/biznes_assistant')
                print(f'Success with password: "{pwd}"')
                
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = \'public\'')
                table_count = cursor.fetchone()[0]
                print(f'Found {table_count} tables')
                
                cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\' ORDER BY table_name')
                tables = cursor.fetchall()
                print('Tables:', [t[0] for t in tables])
                
                # Check if our main tables exist
                main_tables = ['users', 'tenants', 'companies', 'transactions', 'contacts', 'leads', 'deals', 'invoices']
                existing_tables = [t[0] for t in tables]
                
                print('\n=== TABLE STATUS ===')
                for table in main_tables:
                    if table in existing_tables:
                        cursor.execute(f'SELECT COUNT(*) FROM {table}')
                        count = cursor.fetchone()[0]
                        print(f'✅ {table}: {count} records')
                    else:
                        print(f'❌ {table}: NOT FOUND')
                
                conn.close()
                return True
                
            except Exception as e:
                print(f'Failed with password "{pwd}": {e}')
                continue
        
        print('No working password found')
        return False
        
    except Exception as e:
        print(f'Error: {e}')
        return False

if __name__ == "__main__":
    check_database()
