"""
Reports Page
"""
import streamlit as st
from ui import render_alert
from analytics.kpi_calculator import calculate_all_kpis
from analytics.swot_analysis import perform_swot_analysis
from analytics.mistake_detection import detect_all_mistakes
from utils.auth import is_logged_in
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_charts_html(df, kpis):
    """Generate HTML with embedded charts"""
    charts_html = ""
    
    # Color scheme
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140', '#30cfd0']
    
    # 1. Sales Trend Chart
    daily_sales = df.groupby('Date')['Sales'].sum().reset_index()
    fig1 = px.line(daily_sales, x='Date', y='Sales', title='Sales Trend Over Time')
    fig1.update_traces(line_color='#667eea', line_width=3)
    fig1.update_layout(
        height=400, 
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#333')
    )
    charts_html += fig1.to_html(include_plotlyjs='cdn', div_id="sales_trend")
    
    # 2. Product Performance Chart
    product_perf = df.groupby('Product').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).sort_values('Profit', ascending=False).head(10)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=product_perf.index, 
        y=product_perf['Sales'], 
        name='Sales',
        marker_color='#667eea'
    ))
    fig2.add_trace(go.Bar(
        x=product_perf.index, 
        y=product_perf['Profit'], 
        name='Profit',
        marker_color='#43e97b'
    ))
    fig2.update_layout(
        title='Top 10 Products Performance', 
        barmode='group', 
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#333')
    )
    charts_html += fig2.to_html(include_plotlyjs='cdn', div_id="product_perf")
    
    # 3. Regional Distribution Chart
    regional_sales = df.groupby('Region')['Sales'].sum()
    fig3 = px.pie(
        values=regional_sales.values, 
        names=regional_sales.index, 
        title='Sales Distribution by Region',
        color_discrete_sequence=colors
    )
    fig3.update_traces(textposition='inside', textinfo='percent+label')
    fig3.update_layout(
        height=400,
        paper_bgcolor='white',
        font=dict(color='#333')
    )
    charts_html += fig3.to_html(include_plotlyjs='cdn', div_id="regional_dist")
    
    # 4. Profit Margin Trend
    daily_margin = df.groupby('Date')['Profit_Margin'].mean().reset_index()
    fig4 = px.line(daily_margin, x='Date', y='Profit_Margin', 
                   title='Average Profit Margin Trend')
    fig4.update_traces(line_color='#fa709a', line_width=3)
    fig4.update_layout(
        height=400, 
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#333')
    )
    charts_html += fig4.to_html(include_plotlyjs='cdn', div_id="margin_trend")
    
    # 5. Cost vs Revenue Comparison
    monthly_data = df.groupby(df['Date'].dt.to_period('M')).agg({
        'Sales': 'sum',
        'Cost': 'sum',
        'Profit': 'sum'
    }).reset_index()
    monthly_data['Date'] = monthly_data['Date'].astype(str)
    
    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=monthly_data['Date'], 
        y=monthly_data['Sales'], 
        name='Sales', 
        mode='lines+markers',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8, color='#667eea')
    ))
    fig5.add_trace(go.Scatter(
        x=monthly_data['Date'], 
        y=monthly_data['Cost'], 
        name='Cost', 
        mode='lines+markers',
        line=dict(color='#fa709a', width=3),
        marker=dict(size=8, color='#fa709a')
    ))
    fig5.add_trace(go.Scatter(
        x=monthly_data['Date'], 
        y=monthly_data['Profit'], 
        name='Profit', 
        mode='lines+markers',
        line=dict(color='#43e97b', width=3),
        marker=dict(size=8, color='#43e97b')
    ))
    fig5.update_layout(
        title='Monthly Sales, Cost & Profit Comparison', 
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#333')
    )
    charts_html += fig5.to_html(include_plotlyjs='cdn', div_id="monthly_comp")
    
    return charts_html


