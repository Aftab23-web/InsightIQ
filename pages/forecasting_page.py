"""
Forecasting Page
"""
import streamlit as st
from ml_models.forecasting import forecast_multiple_metrics, assess_forecast_risk
from ml_models.scenario_analysis import run_scenario_analysis, run_custom_scenarios
from ui import render_alert, create_line_chart
from utils.auth import is_logged_in
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime


def format_forecast_display(forecast_df, metric_name):
    """Format forecast data for better readability"""
    display_df = forecast_df.copy()
    
    # Convert date to readable format
    display_df['date'] = pd.to_datetime(display_df['date'])
    display_df['Month'] = display_df['date'].dt.strftime('%B %Y')
    
    # Rename columns for clarity
    if 'predicted_sales' in display_df.columns:
        display_df['Expected Sales'] = display_df['predicted_sales'].apply(lambda x: f"₹{x:,.2f}")
        display_df['Lower Range'] = display_df['sales_lower'].apply(lambda x: f"₹{x:,.2f}")
        display_df['Upper Range'] = display_df['sales_upper'].apply(lambda x: f"₹{x:,.2f}")
        display_df['Confidence Range'] = display_df.apply(
            lambda row: f"₹{row['sales_lower']:,.0f} - ₹{row['sales_upper']:,.0f}", axis=1
        )
    elif 'predicted_profit' in display_df.columns:
        display_df['Expected Profit'] = display_df['predicted_profit'].apply(lambda x: f"₹{x:,.2f}")
        display_df['Lower Range'] = display_df['profit_lower'].apply(lambda x: f"₹{x:,.2f}")
        display_df['Upper Range'] = display_df['profit_upper'].apply(lambda x: f"₹{x:,.2f}")
        display_df['Confidence Range'] = display_df.apply(
            lambda row: f"₹{row['profit_lower']:,.0f} - ₹{row['profit_upper']:,.0f}", axis=1
        )
    
    return display_df


