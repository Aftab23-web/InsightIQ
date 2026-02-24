"""
Business Mistake Detection Module
"""
import pandas as pd
import numpy as np


def detect_loss_making_products(df):
    """
    Identify products generating losses
    """
    product_profit = df.groupby('Product').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Cost': 'sum'
    }).reset_index()
    
    loss_products = product_profit[product_profit['Profit'] < 0]
    
    mistakes = []
    for _, row in loss_products.iterrows():
        loss_amount = abs(row['Profit'])
        loss_percent = (loss_amount / row['Sales'] * 100) if row['Sales'] > 0 else 0
        
        mistakes.append({
            'type': 'Loss-Making Product',
            'severity': 'High' if loss_amount > product_profit['Profit'].std() else 'Medium',
            'product': row['Product'],
            'loss_amount': float(loss_amount),
            'loss_percent': float(loss_percent),
            'description': f"Product '{row['Product']}' generated a loss of ₹{loss_amount:,.2f} ({loss_percent:.1f}% of sales)"
        })
    
    return mistakes


def detect_poor_performing_regions(df):
    """
    Identify underperforming regions
    """
    regional_profit = df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Profit_Margin': 'mean'
    }).reset_index()
    
    # Calculate thresholds
    avg_profit_margin = regional_profit['Profit_Margin'].mean()
    std_profit_margin = regional_profit['Profit_Margin'].std()
    threshold = avg_profit_margin - std_profit_margin
    
    poor_regions = regional_profit[regional_profit['Profit_Margin'] < threshold]
    
    mistakes = []
    for _, row in poor_regions.iterrows():
        mistakes.append({
            'type': 'Poor-Performing Region',
            'severity': 'High' if row['Profit_Margin'] < 0 else 'Medium',
            'region': row['Region'],
            'profit_margin': float(row['Profit_Margin']),
            'below_average_by': float(avg_profit_margin - row['Profit_Margin']),
            'description': f"Region '{row['Region']}' has profit margin of {row['Profit_Margin']:.1f}%, significantly below average ({avg_profit_margin:.1f}%)"
        })
    
    return mistakes


