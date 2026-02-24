# 🎯 InsightIQ

A comprehensive, enterprise-grade AI-powered business analytics platform built with Python, Streamlit, and PostgreSQL. This platform transforms raw business data into actionable insights with automated analysis, forecasting, and strategic recommendations.

## ✨ Features

### 📊 Core Analytics
- **Exploratory Data Analysis (EDA)**: Year-wise, month-wise, product-wise, and regional performance analysis
- **Business Mistake Detection**: Automatically identify loss-making products, underperforming regions, and inefficiencies
- **Root Cause Analysis**: AI-powered WHY engine using correlation analysis, feature importance, and SHAP explanations
- **SWOT Analysis**: Data-driven strengths, weaknesses, opportunities, and threats identification

### 🎯 Intelligence & Insights
- **Business Health Score**: 0-100 score based on growth, profitability, efficiency, and stability
- **KPI Dashboard**: Track revenue, growth, efficiency, and stability metrics
- **Anomaly Detection**: Identify sudden drops, cost spikes, and unusual patterns
- **Risk Assessment**: Evaluate business risks and forecast uncertainties

### 🔮 Predictive Analytics
- **Sales & Profit Forecasting**: 6-12 month predictions using Prophet and ARIMA
- **Confidence Intervals**: Prediction ranges with 95% confidence
- **What-If Analysis**: Simulate marketing changes, cost reductions, price adjustments, and product removals
- **Scenario Comparison**: Ranked scenarios by profit impact

### 💡 Recommendation Engine
- **Prioritized Recommendations**: Critical, High, Medium, and Low priority actions
- **Impact Estimation**: Quantified business impact for each recommendation
- **Implementation Guidance**: Action items and effort estimates
- **Multi-Category**: Cost optimization, product strategy, regional strategy, marketing, and growth

### 🎨 Modern UI/UX
- **SaaS-Style Interface**: Premium, animated dashboard with gradient backgrounds
- **Interactive Charts**: Plotly-powered visualizations with hover interactions
- **Lottie Animations**: Loading states and success indicators
- **Card-Based Layout**: Clean, organized information presentation
- **Responsive Design**: Optimized for all screen sizes

## 🛠️ Tech Stack

### Backend
- **Python 3.9+**: Core programming language
- **PostgreSQL**: Database for persistent storage
- **SQLAlchemy**: ORM for database operations
- **Pandas & NumPy**: Data processing and manipulation

### Machine Learning
- **Scikit-learn**: Feature importance, Isolation Forest
- **Prophet**: Time series forecasting
- **ARIMA**: Alternative forecasting method
- **SciPy**: Statistical analysis

### Frontend
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **streamlit-option-menu**: Enhanced navigation
- **streamlit-lottie**: Animations

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### Step 1: Clone or Download

```bash
cd f:/PROJECT'S/MY_PR
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup PostgreSQL Database

1. Install PostgreSQL from [https://www.postgresql.org/download/](https://www.postgresql.org/download/)

2. Create a database:

```sql
CREATE DATABASE business_analytics;
```

3. (Optional) Create a user:

```sql
CREATE USER analytics_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE business_analytics TO analytics_user;
```

### Step 5: Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac
```

Edit `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=business_analytics
DB_USER=your_username
DB_PASSWORD=your_password
```

### Step 6: Initialize Database

The application will automatically create tables on first run, or you can run manually:

```bash
python -c "from database import init_db; init_db()"
```

Alternatively, run the SQL schema manually:

```bash
psql -U your_username -d business_analytics -f database/schema.sql
```

## 🚀 Running the Application

### Start the Streamlit App

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Alternative: Specify Port

```bash
streamlit run app.py --server.port 8080
```

## 📁 Project Structure

