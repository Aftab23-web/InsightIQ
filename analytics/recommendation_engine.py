"""
Business Recommendation Engine
"""
import pandas as pd
import numpy as np


def generate_cost_optimization_recommendations(df, mistakes, kpis):
    """
    Generate recommendations for cost optimization
    """
    recommendations = []
    
    cost_ratio = kpis['revenue']['total_cost'] / kpis['revenue']['total_sales']
    
    # High cost ratio - only if actually high
    if cost_ratio > 0.70:
        potential_savings = kpis['revenue']['total_cost'] * 0.10
        target_ratio = 0.65
        target_savings = kpis['revenue']['total_sales'] * (cost_ratio - target_ratio)
        
        # Determine severity and specifics based on actual ratio
        if cost_ratio > 0.80:
            priority = 'Critical'
            urgency = 'immediate'
            target_reduction = 15
        elif cost_ratio > 0.75:
            priority = 'High'
            urgency = 'urgent'
            target_reduction = 12
        else:
            priority = 'High'
            urgency = 'important'
            target_reduction = 10
        
        # Find specific high-cost areas
        high_cost_details = []
        if 'Product' in df.columns:
            product_costs = df.groupby('Product')['Cost'].sum().sort_values(ascending=False)
            top_cost_product = product_costs.index[0]
            top_cost_amount = product_costs.iloc[0]
            high_cost_details.append(f"Focus on {top_cost_product} which accounts for ₹{top_cost_amount:,.0f} in costs")
        
        if 'Region' in df.columns:
            regional_cost_ratio = df.groupby('Region').agg({'Cost': 'sum', 'Sales': 'sum'})
            regional_cost_ratio['Ratio'] = regional_cost_ratio['Cost'] / regional_cost_ratio['Sales']
            worst_region = regional_cost_ratio['Ratio'].idxmax()
            if regional_cost_ratio.loc[worst_region, 'Ratio'] > cost_ratio:
                high_cost_details.append(f"Prioritize cost reduction in {worst_region} region")
        
        action_items = [
            f"Conduct {urgency} cost audit to identify {target_reduction}% reduction opportunities",
            f"Renegotiate supplier contracts - targeting ₹{potential_savings:,.0f} in savings"
        ] + high_cost_details + [
            f"Benchmark costs against industry standard of 60-65%",
            f"Implement cost tracking dashboard for real-time monitoring"
        ]
        
        recommendations.append({
            'priority': priority,
            'category': 'Cost Optimization',
            'title': f'Reduce Operating Cost Ratio from {cost_ratio*100:.1f}% to {target_ratio*100:.0f}%',
            'description': f"Current cost ratio of {cost_ratio*100:.1f}% significantly limits profitability - each 1% reduction adds ₹{kpis['revenue']['total_sales']*0.01:,.0f} to bottom line",
            'action_items': action_items,
            'estimated_impact': f"Achieving target {target_ratio*100:.0f}% cost ratio would add ₹{target_savings:,.0f} to annual profit",
            'implementation_effort': 'Moderate' if cost_ratio < 0.75 else 'Complex'
        })
    
    # High-cost products - only if they exist
    product_costs = df.groupby('Product').agg({
        'Cost': 'sum',
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    product_costs['Cost_Ratio'] = product_costs['Cost'] / product_costs['Sales']
    high_cost_products = product_costs[product_costs['Cost_Ratio'] > 0.75].sort_values('Cost', ascending=False)
    
    if len(high_cost_products) > 0:
        worst_product = high_cost_products.iloc[0]
        product_name = worst_product['Product']
        product_cost_ratio = worst_product['Cost_Ratio']
        product_cost = worst_product['Cost']
        product_sales = worst_product['Sales']
        
        # Calculate specific opportunities
        if product_cost_ratio > 0.90:
            priority = 'Critical'
            action = 'Discontinue or drastically restructure'
            potential_benefit = abs(worst_product['Profit'])  # Stop the bleeding
        elif product_cost_ratio > 0.85:
            priority = 'Critical'
            action = 'Emergency cost reduction required'
            potential_benefit = product_cost * 0.15
        else:
            priority = 'High'
            action = 'Optimize cost structure'
            potential_benefit = product_cost * 0.12
        
        product_list = ', '.join(high_cost_products['Product'].head(3).tolist())
        
        action_items = [
            f"{action} for {product_name} (cost ratio: {product_cost_ratio*100:.1f}%)",
            f"Analyze cost breakdown: ₹{product_cost:,.0f} cost vs ₹{product_sales:,.0f} sales",
            f"Evaluate alternative suppliers or materials for cost reduction",
            f"Consider price increase if quality justifies it"
        ]
        
        if len(high_cost_products) > 1:
            action_items.append(f"Also review {len(high_cost_products)-1} other high-cost products: {', '.join(high_cost_products['Product'].iloc[1:3].tolist())}")
        
        recommendations.append({
            'priority': priority,
            'category': 'Product Cost',
            'title': f'Fix {product_name} Cost Structure ({product_cost_ratio*100:.0f}% Cost Ratio)',
            'description': f"{product_name} costs ₹{product_cost:,.0f} to generate ₹{product_sales:,.0f} in sales - unsustainable economics",
            'action_items': action_items,
            'estimated_impact': f"Cost optimization could recover ₹{potential_benefit:,.0f} in profit",
            'implementation_effort': 'Moderate' if product_cost_ratio < 0.85 else 'Easy (discontinue)'
        })
    
    return recommendations


def generate_product_strategy_recommendations(df, mistakes, swot):
    """
    Generate comprehensive product-focused recommendations for ALL products
    """
    recommendations = []
    
    # Analyze all products comprehensively
    product_analysis = df.groupby('Product').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Cost': 'sum',
        'Profit_Margin': 'mean'
    }).reset_index()
    
    total_sales = df['Sales'].sum()
    product_analysis['Sales_Share'] = (product_analysis['Sales'] / total_sales * 100)
    product_analysis = product_analysis.sort_values('Profit', ascending=False)
    
    # 1. HIGH-MARGIN WINNERS - Scale up strategy
    high_performers = product_analysis[
        (product_analysis['Profit_Margin'] > 30) & 
        (product_analysis['Profit'] > 0)
    ].sort_values('Profit', ascending=False)
    
    if len(high_performers) > 0:
        for idx, product in high_performers.head(2).iterrows():
            product_name = product['Product']
            margin = product['Profit_Margin']
            current_profit = product['Profit']
            sales_share = product['Sales_Share']
            current_sales = product['Sales']
            
            # Calculate growth potential
            if sales_share < 20:
                target_share = min(sales_share + 10, 30)
                growth_potential = (target_share - sales_share) / 100 * total_sales * (margin / 100)
                priority = 'High'
            else:
                target_share = min(sales_share + 5, 40)
                growth_potential = (target_share - sales_share) / 100 * total_sales * (margin / 100)
                priority = 'Medium'
            
            action_items = [
                f"Increase {product_name} market share from {sales_share:.1f}% to {target_share:.0f}%",
                f"Invest 30-40% more in marketing for this {margin:.1f}% margin product",
                f"Create premium bundles or value-adds to justify pricing",
                f"Expand distribution channels targeting ₹{current_sales * 0.3:,.0f} additional sales",
                f"Train sales team on {product_name} features and upselling techniques"
            ]
            
            recommendations.append({
                'priority': priority,
                'category': 'Growth Strategy',
                'title': f"Scale {product_name} - High-Margin Winner ({margin:.1f}% margin)",
                'description': f"{product_name} generates ₹{current_profit:,.0f} profit with excellent {margin:.1f}% margin but only {sales_share:.1f}% market share - massive untapped potential",
                'action_items': action_items,
                'estimated_impact': f"Growing to {target_share:.0f}% share could add ₹{growth_potential:,.0f} in annual profit",
                'implementation_effort': 'Moderate'
            })
    
    # 2. UNDERPERFORMERS - Turnaround or exit strategy
    underperformers = product_analysis[
        (product_analysis['Profit'] < 0) |
        ((product_analysis['Profit_Margin'] < 15) & (product_analysis['Profit_Margin'] > 0))
    ].sort_values('Profit')
    
    if len(underperformers) > 0:
        for idx, product in underperformers.head(2).iterrows():
            product_name = product['Product']
            margin = product['Profit_Margin']
            profit = product['Profit']
            sales = product['Sales']
            cost = product['Cost']
            sales_share = product['Sales_Share']
            
            if profit < 0:
                # LOSS-MAKING - Exit strategy
                loss_amount = abs(profit)
                priority = 'Critical' if loss_amount > total_sales * 0.05 else 'High'
                
                action_items = [
                    f"Immediately discontinue {product_name} - losing ₹{loss_amount:,.0f} annually",
                    f"Phase out inventory within 60 days through clearance sales",
                    f"Redirect {sales_share:.1f}% market capacity to profitable products",
                    f"Analyze why {product_name} failed: pricing, positioning, or market fit",
                    f"Transfer customers to alternative profitable products"
                ]
                
                recommendations.append({
                    'priority': priority,
                    'category': 'Product Portfolio',
                    'title': f"Exit {product_name} - Bleeding ₹{loss_amount:,.0f} Annually",
                    'description': f"{product_name} has {margin:.1f}% margin, generating ₹{loss_amount:,.0f} in losses with {sales_share:.1f}% market share - immediate action required",
                    'action_items': action_items,
                    'estimated_impact': f"Stop ₹{loss_amount:,.0f} annual losses immediately - direct profit improvement",
                    'implementation_effort': 'Easy'
                })
            else:
                # LOW-MARGIN - Turnaround strategy
                target_margin = 25
                margin_gap = target_margin - margin
                improvement_potential = sales * (margin_gap / 100)
                priority = 'High' if margin < 10 else 'Medium'
                
                # Calculate specific improvements
                cost_reduction_target = cost * 0.10
                price_increase_potential = sales * 0.08
                
                action_items = [
                    f"Improve {product_name} margin from {margin:.1f}% to {target_margin:.0f}% target",
                    f"Reduce unit costs by 10% (₹{cost_reduction_target:,.0f} opportunity)",
                    f"Test 5-8% price increase - potential ₹{price_increase_potential:,.0f} additional revenue",
                    f"Reposition {product_name} with value-added features or services",
                    f"If improvements fail in 6 months, consider discontinuation"
                ]
                
                recommendations.append({
                    'priority': priority,
                    'category': 'Product Optimization',
                    'title': f"Turnaround {product_name} - Low {margin:.1f}% Margin",
                    'description': f"{product_name} generates only ₹{profit:,.0f} profit at {margin:.1f}% margin ({sales_share:.1f}% share) - significant improvement potential",
                    'action_items': action_items,
                    'estimated_impact': f"Achieving {target_margin:.0f}% margin adds ₹{improvement_potential:,.0f} annual profit, or exit to redirect resources",
                    'implementation_effort': 'Moderate'
                })
    
    # 3. MID-TIER PERFORMERS - Optimization strategy
    mid_performers = product_analysis[
        (product_analysis['Profit_Margin'] >= 15) & 
        (product_analysis['Profit_Margin'] <= 30) &
        (product_analysis['Profit'] > 0) &
        (~product_analysis['Product'].isin(high_performers['Product'] if len(high_performers) > 0 else []))
    ].sort_values('Sales', ascending=False)
    
    if len(mid_performers) > 0:
        for idx, product in mid_performers.head(2).iterrows():
            product_name = product['Product']
            margin = product['Profit_Margin']
            profit = product['Profit']
            sales = product['Sales']
            sales_share = product['Sales_Share']
            
            # Determine improvement strategy based on position
            target_margin = 30
            margin_improvement = (target_margin - margin) / 100 * sales
            volume_growth = sales * 0.20 * (margin / 100)
            
            action_items = [
                f"Optimize {product_name}: Currently {margin:.1f}% margin, {sales_share:.1f}% market share",
                f"Path 1 - Margin: Increase to {target_margin:.0f}% through cost reduction/pricing (₹{margin_improvement:,.0f})",
                f"Path 2 - Volume: Grow sales 20% through targeted marketing (₹{volume_growth:,.0f})",
                f"Path 3 - Bundle: Create packages with high-margin products",
                f"Analyze customer segments: Who buys {product_name} and what else they want"
            ]
            
            recommendations.append({
                'priority': 'Medium',
                'category': 'Product Optimization',
                'title': f"Optimize {product_name} - Solid Performer with Upside",
                'description': f"{product_name} is performing steadily with ₹{profit:,.0f} profit at {margin:.1f}% margin ({sales_share:.1f}% share) - multiple paths to enhancement",
                'action_items': action_items,
                'estimated_impact': f"Margin OR volume improvements could add ₹{max(margin_improvement, volume_growth):,.0f} annually",
                'implementation_effort': 'Moderate'
            })
    
    # 4. SMALL-SHARE PRODUCTS - Growth or consolidation
    small_share_products = product_analysis[
        (product_analysis['Sales_Share'] < 10) &
        (product_analysis['Profit'] > 0) &
        (~product_analysis['Product'].isin(high_performers['Product'] if len(high_performers) > 0 else []))
    ]
    
    if len(small_share_products) >= 2:
        total_small_profit = small_share_products['Profit'].sum()
        total_small_share = small_share_products['Sales_Share'].sum()
        avg_margin = small_share_products['Profit_Margin'].mean()
        product_names = ', '.join(small_share_products['Product'].head(3).tolist())
        
        if len(small_share_products) > 3:
            product_names += f" (+{len(small_share_products)-3} more)"
        
        # If margins are decent, grow; if poor, consolidate
        if avg_margin > 20:
            priority = 'Medium'
            strategy = 'Cross-selling and bundling'
            potential = total_small_profit * 1.5
            
            action_items = [
                f"Bundle small-share products ({product_names}) into value packages",
                f"Cross-sell: Customers buying main products should see these",
                f"Create \"discovery\" promotions for {len(small_share_products)} niche products",
                f"Target growing combined {total_small_share:.1f}% share to 15-18%",
                f"Track: Are these future stars or permanent niche products?"
            ]
        else:
            priority = 'Medium'
            strategy = 'Consolidate or discontinue'
            potential = total_small_profit * 0.5  # Savings from reduced SKU complexity
            
            action_items = [
                f"Review {len(small_share_products)} small-share products: {product_names}",
                f"Combined {total_small_share:.1f}% share, {avg_margin:.1f}% avg margin - complexity cost?",
                f"Eliminate bottom 50% of low-volume SKUs to reduce operational costs",
                f"Focus resources on top 3-5 core products with proven demand",
                f"Measure: Is product variety worth the inventory/management cost?"
            ]
        
        recommendations.append({
            'priority': priority,
            'category': 'Product Portfolio',
            'title': f"{strategy} for {len(small_share_products)} Small-Share Products",
            'description': f"{len(small_share_products)} products combine for {total_small_share:.1f}% market share and ₹{total_small_profit:,.0f} profit at {avg_margin:.1f}% avg margin",
            'action_items': action_items,
            'estimated_impact': f"{'Growing' if avg_margin > 20 else 'Streamlining'} portfolio could {'add' if avg_margin > 20 else 'save'} ₹{potential:,.0f} annually",
            'implementation_effort': 'Moderate'
        })
    
    return recommendations


