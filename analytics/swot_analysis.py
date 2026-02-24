"""
Strength & Weakness Analysis Module
"""
import pandas as pd
import numpy as np


def identify_strengths(df):
    """
    Identify business strengths from data
    """
    strengths = []
    
    # High-profit products
    product_profit = df.groupby('Product').agg({
        'Profit': 'sum',
        'Profit_Margin': 'mean',
        'Sales': 'sum'
    }).reset_index()
    
    avg_margin = product_profit['Profit_Margin'].mean()
    high_profit_products = product_profit[
        (product_profit['Profit'] > 0) & 
        (product_profit['Profit_Margin'] > avg_margin)
    ].sort_values('Profit', ascending=False)
    
    if len(high_profit_products) > 0:
        top_product = high_profit_products.iloc[0]
        strengths.append({
            'category': 'Product',
            'title': f"Strong Product: {top_product['Product']}",
            'metric': 'Profit',
            'value': float(top_product['Profit']),
            'description': f"{top_product['Product']} generates ₹{top_product['Profit']:,.2f} in profit with {top_product['Profit_Margin']:.1f}% margin",
            'impact': 'High'
        })
    
    # Strong regions
    regional_profit = df.groupby('Region').agg({
        'Profit': 'sum',
        'Profit_Margin': 'mean',
        'Sales': 'sum'
    }).reset_index()
    
    strong_regions = regional_profit[regional_profit['Profit'] > 0].sort_values('Profit', ascending=False)
    
    if len(strong_regions) > 0:
        top_region = strong_regions.iloc[0]
        strengths.append({
            'category': 'Region',
            'title': f"Strong Region: {top_region['Region']}",
            'metric': 'Profit',
            'value': float(top_region['Profit']),
            'description': f"{top_region['Region']} is the top-performing region with ₹{top_region['Profit']:,.2f} profit",
            'impact': 'High'
        })
    
    # Consistent growth
    if 'Year' in df.columns:
        yearly_sales = df.groupby('Year')['Sales'].sum()
        
        if len(yearly_sales) >= 2:
            growth_rates = yearly_sales.pct_change().dropna()
            
            if len(growth_rates) > 0 and growth_rates.mean() > 0.05:  # 5% average growth
                strengths.append({
                    'category': 'Growth',
                    'title': 'Consistent Revenue Growth',
                    'metric': 'Growth Rate',
                    'value': float(growth_rates.mean() * 100),
                    'description': f"Average annual growth rate of {growth_rates.mean()*100:.1f}%",
                    'impact': 'High'
                })
    
    # Efficient marketing
    if 'Marketing_Spend' in df.columns:
        total_marketing = df['Marketing_Spend'].sum()
        total_sales = df['Sales'].sum()
        
        if total_marketing > 0:
            marketing_efficiency = total_sales / total_marketing
            
            if marketing_efficiency > 5:  # 5x return on marketing
                strengths.append({
                    'category': 'Marketing',
                    'title': 'High Marketing Efficiency',
                    'metric': 'Marketing ROI',
                    'value': float(marketing_efficiency),
                    'description': f"Marketing generates {marketing_efficiency:.1f}x return on investment",
                    'impact': 'Medium'
                })
    
    # Stable profit margins
    if 'Profit_Margin' in df.columns:
        margin_std = df['Profit_Margin'].std()
        avg_margin = df['Profit_Margin'].mean()
        
        if margin_std < 10 and avg_margin > 15:  # Stable and healthy
            strengths.append({
                'category': 'Profitability',
                'title': 'Stable Profit Margins',
                'metric': 'Profit Margin',
                'value': float(avg_margin),
                'description': f"Consistent profit margin averaging {avg_margin:.1f}% with low volatility",
                'impact': 'Medium'
            })
    
    return strengths


