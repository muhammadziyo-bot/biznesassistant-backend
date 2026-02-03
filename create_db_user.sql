-- SQL script to create a new database user for your application
-- Run this in PostgreSQL as a superuser

-- Create the user with password
CREATE USER bizcore_user WITH PASSWORD 'bizcore123';

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE biznes_assistant TO bizcore_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bizcore_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bizcore_user;

-- Set default permissions for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO bizcore_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO bizcore_user;

-- Make the user a superuser if needed (for development)
ALTER USER bizcore_user SUPERUSER;

-- Test the connection
-- You can now connect with: postgresql://bizcore_user:bizcore123@localhost:5432/biznes_assistant