def generate_regional_strategy_recommendations(df, mistakes):
    """
    Generate region-focused recommendations
    """
    recommendations = []
    
    # Poor-performing regions - specific actions
    poor_regions = [m for m in mistakes['all_mistakes'] if m.get('type') == 'Poor-Performing Region']
    
    if poor_regions:
        # Get detailed regional analysis
        regional_analysis = df.groupby('Region').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Profit_Margin': 'mean'
        }).reset_index().sort_values('Profit', ascending=False)
        
        best_region = regional_analysis.iloc[0]
        worst_region_info = poor_regions[0]
        worst_region_name = worst_region_info.get('region', '')
        
        worst_region_data = regional_analysis[regional_analysis['Region'] == worst_region_name]
        if len(worst_region_data) > 0:
            worst_margin = worst_region_data.iloc[0]['Profit_Margin']
            worst_profit = worst_region_data.iloc[0]['Profit']
            best_margin = best_region['Profit_Margin']
            
            margin_gap = best_margin - worst_margin
            sales_in_worst = worst_region_data.iloc[0]['Sales']
            improvement_potential = sales_in_worst * (margin_gap / 100)
            
            action_items = [
                f"Analyze what makes {best_region['Region']} successful ({best_margin:.1f}% margin vs {worst_margin:.1f}% in {worst_region_name})",
                f"Replicate {best_region['Region']}'s pricing, product mix, and go-to-market strategy",
                f"Investigate local competition and market dynamics in {worst_region_name}",
                f"Target {margin_gap/2:.1f}% margin improvement in next 6 months"
            ]
            
            if len(poor_regions) > 1:
                other_regions = ', '.join([m.get('region', '') for m in poor_regions[1:3]])
                action_items.append(f"Apply learnings to {len(poor_regions)-1} other underperforming regions: {other_regions}")
            
            recommendations.append({
                'priority': 'High',
                'category': 'Regional Strategy',
                'title': f'Fix {worst_region_name}: {margin_gap:.1f}% Below Top Region',
                'description': f"{worst_region_name} margin of {worst_margin:.1f}% significantly trails {best_region['Region']}'s {best_margin:.1f}% - ₹{improvement_potential:,.0f} profit opportunity",
                'action_items': action_items,
                'estimated_impact': f"Closing half the gap would add ₹{improvement_potential/2:,.0f} in profit from {worst_region_name} alone",
                'implementation_effort': 'Moderate'
            })
    
    # Regional concentration risk - only if actually concentrated
    regional_sales = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
    top_region_share = regional_sales.iloc[0] / regional_sales.sum()
    top_region_name = regional_sales.index[0]
    
    if top_region_share > 0.50:  # Only if actually >50%
        second_region = regional_sales.index[1] if len(regional_sales) > 1 else 'other regions'
        second_sales = regional_sales.iloc[1] if len(regional_sales) > 1 else 0
        sales_gap = regional_sales.iloc[0] - second_sales
        
        priority = 'High' if top_region_share > 0.60 else 'Medium'
        
        action_items = [
            f"Reduce dependency on {top_region_name} (currently {top_region_share*100:.0f}% of total sales)",
            f"Invest in expanding {second_region} to close ₹{sales_gap:,.0f} gap",
            f"Develop market entry strategy for underserved regions",
            f"Target: Reduce {top_region_name} share to <45% within 18 months"
        ]
        
        recommendations.append({
            'priority': priority,
            'category': 'Risk Management',
            'title': f'Diversify Beyond {top_region_name} ({top_region_share*100:.0f}% Concentration)',
            'description': f"Over-reliance on {top_region_name} ({top_region_share*100:.0f}% of sales, ₹{regional_sales.iloc[0]:,.0f}) creates vulnerability to regional disruption",
            'action_items': action_items,
            'estimated_impact': f"Balanced regional mix reduces risk and unlocks ₹{sales_gap*0.3:,.0f} growth potential",
            'implementation_effort': 'Complex'
        })
    
    return recommendations


