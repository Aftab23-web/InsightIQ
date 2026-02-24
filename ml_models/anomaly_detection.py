"""
Anomaly Detection Module
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from scipy import stats


def detect_statistical_anomalies(df, column='Sales', threshold=3):
    """
    Detect anomalies using statistical methods (Z-score) with null handling
    """
    # Ensure no null values
    df = df.copy()
    df[column] = df[column].fillna(0)
    
    # Remove infinite values
    df[column] = df[column].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Calculate Z-scores only if we have enough data
    if len(df[column]) < 3:
        return pd.DataFrame()
    
    # Calculate Z-scores
    z_scores = np.abs(stats.zscore(df[column]))
    
    # Identify anomalies
    anomalies = df.copy()
    anomalies['z_score'] = z_scores
    anomalies['is_anomaly'] = z_scores > threshold
    
    anomaly_records = anomalies[anomalies['is_anomaly']]
    
    return anomaly_records


def detect_isolation_forest_anomalies(df, columns=['Sales', 'Cost', 'Profit']):
    """
    Detect anomalies using Isolation Forest
    """
    # Select features
    available_cols = [col for col in columns if col in df.columns]
    
    if len(available_cols) < 2:
        return pd.DataFrame()
    
    # Prepare data
    X = df[available_cols].dropna()
    
    if len(X) < 10:
        return pd.DataFrame()
    
    # Fit Isolation Forest
    iso_forest = IsolationForest(contamination=0.1, random_state=42)
    predictions = iso_forest.fit_predict(X)
    
    # Add predictions to dataframe
    df_with_predictions = df.loc[X.index].copy()
    df_with_predictions['anomaly_score'] = iso_forest.score_samples(X)
    df_with_predictions['is_anomaly'] = predictions == -1
    
    anomalies = df_with_predictions[df_with_predictions['is_anomaly']]
    
    return anomalies


def detect_sudden_drops(df, metric='Sales', threshold=-30):
    """
    Detect sudden drops in metrics (>30% decline) with null handling
    """
    df_sorted = df.sort_values('Date').copy()
    
    # Ensure no null values
    df_sorted[metric] = df_sorted[metric].fillna(0)
    df_sorted[metric] = df_sorted[metric].replace([np.inf, -np.inf], 0)
    
    # Calculate period-over-period change
    df_sorted[f'{metric}_change'] = df_sorted[metric].pct_change() * 100
    df_sorted[f'{metric}_change'] = df_sorted[f'{metric}_change'].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Identify sudden drops
    sudden_drops = df_sorted[df_sorted[f'{metric}_change'] < threshold]
    
    anomalies = []
    for _, row in sudden_drops.iterrows():
        change_pct = abs(row[f'{metric}_change'])
        prev_value = row[metric] / (1 + row[f'{metric}_change']/100) if row[f'{metric}_change'] != -100 else row[metric]
        abs_drop = prev_value - row[metric]
        
        # Determine severity and create detailed description
        if change_pct > 50:
            severity = 'Critical'
            impact = 'severe'
            urgency = 'immediate attention required'
        elif change_pct > 40:
            severity = 'High'
            impact = 'significant'
            urgency = 'urgent investigation needed'
        else:
            severity = 'Medium'
            impact = 'moderate'
            urgency = 'review recommended'
        
        # Check if there's context about product or region
        context_info = ""
        if 'Product' in row and pd.notna(row['Product']):
            context_info += f"\n• Affected product: {row['Product']}"
        if 'Region' in row and pd.notna(row['Region']):
            context_info += f"\n• Affected region: {row['Region']}"
        
        # Generate dynamic causes based on magnitude and context
        causes = []
        if change_pct > 60:
            causes.extend([
                "Critical operational disruption or system failure",
                "Major external crisis or market collapse",
                "Complete stockout or supply chain breakdown"
            ])
        elif change_pct > 45:
            causes.extend([
                "Significant competitive pressure or market shift",
                "Large customer loss or contract cancellation",
                "Severe pricing or promotional issues"
            ])
        else:
            causes.extend([
                "Changing market conditions or customer preferences",
                "Seasonal fluctuation or calendar effects",
                "Competitor promotional activities or pricing changes"
            ])
        
        if metric == 'Sales':
            causes.append("Product availability or inventory management issues")
        elif metric == 'Profit':
            causes.append("Rising costs or margin compression")
        
        # Generate dynamic actions based on severity and metric
        actions = []
        if severity == 'Critical':
            actions.extend([
                f"Immediate investigation of {metric.lower()} decline root cause",
                "Emergency meeting with key stakeholders",
                "Activate contingency plans and corrective measures"
            ])
        else:
            actions.extend([
                f"Detailed analysis of {metric.lower()} trends over the past 30 days",
                "Compare performance with the same period last year",
                "Identify specific contributing factors and patterns"
            ])
        
        if metric == 'Sales':
            actions.append("Review pricing strategy and product positioning")
        elif metric == 'Profit':
            actions.append("Analyze cost structure and margin opportunities")
        
        description = f"""{metric} experienced a {impact} decline of {change_pct:.1f}% on {row['Date'].strftime('%Y-%m-%d')} - {urgency}.

