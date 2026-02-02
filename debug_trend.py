"""
Debug trend data generation
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.services.kpi_service import KPIService
from app.models.kpi import KPICategory, KPIPeriod

def debug_trend():
    """Debug trend data generation"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as db:
        # Test for tenant 2 (new tenant)
        kpi_service = KPIService(db, tenant_id=2)
        
        print("Testing trend data for tenant 2:")
        trend_data = kpi_service.generate_trend_data(3, KPICategory.REVENUE, KPIPeriod.MONTHLY, 12)
        print(f"Trend data points: {len(trend_data)}")
        for i, point in enumerate(trend_data):
            print(f"  {i+1}: {point}")
        
        print("\nTesting trend data for tenant 1 (demo):")
        kpi_service_demo = KPIService(db, tenant_id=1)
        trend_data_demo = kpi_service_demo.generate_trend_data(1, KPICategory.REVENUE, KPIPeriod.MONTHLY, 12)
        print(f"Trend data points: {len(trend_data_demo)}")
        for i, point in enumerate(trend_data_demo[:3]):  # Show first 3
            print(f"  {i+1}: {point}")

if __name__ == "__main__":
    debug_trend()
