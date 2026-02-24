"""
What-If Scenario Analysis Module
"""
import pandas as pd
import numpy as np


def simulate_marketing_change(df, change_percent, effectiveness=0.4):
    """
    Simulate impact of marketing spend change
    effectiveness: how much each 10% marketing change affects sales (default 0.4 = 4% sales impact per 10% marketing)
    """
    # Calculate current metrics
    current_marketing = df['Marketing_Spend'].sum()
    current_sales = df['Sales'].sum()
    current_profit = df['Profit'].sum()
    current_roi = (current_sales / current_marketing) if current_marketing > 0 else 0
    
    # Simulate new marketing spend
    new_marketing = current_marketing * (1 + change_percent / 100)
    marketing_delta = new_marketing - current_marketing
    
    # Estimate sales impact based on user-defined effectiveness
    if change_percent > 0:
        sales_multiplier = 1 + (change_percent * effectiveness / 100)
    else:
        sales_multiplier = 1 + (change_percent * (effectiveness * 0.75) / 100)  # Less effective when reducing
    
    new_sales = current_sales * sales_multiplier
    sales_delta = new_sales - current_sales
    
    # Profit impact (sales increase - additional marketing cost)
    current_margin = (current_profit / current_sales) if current_sales > 0 else 0
    profit_from_new_sales = sales_delta * current_margin
    new_profit = current_profit + profit_from_new_sales - marketing_delta
    profit_delta = new_profit - current_profit
    
    direction = "Increase" if change_percent > 0 else "Decrease"
    
    return {
        'scenario': f"{abs(change_percent)}% Marketing Spend {direction}",
        'current': {
            'marketing_spend': float(current_marketing),
            'sales': float(current_sales),
            'profit': float(current_profit),
            'roi': float(current_roi)
        },
        'projected': {
            'marketing_spend': float(new_marketing),
            'sales': float(new_sales),
            'profit': float(new_profit),
            'roi': float(new_sales / new_marketing) if new_marketing > 0 else 0
        },
        'impact': {
            'marketing_delta': float(marketing_delta),
            'sales_delta': float(sales_delta),
            'profit_delta': float(profit_delta),
            'sales_change_pct': float((new_sales / current_sales - 1) * 100) if current_sales > 0 else 0,
            'profit_change_pct': float((new_profit / current_profit - 1) * 100) if current_profit > 0 else 0
        },
        'recommendation': 'Recommended' if profit_delta > 0 else 'Not Recommended'
    }


def simulate_cost_reduction(df, reduction_percent):
    """
    Simulate impact of cost reduction
    """
    current_cost = df['Cost'].sum()
    current_sales = df['Sales'].sum()
    current_profit = df['Profit'].sum()
    
    # New costs
    new_cost = current_cost * (1 - reduction_percent / 100)
    cost_savings = current_cost - new_cost
    
    # Profit impact (direct benefit from cost reduction)
    new_profit = current_profit + cost_savings
    
    # New profit margin
    current_margin = (current_profit / current_sales * 100) if current_sales > 0 else 0
    new_margin = (new_profit / current_sales * 100) if current_sales > 0 else 0
    
    return {
        'scenario': f"{reduction_percent}% Cost Reduction",
        'current': {
            'cost': float(current_cost),
            'sales': float(current_sales),
            'profit': float(current_profit),
            'profit_margin': float(current_margin)
        },
        'projected': {
            'cost': float(new_cost),
            'sales': float(current_sales),  # Sales remain same
            'profit': float(new_profit),
            'profit_margin': float(new_margin)
        },
        'impact': {
            'cost_savings': float(cost_savings),
            'profit_increase': float(cost_savings),
            'margin_improvement': float(new_margin - current_margin),
            'profit_change_pct': float((new_profit / current_profit - 1) * 100) if current_profit > 0 else 0
        },
        'recommendation': 'Highly Recommended - Direct profit improvement'
    }