Financial Impact:
• Previous {metric.lower()}: ₹{prev_value:,.2f}
• Current {metric.lower()}: ₹{row[metric]:,.2f}
• Absolute loss: ₹{abs_drop:,.2f}{context_info}

Possible Causes:
{''.join([f'• {cause}\n' for cause in causes])}
Recommended Actions:
{''.join([f'• {action}\n' for action in actions])}"""
        
        anomalies.append({
            'date': row['Date'],
            'type': f'Critical {metric} Drop' if severity == 'Critical' else f'{metric} Decline Alert',
            'metric': metric,
            'actual_value': float(row[metric]),
            'previous_value': float(prev_value),
            'change_percent': float(row[f'{metric}_change']),
            'severity': severity,
            'description': description
        })
    
    return anomalies


def detect_cost_spikes(df, threshold=2):
    """
    Detect unusual cost spikes
    """
    # Calculate rolling mean and std
    df_sorted = df.sort_values('Date').copy()
    df_sorted['cost_rolling_mean'] = df_sorted['Cost'].rolling(window=5, min_periods=1).mean()
    df_sorted['cost_rolling_std'] = df_sorted['Cost'].rolling(window=5, min_periods=1).std()
    
    # Identify spikes
    df_sorted['cost_zscore'] = (df_sorted['Cost'] - df_sorted['cost_rolling_mean']) / (df_sorted['cost_rolling_std'] + 1e-10)
    
    cost_spikes = df_sorted[df_sorted['cost_zscore'] > threshold]
    
    anomalies = []
    for _, row in cost_spikes.iterrows():
        expected_cost = row['cost_rolling_mean']
        excess_cost = row['Cost'] - expected_cost
        excess_pct = (excess_cost / expected_cost * 100) if expected_cost > 0 else 0
        z_score = row['cost_zscore']
        
        # Dynamic severity and messaging
        if excess_pct > 100:
            severity = 'Critical'
            urgency = 'immediate action required'
        elif excess_pct > 50:
            severity = 'High'
            urgency = 'urgent review needed'
        else:
            severity = 'Medium'
            urgency = 'investigation recommended'
        
        # Context-aware analysis
        context = ""
        if 'Product' in row and pd.notna(row['Product']):
            context += f"\n• Product: {row['Product']}"
        if 'Region' in row and pd.notna(row['Region']):
            context += f"\n• Region: {row['Region']}"
        if 'Sales' in row:
            cost_to_sales_ratio = (row['Cost'] / row['Sales'] * 100) if row['Sales'] > 0 else 0
            context += f"\n• Cost-to-sales ratio: {cost_to_sales_ratio:.1f}%"
        
        # Dynamic causes based on spike magnitude
        causes = []
        if excess_pct > 100:
            causes.extend([
                "Critical supplier pricing issue or emergency procurement",
                "Major operational failure requiring expensive fixes",
                "Possible data entry error or duplicate charges"
            ])
        elif excess_pct > 75:
            causes.extend([
                "Significant supply chain disruption or material shortage",
                "Emergency rush orders with premium charges",
                "Unplanned equipment repairs or replacements"
            ])
        elif excess_pct > 40:
            causes.extend([
                "Supplier price increases or contract renegotiation",
                "Inefficient production run or operational issues",
                "Quality problems requiring additional processing"
            ])
        else:
            causes.extend([
                "Normal supplier price variation or seasonal factors",
                "Small-batch production with higher unit costs",
                "Transportation cost fluctuations or routing changes"
            ])
        
        # Dynamic recommendations
        recommendations = []
        if severity == 'Critical':
            recommendations.extend([
                "Immediate audit of all cost components and invoices",
                "Verify data accuracy and check for duplicate entries",
                "Emergency supplier negotiation if pricing issue"
            ])
        else:
            recommendations.extend([
                "Detailed breakdown analysis of cost increases",
                "Comparison with historical supplier pricing trends",
                "Assessment of operational efficiency during this period"
            ])
        
        recommendations.extend([
            "Evaluate alternative sourcing options to reduce dependency",
            "Implement preventive cost monitoring and alert systems"
        ])
        
        description = f"""Cost spike alert: {excess_pct:.1f}% above expected levels on {row['Date'].strftime('%Y-%m-%d')} - {urgency}.

