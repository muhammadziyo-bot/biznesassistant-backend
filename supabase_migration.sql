-- Migration Script for Supabase
-- Run this in Supabase SQL Editor
-- Generated from SQLAlchemy models for BiznesAssistant
-- Generated on: 2026-02-03

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop all tables in correct order (to avoid foreign key issues)
DROP TABLE IF EXISTS task_comments CASCADE;
DROP TABLE IF EXISTS recurring_schedules CASCADE;
DROP TABLE IF EXISTS invoice_items CASCADE;
DROP TABLE IF EXISTS activities CASCADE;
DROP TABLE IF EXISTS deals CASCADE;
DROP TABLE IF EXISTS leads CASCADE;
DROP TABLE IF EXISTS contacts CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS templates CASCADE;
DROP TABLE IF EXISTS kpi_alerts CASCADE;
DROP TABLE IF EXISTS kpi_trends CASCADE;
DROP TABLE IF EXISTS kpis CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS tenants CASCADE;

-- Create tables in correct order

-- Table: tenants
CREATE TABLE tenants (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    tax_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    industry VARCHAR(100),
    employee_count INTEGER,
    subscription_tier VARCHAR(50) DEFAULT 'basic',
    subscription_status VARCHAR(50) DEFAULT 'trial',
    trial_ends_at TIMESTAMPTZ,
    subscription_ends_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: companies
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
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
    updated_at TIMESTAMPTZ
);

-- Table: users
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL,
    phone VARCHAR,
    role VARCHAR(50) DEFAULT 'manager',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    email_verification_expires TIMESTAMPTZ,
    email_verified_at TIMESTAMPTZ,
    language VARCHAR DEFAULT 'uz',
    company_id INTEGER REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: contacts
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY,
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
    type VARCHAR(50) DEFAULT 'customer',
    is_active BOOLEAN DEFAULT TRUE,
    telegram VARCHAR,
    instagram VARCHAR,
    facebook VARCHAR,
    linkedin VARCHAR,
    assigned_user_id INTEGER NOT NULL REFERENCES users(id),
    company_id INTEGER NOT NULL REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: leads