def identify_weaknesses(df):
    """
    Identify business weaknesses from data
    """
    weaknesses = []
    
    # Loss-making products
    product_profit = df.groupby('Product').agg({
        'Profit': 'sum',
        'Sales': 'sum'
    }).reset_index()
    
    loss_products = product_profit[product_profit['Profit'] < 0].sort_values('Profit')
    
    if len(loss_products) > 0:
        worst_product = loss_products.iloc[0]
        weaknesses.append({
            'category': 'Product',
            'title': f"Loss-Making Product: {worst_product['Product']}",
            'metric': 'Profit',
            'value': float(worst_product['Profit']),
            'description': f"{worst_product['Product']} generates losses of ₹{abs(worst_product['Profit']):,.2f}",
            'severity': 'High'
        })
    
    # Weak regions
    regional_profit = df.groupby('Region').agg({
        'Profit': 'sum',
        'Profit_Margin': 'mean'
    }).reset_index()
    
    avg_margin = regional_profit['Profit_Margin'].mean()
    weak_regions = regional_profit[regional_profit['Profit_Margin'] < avg_margin * 0.5]
    
    if len(weak_regions) > 0:
        worst_region = weak_regions.sort_values('Profit_Margin').iloc[0]
        weaknesses.append({
            'category': 'Region',
            'title': f"Underperforming Region: {worst_region['Region']}",
            'metric': 'Profit Margin',
            'value': float(worst_region['Profit_Margin']),
            'description': f"{worst_region['Region']} has weak profit margin of {worst_region['Profit_Margin']:.1f}%",
            'severity': 'High'
        })
    
    # Declining sales
    if 'Date' in df.columns:
        df_sorted = df.sort_values('Date')
        first_half_sales = df_sorted.head(len(df_sorted) // 2)['Sales'].sum()
        second_half_sales = df_sorted.tail(len(df_sorted) // 2)['Sales'].sum()
        
        if second_half_sales < first_half_sales * 0.9:  # 10% decline
            decline = (second_half_sales / first_half_sales - 1) * 100
            weaknesses.append({
                'category': 'Sales',
                'title': 'Declining Sales Trend',
                'metric': 'Sales Growth',
                'value': float(decline),
                'description': f"Sales declined by {abs(decline):.1f}% in recent period",
                'severity': 'High'
            })
    
    # High cost ratios
    avg_cost_ratio = df['Cost'].sum() / df['Sales'].sum()
    
    if avg_cost_ratio > 0.65:  # Costs > 65% of sales
        weaknesses.append({
            'category': 'Cost',
            'title': 'High Cost Structure',
            'metric': 'Cost Ratio',
            'value': float(avg_cost_ratio * 100),
            'description': f"Costs account for {avg_cost_ratio*100:.1f}% of sales, limiting profitability",
            'severity': 'High' if avg_cost_ratio > 0.75 else 'Medium'
        })
    
    # Poor marketing ROI
    if 'Marketing_Spend' in df.columns:
        total_marketing = df['Marketing_Spend'].sum()
        total_profit = df['Profit'].sum()
        
        if total_marketing > 0:
            marketing_roi = (total_profit / total_marketing - 1) * 100
            
            if marketing_roi < 200:  # Less than 3x return
                weaknesses.append({
                    'category': 'Marketing',
                    'title': 'Low Marketing ROI',
                    'metric': 'ROI',
                    'value': float(marketing_roi),
                    'description': f"Marketing ROI is {marketing_roi:.1f}%, could be improved",
                    'severity': 'Medium'
                })
    
    # Low average profit margin
    if 'Profit_Margin' in df.columns:
        avg_margin = df['Profit_Margin'].mean()
        if avg_margin < 25:  # Less than 25% profit margin
            weaknesses.append({
                'category': 'Profitability',
                'title': 'Below-Target Profit Margins',
                'metric': 'Profit Margin',
                'value': float(avg_margin),
                'description': f"Average profit margin of {avg_margin:.1f}% is below industry targets (25%+)",
                'severity': 'Medium'
            })
    
    return weaknesses


def perform_swot_analysis(df):
    """
    Generate SWOT analysis from data
    """
    strengths = identify_strengths(df)
    weaknesses = identify_weaknesses(df)
    
    # Opportunities (data-driven)
    opportunities = []
    
    # Underutilized high-margin products
    product_analysis = df.groupby('Product').agg({
        'Profit_Margin': 'mean',
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    total_sales = df['Sales'].sum()
    avg_margin = product_analysis['Profit_Margin'].mean()
    
    # Find high-margin, low-volume products
    for _, product in product_analysis.iterrows():
        sales_share = product['Sales'] / total_sales * 100
        if product['Profit_Margin'] > avg_margin * 1.2 and sales_share < 15:
            opportunities.append({
                'category': 'Product Growth',
                'title': f"Scale Up {product['Product']} Sales",
                'description': f"{product['Product']} has excellent {product['Profit_Margin']:.1f}% margin but only {sales_share:.1f}% market share - significant expansion opportunity",
                'potential': 'High'
            })
    
    # Find products with good volume but lower margins that could be optimized
    for _, product in product_analysis.iterrows():
        sales_share = product['Sales'] / total_sales * 100
        if sales_share > 20 and product['Profit_Margin'] < avg_margin:
            improvement_potential = (avg_margin - product['Profit_Margin']) / 100 * product['Sales']
            opportunities.append({
                'category': 'Margin Optimization',
                'title': f"Optimize {product['Product']} Profitability",
                'description': f"{product['Product']} represents {sales_share:.1f}% of sales but has below-average margin ({product['Profit_Margin']:.1f}%) - margin improvement could add ₹{improvement_potential:,.0f} profit",
                'potential': 'High'
            })
    
    # Market expansion based on successful regions
    if 'Region' in df.columns:
        regional_analysis = df.groupby('Region').agg({
            'Sales': 'sum',
            'Profit_Margin': 'mean',
            'Profit': 'sum'
        }).reset_index()
        
        if len(regional_analysis) >= 2:
            regional_analysis = regional_analysis.sort_values('Profit', ascending=False)
            top_region = regional_analysis.iloc[0]
            bottom_region = regional_analysis.iloc[-1]
            
            if bottom_region['Profit'] > 0 and top_region['Profit'] > bottom_region['Profit'] * 2:
                potential_gain = (top_region['Sales'] - bottom_region['Sales'])
                opportunities.append({
                    'category': 'Geographic Expansion',
                    'title': f"Replicate {top_region['Region']} Success Model",
                    'description': f"{top_region['Region']} generates {top_region['Profit']/bottom_region['Profit']:.1f}x more profit than {bottom_region['Region']} - apply winning strategies to boost underperforming regions by up to ₹{potential_gain:,.0f}",
                    'potential': 'High'
                })
    
    # Digital/Automation opportunities based on business scale
    total_transactions = len(df)
    if total_transactions > 100 and 'Marketing_Spend' in df.columns:
        total_marketing = df['Marketing_Spend'].sum()
        if total_marketing > 0:
            opportunities.append({
                'category': 'Digital Transformation',
                'title': 'Automate Marketing and Analytics',
                'description': f"With {total_transactions} transactions and ₹{total_marketing:,.0f} marketing spend, automation could reduce costs by 15-25% while improving targeting effectiveness",
                'potential': 'Medium'
            })
    
    # Customer retention based on repeat business patterns
    if 'Date' in df.columns and len(df) > 50:
        # Analyze if there's growth potential from customer retention
        monthly_avg_sales = df.groupby(df['Date'].dt.to_period('M'))['Sales'].mean().mean()
        if monthly_avg_sales > 0:
            retention_opportunity = monthly_avg_sales * 0.15  # Assume 15% improvement from retention
            opportunities.append({
                'category': 'Customer Retention',
                'title': 'Implement Loyalty and Retention Programs',
                'description': f"Build customer loyalty initiatives - research shows 15% improvement in retention could add ₹{retention_opportunity:,.0f} in monthly recurring revenue",
                'potential': 'Medium'
            })
    
    # Seasonal opportunities
    if 'Month' in df.columns:
        monthly_sales = df.groupby('Month')['Sales'].mean()
        if len(monthly_sales) >= 6:
            peak_month = monthly_sales.idxmax()
            low_month = monthly_sales.idxmin()
            peak_sales = monthly_sales.max()
            low_sales = monthly_sales.min()
            avg_sales = monthly_sales.mean()
            
            if peak_sales > low_sales * 1.5:
                boost_potential = (peak_sales - low_sales) * 0.3
                opportunities.append({
                    'category': 'Seasonal Optimization',
                    'title': f"Boost Off-Peak Performance (Month {low_month})",
                    'description': f"Month {peak_month} generates {(peak_sales/low_sales):.1f}x more sales than month {low_month} - strategic promotions during slow periods could capture ₹{boost_potential:,.0f} additional revenue",
                    'potential': 'Medium'
                })
    
    # Cost reduction opportunities
    avg_cost_ratio = df['Cost'].sum() / df['Sales'].sum() if df['Sales'].sum() > 0 else 0
    if avg_cost_ratio > 0.65:
        potential_savings = df['Sales'].sum() * (avg_cost_ratio - 0.60)
        opportunities.append({
            'category': 'Cost Optimization',
            'title': 'Reduce Operational Cost Ratio',
            'description': f"Current cost ratio of {avg_cost_ratio*100:.1f}% is above optimal (60%) - supply chain optimization and operational efficiency could save ₹{potential_savings:,.0f}",
            'potential': 'High'
        })
    
    # Marketing efficiency improvement
    if 'Marketing_Spend' in df.columns:
        total_marketing = df['Marketing_Spend'].sum()
        total_sales = df['Sales'].sum()
        if total_marketing > 0:
            current_roi = total_sales / total_marketing
            if current_roi < 20:  # Below 20x return
                improvement_potential = total_marketing * 0.2
                opportunities.append({
                    'category': 'Marketing Optimization',
                    'title': 'Improve Marketing ROI Through Targeting',
                    'description': f"Current marketing generates {current_roi:.1f}x return - data-driven targeting and channel optimization could improve efficiency by 20%, saving ₹{improvement_potential:,.0f}",
                    'potential': 'High'
                    })
    
    # Threats (data-driven)
    threats = []
    
    # Market concentration risk - Product
    if 'Product' in df.columns:
        product_sales = df.groupby('Product')['Sales'].sum().sort_values(ascending=False)
        top_product_share = product_sales.iloc[0] / product_sales.sum() * 100
        top_product_name = product_sales.index[0]
        
        if top_product_share > 35:
            threats.append({
                'category': 'Business Risk',
                'title': f"{top_product_name} Concentration Risk",
                'description': f"Over-reliance on {top_product_name} ({top_product_share:.0f}% of sales) creates vulnerability - disruption to this product line would severely impact revenue",
                'severity': 'High' if top_product_share > 50 else 'Medium'
            })
    
    # Regional concentration risk
    if 'Region' in df.columns:
        regional_sales = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
        if len(regional_sales) > 0:
            top_region_share = regional_sales.iloc[0] / regional_sales.sum() * 100
            top_region_name = regional_sales.index[0]
            
            if top_region_share > 40:
                threats.append({
                    'category': 'Geographic Risk',
                    'title': f"{top_region_name} Geographic Dependency",
                    'description': f"{top_region_name} accounts for {top_region_share:.0f}% of total sales - regional economic downturn or competition could significantly impact overall business",
                    'severity': 'Medium'
                })
    
    # Declining profit margins trend
    if 'Year' in df.columns and 'Profit_Margin' in df.columns:
        yearly_margin = df.groupby('Year')['Profit_Margin'].mean()
        
        if len(yearly_margin) >= 2:
            margin_change = yearly_margin.iloc[-1] - yearly_margin.iloc[0]
            annual_decline = margin_change / len(yearly_margin)
            
            if annual_decline < -1.5:
                projected_loss = abs(annual_decline) * df['Sales'].sum() / 100 * 2
                threats.append({
                    'category': 'Profitability Erosion',
                    'title': 'Declining Profit Margin Trend',
                    'description': f"Profit margins declining by {abs(annual_decline):.1f}% annually - if trend continues, could lose ₹{projected_loss:,.0f} in profits over next 2 years",
                    'severity': 'High'
                })
    
    # Sales decline threat
    if 'Date' in df.columns:
        df_sorted = df.sort_values('Date')
        if len(df_sorted) >= 10:
            first_third = df_sorted.head(len(df_sorted) // 3)['Sales'].sum()
            last_third = df_sorted.tail(len(df_sorted) // 3)['Sales'].sum()
            
            if last_third < first_third * 0.85:
                decline_pct = (1 - last_third / first_third) * 100
                revenue_loss = first_third - last_third
                threats.append({
                    'category': 'Revenue Decline',
                    'title': 'Downward Sales Trajectory',
                    'description': f"Recent sales declined {decline_pct:.1f}% compared to earlier period - revenue loss of ₹{revenue_loss:,.0f} signals market share erosion or demand weakness",
                    'severity': 'High'
                })
    
    # Multiple loss-making products
    if 'Product' in df.columns:
        product_profit = df.groupby('Product').agg({
            'Profit': 'sum',
            'Sales': 'sum'
        }).reset_index()
        
        loss_products = product_profit[product_profit['Profit'] < 0]
        total_losses = abs(loss_products['Profit'].sum())
        
        if len(loss_products) > 0:
            loss_names = ", ".join(loss_products['Product'].head(3).tolist())
            if len(loss_products) > 3:
                loss_names += f" and {len(loss_products) - 3} more"
            
            threats.append({
                'category': 'Product Performance',
                'title': f"{len(loss_products)} Loss-Making Products Draining Profits",
                'description': f"{loss_names} generating combined losses of ₹{total_losses:,.0f} - continued underperformance erodes overall profitability",
                'severity': 'High' if total_losses > df['Profit'].sum() * 0.1 else 'Medium'
            })
    
    # High cost structure vulnerability
    avg_cost_ratio = df['Cost'].sum() / df['Sales'].sum() if df['Sales'].sum() > 0 else 0
    if avg_cost_ratio > 0.70:
        margin_at_risk = df['Sales'].sum() * (avg_cost_ratio - 0.70)
        threats.append({
            'category': 'Cost Structure',
            'title': 'High Cost Base Limits Flexibility',
            'description': f"Costs at {avg_cost_ratio*100:.1f}% of sales leave little buffer - any cost increases or price pressure would quickly eliminate remaining ₹{margin_at_risk:,.0f} profit cushion",
            'severity': 'High' if avg_cost_ratio > 0.80 else 'Medium'
        })
    
    # Competition based on margins
    if 'Profit_Margin' in df.columns:
        avg_margin = df['Profit_Margin'].mean()
        if avg_margin < 30:
            threats.append({
                'category': 'Competitive Pressure',
                'title': 'Thin Margins Signal Intense Competition',
                'description': f"Average margin of {avg_margin:.1f}% indicates commoditized market with limited pricing power - vulnerable to aggressive competitor discounting",
                'severity': 'Medium'
            })
    
    # Marketing efficiency declining
    if 'Marketing_Spend' in df.columns and 'Year' in df.columns:
        yearly_marketing = df.groupby('Year').agg({
            'Marketing_Spend': 'sum',
            'Sales': 'sum'
        })
        
        if len(yearly_marketing) >= 2:
            yearly_marketing['Efficiency'] = yearly_marketing['Sales'] / yearly_marketing['Marketing_Spend']
            efficiency_change = yearly_marketing['Efficiency'].pct_change().mean()
            
            if efficiency_change < -0.1:  # 10% decline
                threats.append({
                    'category': 'Marketing Efficiency',
                    'title': 'Declining Marketing Effectiveness',
                    'description': f"Marketing efficiency declining by {abs(efficiency_change)*100:.1f}% annually - rising customer acquisition costs and market saturation risks",
                    'severity': 'Medium'
                })
    
    # Add positive message if no weaknesses found
    if len(weaknesses) == 0:
        weaknesses.append({
            'category': 'Overall',
            'title': 'Strong Operational Performance',
            'metric': 'Overall Health',
            'value': 100.0,
            'description': 'Great news! No significant weaknesses detected in your current business operations. Your business is performing well across all metrics.',
            'severity': 'Low'
        })
    
    return {
        'strengths': strengths,
        'weaknesses': weaknesses,
        'opportunities': opportunities,
        'threats': threats,
        'summary': {
            'strength_count': len(strengths),
            'weakness_count': len(weaknesses),
            'opportunity_count': len(opportunities),
            'threat_count': len(threats)
        }
    }