Cost Breakdown:
• Expected cost: ₹{expected_cost:,.2f}
• Actual cost: ₹{row['Cost']:,.2f}
• Excess amount: ₹{excess_cost:,.2f}
• Statistical deviation: {z_score:.2f}σ above normal{context}

Probable Root Causes:
{''.join([f'• {cause}\n' for cause in causes])}
Recommended Actions:
{''.join([f'• {rec}\n' for rec in recommendations])}"""
        
        anomalies.append({
            'date': row['Date'],
            'type': 'Cost Spike Alert',
            'metric': 'Cost',
            'actual_value': float(row['Cost']),
            'expected_value': float(expected_cost),
            'excess_amount': float(excess_cost),
            'severity': severity,
            'description': description
        })
    
    return anomalies


def detect_unusual_patterns(df):
    """
    Detect unusual business patterns
    """
    anomalies = []
    
    # Zero or negative sales
    zero_sales = df[df['Sales'] <= 0]
    if len(zero_sales) > 0:
        for _, row in zero_sales.iterrows():
            anomalies.append({
                'date': row['Date'],
                'type': 'Unusual Pattern',
                'metric': 'Sales',
                'actual_value': float(row['Sales']),
                'severity': 'Medium',
                'description': f"Zero or negative sales on {row['Date'].strftime('%Y-%m-%d')}"
            })
    
    # Profit > Sales (data error)
    profit_error = df[df['Profit'] > df['Sales']]
    if len(profit_error) > 0:
        for _, row in profit_error.iterrows():
            anomalies.append({
                'date': row['Date'],
                'type': 'Data Error',
                'metric': 'Profit',
                'actual_value': float(row['Profit']),
                'severity': 'High',
                'description': f"Profit exceeds sales on {row['Date'].strftime('%Y-%m-%d')} - possible data error"
            })
    
    # Extreme profit margins
    if 'Profit_Margin' in df.columns:
        extreme_margins = df[(df['Profit_Margin'] > 90) | (df['Profit_Margin'] < -50)]
        
        for _, row in extreme_margins.iterrows():
            anomalies.append({
                'date': row['Date'],
                'type': 'Unusual Pattern',
                'metric': 'Profit Margin',
                'actual_value': float(row['Profit_Margin']),
                'severity': 'Medium',
                'description': f"Extreme profit margin of {row['Profit_Margin']:.1f}% on {row['Date'].strftime('%Y-%m-%d')}"
            })
    
    return anomalies


def detect_all_anomalies(df):
    """
    Run all anomaly detection methods
    """
    all_anomalies = []
    
    # Sudden drops
    sales_drops = detect_sudden_drops(df, 'Sales', -30)
    all_anomalies.extend(sales_drops)
    
    profit_drops = detect_sudden_drops(df, 'Profit', -30)
    all_anomalies.extend(profit_drops)
    
    # Cost spikes
    cost_spikes = detect_cost_spikes(df, threshold=2)
    all_anomalies.extend(cost_spikes)
    
    # Unusual patterns
    unusual = detect_unusual_patterns(df)
    all_anomalies.extend(unusual)
    
    # Isolation Forest anomalies
    try:
        iso_anomalies = detect_isolation_forest_anomalies(df)
        
        for _, row in iso_anomalies.iterrows():
            # Analyze what makes this anomalous
            avg_sales = df['Sales'].mean()
            avg_profit = df['Profit'].mean() if 'Profit' in df.columns else 0
            avg_cost = df['Cost'].mean() if 'Cost' in df.columns else 0
            
            sales_diff = ((row.get('Sales', 0) - avg_sales) / avg_sales * 100) if avg_sales > 0 else 0
            
            # Determine what's unusual
            unusual_aspects = []
            if abs(sales_diff) > 20:
                unusual_aspects.append(f"Sales {sales_diff:+.1f}% from average")
            if 'Profit' in row and avg_profit > 0:
                profit_diff = ((row['Profit'] - avg_profit) / avg_profit * 100)
                if abs(profit_diff) > 20:
                    unusual_aspects.append(f"Profit {profit_diff:+.1f}% from average")
            if 'Profit_Margin' in row:
                if row['Profit_Margin'] < df['Profit_Margin'].quantile(0.25) or row['Profit_Margin'] > df['Profit_Margin'].quantile(0.75):
                    unusual_aspects.append(f"Profit margin at {row['Profit_Margin']:.1f}%")
            
            unusual_text = ", ".join(unusual_aspects) if unusual_aspects else "Multiple metrics outside normal range"
            
            # Dynamic analysis based on actual deviations
            analysis_parts = []
            if abs(sales_diff) > 50:
                if sales_diff > 0:
                    analysis_parts.append(f"Exceptional sales performance - {sales_diff:.1f}% above average indicates strong demand or successful campaign")
                else:
                    analysis_parts.append(f"Significant sales underperformance - {abs(sales_diff):.1f}% below average requires immediate attention")
            elif abs(sales_diff) > 30:
                if sales_diff > 0:
                    analysis_parts.append(f"Notable sales increase of {sales_diff:.1f}% suggests positive market response")
                else:
                    analysis_parts.append(f"Sales decline of {abs(sales_diff):.1f}% indicates concerning trend")
            
            if 'Profit' in row and avg_profit > 0:
                profit_diff = ((row['Profit'] - avg_profit) / avg_profit * 100)
                if abs(profit_diff) > 40:
                    if profit_diff > 0:
                        analysis_parts.append(f"Profit surge of {profit_diff:.1f}% reflects strong operational efficiency")
                    else:
                        analysis_parts.append(f"Profit erosion of {abs(profit_diff):.1f}% signals margin pressure or cost issues")
            
            if 'Profit_Margin' in row:
                pm = row['Profit_Margin']
                avg_pm = df['Profit_Margin'].mean()
                if pm < 0:
                    analysis_parts.append("Loss-making transaction requiring immediate cost review")
                elif pm < avg_pm - 10:
                    analysis_parts.append(f"Margin compression: {pm:.1f}% vs typical {avg_pm:.1f}%")
                elif pm > avg_pm + 15:
                    analysis_parts.append(f"Exceptional margin of {pm:.1f}% - investigate replicability")
            
            analysis_text = ". ".join(analysis_parts) if analysis_parts else "This data point exhibits multi-dimensional deviation from expected patterns"
            
            # Context-aware causes
            causes = []
            if sales_diff > 40:
                causes.extend([
                    "Successful marketing campaign or viral product moment",
                    "Large bulk order or major customer win",
                    "Competitive advantage or market gap exploitation"
                ])
            elif sales_diff < -40:
                causes.extend([
                    "Competitive pressure or market share loss",
                    "Inventory shortage or supply disruption",
                    "Seasonal downturn or external economic factors"
                ])
            else:
                causes.extend([
                    "Routine business variance or timing differences",
                    "Special event or calendar effect (holiday, weekend)",
                    "Data recording timing or batch processing artifact"
                ])
            
            if 'Product' in row and pd.notna(row['Product']):
                causes.append(f"Product-specific dynamics for {row['Product']}")
            
            # Targeted actions
            actions = []
            if abs(sales_diff) > 50:
                actions.extend([
                    "Deep-dive analysis: What was different on this date?",
                    "Customer feedback review and market intelligence gathering",
                    "Document learnings for strategy replication or risk mitigation"
                ])
            else:
                actions.extend([
                    "Data validation to rule out recording errors",
                    "Contextual review of business operations on this date",
                    "Trend monitoring to see if pattern continues"
                ])
            
            # Add context information
            context_items = []
            if 'Product' in row and pd.notna(row['Product']):
                context_items.append(f"Product: {row['Product']}")
            if 'Region' in row and pd.notna(row['Region']):
                context_items.append(f"Region: {row['Region']}")
            context_line = "\n• " + "\n• ".join(context_items) if context_items else ""
            
            description = f"""Statistical anomaly detected on {row['Date'].strftime('%Y-%m-%d')} - {unusual_text}.

