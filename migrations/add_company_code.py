"""
Add company_code column to companies table
"""
from sqlalchemy import text

def upgrade():
    """Add company_code column with unique constraint"""
    sql = """
    ALTER TABLE companies 
    ADD COLUMN company_code VARCHAR(6) UNIQUE NOT NULL;
    
    -- Generate unique codes for existing companies
    UPDATE companies 
    SET company_code = UPPER(SUBSTRING(MD5(CONCAT(id, name, tax_id)), 1, 6));
    """
    return sql

def downgrade():
    """Remove company_code column"""
    return "ALTER TABLE companies DROP COLUMN company_code;"
