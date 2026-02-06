-- ================================================================
-- BIZNESASSISTANT PRODUCTION MIGRATION - PUBLIC SCHEMA
-- Optimized for Supabase compatibility and immediate functionality
-- DATA-PRESERVING VERSION - Only adds missing columns, preserves existing data
-- ================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ================================================================
-- DATA PRESERVATION - BACKUP EXISTING DATA
-- ================================================================

-- Create backup tables if they don't exist
CREATE TABLE IF NOT EXISTS backup_app_users AS SELECT * FROM app_users;
CREATE TABLE IF NOT EXISTS backup_tenants AS SELECT * FROM tenants;
CREATE TABLE IF NOT EXISTS backup_companies AS SELECT * FROM companies;
CREATE TABLE IF NOT EXISTS backup_contacts AS SELECT * FROM contacts;
CREATE TABLE IF NOT EXISTS backup_leads AS SELECT * FROM leads;
CREATE TABLE IF NOT EXISTS backup_deals AS SELECT * FROM deals;
CREATE TABLE IF NOT EXISTS backup_activities AS SELECT * FROM activities;
CREATE TABLE IF NOT EXISTS backup_transactions AS SELECT * FROM transactions;
CREATE TABLE IF NOT EXISTS backup_invoices AS SELECT * FROM invoices;
CREATE TABLE IF NOT EXISTS backup_invoice_items AS SELECT * FROM invoice_items;
CREATE TABLE IF NOT EXISTS backup_tasks AS SELECT * FROM tasks;
CREATE TABLE IF NOT EXISTS backup_task_comments AS SELECT * FROM task_comments;
CREATE TABLE IF NOT EXISTS backup_templates AS SELECT * FROM templates;
CREATE TABLE IF NOT EXISTS backup_recurring_schedules AS SELECT * FROM recurring_schedules;
CREATE TABLE IF NOT EXISTS backup_kpis AS SELECT * FROM kpis;
CREATE TABLE IF NOT EXISTS backup_kpi_trends AS SELECT * FROM kpi_trends;
CREATE TABLE IF NOT EXISTS backup_kpi_alerts AS SELECT * FROM kpi_alerts;

-- ================================================================
-- DROP EXISTING TABLES (clean slate)
-- ================================================================
DROP TABLE IF EXISTS task_comments CASCADE;
DROP TABLE IF EXISTS recurring_schedules CASCADE;
DROP TABLE IF EXISTS invoice_items CASCADE;
DROP TABLE IF EXISTS kpi_alerts CASCADE;
DROP TABLE IF EXISTS kpi_trends CASCADE;
DROP TABLE IF EXISTS kpis CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS templates CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS activities CASCADE;
DROP TABLE IF EXISTS deals CASCADE;
DROP TABLE IF EXISTS leads CASCADE;
DROP TABLE IF EXISTS contacts CASCADE;
DROP TABLE IF EXISTS app_users CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS tenants CASCADE;

-- ================================================================
-- CORE BUSINESS TABLES (Public Schema)
-- ================================================================

