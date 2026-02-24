"""
Executive Dashboard Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analytics.kpi_calculator import calculate_all_kpis
from analytics.eda import perform_eda
from ml_models.anomaly_detection import detect_all_anomalies
from ui import render_health_score, render_metric_card, create_line_chart, create_pie_chart, render_alert
from utils.auth import is_logged_in


def render():
    """Render executive dashboard"""
    
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
        st.info("Go to **Data Upload** page to upload your business data.")
        st.stop()
    
    df = st.session_state.df
    
    st.markdown("""
        <h1 class="gradient-text"> Executive Dashboard</h1>
        <p style="color: white; font-size: 1.1rem;">High-level overview of your business performance</p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Calculate KPIs
    with st.spinner("Calculating KPIs..."):
        kpis = calculate_all_kpis(df)
    
    # Business Health Score
    col1, col2 = st.columns([1, 2])
    
    with col1:
        health = kpis['health']
        render_health_score(
            health['health_score'],
            health['health_status'],
            health['status_icon']
        )
    
    with col2:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("#### Health Score Components")
        
        # Component scores
        components = health['component_scores']
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Growth Score", f"{components['growth']:.0f}/100")
            st.metric("Efficiency Score", f"{components['efficiency']:.0f}/100")
        
        with col_b:
            st.metric("Profitability Score", f"{components['profitability']:.0f}/100")
            st.metric("Stability Score", f"{components['stability']:.0f}/100")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key Metrics
    st.markdown("###  Key Financial Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    revenue = kpis['revenue']
    growth = kpis['growth']
    efficiency = kpis['efficiency']
    
    with col1:
        st.metric(
            "Total Sales",
            f"₹{revenue['total_sales']:,.0f}",
            delta=f"{growth['sales_growth']:.1f}%" if growth['sales_growth'] != 0 else None
        )
    
    with col2:
        st.metric(
            "Total Profit",
            f"₹{revenue['total_profit']:,.0f}",
            delta=f"{growth['profit_growth']:.1f}%" if growth['profit_growth'] != 0 else None
        )
    
    with col3:
        st.metric(
            "Profit Margin",
            f"{revenue['avg_profit_margin']:.1f}%"
        )
    
    with col4:
        # Display Marketing ROI as multiplier (more intuitive)
        marketing_multiplier = efficiency['marketing_multiplier']
        st.metric(
            "Marketing ROI",
            f"{marketing_multiplier:.1f}x",
            help=f"Every ₹1 spent on marketing generates ₹{marketing_multiplier:.1f} in sales"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts - Dynamic based on data
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("####  Sales & Profit Trend")
        
        if 'Date' in df.columns:
            # Determine best time aggregation based on data span
            date_range = (df['Date'].max() - df['Date'].min()).days
            
            if date_range > 365:  # More than a year - show monthly
                df_copy = df.copy()
                df_copy['Period'] = pd.to_datetime(df_copy['Date']).dt.to_period('M').astype(str)
                trend_data = df_copy.groupby('Period').agg({
                    'Sales': 'sum',
                    'Profit': 'sum'
                }).reset_index()
                x_label = 'Month'
            elif date_range > 90:  # 3-12 months - show weekly
                df_copy = df.copy()
                df_copy['Period'] = pd.to_datetime(df_copy['Date']).dt.to_period('W').astype(str)
                trend_data = df_copy.groupby('Period').agg({
                    'Sales': 'sum',
                    'Profit': 'sum'
                }).reset_index()
                x_label = 'Week'
            else:  # Less than 3 months - show daily
                trend_data = df.groupby('Date').agg({
                    'Sales': 'sum',
                    'Profit': 'sum'
                }).reset_index()
                trend_data['Period'] = trend_data['Date'].astype(str)
                x_label = 'Date'
            
            # Create dual-axis chart
            fig = go.Figure()
            
            # Sales line
            fig.add_trace(go.Scatter(
                x=trend_data['Period'],
                y=trend_data['Sales'],
                name='Sales',
                mode='lines+markers',
                line=dict(color='#667eea', width=3),
                marker=dict(size=6, line=dict(width=2, color='white')),
                yaxis='y1'
            ))
            
            # Profit line
            fig.add_trace(go.Scatter(
                x=trend_data['Period'],
                y=trend_data['Profit'],
                name='Profit',
                mode='lines+markers',
                line=dict(color='#10b981', width=3),
                marker=dict(size=6, line=dict(width=2, color='white')),
                yaxis='y2'
            ))
            
            fig.update_layout(
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font={'family': 'Inter, sans-serif', 'color': 'white'},
                xaxis={'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.1)', 'title': x_label},
                yaxis=dict(
                    title='Sales (₹)',
                    titlefont=dict(color='#667eea'),
                    tickfont=dict(color='#667eea'),
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                yaxis2=dict(
                    title='Profit (₹)',
                    titlefont=dict(color='#10b981'),
                    tickfont=dict(color='#10b981'),
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                height=400,
                showlegend=True,
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                )
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Date column required for trend analysis")
    
    with col2:
        st.markdown("####  Product Performance")
        
        # Get top products by sales or profit
        product_data = df.groupby('Product').agg({
            'Sales': 'sum',
            'Profit': 'sum'
        }).reset_index()
        
        # Sort by sales and get top 10
        product_data = product_data.nlargest(10, 'Sales')
        
        # Create grouped bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Sales',
            y=product_data['Product'],
            x=product_data['Sales'],
            orientation='h',
            marker=dict(color='#667eea'),
            text=product_data['Sales'].apply(lambda x: f'₹{x/1000:.0f}K' if x >= 1000 else f'₹{x:.0f}'),
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            name='Profit',
            y=product_data['Product'],
            x=product_data['Profit'],
            orientation='h',
            marker=dict(color='#10b981'),
            text=product_data['Profit'].apply(lambda x: f'₹{x/1000:.0f}K' if x >= 1000 else f'₹{x:.0f}'),
            textposition='auto'
        ))
        
        fig.update_layout(
            barmode='group',
            showlegend=True,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif', 'color': 'white'},
            xaxis={'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.1)', 'title': 'Amount (₹)'},
            yaxis={'showgrid': False, 'title': ''},
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            )
        )
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Regional Performance & Cost Structure
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("####  Regional Distribution")
        
        # Show both sales and profit by region
        if 'Region' in df.columns:
            regional_data = df.groupby('Region').agg({
                'Sales': 'sum',
                'Profit': 'sum'
            }).reset_index()
            
            # Create pie chart for sales
            fig = px.pie(
                regional_data,
                values='Sales',
                names='Region',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='white', width=2))
            )
            
            fig.update_layout(
                font={'family': 'Inter, sans-serif', 'color': 'white'},
                height=400,
                showlegend=True,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(color='white')
                )
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Region column not available")
    
    with col2:
        st.markdown("####  Cost Structure")
        
        # Calculate actual cost breakdown from data
        total_cost = revenue['total_cost']
        total_marketing = revenue['total_marketing_spend']
        total_profit = revenue['total_profit']
        
        cost_breakdown = pd.DataFrame({
            'Category': ['Cost', 'Marketing', 'Profit'],
            'Amount': [total_cost, total_marketing, total_profit],
            'Percentage': [
                (total_cost / (total_cost + total_marketing + total_profit) * 100),
                (total_marketing / (total_cost + total_marketing + total_profit) * 100),
                (total_profit / (total_cost + total_marketing + total_profit) * 100)
            ]
        })
        
        # Create donut chart
        fig = px.pie(
            cost_breakdown,
            values='Amount',
            names='Category',
            hole=0.4,
            color='Category',
            color_discrete_map={
                'Cost': '#ef4444',
                'Marketing': '#f59e0b',
                'Profit': '#10b981'
            }
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(line=dict(color='white', width=2)),
            hovertemplate='<b>%{label}</b><br>Amount: ₹%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            font={'family': 'Inter, sans-serif', 'color': 'white'},
            height=400,
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color='white')
            )
        )
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Additional Advanced Visualizations
    st.markdown("###  Advanced Analytics")
    
    # Treemap and Sunburst Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Market Share Treemap")
        
        if 'Product' in df.columns and 'Region' in df.columns:
            # Create hierarchical data for treemap
            treemap_data = df.groupby(['Product', 'Region']).agg({
                'Sales': 'sum',
                'Profit': 'sum'
            }).reset_index()
            
            fig = px.treemap(
                treemap_data,
                path=[px.Constant("Total"), 'Product', 'Region'],
                values='Sales',
                color='Profit',
                color_continuous_scale='RdYlGn',
                hover_data={'Sales': ':,.0f', 'Profit': ':,.0f'}
            )
            
            fig.update_traces(
                textposition='middle center',
                marker=dict(line=dict(color='white', width=2))
            )
            
            fig.update_layout(
                font={'family': 'Inter, sans-serif', 'color': 'white'},
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=30, l=0, r=0, b=0)
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Product and Region columns required")
    
    with col2:
        st.markdown("#### Hierarchical Sunburst")
        
        if 'Product' in df.columns and 'Region' in df.columns:
            sunburst_data = df.groupby(['Region', 'Product']).agg({
                'Sales': 'sum',
                'Profit': 'sum'
            }).reset_index()
            
            fig = px.sunburst(
                sunburst_data,
                path=['Region', 'Product'],
                values='Sales',
                color='Profit',
                color_continuous_scale='Viridis',
                hover_data={'Sales': ':,.0f', 'Profit': ':,.0f'}
            )
            
            fig.update_traces(
                textinfo='label+percent parent',
                marker=dict(line=dict(color='white', width=2))
            )
            
            fig.update_layout(
                font={'family': 'Inter, sans-serif', 'color': 'white'},
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=30, l=0, r=0, b=0)
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Product and Region columns required")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Waterfall and Area Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Revenue Chart")
        
        # Calculate waterfall components
        waterfall_data = pd.DataFrame({
            'Category': ['Sales', 'Cost', 'Marketing', 'Profit'],
            'Value': [revenue['total_sales'], -revenue['total_cost'], -revenue['total_marketing_spend'], revenue['total_profit']],
            'Type': ['relative', 'relative', 'relative', 'total']
        })
        
        fig = go.Figure(go.Waterfall(
            name="Revenue",
            orientation="v",
            measure=waterfall_data['Type'],
            x=waterfall_data['Category'],
            y=waterfall_data['Value'],
            text=[f"₹{abs(v):,.0f}" for v in waterfall_data['Value']],
            textposition="outside",
            connector={"line": {"color": "rgba(255,255,255,0.3)"}},
            increasing={"marker": {"color": "#10b981"}},
            decreasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#667eea"}}
        ))
        
        fig.update_layout(
            font={'family': 'Inter, sans-serif', 'color': 'white'},
            height=450,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis={'showgrid': False, 'title': ''},
            yaxis={'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.1)', 'title': 'Amount (₹)'}
        )
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.markdown("####  Cumulative Sales Trend")
        
        if 'Date' in df.columns:
            # Create cumulative trend
            df_sorted = df.sort_values('Date')
            df_sorted['Cumulative_Sales'] = df_sorted['Sales'].cumsum()
            df_sorted['Cumulative_Profit'] = df_sorted['Profit'].cumsum()
            
            # Sample data if too many points
            if len(df_sorted) > 50:
                df_sorted = df_sorted.iloc[::max(len(df_sorted)//50, 1)]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_sorted['Date'],
                y=df_sorted['Cumulative_Sales'],
                fill='tonexty',
                name='Cumulative Sales',
                mode='lines',
                line=dict(color='#667eea', width=2),
                fillcolor='rgba(102, 126, 234, 0.3)'
            ))
            
            fig.add_trace(go.Scatter(
                x=df_sorted['Date'],
                y=df_sorted['Cumulative_Profit'],
                fill='tozeroy',
                name='Cumulative Profit',
                mode='lines',
                line=dict(color='#10b981', width=2),
                fillcolor='rgba(16, 185, 129, 0.3)'
            ))
            
            fig.update_layout(
                font={'family': 'Inter, sans-serif', 'color': 'white'},
                height=450,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis={'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.1)', 'title': 'Date'},
                yaxis={'showgrid': True, 'gridcolor': 'rgba(255,255,255,0.1)', 'title': 'Cumulative Amount (₹)'},
                hovermode='x unified',
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                )
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Date column required")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent Alerts & Anomalies
    with st.spinner("Detecting anomalies..."):
        anomalies = detect_all_anomalies(df)
    
    if anomalies['summary']['total_anomalies'] > 0:
        st.markdown("### Recent Alerts & Anomalies")
        
        # Show top 5 anomalies
        top_anomalies = anomalies['anomalies'][:5]
        
        for anomaly in top_anomalies:
            severity = anomaly.get('severity', 'Low')
            
            # Color code by severity
            if severity == 'Critical':
                icon = '🔴'
                border_color = '#ef4444'
                severity_badge = 'CRITICAL'
            elif severity == 'High':
                icon = '🟠'
                border_color = '#f59e0b'
                severity_badge = 'HIGH'
            elif severity == 'Medium':
                icon = '🟡'
                border_color = '#eab308'
                severity_badge = 'MEDIUM'
            else:
                icon = '🟢'
                border_color = '#10b981'
                severity_badge = 'LOW'
            
            date_str = anomaly.get('date').strftime('%Y-%m-%d') if hasattr(anomaly.get('date'), 'strftime') else str(anomaly.get('date', 'Unknown'))
            
            with st.expander(f"{icon} {anomaly.get('type', 'Anomaly')} - {date_str}", expanded=False):
                # Severity Badge
                st.markdown(f"""
                <div style="display: inline-block; padding: 0.3rem 0.8rem; background: {border_color}; 
                            color: white; border-radius: 20px; font-weight: bold; font-size: 0.85rem; margin-bottom: 1rem;">
                    {severity_badge}
                </div>
                """, unsafe_allow_html=True)
                
                # Parse description to extract sections
                description = anomaly.get('description', 'No description available')
                
                # Extract the summary line (first line before "Business Metrics:")
                if 'Business Metrics:' in description:
                    parts = description.split('Business Metrics:')
                    summary = parts[0].strip()
                    rest = 'Business Metrics:' + parts[1] if len(parts) > 1 else ''
                    
                    # Display summary prominently
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, rgba(231, 76, 60, 0.15), rgba(192, 57, 43, 0.15)); 
                                padding: 1.2rem; border-radius: 10px; 
                                border-left: 5px solid {border_color}; margin-bottom: 1.5rem;
                                box-shadow: 0 2px 10px rgba(0,0,0,0.3);">
                        <p style="color: white; font-size: 1.15rem; margin: 0; line-height: 1.8; font-weight: 500;">
                            {summary}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Extract and display Business Metrics using simpler approach
                    if '• Sales:' in rest:
                        st.markdown("**Business Metrics**")
                        
                        # Extract values directly from anomaly dict if available
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if 'actual_value' in anomaly:
                                st.metric("Sales", f"₹{anomaly['actual_value']:,.0f}")
                            else:
                                # Parse from description
                                try:
                                    sales_line = [line for line in rest.split('•') if 'Sales:' in line][0]
                                    sales_val = sales_line.split(':')[1].split('(')[0].strip()
                                    st.metric("Sales", sales_val)
                                except:
                                    st.metric("Sales", "N/A")
                        
                        with col2:
                            try:
                                profit_line = [line for line in rest.split('•') if 'Profit:' in line][0]
                                profit_val = profit_line.split(':')[1].split('(')[0].strip()
                                st.metric("Profit", profit_val)
                            except:
                                st.metric("Profit", "N/A")
                        
                        with col3:
                            try:
                                margin_line = [line for line in rest.split('•') if 'Profit Margin:' in line or 'Profit margin:' in line][0]
                                margin_val = margin_line.split(':')[1].strip()
                                st.metric("Profit Margin", margin_val)
                            except:
                                st.metric("Profit Margin", "N/A")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Extract and display Analysis
                    if 'Analysis:' in rest:
                        analysis_section = rest.split('Analysis:')[1].split('Possible Causes:')[0] if 'Possible Causes:' in rest else rest.split('Analysis:')[1]
                        st.markdown("<div style='background: rgba(52, 152, 219, 0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;'>", unsafe_allow_html=True)
                        st.markdown("**Analysis**")
                        st.markdown(f"<p style='color: white; line-height: 1.6;'>{analysis_section.strip().replace('•', '').strip()}</p>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Extract and display Possible Causes
                    if 'Possible Causes:' in rest:
                        causes_section = rest.split('Possible Causes:')[1].split('Recommended Actions:')[0] if 'Recommended Actions:' in rest else rest.split('Possible Causes:')[1]
                        causes = [c.strip() for c in causes_section.split('•') if c.strip()]
                        
                        if causes:
                            st.markdown("<div style='background: rgba(241, 196, 15, 0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;'>", unsafe_allow_html=True)
                            st.markdown("**Possible Causes**")
                            st.markdown("<div style='padding-left: 0.5rem;'>", unsafe_allow_html=True)
                            for cause in causes:
                                if cause:
                                    st.markdown(f"<p style='color: white; margin: 0.5rem 0; line-height: 1.6;'> {cause}</p>", unsafe_allow_html=True)
                            st.markdown("</div></div>", unsafe_allow_html=True)
                    
                    # Extract and display Recommended Actions
                    if 'Recommended Actions:' in rest:
                        actions_section = rest.split('Recommended Actions:')[1]
                        actions = [a.strip() for a in actions_section.split('•') if a.strip()]
                        
                        if actions:
                            st.markdown("<div style='background: rgba(46, 204, 113, 0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;'>", unsafe_allow_html=True)
                            st.markdown("**Recommended Actions**")
                            st.markdown("<div style='padding-left: 0.5rem;'>", unsafe_allow_html=True)
                            for action in actions:
                                if action:
                                    st.markdown(f"<p style='color: white; margin: 0.5rem 0; line-height: 1.6;'>✓ {action}</p>", unsafe_allow_html=True)
                            st.markdown("</div></div>", unsafe_allow_html=True)
                else:
                    # Fallback for simple descriptions
                    st.markdown(description)
    
    # Quick Insights
    st.markdown("### Quick Insights")
    
    insights = kpis.get('insights', [])
    
    if insights:
        for insight in insights[:5]:
            severity = insight.get('severity', 'info')
            
            if severity == 'Critical':
                st.error(f"🔴 {insight['message']}")
            elif severity == 'High':
                st.warning(f"🟠 {insight['message']}")
            elif severity == 'Positive':
                st.success(f"🟢 {insight['message']}")
            else:
                st.info(f"🔵 {insight['message']}")
    else:
        st.success("✓ No critical issues detected!")
    
    # Mark analysis as complete
    st.session_state.analysis_complete = True
    
    # Call to action - Navigate to Analytics
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" See Analytics", type="primary", width='stretch', key="see_analytics_cta"):
            st.session_state.main_menu = 3
            st.rerun()
