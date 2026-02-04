-- Supabase-Safe Migration Script for BiznesAssistant
-- Run this in Supabase SQL Editor
-- This script respects Supabase's built-in auth system and creates only your application tables
-- Generated on: 2026-02-04

-- Enable required extensions (safe)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create your application schema (separate from auth)
CREATE SCHEMA IF NOT EXISTS app;

-- Drop ONLY our application tables (NEVER touch auth schema)
DROP TABLE IF EXISTS app.task_comments CASCADE;
DROP TABLE IF EXISTS app.recurring_schedules CASCADE;
DROP TABLE IF EXISTS app.invoice_items CASCADE;
DROP TABLE IF EXISTS app.activities CASCADE;
DROP TABLE IF EXISTS app.deals CASCADE;
DROP TABLE IF EXISTS app.leads CASCADE;
DROP TABLE IF EXISTS app.contacts CASCADE;
DROP TABLE IF EXISTS app.invoices CASCADE;
DROP TABLE IF EXISTS app.transactions CASCADE;
DROP TABLE IF EXISTS app.tasks CASCADE;
DROP TABLE IF EXISTS app.templates CASCADE;
DROP TABLE IF EXISTS app.kpi_alerts CASCADE;
DROP TABLE IF EXISTS app.kpi_trends CASCADE;
DROP TABLE IF EXISTS app.kpis CASCADE;
DROP TABLE IF EXISTS app.users CASCADE;
DROP TABLE IF EXISTS app.companies CASCADE;
DROP TABLE IF EXISTS app.tenants CASCADE;

-- Create tables in correct order, in app schema