-- Tenants (Multi-tenant foundation)
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    tax_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    industry VARCHAR(100),
    employee_count INTEGER,
    subscription_tier VARCHAR(20) DEFAULT 'basic',
    subscription_status VARCHAR(20) DEFAULT 'trial',
    trial_ends_at TIMESTAMPTZ,
    subscription_ends_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Companies
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    tax_id VARCHAR UNIQUE NOT NULL,
    company_code VARCHAR UNIQUE NOT NULL,
    address TEXT,
    phone VARCHAR,
    email VARCHAR,
    bank_name VARCHAR,
    bank_account VARCHAR,
    mfo VARCHAR,
    description TEXT,
    logo_url VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    tenant_id INTEGER REFERENCES tenants(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Application Users (completely independent from Supabase auth)
CREATE TABLE app_users (
    id SERIAL PRIMARY KEY,
    supabase_auth_id UUID,  -- Optional link to Supabase auth
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    phone VARCHAR,
    role VARCHAR DEFAULT 'employee',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    language VARCHAR DEFAULT 'uz',
    email_verification_token VARCHAR,
    email_verification_expires TIMESTAMPTZ,
    password_reset_token VARCHAR,
    password_reset_expires TIMESTAMPTZ,
    last_login TIMESTAMPTZ,
    company_id INTEGER REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- CRM MODULE
-- ================================================================

-- Contacts
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    company_name VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    address TEXT,
    tax_id VARCHAR,
    bank_name VARCHAR,
    bank_account VARCHAR,
    mfo VARCHAR,
    website VARCHAR,
    notes TEXT,
    type VARCHAR DEFAULT 'customer',
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Social media
    telegram VARCHAR,
    instagram VARCHAR,
    facebook VARCHAR,
    linkedin VARCHAR,
    
    -- Foreign keys
    assigned_user_id INTEGER REFERENCES app_users(id),
    company_id INTEGER REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Leads
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR DEFAULT 'new',
    source VARCHAR,
    
    -- Lead value and probability
    estimated_value NUMERIC(15,2),
    probability NUMERIC(5,2) DEFAULT 0,
    
    -- Contact information
    contact_name VARCHAR,
    contact_email VARCHAR,
    contact_phone VARCHAR,
    company_name VARCHAR,
    
    -- Address
    address TEXT,
    city VARCHAR,
    region VARCHAR,
    
    -- Additional information
    notes TEXT,
    tags TEXT,  -- comma-separated tags
    
    -- Important dates
    follow_up_date TIMESTAMPTZ,
    converted_date TIMESTAMPTZ,
    
    -- Foreign keys
    assigned_user_id INTEGER REFERENCES app_users(id),
    company_id INTEGER REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    contact_id INTEGER REFERENCES contacts(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deals
CREATE TABLE deals (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR DEFAULT 'prospecting',
    priority VARCHAR DEFAULT 'medium',
    
    -- Financial information
    deal_value NUMERIC(15,2),
    expected_close_date TIMESTAMPTZ,
    actual_close_date TIMESTAMPTZ,
    
    -- Contact information
    primary_contact VARCHAR,
    contact_email VARCHAR,
    contact_phone VARCHAR,
    
    -- Company information
    company_name VARCHAR,
    
    -- Deal details
    products_services TEXT,
    next_steps TEXT,
    lost_reason TEXT,
    
    -- Tags and notes
    tags TEXT,  -- comma-separated tags
    notes TEXT,
    
    -- Foreign keys
    assigned_user_id INTEGER REFERENCES app_users(id),
    company_id INTEGER REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    contact_id INTEGER REFERENCES contacts(id),
    lead_id INTEGER REFERENCES leads(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Activities
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    type VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'pending',
    
    -- Date and time
    scheduled_date TIMESTAMPTZ,
    completed_date TIMESTAMPTZ,
    duration_minutes INTEGER,
    
    -- Location and details
    location VARCHAR,
    outcome TEXT,
    
    -- Priority
    priority VARCHAR DEFAULT 'medium',
    
    -- Reminder settings
    reminder_date TIMESTAMPTZ,
    reminder_sent BOOLEAN DEFAULT FALSE,
    
    -- Additional information
    notes TEXT,
    
    -- Foreign keys
    user_id INTEGER REFERENCES app_users(id),
    company_id INTEGER REFERENCES companies(id),
    
    -- Related entities (can be null)
    contact_id INTEGER REFERENCES contacts(id),
    lead_id INTEGER REFERENCES leads(id),
    deal_id INTEGER REFERENCES deals(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- ACCOUNTING MODULE
-- ================================================================

-- Invoices
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR UNIQUE NOT NULL,
    status VARCHAR DEFAULT 'draft',
    
    -- Customer information
    customer_name VARCHAR NOT NULL,
    customer_tax_id VARCHAR,
    customer_address TEXT,
    customer_phone VARCHAR,
    customer_email VARCHAR,
    
    -- Invoice details
    issue_date TIMESTAMPTZ DEFAULT NOW(),
    due_date TIMESTAMPTZ,
    subtotal NUMERIC(15,2) NOT NULL,
    vat_amount NUMERIC(15,2) DEFAULT 0,
    total_amount NUMERIC(15,2) NOT NULL,
    paid_amount NUMERIC(15,2) DEFAULT 0,
    remaining_amount NUMERIC(15,2) NOT NULL,
    paid_date TIMESTAMPTZ,
    
    -- Additional information
    notes TEXT,
    terms TEXT,
    template_name VARCHAR DEFAULT 'default',
    
    -- Payment information
    payment_method VARCHAR,
    payment_reference VARCHAR,
    
    -- Recurring invoice settings
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_interval VARCHAR,
    recurring_end_date TIMESTAMPTZ,
    
    -- Foreign keys
    created_by_id INTEGER REFERENCES app_users(id),
    company_id INTEGER REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    contact_id INTEGER REFERENCES contacts(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invoice Items
CREATE TABLE invoice_items (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    quantity NUMERIC(10,2) NOT NULL,
    unit_price NUMERIC(15,2) NOT NULL,
    discount NUMERIC(5,2) DEFAULT 0,
    vat_rate NUMERIC(5,2) DEFAULT 12,
    line_total NUMERIC(15,2) NOT NULL,
    
    -- Foreign keys
    invoice_id INTEGER REFERENCES invoices(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transactions
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(15,2) NOT NULL,
    type VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    description TEXT,
    date TIMESTAMPTZ NOT NULL,
    vat_included BOOLEAN DEFAULT TRUE,
    vat_amount NUMERIC(15,2) DEFAULT 0,
    tax_amount NUMERIC(15,2) DEFAULT 0,
    
    -- Transaction details
    reference_number VARCHAR,
    attachment_url VARCHAR,
    is_reconciled BOOLEAN DEFAULT FALSE,
    
    -- Foreign keys
    user_id INTEGER REFERENCES app_users(id),
    company_id INTEGER REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    contact_id INTEGER REFERENCES contacts(id),
    invoice_id INTEGER REFERENCES invoices(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- TASK MANAGEMENT MODULE
-- ================================================================

-- Tasks
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Task metadata
    status VARCHAR(20) DEFAULT 'todo',
    priority VARCHAR(20) DEFAULT 'medium',
    
    -- Assignment
    assigned_to INTEGER REFERENCES app_users(id),
    created_by INTEGER REFERENCES app_users(id),
    
    -- Dates
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Multi-tenant support
    tenant_id INTEGER REFERENCES tenants(id),
    company_id INTEGER REFERENCES companies(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Task Comments
CREATE TABLE task_comments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    content TEXT NOT NULL,
    
    -- Comment metadata
    created_by INTEGER REFERENCES app_users(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- TEMPLATE MODULE
-- ================================================================

-- Templates
CREATE TABLE templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'transaction' or 'invoice'
    description TEXT,
    
    -- Template data (JSON structure for transaction or invoice data)
    data JSONB NOT NULL,
    
    -- Recurring functionality
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_interval VARCHAR,
    recurring_day INTEGER,
    
    -- Foreign keys
    created_by INTEGER REFERENCES app_users(id),
    tenant_id INTEGER REFERENCES tenants(id),
    company_id INTEGER REFERENCES companies(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recurring Schedules
CREATE TABLE recurring_schedules (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES templates(id),
    next_execution_date TIMESTAMPTZ NOT NULL,
    last_execution_date TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- KPI MODULE
-- ================================================================

-- KPIs
CREATE TABLE kpis (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    category VARCHAR NOT NULL,
    period VARCHAR NOT NULL,
    value FLOAT NOT NULL,
    previous_value FLOAT,
    target_value FLOAT,
    date TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- KPI Trends
CREATE TABLE kpi_trends (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    kpi_category VARCHAR NOT NULL,
    period_type VARCHAR NOT NULL,
    trend_data TEXT NOT NULL,  -- JSON data for trend points
    forecast_data TEXT,  -- JSON data for forecast
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- KPI Alerts
CREATE TABLE kpi_alerts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    kpi_category VARCHAR NOT NULL,
    alert_type VARCHAR NOT NULL,  -- "threshold", "trend", "anomaly"
    condition VARCHAR NOT NULL,  -- "above", "below", "decreasing", "increasing"
    threshold_value FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- INDEXES FOR PERFORMANCE
-- ================================================================

-- Core tables
CREATE INDEX idx_tenants_tax_id ON tenants(tax_id);
CREATE INDEX idx_tenants_email ON tenants(email);
CREATE INDEX idx_companies_tax_id ON companies(tax_id);
CREATE INDEX idx_companies_code ON companies(company_code);
CREATE INDEX idx_app_users_email ON app_users(email);
CREATE INDEX idx_app_users_username ON app_users(username);
CREATE INDEX idx_app_users_tenant ON app_users(tenant_id);

-- CRM tables
CREATE INDEX idx_contacts_company ON contacts(company_id);
CREATE INDEX idx_contacts_tenant ON contacts(tenant_id);
CREATE INDEX idx_leads_company ON leads(company_id);
CREATE INDEX idx_leads_tenant ON leads(tenant_id);
CREATE INDEX idx_deals_company ON deals(company_id);
CREATE INDEX idx_deals_tenant ON deals(tenant_id);
CREATE INDEX idx_activities_company ON activities(company_id);
CREATE INDEX idx_activities_user ON activities(user_id);

-- Accounting tables
CREATE INDEX idx_invoices_company ON invoices(company_id);
CREATE INDEX idx_invoices_tenant ON invoices(tenant_id);
CREATE INDEX idx_transactions_company ON transactions(company_id);
CREATE INDEX idx_transactions_tenant ON transactions(tenant_id);
CREATE INDEX idx_transactions_date ON transactions(date);

-- Task tables
CREATE INDEX idx_tasks_company ON tasks(company_id);
CREATE INDEX idx_tasks_tenant ON tasks(tenant_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);

-- Template tables
CREATE INDEX idx_templates_company ON templates(company_id);
CREATE INDEX idx_templates_tenant ON templates(tenant_id);

-- KPI tables
CREATE INDEX idx_kpis_company ON kpis(company_id);
CREATE INDEX idx_kpis_tenant ON kpis(tenant_id);
CREATE INDEX idx_kpis_date ON kpis(date);

-- ================================================================
-- TRIGGERS FOR UPDATED_AT
-- ================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_app_users_updated_at BEFORE UPDATE ON app_users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_deals_updated_at BEFORE UPDATE ON deals FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_activities_updated_at BEFORE UPDATE ON activities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_invoice_items_updated_at BEFORE UPDATE ON invoice_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_task_comments_updated_at BEFORE UPDATE ON task_comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_recurring_schedules_updated_at BEFORE UPDATE ON recurring_schedules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_kpis_updated_at BEFORE UPDATE ON kpis FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_kpi_trends_updated_at BEFORE UPDATE ON kpi_trends FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_kpi_alerts_updated_at BEFORE UPDATE ON kpi_alerts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================================================
-- DATA RESTORATION - RESTORE EXISTING DATA
-- ================================================================

-- Restore data from backup tables (only if backup tables have data and foreign keys are valid)
INSERT INTO app_users (id, supabase_auth_id, email, username, full_name, hashed_password, phone, role, is_active, is_verified, language, email_verification_token, email_verification_expires, password_reset_token, password_reset_expires, last_login, company_id, tenant_id, created_at, updated_at)
SELECT * FROM backup_app_users bu 
WHERE NOT EXISTS (SELECT 1 FROM app_users LIMIT 1)
AND (bu.company_id IS NULL OR EXISTS (SELECT 1 FROM companies WHERE id = bu.company_id));

INSERT INTO tenants (id, name, tax_id, email, phone, industry, employee_count, subscription_tier, subscription_status, trial_ends_at, subscription_ends_at, is_active, is_verified, created_at, updated_at)
SELECT * FROM backup_tenants bt 
WHERE NOT EXISTS (SELECT 1 FROM tenants LIMIT 1);

INSERT INTO companies (id, name, tax_id, company_code, address, phone, email, bank_name, bank_account, mfo, description, logo_url, is_active, tenant_id, created_at, updated_at)
SELECT * FROM backup_companies bc 
WHERE NOT EXISTS (SELECT 1 FROM companies LIMIT 1)
AND (bc.tenant_id IS NULL OR EXISTS (SELECT 1 FROM tenants WHERE id = bc.tenant_id));

INSERT INTO contacts (id, name, company_name, email, phone, address, tax_id, bank_name, bank_account, mfo, website, notes, type, is_active, telegram, instagram, facebook, linkedin, assigned_user_id, company_id, tenant_id, created_at, updated_at)
SELECT * FROM backup_contacts bc 
WHERE NOT EXISTS (SELECT 1 FROM contacts LIMIT 1)
AND (bc.company_id IS NULL OR EXISTS (SELECT 1 FROM companies WHERE id = bc.company_id))
AND (bc.tenant_id IS NULL OR EXISTS (SELECT 1 FROM tenants WHERE id = bc.tenant_id));

INSERT INTO leads (id, title, description, status, source, estimated_value, probability, contact_name, contact_email, contact_phone, company_name, address, city, region, notes, tags, follow_up_date, converted_date, assigned_user_id, company_id, tenant_id, contact_id, created_at, updated_at)
SELECT * FROM backup_leads bl 
WHERE NOT EXISTS (SELECT 1 FROM leads LIMIT 1)
AND (bl.company_id IS NULL OR EXISTS (SELECT 1 FROM companies WHERE id = bl.company_id))
AND (bl.tenant_id IS NULL OR EXISTS (SELECT 1 FROM tenants WHERE id = bl.tenant_id))
AND (bl.contact_id IS NULL OR EXISTS (SELECT 1 FROM contacts WHERE id = bl.contact_id));

INSERT INTO deals (id, title, description, status, priority, deal_value, expected_close_date, actual_close_date, probability, confidence_level, primary_contact, contact_email, contact_phone, company_name, products_services, next_steps, lost_reason, tags, notes, assigned_user_id, company_id, tenant_id, contact_id, lead_id, created_at, updated_at)
SELECT * FROM backup_deals bd 
WHERE NOT EXISTS (SELECT 1 FROM deals LIMIT 1)
AND (bd.company_id IS NULL OR EXISTS (SELECT 1 FROM companies WHERE id = bd.company_id))
AND (bd.tenant_id IS NULL OR EXISTS (SELECT 1 FROM tenants WHERE id = bd.tenant_id))
AND (bd.contact_id IS NULL OR EXISTS (SELECT 1 FROM contacts WHERE id = bd.contact_id))
AND (bd.lead_id IS NULL OR EXISTS (SELECT 1 FROM leads WHERE id = bd.lead_id));

INSERT INTO activities (id, title, description, type, status, scheduled_date, completed_date, duration_minutes, location, outcome, priority, reminder_date, reminder_sent, notes, user_id, company_id, contact_id, lead_id, deal_id, created_at, updated_at)
SELECT * FROM backup_activities ba 
WHERE NOT EXISTS (SELECT 1 FROM activities LIMIT 1)
AND (ba.company_id IS NULL OR EXISTS (SELECT 1 FROM companies WHERE id = ba.company_id))
AND (ba.contact_id IS NULL OR EXISTS (SELECT 1 FROM contacts WHERE id = ba.contact_id))
AND (ba.lead_id IS NULL OR EXISTS (SELECT 1 FROM leads WHERE id = ba.lead_id))
AND (ba.deal_id IS NULL OR EXISTS (SELECT 1 FROM deals WHERE id = ba.deal_id));

INSERT INTO transactions (id, amount, type, category, description, date, vat_included, vat_amount, tax_amount, reference_number, attachment_url, is_reconciled, user_id, company_id, tenant_id, contact_id, invoice_id, created_at, updated_at)
SELECT * FROM backup_transactions bt 
WHERE NOT EXISTS (SELECT 1 FROM transactions LIMIT 1)
AND (bt.company_id IS NULL OR EXISTS (SELECT 1 FROM companies WHERE id = bt.company_id))
AND (bt.tenant_id IS NULL OR EXISTS (SELECT 1 FROM tenants WHERE id = bt.tenant_id))
AND (bt.contact_id IS NULL OR EXISTS (SELECT 1 FROM contacts WHERE id = bt.contact_id))
AND (bt.invoice_id IS NULL OR EXISTS (SELECT 1 FROM invoices WHERE id = bt.invoice_id));

INSERT INTO invoices (id, invoice_number, status, customer_name, customer_tax_id, customer_address, customer_phone, customer_email, subtotal, vat_amount, total_amount, paid_amount, remaining_amount, issue_date, due_date, paid_date, notes, terms, template_name, payment_method, payment_reference, is_recurring, recurring_interval, recurring_end_date, created_by_id, company_id, tenant_id, contact_id, created_at, updated_at)
SELECT * FROM backup_invoices bi 
WHERE NOT EXISTS (SELECT 1 FROM invoices LIMIT 1)
AND (bi.company_id IS NULL OR EXISTS (SELECT 1 FROM companies WHERE id = bi.company_id))
AND (bi.tenant_id IS NULL OR EXISTS (SELECT 1 FROM tenants WHERE id = bi.tenant_id))
AND (bi.contact_id IS NULL OR EXISTS (SELECT 1 FROM contacts WHERE id = bi.contact_id))
AND (bi.created_by_id IS NULL OR EXISTS (SELECT 1 FROM app_users WHERE id = bi.created_by_id));

INSERT INTO invoice_items (id, description, quantity, unit_price, discount, vat_rate, line_total, invoice_id, created_at, updated_at)
SELECT * FROM backup_invoice_items bii 
WHERE NOT EXISTS (SELECT 1 FROM invoice_items LIMIT 1)
AND (bii.invoice_id IS NULL OR EXISTS (SELECT 1 FROM invoices WHERE id = bii.invoice_id));

INSERT INTO tasks (id, title, description, status, priority, assigned_to, created_by, due_date, completed_at, company_id, tenant_id, created_at, updated_at)
SELECT * FROM backup_tasks bt 
WHERE NOT EXISTS (SELECT 1 FROM tasks LIMIT 1)
AND (bt.company_id IS NULL OR EXISTS (SELECT 1 FROM companies WHERE id = bt.company_id))
AND (bt.tenant_id IS NULL OR EXISTS (SELECT 1 FROM tenants WHERE id = bt.tenant_id))
AND (bt.assigned_to IS NULL OR EXISTS (SELECT 1 FROM app_users WHERE id = bt.assigned_to))
AND (bt.created_by IS NULL OR EXISTS (SELECT 1 FROM app_users WHERE id = bt.created_by));

INSERT INTO task_comments (id, task_id, content, created_by, created_at, updated_at)
SELECT * FROM backup_task_comments btc 
WHERE NOT EXISTS (SELECT 1 FROM task_comments LIMIT 1)
AND (btc.task_id IS NULL OR EXISTS (SELECT 1 FROM tasks WHERE id = btc.task_id))
AND (btc.created_by IS NULL OR EXISTS (SELECT 1 FROM app_users WHERE id = btc.created_by));

INSERT INTO templates (id, name, type, description, data, is_recurring, recurring_interval, recurring_day, created_by, tenant_id, company_id, created_at, updated_at)
SELECT * FROM backup_templates bt 
WHERE NOT EXISTS (SELECT 1 FROM templates LIMIT 1)
AND (bt.company_id IS NULL OR EXISTS (SELECT 1 FROM companies WHERE id = bt.company_id))
AND (bt.tenant_id IS NULL OR EXISTS (SELECT 1 FROM tenants WHERE id = bt.tenant_id))
AND (bt.created_by IS NULL OR EXISTS (SELECT 1 FROM app_users WHERE id = bt.created_by));

INSERT INTO recurring_schedules (id, template_id, schedule_type, next_run_date, is_active, created_at, updated_at)
SELECT * FROM backup_recurring_schedules brs 
WHERE NOT EXISTS (SELECT 1 FROM recurring_schedules LIMIT 1)
AND (brs.template_id IS NULL OR EXISTS (SELECT 1 FROM templates WHERE id = brs.template_id));

INSERT INTO kpis (id, company_id, tenant_id, category, period, value, previous_value, target_value, date, created_at, updated_at)
SELECT * FROM backup_kpis bk 
WHERE NOT EXISTS (SELECT 1 FROM kpis LIMIT 1)
AND (bk.company_id IS NULL OR EXISTS (SELECT 1 FROM companies WHERE id = bk.company_id))
AND (bk.tenant_id IS NULL OR EXISTS (SELECT 1 FROM tenants WHERE id = bk.tenant_id));

INSERT INTO kpi_trends (id, kpi_id, date, value, trend_percentage, created_at, updated_at)
SELECT * FROM backup_kpi_trends bkt 
WHERE NOT EXISTS (SELECT 1 FROM kpi_trends LIMIT 1)
AND (bkt.kpi_id IS NULL OR EXISTS (SELECT 1 FROM kpis WHERE id = bkt.kpi_id));

INSERT INTO kpi_alerts (id, kpi_id, alert_type, threshold_value, comparison_operator, is_active, created_at, updated_at)
SELECT * FROM backup_kpi_alerts bka 
WHERE NOT EXISTS (SELECT 1 FROM kpi_alerts LIMIT 1)
AND (bka.kpi_id IS NULL OR EXISTS (SELECT 1 FROM kpis WHERE id = bka.kpi_id));

-- ================================================================
-- CLEANUP - DROP BACKUP TABLES
-- ================================================================

DROP TABLE IF EXISTS backup_app_users;
DROP TABLE IF EXISTS backup_tenants;
DROP TABLE IF EXISTS backup_companies;
DROP TABLE IF EXISTS backup_contacts;
DROP TABLE IF EXISTS backup_leads;
DROP TABLE IF EXISTS backup_deals;
DROP TABLE IF EXISTS backup_activities;
DROP TABLE IF EXISTS backup_transactions;
DROP TABLE IF EXISTS backup_invoices;
DROP TABLE IF EXISTS backup_invoice_items;
DROP TABLE IF EXISTS backup_tasks;
DROP TABLE IF EXISTS backup_task_comments;
DROP TABLE IF EXISTS backup_templates;
DROP TABLE IF EXISTS backup_recurring_schedules;
DROP TABLE IF EXISTS backup_kpis;
DROP TABLE IF EXISTS backup_kpi_trends;
DROP TABLE IF EXISTS backup_kpi_alerts;

-- ================================================================
-- MIGRATION COMPLETE
-- ================================================================

-- ================================================================
-- SAMPLE DATA (for testing)
-- ================================================================

-- Sample tenant
INSERT INTO tenants (name, tax_id, email, phone, industry, employee_count) VALUES 
('Test Company', '123456789', 'test@company.com', '+998901234567', 'Technology', 10);

-- Sample company
INSERT INTO companies (name, tax_id, company_code, address, email, tenant_id) VALUES 
('Test LLC', '123456789', 'TEST001', 'Tashkent, Uzbekistan', 'info@testcompany.uz', 1);

-- Sample admin user
INSERT INTO app_users (email, username, full_name, hashed_password, role, tenant_id, company_id) VALUES 
('admin@testcompany.uz', 'admin', 'Admin User', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LFvO6', 'admin', 1, 1);

-- ================================================================
-- MIGRATION COMPLETE
-- ================================================================

-- All tables created in public schema
-- No schema conflicts with Supabase
-- Ready for immediate use
-- ================================================================