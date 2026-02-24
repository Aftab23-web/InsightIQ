"""
KPI Calculation and Business Health Score Module
"""
import pandas as pd
import numpy as np
from config import KPI_THRESHOLDS


def calculate_revenue_metrics(df):
    """
    Calculate revenue-related KPIs with null-safe operations
    """
    # Ensure no null values in calculations
    df = df.fillna(0)
    
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    total_cost = df['Cost'].sum()
    total_marketing = df['Marketing_Spend'].sum()
    
    # Null-safe division
    avg_profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    avg_order_value = df['Sales'].mean() if len(df) > 0 else 0
    
    return {
        'total_sales': float(total_sales),
        'total_profit': float(total_profit),
        'total_cost': float(total_cost),
        'total_marketing_spend': float(total_marketing),
        'avg_profit_margin': float(avg_profit_margin),
        'avg_order_value': float(avg_order_value)
    }


def calculate_growth_metrics(df):
    """
    Calculate growth-related KPIs
    """
    if 'Year' not in df.columns or df['Year'].nunique() < 2:
        return {
            'sales_growth': 0,
            'profit_growth': 0,
            'yoy_growth': 0
        }
    
    # Year-over-year growth
    yearly = df.groupby('Year').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    })
    
    if len(yearly) >= 2:
        current_year_sales = yearly['Sales'].iloc[-1]
        previous_year_sales = yearly['Sales'].iloc[-2]
        sales_growth = ((current_year_sales - previous_year_sales) / previous_year_sales * 100) if previous_year_sales > 0 else 0
        
        current_year_profit = yearly['Profit'].iloc[-1]
        previous_year_profit = yearly['Profit'].iloc[-2]
        profit_growth = ((current_year_profit - previous_year_profit) / previous_year_profit * 100) if previous_year_profit > 0 else 0
    else:
        sales_growth = 0
        profit_growth = 0
    
    # Calculate CAGR if multiple years
    if len(yearly) > 2:
        years = len(yearly) - 1
        cagr = ((yearly['Sales'].iloc[-1] / yearly['Sales'].iloc[0]) ** (1/years) - 1) * 100
    else:
        cagr = sales_growth
    
    return {
        'sales_growth': float(sales_growth),
        'profit_growth': float(profit_growth),
        'cagr': float(cagr),
        'yoy_growth': float(sales_growth)
    }


def calculate_efficiency_metrics(df):
    """
    Calculate operational efficiency KPIs
    """
    total_sales = df['Sales'].sum()
    total_cost = df['Cost'].sum()
    total_marketing = df['Marketing_Spend'].sum()
    total_profit = df['Profit'].sum()
    
    # Cost efficiency (lower is better)
    cost_efficiency = (total_cost / total_sales) if total_sales > 0 else 1
    
    # Marketing ROI (raw percentage)
    marketing_roi = ((total_sales - total_marketing) / total_marketing * 100) if total_marketing > 0 else 0
    
    # Marketing ROI Score (normalized to 0-100 for health dashboard)
    # Industry benchmarks: <100% = poor, 200-400% = good, >500% = excellent
    if marketing_roi >= 500:
        marketing_roi_score = 100
    elif marketing_roi >= 400:
        marketing_roi_score = 90
    elif marketing_roi >= 300:
        marketing_roi_score = 80
    elif marketing_roi >= 200:
        marketing_roi_score = 70
    elif marketing_roi >= 100:
        marketing_roi_score = 60
    elif marketing_roi >= 50:
        marketing_roi_score = 40
    elif marketing_roi >= 0:
        marketing_roi_score = 20
    else:
        marketing_roi_score = 0
    
    # Operating margin
    operating_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    
    # Revenue per marketing rupee
    revenue_per_marketing = (total_sales / total_marketing) if total_marketing > 0 else 0
    
    return {
        'cost_efficiency': float(1 - cost_efficiency),  # Convert to efficiency score
        'marketing_roi': float(marketing_roi),  # Raw percentage for display
        'marketing_roi_score': float(marketing_roi_score),  # Normalized score 0-100
        'marketing_multiplier': float(revenue_per_marketing),  # How many x return
        'operating_margin': float(operating_margin),
        'revenue_per_marketing_rupee': float(revenue_per_marketing)
    }


def calculate_stability_metrics(df):
    """
    Calculate business stability metrics
    """
    # Sales volatility (coefficient of variation)
    sales_std = df['Sales'].std()
    sales_mean = df['Sales'].mean()
    sales_cv = (sales_std / sales_mean) if sales_mean > 0 else 0
    
    # Profit volatility
    profit_std = df['Profit'].std()
    profit_mean = df['Profit'].mean()
    profit_cv = (profit_std / profit_mean) if profit_mean > 0 and profit_mean != 0 else 0
    
    # Stability score (0-100, higher is more stable)
    # Lower CV means higher stability
    sales_stability = max(0, 100 - (sales_cv * 100))
    profit_stability = max(0, 100 - (abs(profit_cv) * 100))
    
    overall_stability = (sales_stability + profit_stability) / 2
    
    return {
        'sales_volatility': float(sales_cv),
        'profit_volatility': float(profit_cv),
        'sales_stability_score': float(sales_stability),
        'profit_stability_score': float(profit_stability),
        'overall_stability': float(overall_stability)
    }


