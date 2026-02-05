from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class KPICategory(enum.Enum):
    REVENUE = "revenue"
    EXPENSES = "expenses"
    PROFIT = "profit"
    CUSTOMERS = "customers"
    INVOICES = "invoices"
    LEADS = "leads"
    DEALS = "deals"

class KPIPeriod(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class KPI(Base):
    __tablename__ = "kpis"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)  # Multi-tenant support
    category = Column(Enum(KPICategory), nullable=False)
    period = Column(Enum(KPIPeriod), nullable=False)
    value = Column(Float, nullable=False)
    previous_value = Column(Float, nullable=True)  # For comparison
    target_value = Column(Float, nullable=True)   # Goal value
    date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="kpis")
    tenant = relationship("Tenant", back_populates="kpis")

class KPITrend(Base):
    __tablename__ = "kpi_trends"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    kpi_category = Column(Enum(KPICategory), nullable=False)
    period_type = Column(Enum(KPIPeriod), nullable=False)
    trend_data = Column(Text, nullable=False)  # JSON data for trend points
    forecast_data = Column(Text, nullable=True)  # JSON data for forecast
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="kpi_trends")

class KPIAlert(Base):
    __tablename__ = "kpi_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    kpi_category = Column(Enum(KPICategory), nullable=False)
    alert_type = Column(String, nullable=False)  # "threshold", "trend", "anomaly"
    condition = Column(String, nullable=False)  # "above", "below", "decreasing", "increasing"
    threshold_value = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="kpi_alerts")
