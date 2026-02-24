"""
Database Schema and Models using SQLAlchemy
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DB_CONFIG
import hashlib

Base = declarative_base()


class User(Base):
    """User authentication and profile"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)  # Company_Manager, Data Analytics, Vice President, CEO, Owner
    company_name = Column(String(255), nullable=False)
    company_id = Column(String(100), nullable=False)
    contact_number = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)


class RawData(Base):
    """Raw uploaded business data"""
    __tablename__ = 'raw_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    product = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False)
    sales = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    marketing_spend = Column(Float, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    batch_id = Column(String(50))


class CleanedData(Base):
    """Cleaned and processed data"""
    __tablename__ = 'cleaned_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    product = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False)
    sales = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    marketing_spend = Column(Float, nullable=False)
    
    # Engineered Features
    year = Column(Integer)
    month = Column(Integer)
    quarter = Column(Integer)
    profit_margin = Column(Float)
    roi = Column(Float)
    cost_ratio = Column(Float)
    
    processed_timestamp = Column(DateTime, default=datetime.utcnow)
    batch_id = Column(String(50))


class KPI(Base):
    """Key Performance Indicators"""
    __tablename__ = 'kpis'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(50))
    calculation_date = Column(DateTime, default=datetime.utcnow)
    
    # Revenue Metrics
    total_sales = Column(Float)
    total_profit = Column(Float)
    total_cost = Column(Float)
    avg_profit_margin = Column(Float)
    
    # Growth Metrics
    sales_growth = Column(Float)
    profit_growth = Column(Float)
    
    # Efficiency Metrics
    cost_efficiency = Column(Float)
    roi = Column(Float)
    
    # Health Score
    health_score = Column(Float)
    health_status = Column(String(50))  # Healthy, Warning, Critical


class Prediction(Base):
    """Forecasting predictions"""
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(50))
    prediction_date = Column(Date, nullable=False)
    
    # Predictions
    predicted_sales = Column(Float)
    predicted_profit = Column(Float)
    
    # Confidence Intervals
    sales_lower = Column(Float)
    sales_upper = Column(Float)
    profit_lower = Column(Float)
    profit_upper = Column(Float)
    
    # Metadata
    model_type = Column(String(50))
    confidence_level = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Insight(Base):
    """Business insights and findings"""
    __tablename__ = 'insights'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(50))
    insight_type = Column(String(100))  # Strength, Weakness, Opportunity, Threat, Risk
    category = Column(String(100))  # Product, Region, Cost, Marketing, etc.
    
    title = Column(String(255))
    description = Column(Text)
    impact = Column(String(50))  # High, Medium, Low
    severity = Column(String(50))  # Critical, Warning, Info
    
    # Supporting Data
    metric_name = Column(String(100))
    metric_value = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    """Actionable recommendations"""
    __tablename__ = 'recommendations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(50))
    
    priority = Column(String(50))  # High, Medium, Low
    category = Column(String(100))
    
    title = Column(String(255))
    description = Column(Text)
    action_items = Column(Text)
    
    estimated_impact = Column(String(255))
    implementation_effort = Column(String(50))  # Easy, Moderate, Complex
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Anomaly(Base):
    """Detected anomalies and risks"""
    __tablename__ = 'anomalies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(50))
    detection_date = Column(Date)
    
    anomaly_type = Column(String(100))  # Sales Drop, Cost Spike, Unusual Pattern
    severity = Column(String(50))
    
    description = Column(Text)
    affected_metric = Column(String(100))
    expected_value = Column(Float)
    actual_value = Column(Float)
    deviation_percent = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# Database Connection String
def get_connection_string():
    """Generate database connection string"""
    # Try PostgreSQL first, fall back to SQLite
    try:
        # Check if PostgreSQL is explicitly configured
        if os.getenv('USE_POSTGRES', 'false').lower() == 'true':
            return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    except:
        pass
    
    # Default to SQLite for faster startup
    return "sqlite:///business_analytics.db"


# Create engine and session
engine = None
SessionLocal = None


def init_db():
    """Initialize database connection and create tables"""
    global engine, SessionLocal
    
    try:
        connection_string = get_connection_string()
        engine = create_engine(connection_string, echo=False, connect_args={'check_same_thread': False} if 'sqlite' in connection_string else {})
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        return engine
    except Exception as e:
        print(f"Database initialization error: {e}")
        # Create in-memory SQLite as fallback
        engine = create_engine("sqlite:///:memory:", echo=False, connect_args={'check_same_thread': False})
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine


def get_session():
    """Get database session"""
    if SessionLocal is None:
        init_db()
    return SessionLocal()