def create_forecast_chart(forecast_df, metric_name):
    """Create interactive forecast visualization"""
    
    df = forecast_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    fig = go.Figure()
    
    if 'predicted_sales' in df.columns:
        predicted_col = 'predicted_sales'
        lower_col = 'sales_lower'
        upper_col = 'sales_upper'
        color = '#667eea'
    else:
        predicted_col = 'predicted_profit'
        lower_col = 'profit_lower'
        upper_col = 'profit_upper'
        color = '#43e97b'
    
    # Add confidence interval as a filled area
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df[upper_col],
        mode='lines',
        name='Upper Bound',
        line=dict(width=0),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df[lower_col],
        mode='lines',
        name='Confidence Range',
        fill='tonexty',
        fillcolor=f'rgba(102, 126, 234, 0.2)',
        line=dict(width=0)
    ))
    
    # Add predicted values line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df[predicted_col],
        mode='lines+markers',
        name='Predicted',
        line=dict(color=color, width=3),
        marker=dict(size=8, color=color)
    ))
    
    fig.update_layout(
        title=f'{metric_name} Forecast with Confidence Intervals',
        xaxis_title='Month',
        yaxis_title=f'{metric_name} (₹)',
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    
    return fig


def render():
    """Render forecasting page"""
    
    # Check authentication
    if not is_logged_in():
        render_alert("Please login to access this page", 'warning')
        st.info("Go to **Home** page to login or register.")
        if st.button(" Go to Home"):
            st.session_state.main_menu = 0
            st.rerun()
        st.stop()
    
    if not st.session_state.data_uploaded or st.session_state.df is None:
        render_alert("Please upload data first!", 'warning')
        st.stop()
    
    df = st.session_state.df
    
    st.markdown("""
        <h1 class="gradient-text">Forecasting & Scenarios</h1>
        <p style="color: white; font-size: 1.1rem;">Predict future performance with AI-powered forecasting</p>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["Forecast", "What-If Analysis"])
    
    # Tab 1: Forecast
    with tabs[0]:
        st.markdown("""
            <div style="background: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <p style="color: white; margin: 0;">
                    <strong>How to read forecasts:</strong> The "Expected" value is the most likely outcome. 
                    The "Confidence Range" shows the minimum and maximum values we expect with 95% confidence.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        periods = st.slider("Forecast Periods (months)", 3, 24, 12)
        
        if st.button("Generate Forecast", type="primary", width='stretch'):
            with st.spinner("Generating forecasts with AI models..."):
                forecasts = forecast_multiple_metrics(df, periods)
            
            for metric, result in forecasts.items():
                if 'error' not in result:
                    st.markdown(f"## {metric} Forecast")
                    
                    forecast_df = pd.DataFrame(result['forecast'])
                    
                    # Show chart first
                    chart = create_forecast_chart(forecast_df, metric)
                    st.plotly_chart(chart, width='stretch')
                    
                    # Risk assessment
                    risk = assess_forecast_risk(forecast_df, metric)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        risk_color = "🔴" if risk['risk_level'] == "High" else "🟡" if risk['risk_level'] == "Medium" else "🟢"
                        st.metric("Risk Level", f"{risk_color} {risk['risk_level']}")
                    with col2:
                        st.metric("Avg Uncertainty", f"{risk['avg_uncertainty']:.1f}%")
                    with col3:
                        trend_icon = "📉" if risk['trend_change_pct'] < 0 else "📈"
                        st.metric("Trend Change", f"{trend_icon} {risk['trend_change_pct']:.1f}%")
                    
                    # Format and display detailed forecast table
                    st.markdown("###  Monthly Forecast Details")
                    display_df = format_forecast_display(forecast_df.head(12), metric)
                    
                    if 'predicted_sales' in forecast_df.columns:
                        st.dataframe(
                            display_df[['Month', 'Expected Sales', 'Confidence Range']],
                            width='stretch',
                            hide_index=True
                        )
                    else:
                        st.dataframe(
                            display_df[['Month', 'Expected Profit', 'Confidence Range']],
                            width='stretch',
                            hide_index=True
                        )
                    
                    # Add interpretation
                    if 'predicted_sales' in forecast_df.columns:
                        first_month = display_df.iloc[0]
                        st.info(f"""
                             **Example:** In **{first_month['Month']}**, we expect sales of approximately **{first_month['Expected Sales']}**.
                            This could range between **{first_month['Confidence Range']}** depending on market conditions.
                        """)
                    
                    st.markdown("---")
    
    # Tab 2: What-If
    with tabs[1]:
        st.markdown("### Scenario Analysis")
        st.markdown("""
            <div style="background: rgba(67, 233, 123, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <p style="color: white; margin: 0;">
                    <strong>Create your own scenarios:</strong> Enter custom percentages to see how different business decisions would impact your profits.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # User input section
        st.markdown("####  Build Your Custom Scenarios")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("** Sales & Pricing**")
            
            # Price increase scenario
            price_enabled = st.checkbox("Price Increase/Decrease", value=True, help="Adjust product prices")
            price_change = 0
            if price_enabled:
                price_change = st.slider(
                    "Price Change (%)", 
                    -50, 50, 10, 5,
                    help="Positive = price increase, Negative = price decrease"
                )
            
            # Sales volume scenario
            sales_enabled = st.checkbox("Sales Volume Change", value=False, help="Direct change in sales volume")
            sales_volume_change = 0
            if sales_enabled:
                sales_volume_change = st.slider(
                    "Sales Volume Change (%)", 
                    -50, 100, 20, 5,
                    help="Change in unit sales volume"
                )
        
        with col2:
            st.markdown("** Operations & Marketing**")
            
            # Cost reduction scenario
            cost_enabled = st.checkbox("Cost Reduction/Increase", value=True, help="Change in operating costs")
            cost_change = 0
            if cost_enabled:
                cost_change = st.slider(
                    "Cost Change (%)", 
                    -30, 50, -10, 5,
                    help="Negative = cost reduction, Positive = cost increase"
                )
            
            # Marketing spend scenario
            marketing_enabled = st.checkbox("Marketing Spend Change", value=True, help="Adjust marketing budget")
            marketing_change = 0
            if marketing_enabled:
                marketing_change = st.slider(
                    "Marketing Spend Change (%)", 
                    -50, 100, 20, 10,
                    help="Change in marketing budget"
                )
        
        st.markdown("---")
        
        # Advanced options
        with st.expander(" Advanced Settings"):
            demand_elasticity = st.slider(
                "Demand Elasticity",
                -2.0, 0.0, -0.5, 0.1,
                help="How much demand changes with price changes. -0.5 means 1% price increase leads to 0.5% demand decrease"
            )
            
            marketing_effectiveness = st.slider(
                "Marketing Effectiveness Factor",
                0.1, 1.0, 0.4, 0.05,
                help="How effectively marketing spend converts to sales. 0.4 means 10% marketing increase leads to 4% sales increase"
            )
        
        # Run button
        if st.button(" Run Custom Scenario Analysis", type="primary", width='stretch'):
            # Build custom scenarios based on user input
            custom_scenarios = []
            
            if price_enabled and price_change != 0:
                custom_scenarios.append({
                    'type': 'price_change',
                    'params': {
                        'change_percent': price_change,
                        'demand_elasticity': demand_elasticity
                    }
                })
            
            if cost_enabled and cost_change != 0:
                custom_scenarios.append({
                    'type': 'cost_change',
                    'params': {'change_percent': cost_change}
                })
            
            if marketing_enabled and marketing_change != 0:
                custom_scenarios.append({
                    'type': 'marketing',
                    'params': {
                        'change_percent': marketing_change,
                        'effectiveness': marketing_effectiveness
                    }
                })
            
            if sales_enabled and sales_volume_change != 0:
                custom_scenarios.append({
                    'type': 'sales_volume',
                    'params': {'change_percent': sales_volume_change}
                })
            
            if not custom_scenarios:
                st.warning(" Please enable and configure at least one scenario above.")
            else:
                with st.spinner("Running your custom scenarios..."):
                    scenarios = run_custom_scenarios(df, custom_scenarios)
                
                st.markdown(f"### Analyzed {scenarios['summary']['total_scenarios']} Custom Scenarios")
                
                # Show best scenario
                best = scenarios['best_scenario']
                if best:
                    st.success(f"** Best Scenario:** {best['scenario']}")
                    
                    col1, col2, col3 = st.columns(3)
                    profit_change = best['impact'].get('profit_delta', best['impact'].get('profit_change', 0))
                    
                    with col1:
                        st.metric(
                            "Projected Profit Impact", 
                            f"₹{abs(profit_change):,.2f}",
                            delta=f"{profit_change:+,.2f}",
                            delta_color="normal" if profit_change > 0 else "inverse"
                        )
                    with col2:
                        profit_pct = best['impact'].get('profit_change_pct', 0)
                        st.metric(
                            "Profit Change",
                            f"{profit_pct:+.1f}%",
                            delta=f"{profit_pct:+.1f}%",
                            delta_color="normal" if profit_pct > 0 else "inverse"
                        )
                    with col3:
                        current_profit = best['current'].get('profit', 0)
                        new_profit = best['projected'].get('profit', 0)
                        st.metric("New Profit", f"₹{new_profit:,.0f}", delta=f"from ₹{current_profit:,.0f}")
                
                # Display all scenarios in detail
                st.markdown("---")
                st.markdown("### All Scenario Results")
                
                for idx, scenario in enumerate(scenarios['scenarios'], 1):
                    profit_change = scenario['impact'].get('profit_delta', scenario['impact'].get('profit_change', 0))
                    profit_pct = scenario['impact'].get('profit_change_pct', 0)
                    
                    # Color code based on impact
                    if profit_change > 0:
                        icon = "✅"
                        border_color = "#10b981"
                    elif profit_change < 0:
                        icon = "❌"
                        border_color = "#ef4444"
                    else:
                        icon = "➖"
                        border_color = "#6b7280"
                    
                    with st.expander(f"{icon} {scenario['scenario']}", expanded=(idx == 1)):
                        st.markdown(f"** Recommendation:** {scenario['recommendation']}")
                        
                        # Current vs Projected comparison
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Current State**")
                            st.metric("Sales", f"₹{scenario['current'].get('sales', 0):,.0f}")
                            st.metric("Profit", f"₹{scenario['current'].get('profit', 0):,.0f}")
                            if 'cost' in scenario['current']:
                                st.metric("Cost", f"₹{scenario['current'].get('cost', 0):,.0f}")
                        
                        with col2:
                            st.markdown("**Projected State**")
                            sales_delta = scenario['projected'].get('sales', 0) - scenario['current'].get('sales', 0)
                            st.metric(
                                "Sales", 
                                f"₹{scenario['projected'].get('sales', 0):,.0f}",
                                delta=f"{sales_delta:+,.0f}"
                            )
                            st.metric(
                                "Profit", 
                                f"₹{scenario['projected'].get('profit', 0):,.0f}",
                                delta=f"{profit_change:+,.0f}",
                                delta_color="normal" if profit_change > 0 else "inverse"
                            )
                            if 'cost' in scenario['projected']:
                                cost_delta = scenario['projected'].get('cost', 0) - scenario['current'].get('cost', 0)
                                st.metric(
                                    "Cost", 
                                    f"₹{scenario['projected'].get('cost', 0):,.0f}",
                                    delta=f"{cost_delta:+,.0f}",
                                    delta_color="inverse" if cost_delta > 0 else "normal"
                                )
                        
                        # Impact summary
                        st.markdown("---")
                        st.markdown("** Impact Summary**")
                        impact_color = "green" if profit_change > 0 else "red" if profit_change < 0 else "gray"
                        st.markdown(f":{impact_color}[**Profit Change:** ₹{profit_change:+,.2f} ({profit_pct:+.1f}%)]")
                        
                        # Show additional metrics if available
                        if 'sales_delta' in scenario['impact']:
                            st.markdown(f"**Sales Impact:** ₹{scenario['impact']['sales_delta']:+,.2f}")
                        if 'cost_savings' in scenario['impact']:
                            st.markdown(f"**Cost Savings:** ₹{scenario['impact']['cost_savings']:+,.2f}")
                        if 'margin_improvement' in scenario['impact']:
                            st.markdown(f"**Margin Improvement:** {scenario['impact']['margin_improvement']:+.2f}%")
    
    # Call to action - Navigate to Recommendations
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" See Recommendations", type="primary", width='stretch', key="see_recommendations_cta"):
            st.session_state.main_menu = 6
            st.rerun()