def simulate_product_removal(df, product_name):
    """
    Simulate impact of removing a product
    """
    # Current metrics
    current_sales = df['Sales'].sum()
    current_profit = df['Profit'].sum()
    current_cost = df['Cost'].sum()
    
    # Metrics with product removed
    df_without = df[df['Product'] != product_name]
    new_sales = df_without['Sales'].sum()
    new_profit = df_without['Profit'].sum()
    new_cost = df_without['Cost'].sum()
    
    # Product-specific metrics
    product_data = df[df['Product'] == product_name]
    product_sales = product_data['Sales'].sum()
    product_profit = product_data['Profit'].sum()
    product_cost = product_data['Cost'].sum()
    
    return {
        'scenario': f"Remove Product: {product_name}",
        'product_metrics': {
            'sales': float(product_sales),
            'profit': float(product_profit),
            'cost': float(product_cost),
            'profit_margin': float(product_profit / product_sales * 100) if product_sales > 0 else 0
        },
        'current': {
            'sales': float(current_sales),
            'profit': float(current_profit),
            'cost': float(current_cost)
        },
        'projected': {
            'sales': float(new_sales),
            'profit': float(new_profit),
            'cost': float(new_cost)
        },
        'impact': {
            'sales_loss': float(current_sales - new_sales),
            'profit_change': float(new_profit - current_profit),
            'cost_savings': float(current_cost - new_cost),
            'profit_change_pct': float((new_profit / current_profit - 1) * 100) if current_profit > 0 else 0
        },
        'recommendation': 'Recommended - Remove loss-making product' if product_profit < 0 else 'Not Recommended - Product is profitable'
    }


def simulate_price_increase(df, price_increase_percent, demand_elasticity=-0.5):
    """
    Simulate impact of price increase
    demand_elasticity: % change in quantity for 1% change in price (typically negative)
    """
    current_sales = df['Sales'].sum()
    current_cost = df['Cost'].sum()
    current_profit = df['Profit'].sum()
    
    # New price and quantity
    new_price_multiplier = 1 + (price_increase_percent / 100)
    quantity_change_pct = price_increase_percent * demand_elasticity
    new_quantity_multiplier = 1 + (quantity_change_pct / 100)
    
    # New sales revenue
    new_sales = current_sales * new_price_multiplier * new_quantity_multiplier
    
    # New costs (proportional to quantity)
    new_cost = current_cost * new_quantity_multiplier
    
    # New profit
    new_profit = new_sales - new_cost
    
    return {
        'scenario': f"{price_increase_percent}% Price Increase",
        'assumptions': {
            'demand_elasticity': demand_elasticity,
            'expected_volume_change': float(quantity_change_pct)
        },
        'current': {
            'sales': float(current_sales),
            'cost': float(current_cost),
            'profit': float(current_profit)
        },
        'projected': {
            'sales': float(new_sales),
            'cost': float(new_cost),
            'profit': float(new_profit)
        },
        'impact': {
            'sales_change': float(new_sales - current_sales),
            'profit_change': float(new_profit - current_profit),
            'profit_change_pct': float((new_profit / current_profit - 1) * 100) if current_profit > 0 else 0
        },
        'recommendation': 'Recommended' if new_profit > current_profit else 'Not Recommended'
    }


def run_scenario_analysis(df, scenarios=None):
    """
    Run multiple what-if scenarios
    """
    if scenarios is None:
        # Default scenarios
        scenarios = [
            {'type': 'marketing', 'params': {'change_percent': 20}},
            {'type': 'marketing', 'params': {'change_percent': -20}},
            {'type': 'cost_reduction', 'params': {'reduction_percent': 10}},
            {'type': 'cost_reduction', 'params': {'reduction_percent': 15}},
            {'type': 'price_increase', 'params': {'price_increase_percent': 5}},
            {'type': 'price_increase', 'params': {'price_increase_percent': 10}}
        ]
    
    results = []
    
    for scenario in scenarios:
        scenario_type = scenario['type']
        params = scenario['params']
        
        if scenario_type == 'marketing':
            result = simulate_marketing_change(df, **params)
        elif scenario_type == 'cost_reduction':
            result = simulate_cost_reduction(df, **params)
        elif scenario_type == 'price_increase':
            result = simulate_price_increase(df, **params)
        elif scenario_type == 'product_removal' and 'product_name' in params:
            result = simulate_product_removal(df, **params)
        else:
            continue
        
        results.append(result)
    
    # Rank scenarios by profit impact
    results.sort(key=lambda x: x['impact'].get('profit_change', 0), reverse=True)
    
    return {
        'scenarios': results,
        'best_scenario': results[0] if results else None,
        'summary': {
            'total_scenarios': len(results),
            'positive_impact': len([r for r in results if r['impact'].get('profit_change', 0) > 0])
        }
    }


