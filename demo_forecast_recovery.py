"""
Quick Demo Script - Loss Forecasting & Recovery Feature
Run this to see the forecasting and recovery recommendations in action
"""
from database.models import init_db, get_session, CleanedData
from ml_models.forecasting import forecast_multiple_metrics, assess_forecast_risk
from analytics.recommendation_engine import generate_forecast_recovery_recommendations
import pandas as pd

print("=" * 80)
print(" LOSS FORECASTING & RECOVERY DEMONSTRATION")
print("=" * 80)
print()

# Initialize database
init_db()
session = get_session()

# Get data from database
print(" Loading your business data...")
data = session.query(CleanedData).all()

if not data:
    print(" No data found. Please upload data first through the web app.")
    session.close()
    exit()

# Convert to DataFrame
df = pd.DataFrame([{
    'Date': d.date,
    'Product': d.product,
    'Region': d.region,
    'Sales': d.sales,
    'Cost': d.cost,
    'Profit': d.profit,
    'Marketing_Spend': d.marketing_spend,
    'Profit_Margin': d.profit_margin
} for d in data])

print(f" Loaded {len(df)} records")
print()

# Generate forecast
print(" Generating 12-month forecast using AI...")
print()

forecasts = forecast_multiple_metrics(df, periods=12)

for metric, result in forecasts.items():
    if 'error' in result:
        print(f" {metric}: {result['error']}")
        continue
    
    print("=" * 80)
    print(f" {metric.upper()} FORECAST")
    print("=" * 80)
    print()
    
    forecast_df = pd.DataFrame(result['forecast'])
    
    # Show first 3 months
    print("First 3 Months Prediction:")
    print("-" * 80)
    for idx, row in forecast_df.head(3).iterrows():
        month = pd.to_datetime(row['date']).strftime('%B %Y')
        if metric == 'Sales':
            pred = row['predicted_sales']
            lower = row['sales_lower']
            upper = row['sales_upper']
        else:
            pred = row['predicted_profit']
            lower = row['profit_lower']
            upper = row['profit_upper']
        
        print(f"{month}:")
        print(f"  Expected: ₹{pred:,.0f}")
        print(f"  Range: ₹{lower:,.0f} - ₹{upper:,.0f}")
        print()
    
    # Risk assessment
    risk = assess_forecast_risk(forecast_df, metric)
    
    print("\n" + "=" * 80)
    print("  RISK ASSESSMENT")
    print("=" * 80)
    print(f"Risk Level: {risk['risk_level']}")
    print(f"Average Uncertainty: {risk['avg_uncertainty']:.1f}%")
    print(f"Trend Change: {risk['trend_change_pct']:+.1f}%")
    print()
    
    # Check if we have a declining forecast
    if risk['trend_change_pct'] < -5:
        print("\n" + "=" * 80)
        print(" LOSS DETECTED - GENERATING RECOVERY PLAN")
        print("=" * 80)
        print()
        
        # Generate recovery recommendations
        recovery_recs = generate_forecast_recovery_recommendations(df, forecast_df, metric, risk)
        
        for idx, rec in enumerate(recovery_recs, 1):
            if rec['priority'] == 'Critical':
                icon = '🚨'
            elif rec['priority'] == 'High':
                icon = '⚠️'
            else:
                icon = '📋'
            
            print(f"\n{icon} RECOMMENDATION #{idx}: {rec['priority'].upper()}")
            print("-" * 80)
            print(f"Title: {rec['title']}")
            print(f"\nDescription:")
            print(f"  {rec['description']}")
            print(f"\n Action Items:")
            for action in rec['action_items']:
                print(f"  • {action}")
            print(f"\n Estimated Impact:")
            print(f"  {rec['estimated_impact']}")
            print(f"\n Implementation Effort:")
            print(f"  {rec['implementation_effort']}")
            
            if 'timeline' in rec:
                print(f"\n⏱  Timeline:")
                print(f"  {rec['timeline']}")
            
            if 'success_metrics' in rec:
                print(f"\n Success Metrics:")
                for sm in rec['success_metrics']:
                    print(f"  • {sm}")
            
            print("\n" + "=" * 80)
    
    elif risk['trend_change_pct'] > 10:
        print("\n" + "=" * 80)
        print(" STRONG GROWTH PREDICTED!")
        print("=" * 80)
        print()
        print("Your forecast shows positive growth. Consider:")
        print("  • Scaling up production capacity")
        print("  • Investing in marketing to accelerate growth")
        print("  • Hiring ahead of demand")
        print("  • Securing supplier contracts")
        print()
    
    else:
        print("\n" + "=" * 80)
        print(" STABLE FORECAST")
        print("=" * 80)
        print()
        print("Your forecast shows stable performance.")
        print("Focus on maintaining current strategies while exploring optimization opportunities.")
        print()

session.close()

print("\n" + "=" * 80)
print(" NEXT STEPS:")
print("=" * 80)
print()
print("1. Review the recommendations above")
print("2. Prioritize Critical and High priority items")
print("3. Implement top 2-3 action items within 30 days")
print("4. Track progress in the web app's Forecasting page")
print("5. Upload new data monthly to monitor improvement")
print()
print(" Pro Tip: Start with quick wins (Easy implementation) for fast results!")
print()
print("=" * 80)