```
MY_PR/
├── app.py                          # Main application entry point
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
│
├── database/                       # Database layer
│   ├── __init__.py
│   ├── models.py                   # SQLAlchemy models
│   ├── db_utils.py                 # Database utilities
│   └── schema.sql                  # PostgreSQL schema
│
├── utils/                          # Utility modules
│   ├── __init__.py
│   └── data_processor.py           # Data cleaning & validation
│
├── analytics/                      # Analytics engines
│   ├── __init__.py
│   ├── eda.py                      # Exploratory analysis
│   ├── mistake_detection.py       # Business mistake detection
│   ├── root_cause.py               # Root cause analysis
│   ├── swot_analysis.py            # SWOT analysis
│   ├── kpi_calculator.py           # KPI calculation
│   └── recommendation_engine.py    # Recommendation system
│
├── ml_models/                      # Machine learning models
│   ├── __init__.py
│   ├── forecasting.py              # Time series forecasting
│   ├── anomaly_detection.py        # Anomaly detection
│   └── scenario_analysis.py        # What-if scenarios
│
├── ui/                             # UI components
│   ├── __init__.py
│   ├── styles.py                   # Custom CSS
│   └── components.py               # Reusable UI components
│
└── pages/                          # Application pages
    ├── __init__.py
    ├── home_page.py
    ├── data_upload_page.py
    ├── executive_dashboard_page.py
    ├── analytics_page.py
    ├── insights_page.py
    ├── forecasting_page.py
    ├── recommendations_page.py
    └── reports_page.py
```

## 📊 Data Format

Your CSV file must contain these columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| Date | Date | Transaction date | 2024-01-01 |
| Product | String | Product name | Widget A |
| Region | String | Geographic region | North |
| Sales | Float | Sales amount | 10000.00 |
| Cost | Float | Cost amount | 6000.00 |
| Profit | Float | Profit amount | 4000.00 |
| Marketing_Spend | Float | Marketing expenditure | 500.00 |

### Sample Data 

```csv
Date,Product,Region,Sales,Cost,Profit,Marketing_Spend
2024-01-01,Widget A,North,10000,6000,4000,500
2024-01-02,Widget B,South,15000,9000,6000,750
2024-01-03,Widget A,East,12000,7000,5000,600
```

## 🎯 Usage Guide

### 1. Upload Data
- Navigate to "Data Upload" page
- Upload your CSV file
- System validates and processes data automatically
- Data is saved to PostgreSQL database

### 2. View Dashboard
- Go to "Executive Dashboard"
- See business health score (0-100)
- Review key financial metrics
- Check recent alerts and anomalies

### 3. Analyze Performance
- Visit "Analytics" page
- Explore EDA insights
- Review detected mistakes
- Understand root causes

### 4. Review Insights
- Go to "Insights & SWOT"
- See strengths and weaknesses
- Identify opportunities and threats

### 5. Forecast Future
- Navigate to "Forecasting"
- Generate 12-month predictions
- Run what-if scenarios
- Compare different strategies

### 6. Get Recommendations
- Visit "Recommendations" page
- Review prioritized action items
- See estimated impact
- Plan implementation

## 🔧 Configuration

### Database Settings

Edit `config.py` or `.env`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'business_analytics',
    'user': 'postgres',
    'password': 'your_password'
}
```

### ML Model Settings

```python
ML_CONFIG = {
    'forecast_periods': 12,          # Months to forecast
    'confidence_level': 0.95,        # Confidence interval
    'min_data_points': 30,           # Minimum data required
    'test_size': 0.2,                # Train/test split
    'random_state': 42               # Reproducibility
}
```

### KPI Thresholds

```python
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
    }
}
```

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
# Windows:
net start postgresql-x64-14

# Linux:
sudo systemctl status postgresql
```

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Port Already in Use

```bash
# Use different port
streamlit run app.py --server.port 8502
```

## 📈 Performance Optimization

### For Large Datasets

1. **Batch Processing**: Modify `database/db_utils.py` to use bulk inserts
2. **Indexing**: Add indexes on frequently queried columns
3. **Caching**: Use Streamlit's `@st.cache_data` decorator

### Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_date ON cleaned_data(date);
CREATE INDEX idx_product_region ON cleaned_data(product, region);

-- Vacuum database
VACUUM ANALYZE;
```

## 🚀 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Add secrets in dashboard

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

Build and run:

```bash
docker build -t business-intelligence .
docker run -p 8501:8501 business-intelligence
```

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Support

For issues, questions, or contributions, please refer to the project documentation or create an issue in the repository.

## 🎉 Features Roadmap

- [ ] PDF Report Generation
- [ ] Email Alerts for Critical Issues
- [ ] Multi-user Authentication
- [ ] Custom Dashboard Builder
- [ ] Integration with External Data Sources
- [ ] Mobile App
- [ ] Advanced ML Models (XGBoost, Neural Networks)
- [ ] Real-time Data Streaming

---

**Built with ❤️ using Python, Streamlit, and PostgreSQL**