def generate_marketing_recommendations(df, kpis):
    """
    Generate marketing-focused recommendations
    """
    recommendations = []
    
    # Low marketing ROI - only if actually low
    marketing_roi = kpis['efficiency']['marketing_roi']
    total_marketing = kpis['revenue']['total_marketing_spend']
    total_sales = kpis['revenue']['total_sales']
    
    if marketing_roi < 300:  # Less than 3x return (200% ROI)
        current_return = marketing_roi / 100
        target_return = 4.0  # Target 4x return
        
        if marketing_roi < 100:  # Less than breaking even
            priority = 'Critical'
            description = f"Marketing is losing money: spending ₹{total_marketing:,.0f} to generate ₹{total_marketing * (1 + marketing_roi/100):,.0f} - {marketing_roi:.0f}% return is unsustainable"
            action_focus = 'Emergency restructuring'
        elif marketing_roi < 200:
            priority = 'High'
            description = f"Marketing ROI of {marketing_roi:.0f}% (₹{current_return:.1f}x return) is below break-even threshold - barely covering costs"
            action_focus = 'Immediate optimization'
        else:
            priority = 'Medium'
            description = f"Marketing generating {marketing_roi:.0f}% ROI (₹{current_return:.1f}x) - opportunity to reach industry benchmark of 300-400%"
            action_focus = 'Strategic improvement'
        
        # Calculate specific opportunities
        if 'Product' in df.columns and 'Marketing_Spend' in df.columns:
            product_marketing = df.groupby('Product').agg({
                'Marketing_Spend': 'sum',
                'Sales': 'sum',
                'Profit': 'sum'
            }).reset_index()
            product_marketing['ROI'] = ((product_marketing['Sales'] - product_marketing['Marketing_Spend']) / product_marketing['Marketing_Spend'] * 100)
            
            best_product = product_marketing.loc[product_marketing['ROI'].idxmax()]
            worst_product = product_marketing.loc[product_marketing['ROI'].idxmin()]
            
            action_items = [
                f"{action_focus}: Current {marketing_roi:.0f}% ROI means ₹{total_marketing:,.0f} spend generates only ₹{total_marketing * marketing_roi / 100:,.0f} profit",
                f"Shift budget from {worst_product['Product']} ({worst_product['ROI']:.0f}% ROI) to {best_product['Product']} ({best_product['ROI']:.0f}% ROI)",
                f"Implement attribution tracking to identify high-performing channels",
                f"Target {target_return}x return (₹{total_marketing * target_return:,.0f} from ₹{total_marketing:,.0f} spend)"
            ]
        else:
            action_items = [
                f"{action_focus}: Analyze which marketing channels drive actual sales",
                f"Cut spending on low-ROI activities",
                f"Implement data-driven marketing attribution",
                f"Target {target_return}x return within 6 months"
            ]
        
        improvement_value = total_marketing * (target_return - current_return)
        
        recommendations.append({
            'priority': priority,
            'category': 'Marketing Optimization',
            'title': f'Boost Marketing ROI from {marketing_roi:.0f}% to {(target_return-1)*100:.0f}%',
            'description': description,
            'action_items': action_items,
            'estimated_impact': f"Achieving {target_return}x return would add ₹{improvement_value:,.0f} in profit from same marketing budget",
            'implementation_effort': 'Moderate'
        })
    
    # Seasonal marketing - only if strong pattern exists
    if 'Month' in df.columns:
        monthly_sales = df.groupby('Month').agg({
            'Sales': 'mean',
            'Profit': 'mean'
        })
        
        if len(monthly_sales) >= 6:
            peak_month = monthly_sales['Sales'].idxmax()
            low_month = monthly_sales['Sales'].idxmin()
            peak_sales = monthly_sales.loc[peak_month, 'Sales']
            low_sales = monthly_sales.loc[low_month, 'Sales']
            
            # Only create recommendation if there's significant seasonality
            if peak_sales > low_sales * 1.4:  # At least 40% difference
                seasonality_ratio = peak_sales / low_sales
                avg_sales = monthly_sales['Sales'].mean()
                uplift_potential = (peak_sales - low_sales) * 0.25  # Assume can boost low month by 25% of gap
                
                # Get month names
                month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun',
                             7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
                peak_name = month_names.get(peak_month, str(peak_month))
                low_name = month_names.get(low_month, str(low_month))
                
                action_items = [
                    f"Boost {low_name} performance - currently only ₹{low_sales:,.0f} vs {peak_name}'s ₹{peak_sales:,.0f} ({seasonality_ratio:.1f}x difference)",
                    f"Launch targeted promotions in {low_name} to capture ₹{uplift_potential:,.0f} additional sales",
                    f"Prepare inventory and marketing for {peak_name} peak season",
                    f"Smooth demand curve to reduce {(seasonality_ratio-1)*100:.0f}% volatility"
                ]
                
                # Identify other low months
                below_avg_months = monthly_sales[monthly_sales['Sales'] < avg_sales * 0.85]
                if len(below_avg_months) > 1:
                    other_low = [month_names.get(m, str(m)) for m in below_avg_months.index if m != low_month]
                    if other_low:
                        action_items.append(f"Also address {', '.join(other_low[:2])} underperformance")
                
                recommendations.append({
                    'priority': 'Medium',
                    'category': 'Seasonal Planning',
                    'title': f'Capture {low_name} Opportunity: {seasonality_ratio:.1f}x Seasonal Gap',
                    'description': f"{peak_name} generates ₹{peak_sales:,.0f} while {low_name} only ₹{low_sales:,.0f} - strategic campaigns could boost off-peak performance",
                    'action_items': action_items,
                    'estimated_impact': f"Boosting {low_name} by 25% of gap = ₹{uplift_potential:,.0f} monthly recurring gain",
                    'implementation_effort': 'Easy'
                })
    
    return recommendations