def simulate_sales_volume_change(df, change_percent):
    """
    Simulate direct sales volume change (without price change)
    This affects both sales revenue and costs proportionally
    """
    current_sales = df['Sales'].sum()
    current_cost = df['Cost'].sum()
    current_profit = df['Profit'].sum()
    current_margin = (current_profit / current_sales * 100) if current_sales > 0 else 0
    
    # Volume multiplier
    volume_multiplier = 1 + (change_percent / 100)
    
    # New sales (more volume = more revenue)
    new_sales = current_sales * volume_multiplier
    
    # New costs (more volume = proportionally more cost)
    new_cost = current_cost * volume_multiplier
    
    # New profit
    new_profit = new_sales - new_cost
    
    direction = "Increase" if change_percent > 0 else "Decrease"
    
    return {
        'scenario': f"{abs(change_percent)}% Sales Volume {direction}",
        'current': {
            'sales': float(current_sales),
            'cost': float(current_cost),
            'profit': float(current_profit),
            'margin': float(current_margin)
        },
        'projected': {
            'sales': float(new_sales),
            'cost': float(new_cost),
            'profit': float(new_profit),
            'margin': float((new_profit / new_sales * 100) if new_sales > 0 else 0)
        },
        'impact': {
            'sales_change': float(new_sales - current_sales),
            'cost_change': float(new_cost - current_cost),
            'profit_change': float(new_profit - current_profit),
            'sales_change_pct': float(change_percent),
            'profit_change_pct': float((new_profit / current_profit - 1) * 100) if current_profit > 0 else 0
        },
        'recommendation': 'Recommended' if new_profit > current_profit else 'Not Recommended'
    }


def simulate_cost_increase(df, increase_percent):
    """
    Simulate impact of cost increase (inverse of cost reduction)
    """
    current_sales = df['Sales'].sum()
    current_cost = df['Cost'].sum()
    current_profit = df['Profit'].sum()
    current_margin = (current_profit / current_sales * 100) if current_sales > 0 else 0
    
    # Calculate new cost
    new_cost = current_cost * (1 + increase_percent / 100)
    cost_increase = new_cost - current_cost
    
    # Sales stay the same, profit decreases
    new_profit = current_sales - new_cost
    new_margin = (new_profit / current_sales * 100) if current_sales > 0 else 0
    
    return {
        'scenario': f"{increase_percent}% Cost Increase",
        'current': {
            'sales': float(current_sales),
            'cost': float(current_cost),
            'profit': float(current_profit),
            'margin': float(current_margin)
        },
        'projected': {
            'sales': float(current_sales),
            'cost': float(new_cost),
            'profit': float(new_profit),
            'margin': float(new_margin)
        },
        'impact': {
            'cost_increase': float(cost_increase),
            'profit_decrease': float(current_profit - new_profit),
            'margin_decline': float(new_margin - current_margin),
            'profit_change_pct': float((new_profit / current_profit - 1) * 100) if current_profit > 0 else 0
        },
        'recommendation': 'Warning - Negative impact on profitability'
    }


def run_custom_scenarios(df, custom_scenarios):
    """
    Run user-defined custom scenarios with specific parameters
    Supports: price_change, sales_volume, cost_change, marketing
    """
    results = []
    
    for scenario in custom_scenarios:
        scenario_type = scenario['type']
        params = scenario['params']
        
        if scenario_type == 'price_change':
            # Can be positive (increase) or negative (decrease)
            price_change = params['change_percent']
            demand_elasticity = params.get('demand_elasticity', -0.5)
            result = simulate_price_increase(df, price_change, demand_elasticity=demand_elasticity)
            
        elif scenario_type == 'sales_volume':
            # Direct volume change
            volume_change = params['change_percent']
            result = simulate_sales_volume_change(df, volume_change)
            
        elif scenario_type == 'cost_change':
            # Can be reduction (negative) or increase (positive)
            cost_change = params['change_percent']
            if cost_change < 0:
                result = simulate_cost_reduction(df, abs(cost_change))
            else:
                result = simulate_cost_increase(df, cost_change)
                
        elif scenario_type == 'marketing':
            # Marketing spend change with custom effectiveness
            marketing_change = params['change_percent']
            effectiveness = params.get('effectiveness', 0.4)
            result = simulate_marketing_change(df, marketing_change, effectiveness=effectiveness)
            
        else:
            continue
        
        results.append(result)
    
    # Rank scenarios by profit impact
    if results:
        results.sort(key=lambda x: x['impact'].get('profit_change', x['impact'].get('profit_decrease', 0)), reverse=True)
    
    return {
        'scenarios': results,
        'best_scenario': results[0] if results else None,
        'worst_scenario': results[-1] if results else None,
        'summary': {
            'total_scenarios': len(results),
            'positive_impact': len([r for r in results if r['impact'].get('profit_change', r['impact'].get('profit_decrease', 0)) > 0]),
            'negative_impact': len([r for r in results if r['impact'].get('profit_change', r['impact'].get('profit_decrease', 0)) < 0])
        }
    }
