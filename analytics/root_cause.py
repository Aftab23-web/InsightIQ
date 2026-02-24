"""
Root Cause Analysis Module (WHY Engine)
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from scipy.stats import pearsonr


def calculate_correlations(df):
    """
    Calculate correlations between metrics
    """
    # Select numeric columns
    numeric_cols = ['Sales', 'Cost', 'Profit', 'Marketing_Spend', 
                    'Profit_Margin', 'ROI', 'Cost_Ratio']
    
    available_cols = [col for col in numeric_cols if col in df.columns]
    
    if len(available_cols) < 2:
        return {}
    
    # Calculate correlation matrix
    corr_matrix = df[available_cols].corr()
    
    # Extract significant correlations with Profit
    if 'Profit' in available_cols:
        profit_corr = corr_matrix['Profit'].sort_values(ascending=False)
        
        # Find top positive and negative correlations
        correlations = {
            'profit_correlations': profit_corr.to_dict(),
            'strong_positive': profit_corr[profit_corr > 0.5].to_dict(),
            'strong_negative': profit_corr[profit_corr < -0.5].to_dict()
        }
    else:
        correlations = {'correlation_matrix': corr_matrix.to_dict()}
    
    return correlations


def calculate_feature_importance(df, target='Profit'):
    """
    Calculate feature importance using Random Forest
    """
    # Prepare features
    feature_cols = []
    
    # Numeric features
    numeric_features = ['Sales', 'Cost', 'Marketing_Spend']
    feature_cols.extend([col for col in numeric_features if col in df.columns])
    
    # Time features
    time_features = ['Month', 'Quarter']
    feature_cols.extend([col for col in time_features if col in df.columns])
    
    if len(feature_cols) < 2 or target not in df.columns:
        return {}
    
    # Encode categorical features
    df_encoded = df.copy()
    
    if 'Product' in df.columns:
        product_dummies = pd.get_dummies(df['Product'], prefix='Product')
        df_encoded = pd.concat([df_encoded, product_dummies], axis=1)
        feature_cols.extend(product_dummies.columns.tolist())
    
    if 'Region' in df.columns:
        region_dummies = pd.get_dummies(df['Region'], prefix='Region')
        df_encoded = pd.concat([df_encoded, region_dummies], axis=1)
        feature_cols.extend(region_dummies.columns.tolist())
    
    # Remove any rows with missing values
    df_clean = df_encoded[feature_cols + [target]].dropna()
    
    if len(df_clean) < 10:
        return {}
    
    X = df_clean[feature_cols]
    y = df_clean[target]
    
    # Train Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    rf.fit(X, y)
    
    # Get feature importance
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False)
    
    # Get top features
    top_features = importance_df.head(10).to_dict('records')
    
    return {
        'all_features': importance_df.to_dict('records'),
        'top_features': top_features,
        'model_score': float(rf.score(X, y))
    }


def analyze_profit_drivers(df):
    """
    Identify key drivers of profit/loss
    """
    drivers = []
    
    # Cost efficiency driver
    avg_cost_ratio = df['Cost'].sum() / df['Sales'].sum()
    if avg_cost_ratio > 0.8:
        drivers.append({
            'driver': 'High Cost Ratio',
            'impact': 'Negative',
            'severity': 'High',
            'value': f"{avg_cost_ratio*100:.1f}%",
            'explanation': f"Costs are {avg_cost_ratio*100:.1f}% of sales, leaving minimal profit margin"
        })
    
    # Marketing efficiency driver
    if 'Marketing_Spend' in df.columns and 'Profit' in df.columns:
        total_marketing = df['Marketing_Spend'].sum()
        total_profit = df['Profit'].sum()
        
        if total_marketing > 0:
            marketing_roi = (total_profit / total_marketing - 1) * 100
            
            if marketing_roi < 50:
                drivers.append({
                    'driver': 'Low Marketing ROI',
                    'impact': 'Negative',
                    'severity': 'Medium',
                    'value': f"{marketing_roi:.1f}%",
                    'explanation': f"Marketing ROI is only {marketing_roi:.1f}%, indicating inefficient spending"
                })
    
    # Product mix driver
    if 'Product' in df.columns:
        product_profit = df.groupby('Product')['Profit'].sum().sort_values(ascending=False)
        top_product_share = product_profit.iloc[0] / product_profit.sum() * 100
        
        if top_product_share > 60:
            drivers.append({
                'driver': 'Over-Reliance on Single Product',
                'impact': 'Risk',
                'severity': 'Medium',
                'value': f"{top_product_share:.1f}%",
                'explanation': f"Top product accounts for {top_product_share:.1f}% of profit - high concentration risk"
            })
    
    # Sales volume driver
    avg_sales = df['Sales'].mean()
    recent_sales = df.tail(len(df) // 4)['Sales'].mean()  # Last quarter
    
    if recent_sales < avg_sales * 0.8:
        drivers.append({
            'driver': 'Declining Sales Volume',
            'impact': 'Negative',
            'severity': 'High',
            'value': f"{(recent_sales/avg_sales - 1)*100:.1f}%",
            'explanation': f"Recent sales are {abs((recent_sales/avg_sales - 1)*100):.1f}% below average"
        })
    
    return drivers


def identify_root_causes(df, problem_type='low_profit'):
    """
    Comprehensive root cause analysis
    """
    root_causes = {
        'correlations': calculate_correlations(df),
        'feature_importance': calculate_feature_importance(df),
        'profit_drivers': analyze_profit_drivers(df),
        'summary': []
    }
    
    # Generate summary insights
    if root_causes['feature_importance']:
        top_features = root_causes['feature_importance'].get('top_features', [])[:3]
        
        for feature in top_features:
            root_causes['summary'].append({
                'factor': feature['feature'],
                'importance': f"{feature['importance']*100:.1f}%",
                'description': f"{feature['feature']} has {feature['importance']*100:.1f}% impact on profit"
            })
    
    # Add correlation insights
    if 'profit_correlations' in root_causes['correlations']:
        profit_corr = root_causes['correlations']['profit_correlations']
        
        for metric, corr in list(profit_corr.items())[:5]:
            if metric != 'Profit' and abs(corr) > 0.3:
                direction = 'positive' if corr > 0 else 'negative'
                root_causes['summary'].append({
                    'factor': metric,
                    'correlation': f"{corr:.2f}",
                    'description': f"{metric} has a {direction} correlation ({corr:.2f}) with profit"
                })
    
    return root_causes