def generate_growth_recommendations(df, kpis):
    """
    Generate growth-focused recommendations
    """
    recommendations = []
    
    # Growth strategy - only if growth is actually low or negative
    sales_growth = kpis['growth']['sales_growth']
    total_sales = kpis['revenue']['total_sales']
    
    if sales_growth < 10:  # Below 10% growth
        if sales_growth < 0:
            priority = 'Critical'
            situation = 'declining'
            urgency = 'Immediate turnaround required'
            target_growth = 5
        elif sales_growth < 3:
            priority = 'Critical'
            situation = 'stagnant'
            urgency = 'Urgent growth acceleration needed'
            target_growth = 12
        else:
            priority = 'High'
            situation = 'below target'
            urgency = 'Growth enhancement recommended'
            target_growth = 15
        
        growth_gap = target_growth - sales_growth
        revenue_opportunity = total_sales * (growth_gap / 100)
        
        # Identify specific growth opportunities from data
        action_items = [
            f"{urgency}: Current {sales_growth:.1f}% growth is {situation}"
        ]
        
        # Find underutilized products
        if 'Product' in df.columns:
            product_sales = df.groupby('Product').agg({
                'Sales': 'sum',
                'Profit_Margin': 'mean'
            }).reset_index()
            total_prod_sales = product_sales['Sales'].sum()
            product_sales['Share'] = product_sales['Sales'] / total_prod_sales * 100
            
            high_margin_low_share = product_sales[
                (product_sales['Profit_Margin'] > product_sales['Profit_Margin'].mean()) &
                (product_sales['Share'] < 20)
            ].sort_values('Profit_Margin', ascending=False)
            
            if len(high_margin_low_share) > 0:
                top_opp = high_margin_low_share.iloc[0]
                action_items.append(f"Expand {top_opp['Product']} (high {top_opp['Profit_Margin']:.1f}% margin, only {top_opp['Share']:.1f}% share)")
        
        # Check for regional expansion opportunities
        if 'Region' in df.columns:
            regional_sales = df.groupby('Region')['Sales'].sum()
            if len(regional_sales) > 1:
                underserved = regional_sales[regional_sales < regional_sales.mean() * 0.7]
                if len(underserved) > 0:
                    action_items.append(f"Develop {', '.join(underserved.index.tolist()[:2])} regions (currently underserved)")
        
        action_items.extend([
            f"Target {target_growth}% growth rate through focused initiatives",
            f"Invest in customer acquisition - aim for ₹{revenue_opportunity:,.0f} additional revenue"
        ])
        
        recommendations.append({
            'priority': priority,
            'category': 'Growth Acceleration',
            'title': f'Accelerate Growth from {sales_growth:.1f}% to {target_growth}%',
            'description': f"Current growth rate of {sales_growth:.1f}% is insufficient - business is {situation} and needs {growth_gap:.1f}% acceleration",
            'action_items': action_items,
            'estimated_impact': f"Achieving {target_growth}% growth adds ₹{revenue_opportunity:,.0f} in annual revenue",
            'implementation_effort': 'Complex' if sales_growth < 0 else 'Moderate'
        })
    
    # Customer retention - only if there's evidence of customer churn or opportunity
    if 'Date' in df.columns and len(df) > 30:
        # Analyze if sales per transaction are declining (proxy for customer retention)
        df_sorted = df.sort_values('Date')
        df_sorted['Month'] = pd.to_datetime(df_sorted['Date']).dt.to_period('M')
        
        monthly_metrics = df_sorted.groupby('Month').agg({
            'Sales': ['sum', 'count'],
            'Profit': 'sum'
        })
        
        monthly_metrics.columns = ['Total_Sales', 'Transaction_Count', 'Total_Profit']
        monthly_metrics['Avg_Transaction'] = monthly_metrics['Total_Sales'] / monthly_metrics['Transaction_Count']
        
        if len(monthly_metrics) >= 3:
            recent_avg = monthly_metrics['Avg_Transaction'].tail(3).mean()
            earlier_avg = monthly_metrics['Avg_Transaction'].head(3).mean()
            
            # Only recommend if there's evidence of decline or significant opportunity
            if recent_avg < earlier_avg * 0.90 or earlier_avg > recent_avg * 1.2:
                transaction_change = (recent_avg / earlier_avg - 1) * 100
                
                if transaction_change < -10:
                    priority = 'High'
                    situation = f"Average transaction value declined {abs(transaction_change):.1f}% - indicating customer churn or reduced engagement"
                    retention_value = (earlier_avg - recent_avg) * monthly_metrics['Transaction_Count'].mean() * 12
                else:
                    priority = 'Medium'
                    situation = f"Opportunity to increase repeat business and average transaction value"
                    retention_value = total_sales * 0.20  # Assume 20% improvement potential
                
                action_items = [
                    f"Analyze customer behavior: average transaction ₹{recent_avg:,.0f} vs previous ₹{earlier_avg:,.0f}",
                    f"Implement loyalty program to boost repeat purchase rate",
                    f"Create personalized follow-up campaigns for existing customers",
                    f"Offer volume discounts or subscription models to lock in customers",
                    f"Target 20-25% improvement in customer lifetime value"
                ]
                
                recommendations.append({
                    'priority': priority,
                    'category': 'Customer Retention',
                    'title': f'Build Customer Loyalty Program - ₹{retention_value:,.0f} Opportunity',
                    'description': situation,
                    'action_items': action_items,
                    'estimated_impact': f"Improving retention could add ₹{retention_value:,.0f} in annual recurring revenue",
                    'implementation_effort': 'Moderate'
                })
    
    return recommendations


