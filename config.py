"""
Configuration Management
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'business_analytics'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# Application Settings
APP_CONFIG = {
    'title': os.getenv('APP_TITLE', 'InsightIQ'),
    'layout': 'wide',
    'debug': os.getenv('DEBUG_MODE', 'False').lower() == 'true'
}

# ML Model Configuration
ML_CONFIG = {
    'forecast_periods': int(os.getenv('FORECAST_PERIODS', '12')),
    'confidence_level': float(os.getenv('CONFIDENCE_LEVEL', '0.95')),
    'min_data_points': int(os.getenv('MIN_DATA_POINTS', '30')),
    'test_size': 0.2,
    'random_state': 42
}

# Data Schema
REQUIRED_COLUMNS = ['Date', 'Product', 'Region', 'Sales', 'Cost', 'Profit', 'Marketing_Spend']

# KPI Thresholds
KPI_THRESHOLDS = {
    'health_score': {
        'healthy': 70,
        'warning': 50,
        'critical': 0
    },
    'profit_margin': {
        'good': 20,
        'average': 10,
        'poor': 0
    },
    'cost_efficiency': {
        'efficient': 0.7,
        'moderate': 0.5,
        'inefficient': 0
    }
}

# UI Colors
COLORS = {
    'primary': '#6366f1',
    'secondary': '#8b5cf6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#3b82f6',
    'dark': '#1f2937',
    'light': '#f3f4f6'
}
