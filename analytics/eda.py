"""
Exploratory Data Analysis Module
"""
import pandas as pd
import numpy as np
from collections import defaultdict


def analyze_temporal_trends(df):
    """
    Analyze year-wise, month-wise, and day-wise trends with null handling
    """
    results = {}
    
    # Ensure no null values in critical columns
    df = df.fillna(0)
    
    # Year-wise analysis
    yearly = df.groupby('Year').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Cost': 'sum',
        'Marketing_Spend': 'sum'
    }).reset_index()
    
    # Null-safe profit margin calculation
    yearly['Profit_Margin'] = yearly.apply(
        lambda row: (row['Profit'] / row['Sales'] * 100) if row['Sales'] > 0 else 0, 
        axis=1
    )
    yearly['YoY_Growth'] = yearly['Sales'].pct_change() * 100
    yearly['YoY_Growth'] = yearly['YoY_Growth'].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    results['yearly'] = yearly.to_dict('records')
    
    # Month-wise analysis
    df_copy = df.copy()
    df_copy['Year_Month'] = df_copy['Date'].dt.to_period('M').astype(str)
    df_copy['Month_Name'] = df_copy['Date'].dt.strftime('%B')
    
    monthly = df_copy.groupby(['Year', 'Month', 'Month_Name', 'Year_Month']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Cost': 'sum',
        'Marketing_Spend': 'sum'
    }).reset_index()
    
    # Null-safe calculations
    monthly['Profit_Margin'] = monthly.apply(
        lambda row: (row['Profit'] / row['Sales'] * 100) if row['Sales'] > 0 else 0,
        axis=1
    )
    monthly['MoM_Growth'] = monthly.groupby('Year')['Sales'].pct_change() * 100
    monthly['MoM_Growth'] = monthly['MoM_Growth'].replace([np.inf, -np.inf], np.nan).fillna(0)
    monthly = monthly.sort_values(['Year', 'Month'])
    
    results['monthly'] = monthly.to_dict('records')
    
    # Day-wise analysis
    daily = df.groupby('Date').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Cost': 'sum',
        'Marketing_Spend': 'sum'
    }).reset_index()
    
    # Null-safe calculations
    daily['Profit_Margin'] = daily.apply(
        lambda row: (row['Profit'] / row['Sales'] * 100) if row['Sales'] > 0 else 0,
        axis=1
    )
    daily['Day_of_Week'] = pd.to_datetime(daily['Date']).dt.day_name()
    daily = daily.sort_values('Date', ascending=False)
    
    results['daily'] = daily.to_dict('records')
    
    # Identify trends
    if len(yearly) >= 2:
        recent_growth = yearly['YoY_Growth'].iloc[-1]
        avg_growth = yearly['YoY_Growth'].mean()
        
        results['trend_analysis'] = {
            'recent_growth': float(recent_growth) if not pd.isna(recent_growth) else 0,
            'avg_growth': float(avg_growth) if not pd.isna(avg_growth) else 0,
            'trend': 'Growing' if recent_growth > 0 else 'Declining' if recent_growth < 0 else 'Stable'
        }
    
    return results


def analyze_product_performance(df):
    """
    Analyze product-wise performance with null handling
    """
    # Ensure no null values
    df = df.fillna(0)
    
    product_analysis = df.groupby('Product').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Cost': 'sum',
        'Marketing_Spend': 'sum'
    }).reset_index()
    
    # Null-safe calculations
    product_analysis['Profit_Margin'] = product_analysis.apply(
        lambda row: (row['Profit'] / row['Sales'] * 100) if row['Sales'] > 0 else 0,
        axis=1
    )
    product_analysis['ROI'] = product_analysis.apply(
        lambda row: ((row['Profit'] - row['Marketing_Spend']) / row['Marketing_Spend'] * 100) if row['Marketing_Spend'] > 0 else 0,
        axis=1
    )
    
    # Sort by profit
    product_analysis = product_analysis.sort_values('Profit', ascending=False)
    
    # Identify top and bottom performers
    top_products = product_analysis.head(5).to_dict('records')
    bottom_products = product_analysis.tail(5).to_dict('records')
    
    # Identify loss-making products
    loss_making = product_analysis[product_analysis['Profit'] < 0].to_dict('records')
    
    return {
        'all_products': product_analysis.to_dict('records'),
        'top_performers': top_products,
        'bottom_performers': bottom_products,
        'loss_making': loss_making
    }


