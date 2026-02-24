"""
UI Components for Streamlit App
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


def render_metric_card(title, value, delta=None, icon=None):
    """
    Render animated metric card
    """
    if icon:
        title = f"{icon} {title}"
    
    if delta:
        st.metric(label=title, value=value, delta=delta)
    else:
        st.metric(label=title, value=value)


def render_kpi_card(title, value, subtitle=None, color="#6366f1"):
    """
    Render custom KPI card with styling
    """
    html = f"""
    <div class="kpi-card" style="border-left-color: {color};">
        <h3 style="color: {color}; margin: 0; font-size: 1rem;">{title}</h3>
        <p style="font-size: 2rem; font-weight: 700; margin: 0.5rem 0; color: #1f2937;">{value}</p>
        {f'<p style="color: #6b7280; font-size: 0.875rem; margin: 0;">{subtitle}</p>' if subtitle else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_health_score(score, status, icon):
    """
    Render health score with animation
    """
    # Determine color based on status
    color_map = {
        'Healthy': '#10b981',
        'Warning': '#f59e0b',
        'Critical': '#ef4444'
    }
    color = color_map.get(status, '#6b7280')
    
    html = f"""
    <div class="health-score-container">
        <h2 style="margin: 0; font-size: 1.5rem;">Business Health Score</h2>
        <div class="health-score-value animated-metric">{score:.1f}</div>
        <div class="health-status">
            <span style="font-size: 2rem;">{icon}</span>
            <span>{status}</span>
        </div>
        <div style="margin-top: 1rem;">
            <div style="background-color: rgba(255,255,255,0.2); height: 10px; border-radius: 5px; overflow: hidden;">
                <div style="background-color: {color}; height: 100%; width: {score}%; transition: width 1s ease;"></div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_alert(message, alert_type='info'):
    """
    Render styled alert box
    """
    class_name = f"alert-{alert_type}"
    icon_map = {
        'success': '✓',
        'warning': '⚠',
        'danger': '✗',
        'info': 'ℹ'
    }
    icon = icon_map.get(alert_type, 'ℹ')
    
    html = f"""
    <div class="{class_name}">
        <strong>{icon} {message}</strong>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_insight_card(insight):
    """
    Render insight card
    """
    severity_colors = {
        'High': '#ef4444',
        'Medium': '#f59e0b',
        'Low': '#10b981',
        'Positive': '#10b981'
    }
    color = severity_colors.get(insight.get('severity', 'Low'), '#3b82f6')
    
    html = f"""
    <div class="insight-card" style="border-left-color: {color};">
        <h4 style="margin: 0; color: {color};">{insight.get('title', 'Insight')}</h4>
        <p style="margin: 0.5rem 0 0 0; color: #4b5563;">{insight.get('description', '')}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_recommendation_card(rec):
    """
    Render recommendation card
    """
    priority = rec.get('priority', 'Low')
    priority_class = f"priority-{priority.lower()}"
    
    # Build action items list
    action_items_html = ""
    for action in rec.get('action_items', []):
        action_items_html += f"<li style='color: #4b5563; margin: 0.25rem 0;'>{action}</li>"
    
    # Build complete HTML
    html = f"""<div class="recommendation-card {priority_class}">
<div style="display: flex; justify-content: space-between; align-items: center;">
<h3 style="margin: 0; color: #1f2937;">{rec.get('title', '')}</h3>
<span class="status-badge badge-{priority.lower()}">{priority} Priority</span>
</div>
<p style="color: #6b7280; margin: 0.5rem 0;"><strong>Category:</strong> {rec.get('category', '')}</p>
<p style="color: #4b5563; margin: 0.75rem 0;">{rec.get('description', '')}</p>
<div style="margin-top: 1rem;">
<strong style="color: #1f2937;">Action Items:</strong>
<ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
{action_items_html}
</ul>
</div>
<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
<p style="margin: 0; color: #059669;"><strong> Impact:</strong> {rec.get('estimated_impact', 'N/A')}</p>
<p style="margin: 0.25rem 0 0 0; color: #6b7280;"><strong>⚙️ Effort:</strong> {rec.get('implementation_effort', 'N/A')}</p>
</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def create_gauge_chart(value, title, max_value=100):
    """
    Create gauge chart for metrics
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': "#667eea"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_value * 0.5], 'color': '#fee2e2'},
                {'range': [max_value * 0.5, max_value * 0.7], 'color': '#fef3c7'},
                {'range': [max_value * 0.7, max_value], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif'}
    )
    
    return fig


def create_line_chart(df, x, y, title, color='#667eea'):
    """
    Create animated line chart
    """
    fig = px.line(df, x=x, y=y, title=title, markers=True)
    
    fig.update_traces(
        line=dict(color=color, width=3),
        marker=dict(size=8, line=dict(width=2, color='white'))
    )
    
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif'},
        title={'font': {'size': 20, 'color': '#1f2937'}},
        xaxis={'showgrid': True, 'gridcolor': '#f3f4f6'},
        yaxis={'showgrid': True, 'gridcolor': '#f3f4f6'},
        height=400
    )
    
    return fig


def create_bar_chart(df, x, y, title, color='#667eea'):
    """
    Create bar chart
    """
    fig = px.bar(df, x=x, y=y, title=title)
    
    fig.update_traces(marker_color=color, marker_line_width=0)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif'},
        title={'font': {'size': 20, 'color': '#1f2937'}},
        xaxis={'showgrid': False},
        yaxis={'showgrid': True, 'gridcolor': '#f3f4f6'},
        height=400
    )
    
    return fig


def create_pie_chart(values, names, title):
    """
    Create pie chart
    """
    fig = px.pie(values=values, names=names, title=title, hole=0.4)
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='white', width=2))
    )
    
    fig.update_layout(
        font={'family': 'Inter, sans-serif'},
        title={'font': {'size': 20, 'color': '#1f2937'}},
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    return fig


def render_progress_bar(progress, text=''):
    """
    Render progress bar
    """
    st.progress(progress, text=text)


def render_loading_message(message="Processing..."):
    """
    Render loading message with spinner
    """
    with st.spinner(message):
        pass