def generate_forecast_recovery_recommendations(df, forecast_df, metric_name, risk_assessment):
    """
    Generate actionable recommendations to overcome predicted losses in forecasts
    based on historical company data patterns
    """
    recommendations = []
    
    # Analyze forecast trend
    trend_change = risk_assessment.get('trend_change_pct', 0)
    avg_uncertainty = risk_assessment.get('avg_uncertainty', 0)
    risk_level = risk_assessment.get('risk_level', 'Medium')
    
    # Determine if we have a declining forecast
    is_declining = trend_change < -5
    is_severe_decline = trend_change < -15
    
    # Analyze historical data for recovery opportunities
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    total_cost = df['Cost'].sum()
    avg_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    cost_ratio = (total_cost / total_sales) if total_sales > 0 else 0
    
    # Calculate recovery potential
    predicted_value = forecast_df.iloc[0].get('predicted_sales', forecast_df.iloc[0].get('predicted_profit', 0))
    
    if is_declining or is_severe_decline:
        # RECOMMENDATION 1: Address declining trend with multi-pronged approach
        priority = 'Critical' if is_severe_decline else 'High'
        
        # Identify top performing products/regions for scaling
        top_products = df.groupby('Product').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Profit_Margin': 'mean'
        }).sort_values('Profit', ascending=False)
        
        best_product = top_products.index[0]
        best_product_profit = top_products.iloc[0]['Profit']
        best_product_margin = top_products.iloc[0]['Profit_Margin']
        
        # Regional analysis
        if 'Region' in df.columns:
            regional_perf = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
            top_region = regional_perf.index[0]
            region_sales = regional_perf.iloc[0]
        else:
            top_region = None
        
        # Calculate specific recovery targets
        recovery_needed = abs(trend_change) / 100 * predicted_value
        
        action_items = [
            f"**IMMEDIATE:** Scale up {best_product} (currently {best_product_margin:.1f}% margin) - could add ₹{best_product_profit * 0.2:,.0f} if increased 20%",
            f"**URGENT:** Reduce costs from {cost_ratio*100:.1f}% to 65% - would save ₹{total_sales * (cost_ratio - 0.65):,.0f} annually"
        ]
        
        if top_region:
            action_items.append(f"**EXPAND:** Replicate {top_region} strategy (₹{region_sales:,.0f} sales) to underperforming regions")
        
        # Add product-specific recovery actions
        low_performers = top_products[top_products['Profit'] < 0]
        if len(low_performers) > 0:
            loss_amount = abs(low_performers['Profit'].sum())
            action_items.append(f"**OPTIMIZE:** Fix or discontinue {len(low_performers)} loss-making products - recover ₹{loss_amount:,.0f}")
        
        # Marketing and pricing actions
        action_items.extend([
            f"**PRICING:** Test 5-10% price increase on top 3 products - potential ₹{top_products.head(3)['Sales'].sum() * 0.075:,.0f} gain",
            f"**MARKETING:** Launch targeted campaigns in Q1-Q2 (historically strongest periods)",
            f"**RETENTION:** Implement customer retention program - reducing churn by 10% adds ₹{total_sales * 0.10:,.0f}"
        ])
        
        recommendations.append({
            'priority': priority,
            'category': 'Forecast Recovery',
            'title': f'Reverse {abs(trend_change):.1f}% Predicted Decline in {metric_name}',
            'description': f"Forecast shows {abs(trend_change):.1f}% decline ({risk_level} risk). Based on your data, {best_product} and cost optimization are your fastest paths to recovery.",
            'action_items': action_items,
            'estimated_impact': f"Combined actions could recover ₹{recovery_needed:,.0f}+ and reverse the downward trend",
            'implementation_effort': 'Moderate - requires coordination across sales, operations, and marketing',
            'timeline': '60-90 days for measurable results',
            'success_metrics': [
                f'Achieve {abs(trend_change/2):.1f}% improvement within 2 months',
                f'Reduce cost ratio to 65% or below',
                f'Increase {best_product} sales by 15-20%',
                'Return to positive growth trajectory by Q2'
            ]
        })
        
        # RECOMMENDATION 2: Product Portfolio Optimization
        if len(low_performers) > 0 or len(top_products) > 3:
            product_action_items = []
            
            # Top performers to scale
            for i, (product, data) in enumerate(top_products.head(3).iterrows()):
                product_action_items.append(
                    f"**SCALE:** {product} - invest ₹{data['Sales'] * 0.1:,.0f} to capture 15% more market share"
                )
            
            # Underperformers to fix
            bottom_products = top_products[top_products['Profit_Margin'] < 20].sort_values('Sales', ascending=False)
            if len(bottom_products) > 0:
                for product, data in bottom_products.head(2).iterrows():
                    if data['Profit'] > 0:
                        product_action_items.append(
                            f"**IMPROVE:** {product} margin from {data['Profit_Margin']:.1f}% to 25%+ through cost reduction"
                        )
            
            # Loss makers to eliminate
            if len(low_performers) > 0:
                worst_product = low_performers.iloc[0]
                product_action_items.append(
                    f"**DISCONTINUE:** {worst_product.name} (losing ₹{abs(worst_product['Profit']):,.0f}) - reallocate resources"
                )
            
            total_recovery = best_product_profit * 0.2 + abs(low_performers['Profit'].sum()) if len(low_performers) > 0 else best_product_profit * 0.2
            
            recommendations.append({
                'priority': 'High',
                'category': 'Product Strategy',
                'title': 'Optimize Product Portfolio to Counter Forecast Decline',
                'description': f"Focus resources on proven winners ({top_products.head(3).index.tolist()}) while eliminating drag from underperformers",
                'action_items': product_action_items,
                'estimated_impact': f"₹{total_recovery:,.0f} profit improvement through portfolio optimization",
                'implementation_effort': 'Easy to Moderate',
                'timeline': '30-60 days'
            })
    
    # RECOMMENDATION 3: Risk Mitigation (for high uncertainty)
    if avg_uncertainty > 20:
        risk_actions = [
            f"**DIVERSIFY:** Reduce dependency on single products/regions - current concentration creates {avg_uncertainty:.1f}% uncertainty",
            f"**HEDGE:** Build {avg_uncertainty/2:.0f}% cash reserve to buffer against volatility",
            "**MONITOR:** Implement weekly KPI tracking (sales, costs, margins) for early warning",
            "**AGILITY:** Create contingency plans for best/worst case scenarios"
        ]
        
        # Add specific diversification opportunities
        if 'Region' in df.columns:
            regional_concentration = df.groupby('Region')['Sales'].sum()
            top_region_pct = (regional_concentration.max() / regional_concentration.sum() * 100)
            if top_region_pct > 40:
                risk_actions.append(f"**EXPAND:** {regional_concentration.idxmax()} represents {top_region_pct:.0f}% of sales - expand to other regions")
        
        recommendations.append({
            'priority': 'High',
            'category': 'Risk Management',
            'title': f'Reduce Forecast Uncertainty from {avg_uncertainty:.1f}%',
            'description': f"High uncertainty ({avg_uncertainty:.1f}%) indicates need for diversification and risk management",
            'action_items': risk_actions,
            'estimated_impact': "Improved predictability and resilience to market changes",
            'implementation_effort': 'Moderate',
            'timeline': '90 days for measurable uncertainty reduction'
        })
    
    # RECOMMENDATION 4: Cost Efficiency for Margin Protection
    if cost_ratio > 0.70:
        cost_savings_potential = total_sales * (cost_ratio - 0.65)
        
        # Identify high-cost areas
        product_costs = df.groupby('Product').agg({
            'Cost': 'sum',
            'Sales': 'sum'
        })
        product_costs['Cost_Ratio'] = product_costs['Cost'] / product_costs['Sales']
        high_cost_products = product_costs[product_costs['Cost_Ratio'] > 0.75].sort_values('Cost', ascending=False)
        
        cost_actions = [
            f"**TARGET:** Reduce overall cost ratio from {cost_ratio*100:.1f}% to 65% over 90 days",
            f"**NEGOTIATE:** Renegotiate supplier contracts - target 8-12% cost reduction (₹{total_cost * 0.1:,.0f})"
        ]
        
        if len(high_cost_products) > 0:
            for product, data in high_cost_products.head(2).iterrows():
                cost_actions.append(
                    f"**FIX:** {product} has {data['Cost_Ratio']*100:.0f}% cost ratio - find alternative suppliers or adjust pricing"
                )
        
        cost_actions.extend([
            "**AUTOMATE:** Identify manual processes for automation - reduce labor costs 10-15%",
            f"**TRACK:** Implement daily cost monitoring dashboard for all major expense categories"
        ])
        
        recommendations.append({
            'priority': 'Critical' if cost_ratio > 0.75 else 'High',
            'category': 'Cost Optimization',
            'title': f'Urgent Cost Reduction to Protect Margins Against Decline',
            'description': f"With {metric_name} forecasted to decline, reducing costs from {cost_ratio*100:.1f}% to 65% is critical for survival",
            'action_items': cost_actions,
            'estimated_impact': f"₹{cost_savings_potential:,.0f} annual savings - converts directly to profit",
            'implementation_effort': 'Moderate',
            'timeline': '90 days',
            'success_metrics': [
                'Achieve 65% cost ratio within 3 months',
                f'Save ₹{cost_savings_potential/12:,.0f} per month',
                'Improve gross margin by 5-10 percentage points'
            ]
        })
    
    return recommendations


