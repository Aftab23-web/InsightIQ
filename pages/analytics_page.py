"""
Analytics Page
"""
import streamlit as st
from analytics.eda import perform_eda
from analytics.mistake_detection import detect_all_mistakes
from ui import render_alert, create_bar_chart
from utils.auth import is_logged_in
import pandas as pd


def render():
    """Render analytics page"""
    
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
        <h1 class="gradient-text"> Business Analytics</h1>
        <p style="color: white; font-size: 1.1rem;">Deep dive into your business data</p>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["EDA", "Mistakes", "Root Cause"])
    
    # Tab 1: EDA
    with tabs[0]:
        with st.spinner("Performing exploratory analysis..."):
            eda_results = perform_eda(df)
        
        # Time period selector
        time_view = st.radio(" Select Time Period View:", 
                            ["Year", "Month", "Day"], 
                            horizontal=True,
                            help="Choose how you want to view your performance data")
        
        st.markdown("---")
        
        # Year-wise Performance
        if time_view == "Year":
            st.markdown("### Year-wise Performance")
            if eda_results['temporal_trends'].get('yearly'):
                yearly_df = pd.DataFrame(eda_results['temporal_trends']['yearly'])
                st.dataframe(yearly_df, width='stretch', hide_index=True)
                
                # Visual highlights
                if len(yearly_df) > 0:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        total_sales = yearly_df['Sales'].sum()
                        st.metric("Total Sales (All Years)", f"₹{total_sales:,.0f}")
                    with col2:
                        total_profit = yearly_df['Profit'].sum()
                        st.metric("Total Profit (All Years)", f"₹{total_profit:,.0f}")
                    with col3:
                        avg_margin = yearly_df['Profit_Margin'].mean()
                        st.metric("Avg Profit Margin", f"{avg_margin:.2f}%")
        
        # Month-wise Performance
        elif time_view == "Month":
            st.markdown("### Month-wise Performance")
            if eda_results['temporal_trends'].get('monthly'):
                monthly_df = pd.DataFrame(eda_results['temporal_trends']['monthly'])
                
                # Year filter for months
                if 'Year' in monthly_df.columns:
                    selected_year = st.selectbox("Select Year:", 
                                                 sorted(monthly_df['Year'].unique(), reverse=True),
                                                 help="Filter months by year")
                    monthly_filtered = monthly_df[monthly_df['Year'] == selected_year]
                else:
                    monthly_filtered = monthly_df
                
                # Display monthly data
                display_cols = ['Month_Name', 'Sales', 'Profit', 'Cost', 'Profit_Margin']
                if 'MoM_Growth' in monthly_filtered.columns:
                    display_cols.append('MoM_Growth')
                
                available_cols = [col for col in display_cols if col in monthly_filtered.columns]
                st.dataframe(monthly_filtered[available_cols], width='stretch', hide_index=True)
                
                # Monthly highlights
                if len(monthly_filtered) > 0:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        best_month = monthly_filtered.loc[monthly_filtered['Sales'].idxmax()]
                        st.metric("Best Sales Month", 
                                 best_month.get('Month_Name', 'N/A'),
                                 f"₹{best_month['Sales']:,.0f}")
                    with col2:
                        best_profit_month = monthly_filtered.loc[monthly_filtered['Profit'].idxmax()]
                        st.metric("Best Profit Month", 
                                 best_profit_month.get('Month_Name', 'N/A'),
                                 f"₹{best_profit_month['Profit']:,.0f}")
                    with col3:
                        avg_monthly_sales = monthly_filtered['Sales'].mean()
                        st.metric("Avg Monthly Sales", f"₹{avg_monthly_sales:,.0f}")
        
        # Day-wise Performance
        elif time_view == "Day":
            st.markdown("###  Day-wise Performance")
            if eda_results['temporal_trends'].get('daily'):
                daily_df = pd.DataFrame(eda_results['temporal_trends']['daily'])
                
                # Date range filter
                col1, col2 = st.columns(2)
                with col1:
                    num_days = st.slider("Show last N days:", 7, 90, 30, help="Select number of recent days to display")
                with col2:
                    sort_by = st.selectbox("Sort by:", ['Date', 'Sales', 'Profit'], index=0)
                
                # Filter and sort
                daily_filtered = daily_df.head(num_days) if sort_by == 'Date' else daily_df.nlargest(num_days, sort_by)
                
                # Display daily data
                display_cols = ['Date', 'Day_of_Week', 'Sales', 'Profit', 'Cost', 'Profit_Margin']
                available_cols = [col for col in display_cols if col in daily_filtered.columns]
                st.dataframe(daily_filtered[available_cols], width='stretch', hide_index=True)
                
                # Daily highlights
                if len(daily_filtered) > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        best_day = daily_filtered.loc[daily_filtered['Sales'].idxmax()]
                        st.metric("Best Sales Day", 
                                 pd.to_datetime(best_day['Date']).strftime('%Y-%m-%d'),
                                 f"₹{best_day['Sales']:,.0f}")
                    with col2:
                        avg_daily = daily_filtered['Sales'].mean()
                        st.metric("Avg Daily Sales", f"₹{avg_daily:,.0f}")
                    with col3:
                        total_days_profit = daily_filtered['Profit'].sum()
                        st.metric(f"Total Profit ({num_days}d)", f"₹{total_days_profit:,.0f}")
                    with col4:
                        if 'Day_of_Week' in daily_filtered.columns:
                            best_dow = daily_filtered.groupby('Day_of_Week')['Sales'].mean().idxmax()
                            st.metric("Best Day of Week", best_dow)
        
        st.markdown("---")
        st.markdown("###  Top Products")
        top_products = eda_results['product_performance']['top_performers']
        if top_products:
            for p in top_products[:5]:
                col1, col2, col3 = st.columns(3)
                col1.metric("Product", p['Product'])
                col2.metric("Sales", f"₹{p['Sales']:,.0f}")
                col3.metric("Profit", f"₹{p['Profit']:,.0f}")
    
    # Tab 2: Mistakes
    with tabs[1]:
        with st.spinner("Detecting business mistakes..."):
            mistakes = detect_all_mistakes(df)
        
        st.markdown(f"### Found {mistakes['summary']['total_mistakes']} Issues")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Critical", mistakes['summary']['critical'], delta=None, delta_color="inverse")
        col2.metric("High", mistakes['summary']['high'], delta=None, delta_color="inverse")
        col3.metric("Medium", mistakes['summary']['medium'])
        col4.metric("Low", mistakes['summary']['low'])
        
        st.markdown("### Issues by Category")
        for mistake in mistakes['all_mistakes'][:15]:
            severity_icon = "🔴" if mistake['severity'] == 'Critical' else "🟠" if mistake['severity'] == 'High' else "🟡"
            
            # Create more detailed title for product imbalance issues
            if mistake.get('type') == 'Product Sales Imbalance':
                title = f"{severity_icon} {mistake.get('product', 'Product')} Underperforming vs {mistake.get('dominant_product', 'Top Product')}"
            else:
                title = f"{severity_icon} {mistake.get('type', 'Issue')}"
            
            with st.expander(title, expanded=False):
                st.markdown(f"**Description:** {mistake.get('description', '')}")
                st.markdown(f"**Severity:** {mistake.get('severity', 'Unknown')}")
                
                # Show root causes if available (for product imbalance)
                if 'root_causes' in mistake and mistake['root_causes']:
                    st.markdown("** Root Causes Identified:**")
                    for cause in mistake['root_causes']:
                        st.markdown(f"- {cause}")
                
                # Show action items if available
                if 'action_items' in mistake and mistake['action_items']:
                    st.markdown("** Recommended Actions:**")
                    for action in mistake['action_items']:
                        st.markdown(f"- {action}")
                
                # Show additional metrics
                if mistake.get('type') == 'Product Sales Imbalance':
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Share", f"{mistake.get('sales_share', 0):.1f}%")
                    with col2:
                        st.metric("Top Product Share", f"{mistake.get('dominant_share', 0):.1f}%")
                    with col3:
                        st.metric("Potential Revenue", f"₹{mistake.get('potential_revenue', 0):,.0f}")
    
    # Tab 3: Root Cause
    with tabs[2]:
        from analytics.root_cause import identify_root_causes
        
        with st.spinner("Analyzing root causes..."):
            root_causes = identify_root_causes(df)
        
        # Explanatory Header
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); 
                    padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea; margin-bottom: 2rem;">
            <h3 style="color: white; margin: 0;"> What is Root Cause Analysis?</h3>
            <p style="color: rgba(255,255,255,0.85); margin: 0.5rem 0 0 0; line-height: 1.6;">
                Root cause analysis identifies <strong>WHY</strong> your business metrics are performing the way they are. 
                It shows which factors have the strongest impact on your profits and how they relate to each other.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature Importance Section
        if root_causes.get('feature_importance') and root_causes['feature_importance'].get('top_features'):
            st.markdown("### Impact Analysis: What Drives Your Profits?")
            st.markdown("""
            <p style="color: rgba(255,255,255,0.7); margin-bottom: 1rem;">
                These factors have the strongest influence on your profit. Higher percentages mean bigger impact.
            </p>
            """, unsafe_allow_html=True)
            
            top_features = root_causes['feature_importance']['top_features'][:5]
            
            # Define meaningful insights for each factor type
            factor_insights = {
                'Sales': {
                    'high': ' Revenue generation is your primary profit driver. Focus on increasing sales volume and value.',
                    'medium': ' Sales significantly impact profits. Consider strategies to boost revenue while maintaining margins.',
                    'low': ' Sales have some influence on profits, but cost control may be more critical.'
                },
                'Cost': {
                    'high': ' Cost is your biggest profit factor. Reducing expenses by even 5-10% could dramatically improve profitability.',
                    'medium': ' Cost management significantly affects your bottom line. Look for waste reduction opportunities.',
                    'low': '✓ Costs are well-controlled. Focus on revenue growth for better profits.'
                },
                'Marketing_Spend': {
                    'high': ' Marketing drives your profits strongly. Every rupee spent yields measurable returns - optimize your campaigns.',
                    'medium': ' Marketing investment shows solid returns. Analyze which channels work best and double down.',
                    'low': ' Marketing has limited profit impact. Consider if you\'re underspending or need better targeting.'
                },
                'Product': {
                    'high': 'Product mix is crucial for profits. Focus on high-margin products and phase out underperformers.',
                    'medium': ' Product selection matters. Analyze which products are most profitable and promote them.',
                    'low': ' Product variety has minimal profit impact. Your product mix is balanced across profitability.'
                },
                'Region': {
                    'high': ' Geographic performance varies dramatically. Focus resources on high-performing regions.',
                    'medium': ' Regional differences affect profits. Identify winning markets and replicate success.',
                    'low': ' Profits are consistent across regions. Your business scales uniformly geographically.'
                },
                'Month': {
                    'high': 'Strong seasonal patterns exist. Plan inventory, staffing, and marketing around peak periods.',
                    'medium': ' Timing matters for profits. Identify and capitalize on high-profit months.',
                    'low': ' Minimal seasonal variation. Your business maintains steady profitability year-round.'
                },
                'Quarter': {
                    'high': ' Quarterly cycles heavily impact profits. Align business planning with these patterns.',
                    'medium': ' Quarterly trends influence profitability. Track and prepare for predictable cycles.',
                    'low': ' Profits remain stable across quarters. No significant seasonal business cycles detected.'
                },
                'Year': {
                    'high': ' Year-over-year trends dominate profits. Market conditions or business maturity are key factors.',
                    'medium': ' Annual patterns exist. Consider multi-year strategies for sustainable growth.',
                    'low': ' No strong year-to-year variations. Your business maintains consistent profitability.'
                },
                'DayOfWeek': {
                    'high': ' Weekday performance varies significantly. Optimize staffing and promotions by day.',
                    'medium': ' Day of week affects profits. Plan operations around peak performance days.',
                    'low': ' Consistent daily performance. No need to adjust operations by weekday.'
                }
            }
            
            for idx, feature in enumerate(top_features):
                feature_name = feature['feature']
                importance = feature['importance'] * 100
                
                # Determine color and impact level based on importance
                if importance > 30:
                    color = '#ef4444'  # Red for high impact
                    icon = '🔴'
                    impact_level = 'high'
                    impact_text = 'CRITICAL DRIVER'
                elif importance > 20:
                    color = '#f59e0b'  # Orange for medium-high
                    icon = '🟠'
                    impact_level = 'high'
                    impact_text = 'MAJOR FACTOR'
                elif importance > 10:
                    color = '#eab308'  # Yellow for medium
                    icon = '🟡'
                    impact_level = 'medium'
                    impact_text = 'SIGNIFICANT FACTOR'
                else:
                    color = '#10b981'  # Green for low
                    icon = '🟢'
                    impact_level = 'low'
                    impact_text = 'MINOR FACTOR'
                
                # Get contextual insight for this factor
                insight = 'This factor influences your profit outcomes.'  # Default
                for key in factor_insights.keys():
                    if key.lower() in feature_name.lower():
                        insight = factor_insights[key][impact_level]
                        break
                
                # Create visual progress bar with meaningful insight
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); padding: 1.2rem; border-radius: 10px; margin-bottom: 1rem; 
                            border-left: 4px solid {color}; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="color: white; font-weight: bold; font-size: 1.15rem;">{icon} {feature_name}</span>
                        <div style="text-align: right;">
                            <div style="color: {color}; font-weight: bold; font-size: 1.3rem;">{importance:.1f}%</div>
                            <div style="color: {color}; font-size: 0.75rem; font-weight: 600; opacity: 0.9;">{impact_text}</div>
                        </div>
                    </div>
                    <div style="width: 100%; background: rgba(255,255,255,0.1); height: 24px; border-radius: 12px; overflow: hidden; margin: 0.8rem 0;">
                        <div style="width: {importance}%; background: linear-gradient(90deg, {color}, {color}dd); 
                                    height: 100%; transition: width 0.5s ease; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px;">
                            <span style="color: white; font-size: 0.75rem; font-weight: bold;">{importance:.1f}%</span>
                        </div>
                    </div>
                    <p style="color: rgba(255,255,255,0.85); margin: 0.8rem 0 0 0; font-size: 0.95rem; line-height: 1.6; 
                               background: rgba(0,0,0,0.2); padding: 0.8rem; border-radius: 6px;">
                        {insight}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Correlation Analysis Section
        if 'profit_correlations' in root_causes.get('correlations', {}):
            st.markdown("### Relationship Analysis: How Factors Connect")
            st.markdown("""
            <p style="color: rgba(255,255,255,0.7); margin-bottom: 1rem;">
                Correlation shows how closely two factors move together. Values closer to +1.00 or -1.00 indicate stronger relationships.
            </p>
            """, unsafe_allow_html=True)
            
            profit_corr = root_causes['correlations']['profit_correlations']
            
            # Display correlations in a more visual way
            for metric, corr in list(profit_corr.items())[:6]:
                if metric != 'Profit' and abs(corr) > 0.1:
                    if corr > 0.7:
                        strength = "Very Strong Positive"
                        color = '#10b981'
                        explanation = "When this increases, profit strongly tends to increase too"
                    elif corr > 0.4:
                        strength = "Strong Positive"
                        color = '#3b82f6'
                        explanation = "When this increases, profit tends to increase"
                    elif corr > 0:
                        strength = "Weak Positive"
                        color = '#8b5cf6'
                        explanation = "When this increases, profit slightly tends to increase"
                    elif corr > -0.4:
                        strength = "Weak Negative"
                        color = '#f59e0b'
                        explanation = "When this increases, profit slightly tends to decrease"
                    elif corr > -0.7:
                        strength = "Strong Negative"
                        color = '#ef4444'
                        explanation = "When this increases, profit tends to decrease"
                    else:
                        strength = "Very Strong Negative"
                        color = '#dc2626'
                        explanation = "When this increases, profit strongly tends to decrease"
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; 
                                    border-left: 4px solid {color}; margin-bottom: 0.8rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span style="font-size: 1.5rem;">{icon}</span>
                                    <span style="color: white; font-weight: bold; font-size: 1.05rem; margin-left: 0.5rem;">
                                        {metric} ↔ Profit
                                    </span>
                                </div>
                                <span style="color: {color}; font-weight: bold; font-size: 1.1rem;">{corr:.2f}</span>
                            </div>
                            <p style="color: rgba(255,255,255,0.7); margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                                {strength} Relationship: {explanation}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem 0;">
                            <div style="color: {color}; font-size: 2rem; font-weight: bold;">{strength.split()[0]}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Key Takeaways
        st.markdown("### Key Takeaways")
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%); 
                    padding: 1.5rem; border-radius: 10px; border-left: 4px solid #10b981;">
            <p style="color: white; margin: 0; line-height: 1.8;">
                <strong> How to Use This Information:</strong><br><br>
                • <strong>Focus on High-Impact Factors:</strong> Prioritize improving factors with 30%+ impact<br>
                • <strong>Watch Strong Correlations:</strong> Monitor relationships above 0.7 (positive or negative)<br>
                • <strong>Optimize Spending:</strong> If Cost has high negative correlation, focus on cost reduction<br>
                • <strong>Leverage Positives:</strong> Double down on factors that strongly correlate with profit growth
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to action - Navigate to Insights & SWOT
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" See Insights & SWOT", type="primary", width='stretch', key="see_insights_swot_cta"):
            st.session_state.main_menu = 4
            st.rerun()
