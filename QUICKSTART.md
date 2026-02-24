# 🚀 Quick Start Guide

## Installation (5 Minutes)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup PostgreSQL

**Option A: Local PostgreSQL**

```bash
# Install PostgreSQL from https://www.postgresql.org/download/
# Create database
psql -U postgres
CREATE DATABASE business_analytics;
\q
```

**Option B: Use SQLite (No PostgreSQL needed)**

Modify `database/models.py`:

```python
# Change this line:
engine = create_engine(connection_string, echo=False)

# To this:
engine = create_engine('sqlite:///business_analytics.db', echo=False)
```

### 3. Configure Environment

```bash
# Copy environment template
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env with your database credentials
```

### 4. Run the Application

```bash
streamlit run app.py
```

Open browser to `http://localhost:8501`

## First Time Usage

### Step 1: Upload Data

1. Click "Data Upload" in sidebar
2. Upload your CSV file with required columns:
   - Date, Product, Region, Sales, Cost, Profit, Marketing_Spend
3. Click "Save & Continue to Analysis"

### Step 2: View Dashboard

1. Go to "Executive Dashboard"
2. See your business health score
3. Review key metrics and charts

### Step 3: Explore Insights

1. Visit "Analytics" for detailed analysis
2. Check "Insights & SWOT" for strategic insights
3. Go to "Forecasting" for predictions
4. Review "Recommendations" for action items

## Sample Data

Create `sample_data.csv`:

```csv
Date,Product,Region,Sales,Cost,Profit,Marketing_Spend
2024-01-01,Laptop,North,50000,30000,20000,2000
2024-01-02,Phone,South,40000,25000,15000,1500
2024-01-03,Tablet,East,30000,18000,12000,1000
2024-01-04,Laptop,West,55000,32000,23000,2200
2024-01-05,Phone,North,45000,28000,17000,1800
2024-01-06,Tablet,South,35000,20000,15000,1200
2024-01-07,Laptop,East,60000,35000,25000,2500
2024-01-08,Phone,West,50000,30000,20000,2000
2024-01-09,Tablet,North,40000,22000,18000,1500
2024-01-10,Laptop,South,65000,38000,27000,2800
```

## Common Issues

### "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### "Database connection failed"
- Check PostgreSQL is running
- Verify credentials in `.env`
- Or use SQLite option (see step 2)

### "Port already in use"
```bash
streamlit run app.py --server.port 8502
```

## Need Help?

Check the full README.md for detailed documentation!