def generate_all_recommendations(df, mistakes, kpis, swot):
    """
    Generate comprehensive prioritized recommendations
    """
    all_recommendations = []
    
    # Collect recommendations from all categories
    all_recommendations.extend(generate_cost_optimization_recommendations(df, mistakes, kpis))
    all_recommendations.extend(generate_product_strategy_recommendations(df, mistakes, swot))
    all_recommendations.extend(generate_regional_strategy_recommendations(df, mistakes))
    all_recommendations.extend(generate_marketing_recommendations(df, kpis))
    all_recommendations.extend(generate_growth_recommendations(df, kpis))
    
    # Sort by priority
    priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    all_recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'Low'), 3))
    
    # Generate executive summary
    critical_count = len([r for r in all_recommendations if r['priority'] == 'Critical'])
    high_count = len([r for r in all_recommendations if r['priority'] == 'High'])
    
    summary = {
        'total_recommendations': len(all_recommendations),
        'critical': critical_count,
        'high': high_count,
        'medium': len([r for r in all_recommendations if r['priority'] == 'Medium']),
        'low': len([r for r in all_recommendations if r['priority'] == 'Low']),
        'top_priority': all_recommendations[0] if all_recommendations else None
    }
    
    return {
        'recommendations': all_recommendations,
        'summary': summary,
        'by_category': {
            'cost_optimization': [r for r in all_recommendations if r['category'] in ['Cost Optimization', 'Product Cost']],
            'product_strategy': [r for r in all_recommendations if r['category'] in ['Product Portfolio', 'Growth Strategy']],
            'regional_strategy': [r for r in all_recommendations if r['category'] in ['Regional Strategy', 'Risk Management']],
            'marketing': [r for r in all_recommendations if r['category'] in ['Marketing Optimization', 'Seasonal Planning']],
            'growth': [r for r in all_recommendations if r['category'] in ['Growth Acceleration', 'Customer Retention']]
        }
    }