def generate_executive_summary(df, kpis):
    """Generate executive summary report content"""
    report = f"""
# EXECUTIVE BUSINESS INTELLIGENCE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## EXECUTIVE SUMMARY

### Key Performance Indicators

**Revenue Metrics:**
- Total Sales: ₹{kpis['revenue']['total_sales']:,.2f}
- Total Profit: ₹{kpis['revenue']['total_profit']:,.2f}
- Average Profit Margin: {kpis['revenue']['avg_profit_margin']:.1f}%

**Performance:**
- Total Cost: ₹{kpis['revenue']['total_cost']:,.2f}
- Cost Ratio: {(kpis['revenue']['total_cost']/kpis['revenue']['total_sales']*100):.1f}%
- Marketing Spend: ₹{kpis['revenue']['total_marketing_spend']:,.2f}

---

## PRODUCT ANALYSIS

### Top Performing Products
"""
    
    product_performance = df.groupby('Product').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Profit_Margin': 'mean'
    }).sort_values('Profit', ascending=False)
    
    for idx, (product, row) in enumerate(product_performance.head(5).iterrows(), 1):
        report += f"\n{idx}. **{product}**\n"
        report += f"   - Sales: ₹{row['Sales']:,.2f}\n"
        report += f"   - Profit: ₹{row['Profit']:,.2f}\n"
        report += f"   - Margin: {row['Profit_Margin']:.1f}%\n"
    
    report += "\n---\n\n## REGIONAL PERFORMANCE\n\n"
    
    regional_performance = df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).sort_values('Profit', ascending=False)
    
    for region, row in regional_performance.iterrows():
        report += f"**{region}:**\n"
        report += f"- Sales: ₹{row['Sales']:,.2f}\n"
        report += f"- Profit: ₹{row['Profit']:,.2f}\n\n"
    
    report += "---\n\n## RECOMMENDATIONS\n\n"
    report += "1. Focus on expanding top-performing products\n"
    report += "2. Optimize costs in underperforming regions\n"
    report += "3. Implement targeted marketing strategies\n"
    report += "4. Monitor and improve profit margins\n"
    report += "5. Leverage data analytics for continuous improvement\n"
    
    report += "\n---\n\n*Report generated by InsightIQ*\n"
    
    return report


def generate_detailed_analytics(df):
    """Generate detailed analytics report"""
    report = f"""
# DETAILED ANALYTICS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## DATA OVERVIEW

- Total Records: {len(df):,}
- Date Range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}
- Products: {df['Product'].nunique()}
- Regions: {df['Region'].nunique()}

---

## STATISTICAL SUMMARY

"""
    
    numeric_cols = ['Sales', 'Cost', 'Profit', 'Profit_Margin']
    stats_df = df[numeric_cols].describe()
    
    for col in numeric_cols:
        report += f"\n### {col}\n"
        report += f"- Mean: ₹{stats_df.loc['mean', col]:,.2f}\n"
        report += f"- Median: ₹{stats_df.loc['50%', col]:,.2f}\n"
        report += f"- Std Dev: ₹{stats_df.loc['std', col]:,.2f}\n"
        report += f"- Min: ₹{stats_df.loc['min', col]:,.2f}\n"
        report += f"- Max: ₹{stats_df.loc['max', col]:,.2f}\n"
    
    return report