CREATE TABLE leads (
    id INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'new',
    source VARCHAR(50),
    estimated_value NUMERIC(15, 2),
    probability NUMERIC(5, 2) DEFAULT 0,
    contact_name VARCHAR NOT NULL,
    contact_email VARCHAR,
    contact_phone VARCHAR,
    company_name VARCHAR,
    address TEXT,
    city VARCHAR,
    region VARCHAR,
    notes TEXT,
    tags TEXT,
    follow_up_date TIMESTAMPTZ,
    converted_date TIMESTAMPTZ,
    assigned_user_id INTEGER NOT NULL REFERENCES users(id),
    company_id INTEGER NOT NULL REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    contact_id INTEGER REFERENCES contacts(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: deals
CREATE TABLE deals (
    id INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'prospecting',
    priority VARCHAR(50) DEFAULT 'medium',
    deal_value NUMERIC(15, 2),
    expected_close_date TIMESTAMPTZ,
    actual_close_date TIMESTAMPTZ,
    probability NUMERIC(5, 2) DEFAULT 0,
    confidence_level NUMERIC(5, 2) DEFAULT 0,
    primary_contact VARCHAR NOT NULL,
    contact_email VARCHAR,
    contact_phone VARCHAR,
    company_name VARCHAR,
    products_services TEXT,
    next_steps TEXT,
    lost_reason TEXT,
    tags TEXT,
    notes TEXT,
    assigned_user_id INTEGER NOT NULL REFERENCES users(id),
    company_id INTEGER NOT NULL REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    contact_id INTEGER REFERENCES contacts(id),
    lead_id INTEGER REFERENCES leads(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: activities
CREATE TABLE activities (
    id INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    scheduled_date TIMESTAMPTZ,
    completed_date TIMESTAMPTZ,
    duration_minutes INTEGER,
    location VARCHAR,
    outcome TEXT,
    priority VARCHAR DEFAULT 'medium',
    reminder_date TIMESTAMPTZ,
    reminder_sent BOOLEAN DEFAULT FALSE,
    notes TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    company_id INTEGER NOT NULL REFERENCES companies(id),
    contact_id INTEGER REFERENCES contacts(id),
    lead_id INTEGER REFERENCES leads(id),
    deal_id INTEGER REFERENCES deals(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: invoices
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    invoice_number VARCHAR UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    customer_name VARCHAR NOT NULL,
    customer_tax_id VARCHAR,
    customer_address TEXT,
    customer_phone VARCHAR,
    customer_email VARCHAR,
    subtotal NUMERIC(15, 2) NOT NULL,
    vat_amount NUMERIC(15, 2) DEFAULT 0,
    total_amount NUMERIC(15, 2) NOT NULL,
    paid_amount NUMERIC(15, 2) DEFAULT 0,
    remaining_amount NUMERIC(15, 2) NOT NULL,
    issue_date TIMESTAMPTZ NOT NULL,
    due_date TIMESTAMPTZ NOT NULL,
    paid_date TIMESTAMPTZ,
    notes TEXT,
    terms TEXT,
    template_name VARCHAR DEFAULT 'default',
    payment_method VARCHAR,
    payment_reference VARCHAR,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_interval VARCHAR,
    recurring_end_date TIMESTAMPTZ,
    created_by_id INTEGER NOT NULL REFERENCES users(id),
    company_id INTEGER NOT NULL REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    contact_id INTEGER REFERENCES contacts(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: invoice_items
CREATE TABLE invoice_items (
    id INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    quantity NUMERIC(10, 2) NOT NULL,
    unit_price NUMERIC(15, 2) NOT NULL,
    discount NUMERIC(5, 2) DEFAULT 0,
    vat_rate NUMERIC(5, 2) DEFAULT 12,
    line_total NUMERIC(15, 2) NOT NULL,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: transactions
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    amount NUMERIC(15, 2) NOT NULL,
    type VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    date TIMESTAMPTZ NOT NULL,
    vat_included BOOLEAN DEFAULT TRUE,
    vat_amount NUMERIC(15, 2) DEFAULT 0,
    tax_amount NUMERIC(15, 2) DEFAULT 0,
    reference_number VARCHAR,
    attachment_url VARCHAR,
    is_reconciled BOOLEAN DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    company_id INTEGER NOT NULL REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    contact_id INTEGER REFERENCES contacts(id),
    invoice_id INTEGER REFERENCES invoices(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: tasks
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'todo' NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium' NOT NULL,
    assigned_to INTEGER REFERENCES users(id),
    created_by INTEGER NOT NULL REFERENCES users(id),
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    company_id INTEGER NOT NULL REFERENCES companies(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: task_comments
CREATE TABLE task_comments (
    id INTEGER PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id),
    content TEXT NOT NULL,
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: templates
CREATE TABLE templates (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    data JSONB NOT NULL,
    is_recurring BOOLEAN DEFAULT FALSE NOT NULL,
    recurring_interval VARCHAR(20),
    recurring_day INTEGER,
    created_by INTEGER NOT NULL REFERENCES users(id),
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    company_id INTEGER NOT NULL REFERENCES companies(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: recurring_schedules
CREATE TABLE recurring_schedules (
    id INTEGER PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES templates(id),
    next_execution_date TIMESTAMPTZ NOT NULL,
    last_execution_date TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE NOT NULL
);

-- Table: kpis
CREATE TABLE kpis (
    id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    tenant_id INTEGER REFERENCES tenants(id),
    category VARCHAR(50) NOT NULL,
    period VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    previous_value FLOAT,
    target_value FLOAT,
    date TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: kpi_trends
CREATE TABLE kpi_trends (
    id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    kpi_category VARCHAR(50) NOT NULL,
    period_type VARCHAR(50) NOT NULL,
    trend_data TEXT NOT NULL,
    forecast_data TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Table: kpi_alerts
CREATE TABLE kpi_alerts (
    id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    kpi_category VARCHAR(50) NOT NULL,
    alert_type VARCHAR NOT NULL,
    condition VARCHAR NOT NULL,
    threshold_value FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_tenants_email ON tenants(email);
CREATE INDEX idx_tenants_tax_id ON tenants(tax_id);
CREATE INDEX idx_tenants_created_at ON tenants(created_at);

CREATE INDEX idx_companies_tenant_id ON companies(tenant_id);
CREATE INDEX idx_companies_email ON companies(email);
CREATE INDEX idx_companies_tax_id ON companies(tax_id);
CREATE INDEX idx_companies_company_code ON companies(company_code);
CREATE INDEX idx_companies_created_at ON companies(created_at);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_company_id ON users(company_id);
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_created_at ON users(created_at);

CREATE INDEX idx_contacts_company_id ON contacts(company_id);
CREATE INDEX idx_contacts_assigned_user_id ON contacts(assigned_user_id);
CREATE INDEX idx_contacts_tenant_id ON contacts(tenant_id);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_created_at ON contacts(created_at);

CREATE INDEX idx_leads_company_id ON leads(company_id);
CREATE INDEX idx_leads_assigned_user_id ON leads(assigned_user_id);
CREATE INDEX idx_leads_contact_id ON leads(contact_id);
CREATE INDEX idx_leads_tenant_id ON leads(tenant_id);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created_at ON leads(created_at);

CREATE INDEX idx_deals_company_id ON deals(company_id);
CREATE INDEX idx_deals_assigned_user_id ON deals(assigned_user_id);
CREATE INDEX idx_deals_contact_id ON deals(contact_id);
CREATE INDEX idx_deals_lead_id ON deals(lead_id);
CREATE INDEX idx_deals_tenant_id ON deals(tenant_id);
CREATE INDEX idx_deals_status ON deals(status);
CREATE INDEX idx_deals_created_at ON deals(created_at);

CREATE INDEX idx_activities_user_id ON activities(user_id);
CREATE INDEX idx_activities_company_id ON activities(company_id);
CREATE INDEX idx_activities_contact_id ON activities(contact_id);
CREATE INDEX idx_activities_lead_id ON activities(lead_id);
CREATE INDEX idx_activities_deal_id ON activities(deal_id);
CREATE INDEX idx_activities_status ON activities(status);
CREATE INDEX idx_activities_created_at ON activities(created_at);

CREATE INDEX idx_invoices_created_by_id ON invoices(created_by_id);
CREATE INDEX idx_invoices_company_id ON invoices(company_id);
CREATE INDEX idx_invoices_contact_id ON invoices(contact_id);
CREATE INDEX idx_invoices_tenant_id ON invoices(tenant_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_invoice_number ON invoices(invoice_number);
CREATE INDEX idx_invoices_created_at ON invoices(created_at);

CREATE INDEX idx_invoice_items_invoice_id ON invoice_items(invoice_id);
CREATE INDEX idx_invoice_items_created_at ON invoice_items(created_at);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_company_id ON transactions(company_id);
CREATE INDEX idx_transactions_contact_id ON transactions(contact_id);
CREATE INDEX idx_transactions_invoice_id ON transactions(invoice_id);
CREATE INDEX idx_transactions_tenant_id ON transactions(tenant_id);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);

CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_created_by ON tasks(created_by);
CREATE INDEX idx_tasks_tenant_id ON tasks(tenant_id);
CREATE INDEX idx_tasks_company_id ON tasks(company_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);

CREATE INDEX idx_task_comments_task_id ON task_comments(task_id);
CREATE INDEX idx_task_comments_created_by ON task_comments(created_by);
CREATE INDEX idx_task_comments_created_at ON task_comments(created_at);

CREATE INDEX idx_templates_created_by ON templates(created_by);
CREATE INDEX idx_templates_tenant_id ON templates(tenant_id);
CREATE INDEX idx_templates_company_id ON templates(company_id);
CREATE INDEX idx_templates_type ON templates(type);
CREATE INDEX idx_templates_created_at ON templates(created_at);

CREATE INDEX idx_recurring_schedules_template_id ON recurring_schedules(template_id);
CREATE INDEX idx_recurring_schedules_next_execution ON recurring_schedules(next_execution_date);

CREATE INDEX idx_kpis_company_id ON kpis(company_id);
CREATE INDEX idx_kpis_tenant_id ON kpis(tenant_id);
CREATE INDEX idx_kpis_category ON kpis(category);
CREATE INDEX idx_kpis_period ON kpis(period);
CREATE INDEX idx_kpis_date ON kpis(date);
CREATE INDEX idx_kpis_created_at ON kpis(created_at);

CREATE INDEX idx_kpi_trends_company_id ON kpi_trends(company_id);
CREATE INDEX idx_kpi_trends_kpi_category ON kpi_trends(kpi_category);
CREATE INDEX idx_kpi_trends_period_type ON kpi_trends(period_type);

CREATE INDEX idx_kpi_alerts_company_id ON kpi_alerts(company_id);
CREATE INDEX idx_kpi_alerts_kpi_category ON kpi_alerts(kpi_category);
CREATE INDEX idx_kpi_alerts_created_at ON kpi_alerts(created_at);

-- Set up Row Level Security (RLS) for multi-tenant isolation
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE recurring_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE kpis ENABLE ROW LEVEL SECURITY;
ALTER TABLE kpi_trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE kpi_alerts ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (basic example - adjust according to your auth strategy)
CREATE POLICY "Users can view own tenant data" ON tenants
    USING (auth.uid()::text = id::text);

CREATE POLICY "Users can view own company data" ON companies
    USING (tenant_id IN (SELECT id FROM tenants WHERE auth.uid()::text = id::text));

-- Add similar policies for other tables based on tenant_id
-- This is a basic example - you may want more sophisticated policies

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_deals_updated_at BEFORE UPDATE ON deals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_activities_updated_at BEFORE UPDATE ON activities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoice_items_updated_at BEFORE UPDATE ON invoice_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_kpis_updated_at BEFORE UPDATE ON kpis
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Migration completed successfully!
-- Your BiznesAssistant database is now ready for use in Supabase.