def calculate_health_score(df):
    """
    Calculate overall business health score (0-100)
    """
    scores = {}
    weights = {}
    
    # Revenue Growth Score (0-100)
    growth_metrics = calculate_growth_metrics(df)
    sales_growth = growth_metrics['sales_growth']
    
    if sales_growth >= 20:
        growth_score = 100
    elif sales_growth >= 10:
        growth_score = 80
    elif sales_growth >= 5:
        growth_score = 60
    elif sales_growth >= 0:
        growth_score = 40
    else:
        growth_score = max(0, 40 + sales_growth)  # Penalize negative growth
    
    scores['growth'] = growth_score
    weights['growth'] = 0.25
    
    # Profitability Score (0-100)
    revenue_metrics = calculate_revenue_metrics(df)
    profit_margin = revenue_metrics['avg_profit_margin']
    
    if profit_margin >= 25:
        profitability_score = 100
    elif profit_margin >= 15:
        profitability_score = 80
    elif profit_margin >= 10:
        profitability_score = 60
    elif profit_margin >= 5:
        profitability_score = 40
    else:
        profitability_score = max(0, 20 + profit_margin * 2)
    
    scores['profitability'] = profitability_score
    weights['profitability'] = 0.30
    
    # Efficiency Score (0-100) - combining cost efficiency and marketing efficiency
    efficiency_metrics = calculate_efficiency_metrics(df)
    cost_efficiency = efficiency_metrics['cost_efficiency']
    marketing_roi_score = efficiency_metrics['marketing_roi_score']
    
    # Combine cost efficiency and marketing ROI
    if cost_efficiency >= 0.4:
        cost_score = 100
    elif cost_efficiency >= 0.3:
        cost_score = 80
    elif cost_efficiency >= 0.2:
        cost_score = 60
    elif cost_efficiency >= 0.1:
        cost_score = 40
    else:
        cost_score = 20
    
    # Weight cost efficiency (60%) and marketing efficiency (40%)
    efficiency_score = (cost_score * 0.6) + (marketing_roi_score * 0.4)
    
    scores['efficiency'] = efficiency_score
    weights['efficiency'] = 0.25
    
    # Stability Score (0-100)
    stability_metrics = calculate_stability_metrics(df)
    stability_score = stability_metrics['overall_stability']
    
    scores['stability'] = stability_score
    weights['stability'] = 0.20
    
    # Calculate weighted health score
    health_score = sum(scores[key] * weights[key] for key in scores)
    
    # Determine health status
    thresholds = KPI_THRESHOLDS['health_score']
    if health_score >= thresholds['healthy']:
        health_status = 'Healthy'
        status_icon = '🟢'
    elif health_score >= thresholds['warning']:
        health_status = 'Warning'
        status_icon = '🟡'
    else:
        health_status = 'Critical'
        status_icon = '🔴'
    
    return {
        'health_score': float(health_score),
        'health_status': health_status,
        'status_icon': status_icon,
        'component_scores': {
            'growth': float(growth_score),
            'profitability': float(profitability_score),
            'efficiency': float(efficiency_score),
            'stability': float(stability_score)
        },
        'weights': weights
    }


def calculate_all_kpis(df):
    """
    Calculate all KPIs and generate comprehensive report
    """
    kpis = {
        'revenue': calculate_revenue_metrics(df),
        'growth': calculate_growth_metrics(df),
        'efficiency': calculate_efficiency_metrics(df),
        'stability': calculate_stability_metrics(df),
        'health': calculate_health_score(df)
    }
    
    # Generate summary insights
    insights = []
    
    # Revenue insights
    if kpis['revenue']['avg_profit_margin'] < 10:
        insights.append({
            'category': 'Revenue',
            'severity': 'High',
            'message': f"Profit margin of {kpis['revenue']['avg_profit_margin']:.1f}% is below healthy threshold (10%)"
        })
    
    # Growth insights
    if kpis['growth']['sales_growth'] < 0:
        insights.append({
            'category': 'Growth',
            'severity': 'Critical',
            'message': f"Sales declining by {abs(kpis['growth']['sales_growth']):.1f}% - immediate action required"
        })
    elif kpis['growth']['sales_growth'] > 20:
        insights.append({
            'category': 'Growth',
            'severity': 'Positive',
            'message': f"Strong sales growth of {kpis['growth']['sales_growth']:.1f}%"
        })
    
    # Efficiency insights
    if kpis['efficiency']['cost_efficiency'] < 0.2:
        insights.append({
            'category': 'Efficiency',
            'severity': 'High',
            'message': "Low cost efficiency - focus on cost optimization"
        })
    
    kpis['insights'] = insights
    
    return kpis


def get_kpi_trends(df):
    """
    Calculate KPI trends over time
    """
    if 'Year' not in df.columns:
        return {}
    
    yearly_kpis = []
    
    for year in sorted(df['Year'].unique()):
        year_data = df[df['Year'] == year]
        
        kpis = {
            'year': int(year),
            'total_sales': float(year_data['Sales'].sum()),
            'total_profit': float(year_data['Profit'].sum()),
            'avg_profit_margin': float(year_data['Profit'].sum() / year_data['Sales'].sum() * 100) if year_data['Sales'].sum() > 0 else 0,
            'total_cost': float(year_data['Cost'].sum())
        }
        
        yearly_kpis.append(kpis)
    
    return {
        'yearly_trends': yearly_kpis,
        'trend_direction': 'up' if len(yearly_kpis) >= 2 and yearly_kpis[-1]['total_sales'] > yearly_kpis[-2]['total_sales'] else 'down'
    }
