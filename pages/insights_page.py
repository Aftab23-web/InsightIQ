"""
Insights & SWOT Page
"""
import streamlit as st
from analytics.swot_analysis import perform_swot_analysis
from ui import render_alert
from utils.auth import is_logged_in


def render():
    """Render insights page"""
    
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
        <h1 class="gradient-text"> Insights & SWOT Analysis</h1>
        <p style="color: white; font-size: 1.1rem;">Strategic business insights to guide your decisions</p>
    """, unsafe_allow_html=True)
    
    # SWOT Explanation
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); 
                padding: 1.5rem; border-radius: 10px; border-left: 4px solid #667eea; margin: 1rem 0 2rem 0;">
        <h3 style="color: white; margin: 0 0 0.5rem 0;"> What is SWOT Analysis?</h3>
        <p style="color: rgba(255,255,255,0.85); margin: 0; line-height: 1.6;">
            SWOT helps you understand your business position by analyzing four key areas:<br>
            • <strong>Strengths</strong> - What you're doing well (your competitive advantages)<br>
            • <strong>Weaknesses</strong> - Areas that need improvement<br>
            • <strong>Opportunities</strong> - Potential ways to grow and improve<br>
            • <strong>Threats</strong> - External challenges to watch out for
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Analyzing your business data..."):
        swot = perform_swot_analysis(df)
    
    # SWOT Matrix
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("###  Strengths (What You're Good At)")
        st.markdown("<p style='color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-bottom: 1rem;'>These are your competitive advantages - keep doing these!</p>", unsafe_allow_html=True)
        
        if swot['strengths']:
            for idx, strength in enumerate(swot['strengths'], 1):
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%); 
                            padding: 1.2rem; border-radius: 10px; border-left: 4px solid #10b981; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="background: #10b981; color: white; border-radius: 50%; 
                                    width: 28px; height: 28px; display: flex; align-items: center; 
                                    justify-content: center; font-weight: bold; margin-right: 0.8rem;">
                            {idx}
                        </span>
                        <h4 style="color: #10b981; margin: 0; font-size: 1.1rem;">{strength['title']}</h4>
                    </div>
                    <p style="color: white; margin: 0; line-height: 1.6; font-size: 0.95rem;">
                        {strength['description']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(" No clear strengths identified yet. Upload more data to get better insights.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("###  Opportunities (Ways to Grow)")
        st.markdown("<p style='color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-bottom: 1rem;'>These are potential areas for growth and improvement.</p>", unsafe_allow_html=True)
        
        if swot['opportunities']:
            for idx, opp in enumerate(swot['opportunities'], 1):
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.15) 100%); 
                            padding: 1.2rem; border-radius: 10px; border-left: 4px solid #3b82f6; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="background: #3b82f6; color: white; border-radius: 50%; 
                                    width: 28px; height: 28px; display: flex; align-items: center; 
                                    justify-content: center; font-weight: bold; margin-right: 0.8rem;">
                            {idx}
                        </span>
                        <h4 style="color: #3b82f6; margin: 0; font-size: 1.1rem;">{opp['title']}</h4>
                    </div>
                    <p style="color: white; margin: 0; line-height: 1.6; font-size: 0.95rem;">
                        {opp['description']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(" Consider expanding to new markets or launching new products to find growth opportunities.")
    
    with col2:
        st.markdown("###  Weaknesses (Areas to Improve)")
        st.markdown("<p style='color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-bottom: 1rem;'>These areas need attention to strengthen your business.</p>", unsafe_allow_html=True)
        
        if swot['weaknesses']:
            for idx, weakness in enumerate(swot['weaknesses'], 1):
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.15) 100%); 
                            padding: 1.2rem; border-radius: 10px; border-left: 4px solid #f59e0b; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="background: #f59e0b; color: white; border-radius: 50%; 
                                    width: 28px; height: 28px; display: flex; align-items: center; 
                                    justify-content: center; font-weight: bold; margin-right: 0.8rem;">
                            {idx}
                        </span>
                        <h4 style="color: #f59e0b; margin: 0; font-size: 1.1rem;">{weakness['title']}</h4>
                    </div>
                    <p style="color: white; margin: 0; line-height: 1.6; font-size: 0.95rem;">
                        {weakness['description']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%); 
                        padding: 1.2rem; border-radius: 10px; border-left: 4px solid #10b981;">
                <p style="color: white; margin: 0; line-height: 1.6;">
                     <strong>Great news!</strong> No significant weaknesses detected in your current business operations. 
                    Your business is performing well across all metrics.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("###  Threats (Risks to Watch)")
        st.markdown("<p style='color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-bottom: 1rem;'>External challenges that could impact your business.</p>", unsafe_allow_html=True)
        
        if swot['threats']:
            for idx, threat in enumerate(swot['threats'], 1):
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%); 
                            padding: 1.2rem; border-radius: 10px; border-left: 4px solid #ef4444; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="background: #ef4444; color: white; border-radius: 50%; 
                                    width: 28px; height: 28px; display: flex; align-items: center; 
                                    justify-content: center; font-weight: bold; margin-right: 0.8rem;">
                            {idx}
                        </span>
                        <h4 style="color: #ef4444; margin: 0; font-size: 1.1rem;">{threat['title']}</h4>
                    </div>
                    <p style="color: white; margin: 0; line-height: 1.6; font-size: 0.95rem;">
                        {threat['description']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%); 
                        padding: 1.2rem; border-radius: 10px; border-left: 4px solid #10b981;">
                <p style="color: white; margin: 0; line-height: 1.6;">
                     <strong>All clear!</strong> No immediate threats identified. Continue monitoring market conditions 
                    and stay alert to industry changes.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Action Plan
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%); 
                padding: 2rem; border-radius: 15px; border: 2px solid rgba(139, 92, 246, 0.3);">
        <h3 style="color: white; margin: 0 0 1rem 0;"> What Should You Do Next?</h3>
        <div style="color: rgba(255,255,255,0.85); line-height: 1.8;">
            <p style="margin: 0.5rem 0;"><strong>1. Build on Strengths:</strong> Double down on what's working well</p>
            <p style="margin: 0.5rem 0;"><strong>2. Fix Weaknesses:</strong> Create action plans to address weak areas</p>
            <p style="margin: 0.5rem 0;"><strong>3. Seize Opportunities:</strong> Invest in high-potential growth areas</p>
            <p style="margin: 0.5rem 0;"><strong>4. Mitigate Threats:</strong> Develop contingency plans for risks</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Call to action - Navigate to Forecasting
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" See Forecasting", type="primary", width='stretch', key="see_forecasting_cta"):
            st.session_state.main_menu = 5
            st.rerun()