def detect_high_cost_low_profit(df):
    """
    Identify scenarios with high costs but low profits
    """
    # Calculate efficiency metrics per product-region combination
    efficiency = df.groupby(['Product', 'Region']).agg({
        'Sales': 'sum',
        'Cost': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    efficiency['Cost_Ratio'] = efficiency['Cost'] / efficiency['Sales']
    efficiency['Profit_Margin'] = (efficiency['Profit'] / efficiency['Sales'] * 100)
    
    # High cost (>70%) but low profit (<10%)
    inefficient = efficiency[(efficiency['Cost_Ratio'] > 0.7) & (efficiency['Profit_Margin'] < 10)]
    
    mistakes = []
    for _, row in inefficient.iterrows():
        mistakes.append({
            'type': 'High Cost - Low Profit',
            'severity': 'High',
            'product': row['Product'],
            'region': row['Region'],
            'cost_ratio': float(row['Cost_Ratio'] * 100),
            'profit_margin': float(row['Profit_Margin']),
            'description': f"{row['Product']} in {row['Region']}: Cost is {row['Cost_Ratio']*100:.1f}% of sales but profit margin only {row['Profit_Margin']:.1f}%"
        })
    
    return mistakes


def detect_inefficient_marketing(df):
    """
    Identify inefficient marketing spend
    """
    marketing_roi = df.groupby(['Product', 'Region']).agg({
        'Marketing_Spend': 'sum',
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    marketing_roi['ROI'] = ((marketing_roi['Profit'] - marketing_roi['Marketing_Spend']) / 
                             marketing_roi['Marketing_Spend'] * 100)
    marketing_roi['Marketing_Efficiency'] = marketing_roi['Sales'] / marketing_roi['Marketing_Spend']
    
    # Negative ROI or very low efficiency
    inefficient = marketing_roi[(marketing_roi['ROI'] < 0) | (marketing_roi['Marketing_Efficiency'] < 2)]
    
    mistakes = []
    for _, row in inefficient.iterrows():
        if row['ROI'] < 0:
            severity = 'Critical'
            desc = f"Marketing spend for {row['Product']} in {row['Region']} has negative ROI of {row['ROI']:.1f}%"
        else:
            severity = 'Medium'
            desc = f"Marketing efficiency for {row['Product']} in {row['Region']} is only {row['Marketing_Efficiency']:.1f}x return"
        
        mistakes.append({
            'type': 'Inefficient Marketing Spend',
            'severity': severity,
            'product': row['Product'],
            'region': row['Region'],
            'roi': float(row['ROI']),
            'efficiency': float(row['Marketing_Efficiency']),
            'description': desc
        })
    
    return mistakes


def detect_declining_trends(df):
    """
    Identify products/regions with declining performance
    """
    mistakes = []
    
    # Product-wise trend analysis
    for product in df['Product'].unique():
        product_data = df[df['Product'] == product].sort_values('Date')
        
        if len(product_data) >= 3:
            recent_sales = product_data.tail(3)['Sales'].mean()
            older_sales = product_data.head(3)['Sales'].mean()
            
            if older_sales > 0:
                decline = ((recent_sales - older_sales) / older_sales * 100)
                
                if decline < -20:  # More than 20% decline
                    mistakes.append({
                        'type': 'Declining Performance',
                        'severity': 'High' if decline < -40 else 'Medium',
                        'product': product,
                        'decline_percent': float(decline),
                        'description': f"Product '{product}' shows {abs(decline):.1f}% decline in recent performance"
                    })
    
    return mistakes


def detect_product_sales_imbalance(df):
    """
    Identify when one product dominates sales while others underperform
    """
    mistakes = []
    
    # Analyze product sales distribution
    product_analysis = df.groupby('Product').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Profit_Margin': 'mean',
        'Cost': 'sum',
        'Marketing_Spend': 'sum'
    }).reset_index()
    
    total_sales = product_analysis['Sales'].sum()
    product_analysis['Sales_Share'] = (product_analysis['Sales'] / total_sales * 100)
    product_analysis = product_analysis.sort_values('Sales', ascending=False)
    
    # Check if there's significant imbalance
    if len(product_analysis) >= 2:
        top_product = product_analysis.iloc[0]
        top_share = top_product['Sales_Share']
        
        # If one product dominates (>40% share) and others are significantly lower
        if top_share > 40:
            underperforming_products = product_analysis[
                product_analysis['Sales_Share'] < (top_share / 3)
            ].iloc[1:]  # Exclude the top product
            
            if len(underperforming_products) > 0:
                # Analyze why other products aren't selling
                for _, product in underperforming_products.iterrows():
                    reasons = []
                    product_name = product['Product']
                    product_share = product['Sales_Share']
                    product_sales = product['Sales']
                    
                    # Compare with top product to identify issues
                    top_margin = top_product['Profit_Margin']
                    product_margin = product['Profit_Margin']
                    
                    # Reason 1: Poor pricing/margins
                    if product_margin < top_margin - 10:
                        reasons.append(f"Low profit margin ({product_margin:.1f}% vs top product's {top_margin:.1f}%) suggests pricing issues or high costs")
                    
                    # Reason 2: Insufficient marketing
                    if product['Marketing_Spend'] > 0 and top_product['Marketing_Spend'] > 0:
                        top_marketing_ratio = top_product['Marketing_Spend'] / top_product['Sales']
                        product_marketing_ratio = product['Marketing_Spend'] / product['Sales'] if product['Sales'] > 0 else 0
                        
                        if product_marketing_ratio < top_marketing_ratio * 0.5:
                            reasons.append(f"Under-marketed: only ₹{product['Marketing_Spend']:,.0f} marketing spend (top product: ₹{top_product['Marketing_Spend']:,.0f})")
                        elif product_marketing_ratio > top_marketing_ratio * 1.5:
                            marketing_efficiency_top = top_product['Sales'] / top_product['Marketing_Spend']
                            marketing_efficiency_product = product['Sales'] / product['Marketing_Spend'] if product['Marketing_Spend'] > 0 else 0
                            reasons.append(f"Ineffective marketing: spending {product_marketing_ratio*100:.1f}% on marketing but only {marketing_efficiency_product:.1f}x return (vs {marketing_efficiency_top:.1f}x for top product)")
                    
                    # Reason 3: Regional availability issues
                    if 'Region' in df.columns:
                        top_product_regions = df[df['Product'] == top_product['Product']]['Region'].nunique()
                        product_regions = df[df['Product'] == product_name]['Region'].nunique()
                        
                        if product_regions < top_product_regions:
                            reasons.append(f"Limited regional presence: available in {product_regions} regions (top product in {top_product_regions} regions)")
                    
                    # Reason 4: Cost structure
                    top_cost_ratio = top_product['Cost'] / top_product['Sales'] if top_product['Sales'] > 0 else 0
                    product_cost_ratio = product['Cost'] / product['Sales'] if product['Sales'] > 0 else 0
                    
                    if product_cost_ratio > top_cost_ratio * 1.2:
                        reasons.append(f"High cost structure: {product_cost_ratio*100:.1f}% cost-to-sales ratio (top product: {top_cost_ratio*100:.1f}%)")
                    
                    # Reason 5: Product positioning
                    if len(reasons) == 0:
                        reasons.append("Possible product-market fit issues, poor positioning, or lack of customer awareness")
                    
                    # Create mistake entry
                    gap = top_share - product_share
                    potential_revenue = (gap / 100) * total_sales * 0.3  # Assume can capture 30% of gap
                    
                    severity = 'High' if product_share < 5 and top_share > 50 else 'Medium'
                    
                    description = f"{top_product['Product']} dominates with {top_share:.1f}% market share while {product_name} has only {product_share:.1f}% - leaving ₹{potential_revenue:,.0f} revenue opportunity untapped"
                    
                    mistakes.append({
                        'type': 'Product Sales Imbalance',
                        'severity': severity,
                        'product': product_name,
                        'dominant_product': top_product['Product'],
                        'sales_share': float(product_share),
                        'dominant_share': float(top_share),
                        'gap_percent': float(gap),
                        'potential_revenue': float(potential_revenue),
                        'description': description,
                        'root_causes': reasons,
                        'action_items': [
                            f"Analyze why {top_product['Product']} succeeds: pricing, quality, marketing approach",
                            f"Address identified issues: {'; '.join(reasons[:2])}",
                            f"Consider product refresh, rebranding, or discontinuation if unviable",
                            f"Reallocate resources from {product_name} to {top_product['Product']} if optimization fails"
                        ]
                    })
    
    return mistakes


def detect_all_mistakes(df):
    """
    Run all mistake detection algorithms
    """
    all_mistakes = {
        'loss_making_products': detect_loss_making_products(df),
        'poor_performing_regions': detect_poor_performing_regions(df),
        'high_cost_low_profit': detect_high_cost_low_profit(df),
        'inefficient_marketing': detect_inefficient_marketing(df),
        'declining_trends': detect_declining_trends(df),
        'product_sales_imbalance': detect_product_sales_imbalance(df)
    }
    
    # Flatten all mistakes into a single list with priority
    mistakes_list = []
    for category, mistakes in all_mistakes.items():
        for mistake in mistakes:
            mistake['category'] = category
            mistakes_list.append(mistake)
    
    # Sort by severity
    severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    mistakes_list.sort(key=lambda x: severity_order.get(x.get('severity', 'Low'), 3))
    
    return {
        'by_category': all_mistakes,
        'all_mistakes': mistakes_list,
        'summary': {
            'total_mistakes': len(mistakes_list),
            'critical': len([m for m in mistakes_list if m.get('severity') == 'Critical']),
            'high': len([m for m in mistakes_list if m.get('severity') == 'High']),
            'medium': len([m for m in mistakes_list if m.get('severity') == 'Medium']),
            'low': len([m for m in mistakes_list if m.get('severity') == 'Low'])
        }
    }