def analyze_regional_performance(df):
    """
    Analyze region-wise performance with null handling
    """
    # Ensure no null values
    df = df.fillna(0)
    
    regional_analysis = df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Cost': 'sum',
        'Marketing_Spend': 'sum'
    }).reset_index()
    
    # Null-safe calculations
    regional_analysis['Profit_Margin'] = regional_analysis.apply(
        lambda row: (row['Profit'] / row['Sales'] * 100) if row['Sales'] > 0 else 0,
        axis=1
    )
    regional_analysis['ROI'] = regional_analysis.apply(
        lambda row: ((row['Profit'] - row['Marketing_Spend']) / row['Marketing_Spend'] * 100) if row['Marketing_Spend'] > 0 else 0,
        axis=1
    )
    
    # Sort by profit
    regional_analysis = regional_analysis.sort_values('Profit', ascending=False)
    
    # Identify top and bottom regions
    top_regions = regional_analysis.head(5).to_dict('records')
    bottom_regions = regional_analysis.tail(5).to_dict('records')
    
    return {
        'all_regions': regional_analysis.to_dict('records'),
        'top_performers': top_regions,
        'bottom_performers': bottom_regions
    }


def analyze_profit_cost_relationship(df):
    """
    Analyze relationship between profit, cost, and sales with null handling
    """
    # Ensure no null values
    df = df.copy().fillna(0)
    
    # Calculate correlations
    correlations = df[['Sales', 'Cost', 'Profit', 'Marketing_Spend']].corr()
    
    # Identify inefficiencies with null-safe division
    df['Cost_Efficiency'] = df.apply(
        lambda row: (row['Sales'] / row['Cost']) if row['Cost'] > 0 else 0,
        axis=1
    )
    
    inefficient = df[df['Cost_Efficiency'] < 1.2]  # Less than 20% margin on cost
    
    # Null-safe calculations
    total_sales = df['Sales'].sum()
    total_cost = df['Cost'].sum()
    avg_cost_ratio = float(total_cost / total_sales) if total_sales > 0 else 0
    avg_efficiency = float(df['Cost_Efficiency'].mean()) if len(df) > 0 else 0
    
    return {
        'correlations': correlations.to_dict(),
        'avg_cost_ratio': avg_cost_ratio,
        'inefficient_records': len(inefficient),
        'avg_efficiency': avg_efficiency
    }


def detect_seasonal_patterns(df):
    """
    Detect seasonal patterns in sales and profit with null handling
    """
    # Ensure no null values
    df = df.copy().fillna(0)
    
    monthly_avg = df.groupby('Month').agg({
        'Sales': 'mean',
        'Profit': 'mean'
    }).reset_index()
    
    # Calculate seasonality index with null-safe division
    overall_avg_sales = df['Sales'].mean()
    if overall_avg_sales > 0:
        monthly_avg['Seasonality_Index'] = (monthly_avg['Sales'] / overall_avg_sales * 100)
    else:
        monthly_avg['Seasonality_Index'] = 0
    
    # Identify peak and low seasons
    peak_months = monthly_avg.nlargest(3, 'Sales')[['Month', 'Sales']].to_dict('records')
    low_months = monthly_avg.nsmallest(3, 'Sales')[['Month', 'Sales']].to_dict('records')
    
    return {
        'monthly_patterns': monthly_avg.to_dict('records'),
        'peak_months': peak_months,
        'low_months': low_months,
        'has_seasonality': monthly_avg['Seasonality_Index'].std() > 10
    }


def perform_eda(df):
    """
    Comprehensive Exploratory Data Analysis
    """
    eda_results = {
        'temporal_trends': analyze_temporal_trends(df),
        'product_performance': analyze_product_performance(df),
        'regional_performance': analyze_regional_performance(df),
        'profit_cost_analysis': analyze_profit_cost_relationship(df),
        'seasonal_patterns': detect_seasonal_patterns(df)
    }
    
    return eda_results