def generate_pdf_report(df, kpis, report_type):
    """Generate fast PDF report with optimized tables"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Title
    story.append(Paragraph(f"{report_type}", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    
    # KPI Table
    kpi_data = [
        ['Metric', 'Value'],
        ['Total Sales', f"₹{kpis['revenue']['total_sales']:,.2f}"],
        ['Total Profit', f"₹{kpis['revenue']['total_profit']:,.2f}"],
        ['Profit Margin', f"{kpis['revenue']['avg_profit_margin']:.1f}%"],
        ['Total Cost', f"₹{kpis['revenue']['total_cost']:,.2f}"],
        ['Marketing Spend', f"₹{kpis['revenue']['total_marketing_spend']:,.2f}"]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[3*inch, 3*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Sales Trend Summary (Table instead of chart for speed)
    story.append(Paragraph("SALES TREND SUMMARY", heading_style))
    monthly_sales = df.groupby(pd.to_datetime(df['Date']).dt.to_period('M')).agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).tail(6).reset_index()
    monthly_sales['Date'] = monthly_sales['Date'].astype(str)
    
    trend_data = [['Period', 'Sales', 'Profit']]
    for _, row in monthly_sales.iterrows():
        trend_data.append([
            str(row['Date']),
            f"₹{row['Sales']:,.0f}",
            f"₹{row['Profit']:,.0f}"
        ])
    
    trend_table = Table(trend_data, colWidths=[2*inch, 2*inch, 2*inch])
    trend_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white])
    ]))
    story.append(trend_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Product Performance
    story.append(Paragraph("TOP PERFORMING PRODUCTS", heading_style))
    product_performance = df.groupby('Product').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Profit_Margin': 'mean'
    }).sort_values('Profit', ascending=False).head(10).reset_index()
    
    product_data = [['Rank', 'Product', 'Sales', 'Profit', 'Margin']]
    for idx, row in product_performance.iterrows():
        product_data.append([
            str(idx + 1),
            str(row['Product'])[:30],  # Truncate long names
            f"₹{row['Sales']:,.0f}",
            f"₹{row['Profit']:,.0f}",
            f"{row['Profit_Margin']:.1f}%"
        ])
    
    product_table = Table(product_data, colWidths=[0.6*inch, 2.2*inch, 1.3*inch, 1.3*inch, 0.9*inch])
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white])
    ]))
    story.append(product_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Regional Performance
    story.append(Paragraph("REGIONAL PERFORMANCE", heading_style))
    regional_performance = df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Profit_Margin': 'mean'
    }).sort_values('Profit', ascending=False).reset_index()
    
    regional_data = [['Region', 'Sales', 'Profit', 'Margin']]
    for _, row in regional_performance.iterrows():
        regional_data.append([
            str(row['Region']),
            f"₹{row['Sales']:,.0f}",
            f"₹{row['Profit']:,.0f}",
            f"{row['Profit_Margin']:.1f}%"
        ])
    
    regional_table = Table(regional_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.2*inch])
    regional_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(regional_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Business Health Score
    story.append(Paragraph("BUSINESS HEALTH METRICS", heading_style))
    health = kpis.get('health', {})
    health_data = [
        ['Metric', 'Score', 'Status'],
        ['Overall Health', f"{health.get('health_score', 0):.1f}/100", health.get('health_status', 'N/A')],
        ['Revenue Growth', f"{health.get('revenue_growth', 0):.1f}%", '✓' if health.get('revenue_growth', 0) > 0 else '✗'],
        ['Profit Margin', f"{kpis['revenue']['avg_profit_margin']:.1f}%", '✓' if kpis['revenue']['avg_profit_margin'] > 20 else '⚠'],
    ]
    
    health_table = Table(health_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    health_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgoldenrodyellow),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(health_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    story.append(Paragraph("KEY RECOMMENDATIONS", heading_style))
    recommendations = [
        "Focus on expanding top-performing products to maximize revenue",
        "Optimize marketing spend in high-ROI regions for better returns",
        "Address underperforming product lines through strategic review",
        "Implement dynamic pricing strategies to improve margins",
        "Enhance customer retention programs to reduce acquisition costs",
        "Monitor seasonal trends for better inventory planning"
    ]
    
    for idx, rec in enumerate(recommendations, 1):
        story.append(Paragraph(f"{idx}. {rec}", styles['Normal']))
        story.append(Spacer(1, 0.08*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_html_report(df, kpis, report_type):
    """Generate complete HTML report with charts and analysis"""
    
    charts_html = generate_charts_html(df, kpis)
    
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{report_type} - Business Intelligence Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #764ba2;
            margin-top: 30px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .kpi-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .kpi-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .kpi-card .value {{
            font-size: 28px;
            font-weight: bold;
            margin: 0;
        }}
        .chart-section {{
            margin: 40px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            text-align: center;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1> {report_type}</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2> Key Performance Indicators</h2>
        <div class="kpi-grid">
            <div class="kpi-card">
                <h3>Total Sales</h3>
                <p class="value">₹{kpis['revenue']['total_sales']:,.0f}</p>
            </div>
            <div class="kpi-card">
                <h3>Total Profit</h3>
                <p class="value">₹{kpis['revenue']['total_profit']:,.0f}</p>
            </div>
            <div class="kpi-card">
                <h3>Profit Margin</h3>
                <p class="value">{kpis['revenue']['avg_profit_margin']:.1f}%</p>
            </div>
            <div class="kpi-card">
                <h3>Total Cost</h3>
                <p class="value">₹{kpis['revenue']['total_cost']:,.0f}</p>
            </div>
        </div>
        
        <div class="chart-section">
            <h2> Visual Analytics</h2>
            {charts_html}
        </div>
        
        <h2> Top Products Performance</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Product</th>
                    <th>Sales</th>
                    <th>Profit</th>
                    <th>Margin</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add top products table
    product_performance = df.groupby('Product').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Profit_Margin': 'mean'
    }).sort_values('Profit', ascending=False).head(10)
    
    for idx, (product, row) in enumerate(product_performance.iterrows(), 1):
        html_template += f"""
                <tr>
                    <td>{idx}</td>
                    <td><strong>{product}</strong></td>
                    <td>₹{row['Sales']:,.2f}</td>
                    <td>₹{row['Profit']:,.2f}</td>
                    <td>{row['Profit_Margin']:.1f}%</td>
                </tr>
