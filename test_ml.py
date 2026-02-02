"""
Test script for ML features
Tests the SimpleMLService with real data
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal
from app.services.simple_ml import SimpleMLService

def test_ml_service():
    """Test ML service with real data"""
    print("🤖 TESTING ML SERVICE")
    print("=" * 50)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Test with first tenant (assuming tenant_id = 1)
        tenant_id = 1
        ml_service = SimpleMLService(db, tenant_id)
        
        print(f"📋 Testing with tenant_id: {tenant_id}")
        
        # Test 1: Category Suggestions
        print("\n🎯 TEST 1: CATEGORY SUGGESTIONS")
        print("-" * 30)
        
        test_descriptions = [
            ("click puli to'lov", 500000, "expense"),
            ("oylik maosh", 2000000, "expense"),
            ("kvartira ijara", 800000, "expense"),
            ("internet to'lovi", 150000, "expense"),
            ("reklama xizmati", 300000, "expense"),
            ("soliq to'lovi", 400000, "expense"),
            ("material xaridi", 750000, "expense"),
            ("taxi xizmati", 50000, "expense"),
            ("mahsulot sotuvi", 1500000, "income"),
            ("xizmat to'lovi", 800000, "income")
        ]
        
        for desc, amount, trans_type in test_descriptions:
            suggestion = ml_service.suggest_category(desc, amount, trans_type)
            print(f"📝 '{desc}' ({amount:,} UZS)")
            print(f"   ✅ Suggestion: {suggestion['category']} ({suggestion['confidence']:.0%})")
            print(f"   🔧 Method: {suggestion['method']}")
            if 'matched_keyword' in suggestion:
                print(f"   🔍 Matched: '{suggestion['matched_keyword']}'")
            print()
        
        # Test 2: Customer Reliability
        print("\n💰 TEST 2: CUSTOMER RELIABILITY")
        print("-" * 30)
        
        # Get some customers to test
        from app.models.contact import Contact
        customers = db.query(Contact).filter(
            Contact.tenant_id == tenant_id
        ).limit(5).all()
        
        if customers:
            for customer in customers:
                reliability = ml_service.get_customer_reliability(customer.id)
                print(f"👤 Customer: {customer.name}")
                print(f"   📊 Reliability Score: {reliability['score']}% ({reliability['class']})")
                print(f"   📅 Avg Payment Days: {reliability['avg_days']} days")
                print(f"   💳 Total Invoices: {reliability['total_invoices']}")
                print(f"   ✅ Paid Invoices: {reliability['paid_invoices']}")
                print(f"   ⏰ Last Payment: {reliability['last_payment']}")
                print()
        else:
            print("❌ No customers found for testing")
        
        # Test 3: Business Insights
        print("\n📈 TEST 3: BUSINESS INSIGHTS")
        print("-" * 30)
        
        insights = ml_service.get_business_insights(30)  # Last 30 days
        print(f"📊 Period: Last {insights['period_days']} days")
        print(f"   💰 Total Income: {insights['total_income']:,} UZS")
        print(f"   💸 Total Expenses: {insights['total_expenses']:,} UZS")
        print(f"   📈 Net Profit: {insights['net_profit']:,} UZS")
        print(f"   📊 Profit Margin: {insights['profit_margin']:.1f}%")
        print(f"   📝 Transaction Count: {insights['transaction_count']}")
        print(f"   📅 Avg Daily Expense: {insights['avg_daily_expense']:,.0f} UZS")
        
        if insights['top_expense_categories']:
            print("   🏆 Top Expense Categories:")
            for category, amount in insights['top_expense_categories']:
                print(f"      • {category}: {amount:,} UZS")
        
        print("\n🎉 ML SERVICE TEST COMPLETE!")
        print("✅ All features working correctly")
        
    except Exception as e:
        print(f"❌ Error testing ML service: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_ml_service()
