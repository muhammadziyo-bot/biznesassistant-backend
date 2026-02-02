"""
Data seeding script for the BiznesAssistant application.
Run this script to populate the database with sample data for development/demo.
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.transaction import Transaction, TransactionType, TransactionCategory
from app.models.invoice import Invoice, InvoiceStatus
from app.models.contact import Contact
from app.models.lead import Lead, LeadStatus
from app.models.deal import Deal, DealStatus
from app.models.user import User, UserRole
from app.models.company import Company
from app.utils.auth import get_password_hash
from datetime import datetime, timedelta
import random

def create_test_user_and_company():
    """Create test user and company if they don't exist."""
    db = SessionLocal()
    try:
        # Create or get test company
        company = db.query(Company).filter(Company.name == "Demo Company").first()
        if not company:
            company = db.query(Company).filter(Company.tax_id == "123456789").first()
        
        if not company:
            company = Company(
                name="Demo Company",
                tax_id="123456789",
                address="Demo Address, Tashkent, Uzbekistan",
                phone="+998901234567",
                email="demo@company.com"
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            print("Created new Demo Company")
        else:
            print(f"Using existing company: {company.name}")
        
        # Create or get test admin user
        admin_user = db.query(User).filter(User.email == "admin@demo.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@demo.com",
                username="demo_admin",
                full_name="Demo Admin",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
                company_id=company.id
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("Created new admin user")
        else:
            print(f"Using existing admin user: {admin_user.email}")
        
        # Create or get test accountant user
        accountant_user = db.query(User).filter(User.email == "accountant@demo.com").first()
        if not accountant_user:
            accountant_user = User(
                email="accountant@demo.com",
                username="demo_accountant",
                full_name="Demo Accountant",
                hashed_password=get_password_hash("accountant123"),
                role=UserRole.ACCOUNTANT,
                is_active=True,
                is_verified=True,
                company_id=company.id
            )
            db.add(accountant_user)
            db.commit()
            db.refresh(accountant_user)
            print("Created new accountant user")
        else:
            print(f"Using existing accountant user: {accountant_user.email}")
        
        # Create or get test manager user
        manager_user = db.query(User).filter(User.email == "manager@demo.com").first()
        if not manager_user:
            manager_user = User(
                email="manager@demo.com",
                username="demo_manager",
                full_name="Demo Manager",
                hashed_password=get_password_hash("manager123"),
                role=UserRole.MANAGER,
                is_active=True,
                is_verified=True,
                company_id=company.id
            )
            db.add(manager_user)
            db.commit()
            db.refresh(manager_user)
            print("Created new manager user")
        else:
            print(f"Using existing manager user: {manager_user.email}")
        
        print("Test users and company ready")
        return company, [admin_user, accountant_user, manager_user]
        
    except Exception as e:
        print(f"Error creating test users: {e}")
        db.rollback()
        return None, []
    finally:
        db.close()

def create_sample_transactions(company_id: int, user_id: int):
    """Create sample transactions for the past 12 months."""
    db = SessionLocal()
    try:
        # Check if transactions already exist
        existing_count = db.query(Transaction).filter(Transaction.company_id == company_id).count()
        if existing_count > 100:  # If we already have data, skip
            print(f"Transactions already exist ({existing_count} records)")
            return
        
        print("Creating sample transactions...")
        
        for months_ago in range(12):
            for day in range(30):
                date = datetime.utcnow() - timedelta(days=months_ago*30 + day)
                
                # Create income transactions
                for _ in range(random.randint(1, 3)):
                    transaction = Transaction(
                        company_id=company_id,
                        user_id=user_id,
                        type=TransactionType.INCOME,
                        amount=random.uniform(1000, 8000),
                        description=f"Sales revenue {date.strftime('%Y-%m-%d')}",
                        date=date,
                        category=random.choice([TransactionCategory.SALES, TransactionCategory.SERVICES])
                    )
                    db.add(transaction)
                
                # Create expense transactions
                for _ in range(random.randint(1, 2)):
                    transaction = Transaction(
                        company_id=company_id,
                        user_id=user_id,
                        type=TransactionType.EXPENSE,
                        amount=random.uniform(500, 3000),
                        description=f"Operating expense {date.strftime('%Y-%m-%d')}",
                        date=date,
                        category=random.choice([
                            TransactionCategory.RENT, 
                            TransactionCategory.UTILITIES,
                            TransactionCategory.MARKETING,
                            TransactionCategory.SALARIES
                        ])
                    )
                    db.add(transaction)
        
        db.commit()
        print("Sample transactions created")
        
    except Exception as e:
        print(f"Error creating transactions: {e}")
        db.rollback()
    finally:
        db.close()

def create_sample_contacts(company_id: int, user_id: int):
    """Create sample contacts."""
    db = SessionLocal()
    try:
        existing_count = db.query(Contact).filter(Contact.company_id == company_id).count()
        if existing_count > 20:
            print(f"Contacts already exist ({existing_count} records)")
            return
        
        print("Creating sample contacts...")
        
        for i in range(50):
            contact = Contact(
                company_id=company_id,
                assigned_user_id=user_id,
                name=f"Contact {i+1}",
                email=f"contact{i+1}@example.com",
                phone=f"+99890{i:08d}",
                company_name=f"Company {i+1}",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
            )
            db.add(contact)
        
        db.commit()
        print("Sample contacts created")
        
    except Exception as e:
        print(f"Error creating contacts: {e}")
        db.rollback()
    finally:
        db.close()

def create_sample_leads(company_id: int, user_id: int):
    """Create sample leads."""
    db = SessionLocal()
    try:
        existing_count = db.query(Lead).filter(Lead.company_id == company_id).count()
        if existing_count > 10:
            print(f"Leads already exist ({existing_count} records)")
            return
        
        print("Creating sample leads...")
        
        for i in range(30):
            lead = Lead(
                company_id=company_id,
                assigned_user_id=user_id,
                title=f"Lead {i+1}",
                description=f"Business opportunity {i+1}",
                status=random.choice(list(LeadStatus)),
                estimated_value=random.uniform(1000, 15000),
                contact_name=f"Lead Contact {i+1}",
                contact_email=f"lead{i+1}@example.com",
                contact_phone=f"+99891{i:08d}",
                company_name=f"Lead Company {i+1}",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 180))
            )
            db.add(lead)
        
        db.commit()
        print("Sample leads created")
        
    except Exception as e:
        print(f"Error creating leads: {e}")
        db.rollback()
    finally:
        db.close()