"""
    
    html_template += """
            </tbody>
        </table>
        
        <h2> Regional Performance</h2>
        <table>
            <thead>
                <tr>
                    <th>Region</th>
                    <th>Sales</th>
                    <th>Profit</th>
                    <th>Orders</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add regional performance table
    regional_performance = df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Date': 'count'
    }).sort_values('Profit', ascending=False)
    regional_performance.columns = ['Sales', 'Profit', 'Orders']
    
    for region, row in regional_performance.iterrows():
        html_template += f"""
                <tr>
                    <td><strong>{region}</strong></td>
                    <td>₹{row['Sales']:,.2f}</td>
                    <td>₹{row['Profit']:,.2f}</td>
                    <td>{row['Orders']:,}</td>
                </tr>
"""
    
    html_template += f"""
            </tbody>
        </table>
        
        <h2> Strategic Recommendations</h2>
        <ol>
            <li><strong>Product Optimization:</strong> Focus on expanding top-performing products that show high profit margins</li>
            <li><strong>Cost Management:</strong> Review cost structure in underperforming regions to improve profitability</li>
            <li><strong>Marketing Strategy:</strong> Implement targeted campaigns based on regional performance data</li>
            <li><strong>Margin Improvement:</strong> Monitor and optimize profit margins across all product lines</li>
            <li><strong>Data-Driven Decisions:</strong> Continue leveraging analytics for continuous business improvement</li>
        </ol>
        
        <div class="footer">
            <p><strong>InsightIQ</strong></p>
            <p>Confidential Business Report • {datetime.now().strftime('%Y')}</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_template


def render():
    """Render reports page"""
    
    # Check authentication
    if not is_logged_in():
        render_alert("Please login to access this page", 'warning')
        st.info("Go to **Home** page to login or register.")
        if st.button("🏠 Go to Home"):
            st.session_state.main_menu = 0
            st.rerun()
        st.stop()
    
    if not st.session_state.data_uploaded or st.session_state.df is None:
        render_alert("Please upload data first!", 'warning')
        st.stop()
    
    df = st.session_state.df
    
    st.markdown("""
        <h1 class="gradient-text"> Executive Reports</h1>
        <p style="color: white; font-size: 1.1rem;">Generate comprehensive business reports with interactive charts</p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Report options
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Select Report Type",
            ["Executive Summary", "Detailed Analytics", "Performance Report", "SWOT Analysis"]
        )
    
    with col2:
        format_type = st.selectbox("Format", ["HTML with Charts", "Markdown"])
    
    if st.button(" Generate Report", type="primary", width='stretch'):
        with st.spinner("Generating comprehensive report with charts..."):
            # Calculate KPIs
            kpis = calculate_all_kpis(df)
            
            if format_type == "HTML with Charts":
                # Generate PDF report with charts
                with st.spinner("Generating PDF report with charts..."):
                    pdf_bytes = generate_pdf_report(df, kpis, report_type)
                
                st.success("PDF Report with charts generated successfully!")
                
                # Download button for PDF
                st.download_button(
                    label="Download PDF Report (with Charts)",
                    data=pdf_bytes,
                    file_name=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    type="primary",
                    width='stretch'
                )
                
                st.info("**Tip:** The PDF report includes all charts and analytics in a professional format ready for sharing.")
                
            else:
                # Generate Markdown report (original format)
                if report_type == "Executive Summary":
                    report_content = generate_executive_summary(df, kpis)
                elif report_type == "Detailed Analytics":
                    report_content = generate_detailed_analytics(df)
                elif report_type == "Performance Report":
                    report_content = generate_executive_summary(df, kpis)
                else:  # SWOT Analysis
                    swot = perform_swot_analysis(df)
                    report_content = f"""
# SWOT ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## STRENGTHS ({len(swot['strengths'])})

"""
                    for s in swot['strengths']:
                        report_content += f"- **{s['title']}:** {s['description']}\n"
                    
                    report_content += f"\n## WEAKNESSES ({len(swot['weaknesses'])})\n\n"
                    for w in swot['weaknesses']:
                        report_content += f"- **{w['title']}:** {w['description']}\n"
                    
                    report_content += f"\n## OPPORTUNITIES ({len(swot['opportunities'])})\n\n"
                    for o in swot['opportunities']:
                        report_content += f"- **{o['title']}:** {o['description']}\n"
                    
                    report_content += f"\n## THREATS ({len(swot['threats'])})\n\n"
                    for t in swot['threats']:
                        report_content += f"- **{t['title']}:** {t['description']}\n"
                
                st.success("Report generated successfully!")
                
                # Display report
                st.markdown("---")
                st.markdown(report_content)
                st.markdown("---")
                
                # Download button
                st.download_button(
                    label="Download Markdown Report",
                    data=report_content,
                    file_name=f"{report_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    type="primary",
                    width='stretch'
                )
                
                st.info("Tip: Convert Markdown to PDF using online tools or Pandoc")