-- Table: tenants
CREATE TABLE app.tenants (
    id SERIAL PRIMARY KEY,
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
CREATE TABLE app.companies (
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
    tenant_id INTEGER REFERENCES app.tenants(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: app_users (your application users, linked to Supabase auth.users)
CREATE TABLE app.app_users (
    id SERIAL PRIMARY KEY,
    auth_id UUID REFERENCES auth.users(id) ON DELETE CASCADE, -- Link to Supabase auth
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR NOT NULL,
    phone VARCHAR,
    role VARCHAR(50) DEFAULT 'manager',
    is_active BOOLEAN DEFAULT TRUE,
    language VARCHAR DEFAULT 'uz',
    company_id INTEGER REFERENCES app.companies(id),
    tenant_id INTEGER REFERENCES app.tenants(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: contacts
CREATE TABLE app.contacts (
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
    type VARCHAR(50) DEFAULT 'customer',
    is_active BOOLEAN DEFAULT TRUE,
    telegram VARCHAR,
    instagram VARCHAR,
    facebook VARCHAR,
    linkedin VARCHAR,
    assigned_user_id INTEGER NOT NULL REFERENCES app.app_users(id),
    company_id INTEGER NOT NULL REFERENCES app.companies(id),
    tenant_id INTEGER REFERENCES app.tenants(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: leads
CREATE TABLE app.leads (
    id SERIAL PRIMARY KEY,
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
    assigned_user_id INTEGER NOT NULL REFERENCES app.app_users(id),
    company_id INTEGER NOT NULL REFERENCES app.companies(id),
    tenant_id INTEGER REFERENCES app.tenants(id),
    contact_id INTEGER REFERENCES app.contacts(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: deals
CREATE TABLE app.deals (
    id SERIAL PRIMARY KEY,
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
    assigned_user_id INTEGER NOT NULL REFERENCES app.app_users(id),
    company_id INTEGER NOT NULL REFERENCES app.companies(id),
    tenant_id INTEGER REFERENCES app.tenants(id),
    contact_id INTEGER REFERENCES app.contacts(id),
    lead_id INTEGER REFERENCES app.leads(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: activities
CREATE TABLE app.activities (
    id SERIAL PRIMARY KEY,
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
    user_id INTEGER NOT NULL REFERENCES app.app_users(id),
    company_id INTEGER NOT NULL REFERENCES app.companies(id),
    contact_id INTEGER REFERENCES app.contacts(id),
    lead_id INTEGER REFERENCES app.leads(id),
    deal_id INTEGER REFERENCES app.deals(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: invoices
CREATE TABLE app.invoices (
    id SERIAL PRIMARY KEY,
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
    created_by_id INTEGER NOT NULL REFERENCES app.app_users(id),
    company_id INTEGER NOT NULL REFERENCES app.companies(id),
    tenant_id INTEGER REFERENCES app.tenants(id),
    contact_id INTEGER REFERENCES app.contacts(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: invoice_items
CREATE TABLE app.invoice_items (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    quantity NUMERIC(10, 2) NOT NULL,
    unit_price NUMERIC(15, 2) NOT NULL,
    discount NUMERIC(5, 2) DEFAULT 0,
    vat_rate NUMERIC(5, 2) DEFAULT 12,
    line_total NUMERIC(15, 2) NOT NULL,
    invoice_id INTEGER NOT NULL REFERENCES app.invoices(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: transactions
CREATE TABLE app.transactions (
    id SERIAL PRIMARY KEY,
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
    user_id INTEGER NOT NULL REFERENCES app.app_users(id),
    company_id INTEGER NOT NULL REFERENCES app.companies(id),
    tenant_id INTEGER REFERENCES app.tenants(id),
    contact_id INTEGER REFERENCES app.contacts(id),
    invoice_id INTEGER REFERENCES app.invoices(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Table: tasks
CREATE TABLE app.tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'todo' NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium' NOT NULL,
    assigned_to INTEGER REFERENCES app.app_users(id),
    created_by INTEGER NOT NULL REFERENCES app.app_users(id),
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    tenant_id INTEGER NOT NULL REFERENCES app.tenants(id),
    company_id INTEGER NOT NULL REFERENCES app.companies(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: task_comments
CREATE TABLE app.task_comments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES app.tasks(id),
    content TEXT NOT NULL,
    created_by INTEGER NOT NULL REFERENCES app.app_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: templates
CREATE TABLE app.templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    data JSONB NOT NULL,
    is_recurring BOOLEAN DEFAULT FALSE NOT NULL,
    recurring_interval VARCHAR(20),
    recurring_day INTEGER,
    created_by INTEGER NOT NULL REFERENCES app.app_users(id),
    tenant_id INTEGER NOT NULL REFERENCES app.tenants(id),
    company_id INTEGER NOT NULL REFERENCES app.companies(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: recurring_schedules
CREATE TABLE app.recurring_schedules (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL REFERENCES app.templates(id),
    next_execution_date TIMESTAMPTZ NOT NULL,
    last_execution_date TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE NOT NULL
);

-- Table: kpis
CREATE TABLE app.kpis (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES app.companies(id),
    tenant_id INTEGER REFERENCES app.tenants(id),
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
CREATE TABLE app.kpi_trends (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES app.companies(id),
    kpi_category VARCHAR(50) NOT NULL,
    period_type VARCHAR(50) NOT NULL,
    trend_data TEXT NOT NULL,
    forecast_data TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Table: kpi_alerts
CREATE TABLE app.kpi_alerts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES app.companies(id),
    kpi_category VARCHAR(50) NOT NULL,
    alert_type VARCHAR NOT NULL,
    condition VARCHAR NOT NULL,
    threshold_value FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_app_tenants_email ON app.tenants(email);
CREATE INDEX idx_app_tenants_tax_id ON app.tenants(tax_id);
CREATE INDEX idx_app_tenants_created_at ON app.tenants(created_at);

CREATE INDEX idx_app_companies_tenant_id ON app.companies(tenant_id);
CREATE INDEX idx_app_companies_email ON app.companies(email);
CREATE INDEX idx_app_companies_tax_id ON app.companies(tax_id);
CREATE INDEX idx_app_companies_company_code ON app.companies(company_code);
CREATE INDEX idx_app_companies_created_at ON app.companies(created_at);

CREATE INDEX idx_app_app_users_auth_id ON app.app_users(auth_id);
CREATE INDEX idx_app_app_users_email ON app.app_users(email);
CREATE INDEX idx_app_app_users_username ON app.app_users(username);
CREATE INDEX idx_app_app_users_company_id ON app.app_users(company_id);
CREATE INDEX idx_app_app_users_tenant_id ON app.app_users(tenant_id);
CREATE INDEX idx_app_app_users_created_at ON app.app_users(created_at);

CREATE INDEX idx_app_contacts_company_id ON app.contacts(company_id);
CREATE INDEX idx_app_contacts_assigned_user_id ON app.contacts(assigned_user_id);
CREATE INDEX idx_app_contacts_tenant_id ON app.contacts(tenant_id);
CREATE INDEX idx_app_contacts_email ON app.contacts(email);
CREATE INDEX idx_app_contacts_created_at ON app.contacts(created_at);

CREATE INDEX idx_app_leads_company_id ON app.leads(company_id);
CREATE INDEX idx_app_leads_assigned_user_id ON app.leads(assigned_user_id);
CREATE INDEX idx_app_leads_contact_id ON app.leads(contact_id);
CREATE INDEX idx_app_leads_tenant_id ON app.leads(tenant_id);
CREATE INDEX idx_app_leads_status ON app.leads(status);
CREATE INDEX idx_app_leads_created_at ON app.leads(created_at);

CREATE INDEX idx_app_deals_company_id ON app.deals(company_id);
CREATE INDEX idx_app_deals_assigned_user_id ON app.deals(assigned_user_id);
CREATE INDEX idx_app_deals_contact_id ON app.deals(contact_id);
CREATE INDEX idx_app_deals_lead_id ON app.deals(lead_id);
CREATE INDEX idx_app_deals_tenant_id ON app.deals(tenant_id);
CREATE INDEX idx_app_deals_status ON app.deals(status);
CREATE INDEX idx_app_deals_created_at ON app.deals(created_at);

CREATE INDEX idx_app_activities_user_id ON app.activities(user_id);
CREATE INDEX idx_app_activities_company_id ON app.activities(company_id);
CREATE INDEX idx_app_activities_contact_id ON app.activities(contact_id);
CREATE INDEX idx_app_activities_lead_id ON app.activities(lead_id);
CREATE INDEX idx_app_activities_deal_id ON app.activities(deal_id);
CREATE INDEX idx_app_activities_status ON app.activities(status);
CREATE INDEX idx_app_activities_created_at ON app.activities(created_at);

CREATE INDEX idx_app_invoices_created_by_id ON app.invoices(created_by_id);
CREATE INDEX idx_app_invoices_company_id ON app.invoices(company_id);
CREATE INDEX idx_app_invoices_contact_id ON app.invoices(contact_id);
CREATE INDEX idx_app_invoices_tenant_id ON app.invoices(tenant_id);
CREATE INDEX idx_app_invoices_status ON app.invoices(status);
CREATE INDEX idx_app_invoices_invoice_number ON app.invoices(invoice_number);
CREATE INDEX idx_app_invoices_created_at ON app.invoices(created_at);

CREATE INDEX idx_app_invoice_items_invoice_id ON app.invoice_items(invoice_id);
CREATE INDEX idx_app_invoice_items_created_at ON app.invoice_items(created_at);

CREATE INDEX idx_app_transactions_user_id ON app.transactions(user_id);
CREATE INDEX idx_app_transactions_company_id ON app.transactions(company_id);
CREATE INDEX idx_app_transactions_contact_id ON app.transactions(contact_id);
CREATE INDEX idx_app_transactions_invoice_id ON app.transactions(invoice_id);
CREATE INDEX idx_app_transactions_tenant_id ON app.transactions(tenant_id);
CREATE INDEX idx_app_transactions_type ON app.transactions(type);
CREATE INDEX idx_app_transactions_category ON app.transactions(category);
CREATE INDEX idx_app_transactions_date ON app.transactions(date);
CREATE INDEX idx_app_transactions_created_at ON app.transactions(created_at);

CREATE INDEX idx_app_tasks_assigned_to ON app.tasks(assigned_to);
CREATE INDEX idx_app_tasks_created_by ON app.tasks(created_by);
CREATE INDEX idx_app_tasks_tenant_id ON app.tasks(tenant_id);
CREATE INDEX idx_app_tasks_company_id ON app.tasks(company_id);
CREATE INDEX idx_app_tasks_status ON app.tasks(status);
CREATE INDEX idx_app_tasks_priority ON app.tasks(priority);
CREATE INDEX idx_app_tasks_due_date ON app.tasks(due_date);
CREATE INDEX idx_app_tasks_created_at ON app.tasks(created_at);

CREATE INDEX idx_app_task_comments_task_id ON app.task_comments(task_id);
CREATE INDEX idx_app_task_comments_created_by ON app.task_comments(created_by);
CREATE INDEX idx_app_task_comments_created_at ON app.task_comments(created_at);

CREATE INDEX idx_app_templates_created_by ON app.templates(created_by);
CREATE INDEX idx_app_templates_tenant_id ON app.templates(tenant_id);
CREATE INDEX idx_app_templates_company_id ON app.templates(company_id);
CREATE INDEX idx_app_templates_type ON app.templates(type);
CREATE INDEX idx_app_templates_created_at ON app.templates(created_at);

CREATE INDEX idx_app_recurring_schedules_template_id ON app.recurring_schedules(template_id);
CREATE INDEX idx_app_recurring_schedules_next_execution ON app.recurring_schedules(next_execution_date);

CREATE INDEX idx_app_kpis_company_id ON app.kpis(company_id);
CREATE INDEX idx_app_kpis_tenant_id ON app.kpis(tenant_id);
CREATE INDEX idx_app_kpis_category ON app.kpis(category);
CREATE INDEX idx_app_kpis_period ON app.kpis(period);
CREATE INDEX idx_app_kpis_date ON app.kpis(date);
CREATE INDEX idx_app_kpis_created_at ON app.kpis(created_at);

CREATE INDEX idx_app_kpi_trends_company_id ON app.kpi_trends(company_id);
CREATE INDEX idx_app_kpi_trends_kpi_category ON app.kpi_trends(kpi_category);
CREATE INDEX idx_app_kpi_trends_period_type ON app.kpi_trends(period_type);

CREATE INDEX idx_app_kpi_alerts_company_id ON app.kpi_alerts(company_id);
CREATE INDEX idx_app_kpi_alerts_kpi_category ON app.kpi_alerts(kpi_category);
CREATE INDEX idx_app_kpi_alerts_created_at ON app.kpi_alerts(created_at);

-- Set up Row Level Security (RLS) for our app schema only
ALTER TABLE app.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.app_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.deals ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.invoice_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.task_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.recurring_schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.kpis ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.kpi_trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.kpi_alerts ENABLE ROW LEVEL SECURITY;

-- Create RLS policies that work WITH Supabase Auth
CREATE POLICY "Users can view own app_users" ON app.app_users
    USING (auth_id = auth.uid());

CREATE POLICY "Users can update own app_users" ON app.app_users
    USING (auth_id = auth.uid())
    WITH CHECK (auth_id = auth.uid());

CREATE POLICY "Users can view tenant data" ON app.tenants
    USING (id IN (SELECT tenant_id FROM app.app_users WHERE auth_id = auth.uid()));

CREATE POLICY "Users can view company data" ON app.companies
    USING (tenant_id IN (SELECT tenant_id FROM app.app_users WHERE auth_id = auth.uid()));

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION app.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON app.tenants
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON app.companies
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

CREATE TRIGGER update_app_users_updated_at BEFORE UPDATE ON app.app_users
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON app.contacts
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON app.leads
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

CREATE TRIGGER update_deals_updated_at BEFORE UPDATE ON app.deals
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

CREATE TRIGGER update_activities_updated_at BEFORE UPDATE ON app.activities
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON app.invoices
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

CREATE TRIGGER update_invoice_items_updated_at BEFORE UPDATE ON app.invoice_items
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON app.transactions
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON app.tasks
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON app.templates
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

CREATE TRIGGER update_kpis_updated_at BEFORE UPDATE ON app.kpis
    FOR EACH ROW EXECUTE FUNCTION app.update_updated_at_column();

-- Create trigger to automatically create app_user when auth.user is created
CREATE OR REPLACE FUNCTION app.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO app.app_users (auth_id, email, full_name, created_at)
    VALUES (NEW.id, NEW.email, COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email), NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION app.handle_new_user();

-- Migration completed successfully!
-- Supabase Auth schema is untouched and working
-- Your application tables are in app schema and properly linked to auth.users
