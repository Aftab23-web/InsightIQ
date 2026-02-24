"""
Recommendations Page
"""
import streamlit as st
from analytics.recommendation_engine import generate_all_recommendations
from analytics.mistake_detection import detect_all_mistakes
from analytics.swot_analysis import perform_swot_analysis
from analytics.kpi_calculator import calculate_all_kpis
from ui import render_alert, render_recommendation_card
from utils.auth import is_logged_in


def render():
    """Render recommendations page"""
    
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
        <h1 class="gradient-text"> Recommendations</h1>
        <p style="color: white; font-size: 1.1rem;">Actionable strategies to improve performance</p>
    """, unsafe_allow_html=True)
    
    with st.spinner("Generating recommendations..."):
        mistakes = detect_all_mistakes(df)
        kpis = calculate_all_kpis(df)
        swot = perform_swot_analysis(df)
        
        recommendations = generate_all_recommendations(df, mistakes, kpis, swot)
    
    # Summary
    st.markdown("###  Recommendation Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    summary = recommendations['summary']
    
    col1.metric("Total", summary['total_recommendations'])
    col2.metric("Critical", summary['critical'])
    col3.metric("High", summary['high'])
    col4.metric("Medium", summary['medium'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recommendations by priority
    priority_filter = st.selectbox("Filter by Priority", ["All", "Critical", "High", "Medium", "Low"])
    
    recs = recommendations['recommendations']
    
    if priority_filter != "All":
        recs = [r for r in recs if r['priority'] == priority_filter]
    
    st.markdown(f"### Showing {len(recs)} Recommendations")
    
    for rec in recs:
        render_recommendation_card(rec)
    
    # Call to action - Navigate to Reports
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" Generate a Report", type="primary", width='stretch', key="generate_report_cta"):
            st.session_state.main_menu = 7
            st.rerun()
