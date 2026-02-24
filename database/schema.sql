-- SQL Schema for PostgreSQL Database Setup
-- Run this script to manually create the database and tables

-- Create Database (run separately as postgres user)
-- CREATE DATABASE business_analytics;

-- Connect to business_analytics database and create tables

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_id VARCHAR(100) NOT NULL,
    contact_number VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Raw Data Table
CREATE TABLE IF NOT EXISTS raw_data (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    product VARCHAR(255) NOT NULL,
    region VARCHAR(255) NOT NULL,
    sales FLOAT NOT NULL,
    cost FLOAT NOT NULL,
    profit FLOAT NOT NULL,
    marketing_spend FLOAT NOT NULL,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(50)
);

-- Cleaned Data Table
CREATE TABLE IF NOT EXISTS cleaned_data (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    product VARCHAR(255) NOT NULL,
    region VARCHAR(255) NOT NULL,
    sales FLOAT NOT NULL,
    cost FLOAT NOT NULL,
    profit FLOAT NOT NULL,
    marketing_spend FLOAT NOT NULL,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    profit_margin FLOAT,
    roi FLOAT,
    cost_ratio FLOAT,
    processed_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(50)
);

-- KPIs Table
CREATE TABLE IF NOT EXISTS kpis (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50),
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_sales FLOAT,
    total_profit FLOAT,
    total_cost FLOAT,
    avg_profit_margin FLOAT,
    sales_growth FLOAT,
    profit_growth FLOAT,
    cost_efficiency FLOAT,
    roi FLOAT,
    health_score FLOAT,
    health_status VARCHAR(50)
);

-- Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50),
    prediction_date DATE NOT NULL,
    predicted_sales FLOAT,
    predicted_profit FLOAT,
    sales_lower FLOAT,
    sales_upper FLOAT,
    profit_lower FLOAT,
    profit_upper FLOAT,
    model_type VARCHAR(50),
    confidence_level FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insights Table
CREATE TABLE IF NOT EXISTS insights (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50),
    insight_type VARCHAR(100),
    category VARCHAR(100),
    title VARCHAR(255),
    description TEXT,
    impact VARCHAR(50),
    severity VARCHAR(50),
    metric_name VARCHAR(100),
    metric_value FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations Table
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50),
    priority VARCHAR(50),
    category VARCHAR(100),
    title VARCHAR(255),
    description TEXT,
    action_items TEXT,
    estimated_impact VARCHAR(255),
    implementation_effort VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Anomalies Table
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50),
    detection_date DATE,
    anomaly_type VARCHAR(100),
    severity VARCHAR(50),
    description TEXT,
    affected_metric VARCHAR(100),
    expected_value FLOAT,
    actual_value FLOAT,
    deviation_percent FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes for Performance
CREATE INDEX idx_cleaned_data_batch ON cleaned_data(batch_id);
CREATE INDEX idx_cleaned_data_date ON cleaned_data(date);
CREATE INDEX idx_predictions_batch ON predictions(batch_id);
CREATE INDEX idx_insights_batch ON insights(batch_id);
CREATE INDEX idx_recommendations_batch ON recommendations(batch_id);
CREATE INDEX idx_anomalies_batch ON anomalies(batch_id);

-- Grant Permissions (adjust username as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_username;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_username;