Business Metrics:
• Sales: ₹{row.get('Sales', 0):,.2f} (average: ₹{avg_sales:,.2f}, deviation: {sales_diff:+.1f}%)
• Profit: ₹{row.get('Profit', 0):,.2f} (average: ₹{avg_profit:,.2f})
• Profit Margin: {row.get('Profit_Margin', 0):.1f}%{context_line}

Analysis:
{analysis_text}

Possible Causes:
{''.join([f'• {cause}\n' for cause in causes])}
Recommended Actions:
{''.join([f'• {action}\n' for action in actions])}"""
            
            all_anomalies.append({
                'date': row['Date'],
                'type': 'Statistical Pattern Anomaly',
                'metric': 'Multiple Metrics',
                'actual_value': float(row.get('Sales', 0)),
                'severity': 'Low',
                'description': description
            })
    except Exception as e:
        pass  # Skip if isolation forest fails
    
    # Sort by severity and date
    severity_order = {'High': 0, 'Medium': 1, 'Low': 2}
    all_anomalies.sort(key=lambda x: (severity_order.get(x['severity'], 2), x['date']), reverse=True)
    
    return {
        'anomalies': all_anomalies,
        'summary': {
            'total_anomalies': len(all_anomalies),
            'high_severity': len([a for a in all_anomalies if a['severity'] == 'High']),
            'medium_severity': len([a for a in all_anomalies if a['severity'] == 'Medium']),
            'low_severity': len([a for a in all_anomalies if a['severity'] == 'Low'])
        }
    }