def create_sample_deals(company_id: int, user_id: int):
    """Create sample deals."""
    db = SessionLocal()
    try:
        existing_count = db.query(Deal).filter(Deal.company_id == company_id).count()
        if existing_count > 10:
            print(f"Deals already exist ({existing_count} records)")
            return
        
        print("Creating sample deals...")
        
        for i in range(20):
            deal = Deal(
                company_id=company_id,
                assigned_user_id=user_id,
                title=f"Deal {i+1}",
                description=f"Business deal {i+1}",
                status=random.choice(list(DealStatus)),
                deal_value=random.uniform(5000, 50000),
                primary_contact=f"Deal Contact {i+1}",
                company_name=f"Deal Company {i+1}",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 120))
            )
            db.add(deal)
        
        db.commit()
        print("Sample deals created")
        
    except Exception as e:
        print(f"Error creating deals: {e}")
        db.rollback()
    finally:
        db.close()

def create_sample_invoices(company_id: int, user_id: int):
    """Create sample invoices."""
    db = SessionLocal()
    try:
        existing_count = db.query(Invoice).filter(Invoice.company_id == company_id).count()
        if existing_count > 10:
            print(f"Invoices already exist ({existing_count} records)")
            return
        
        print("Creating sample invoices...")
        
        for i in range(25):
            total_amount = random.uniform(2000, 15000)
            invoice = Invoice(
                company_id=company_id,
                created_by_id=user_id,
                invoice_number=f"INV-{2024}-{i+1:03d}",
                customer_name=f"Customer {i+1}",
                subtotal=total_amount,
                total_amount=total_amount,
                remaining_amount=total_amount * random.uniform(0, 1),
                status=random.choice(list(InvoiceStatus)),
                issue_date=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                due_date=datetime.utcnow() + timedelta(days=random.randint(15, 60))
            )
            db.add(invoice)
        
        db.commit()
        print("Sample invoices created")
        
    except Exception as e:
        print(f"Error creating invoices: {e}")
        db.rollback()
    finally:
        db.close()

def seed_all_data():
    """Seed all sample data."""
    print("Starting data seeding...")
    
    # Create test users and company
    company, users = create_test_user_and_company()
    if not company:
        print("Failed to create company/users. Aborting.")
        return
    
    admin_user = users[0]  # Use admin user for creating data
    company_id = company.id
    
    # Create sample data
    create_sample_transactions(company_id, admin_user.id)
    create_sample_contacts(company_id, admin_user.id)
    create_sample_leads(company_id, admin_user.id)
    create_sample_deals(company_id, admin_user.id)
    create_sample_invoices(company_id, admin_user.id)
    
    print("Data seeding completed!")
    print("\nLogin Credentials:")
    print("Admin: admin@demo.com / admin123")
    print("Accountant: accountant@demo.com / accountant123")
    print("Manager: manager@demo.com / manager123")

if __name__ == "__main__":
    seed_all_data()
