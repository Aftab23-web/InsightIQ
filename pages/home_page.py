"""
Home Page
"""
import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
from utils.auth import is_logged_in, get_current_user, logout_user


@st.cache_data(ttl=3600, show_spinner=False)
def load_lottie_url(url):
    """Load Lottie animation from URL (cached for 1 hour)"""
    try:
        r = requests.get(url, timeout=1)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


def render():
    """Render home page"""
    
    # Check authentication status and show login/logout button
    if is_logged_in():
        user = get_current_user()
        col1, col2, col3 = st.columns([3, 1, 1])
        with col2:
            st.markdown(f"<div style='text-align: right; padding: 1rem; color: white;'>👤 {user['username']}<br><small>{user['role']}</small></div>", unsafe_allow_html=True)
        with col3:
            if st.button("🚪 Logout", key="logout_btn"):
                logout_user()
                st.session_state.main_menu = 0
                st.success("Logged out successfully!")
                time.sleep(1)
                st.rerun()
    else:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col2:
            if st.button(" Login", key="login_btn", width='stretch'):
                st.session_state.show_login = True
                st.session_state.show_register = False
                st.rerun()
        with col3:
            if st.button(" Register", key="register_btn", width='stretch'):
                st.session_state.show_register = True
                st.session_state.show_login = False
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Animated Header with Gradient
    st.markdown("""
        <style>
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
        }
        
        @keyframes float {
            0%, 100% {
                transform: translateY(0px);
            }
            50% {
                transform: translateY(-20px);
            }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .hero-title {
            animation: fadeInDown 1s ease-out;
        }
        
        .hero-subtitle {
            animation: fadeInUp 1.2s ease-out;
        }
        
        .feature-card {
            animation: fadeInUp 1.5s ease-out;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        }
        
        .stat-number {
            animation: pulse 2s ease-in-out infinite;
            font-size: 3rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .floating-icon {
            animation: float 3s ease-in-out infinite;
            display: inline-block;
        }
        </style>
        
        <div class="hero-title">
            <h1 class="gradient-text" style="font-size: 3.5rem; text-align: center; margin-bottom: 0; font-weight: 800;">
                 InsightIQ
            </h1>
        </div>
        <div class="hero-subtitle">
            <p style="text-align: center; font-size: 1.4rem; color: white; margin-top: 1rem; font-weight: 300;">
                Transform Raw Data into Strategic Decisions with AI-Powered Analytics
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Hero Animation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        lottie_ai = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_8nsh2rjx.json")
        if lottie_ai:
            st_lottie(lottie_ai, height=250, key="ai_animation")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Stats Counter
    st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 2rem;'>Platform Capabilities</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-card" style="text-align: center; padding: 2rem;">
                <div class="stat-number">10+</div>
                <p style="color: white; font-size: 1.1rem; margin-top: 0.5rem;">AI Models</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card" style="text-align: center; padding: 2rem;">
                <div class="stat-number">50+</div>
                <p style="color: white; font-size: 1.1rem; margin-top: 0.5rem;">KPIs Tracked</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card" style="text-align: center; padding: 2rem;">
                <div class="stat-number">100%</div>
                <p style="color: white; font-size: 1.1rem; margin-top: 0.5rem;">Automated</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-card" style="text-align: center; padding: 2rem;">
                <div class="stat-number">24/7</div>
                <p style="color: white; font-size: 1.1rem; margin-top: 0.5rem;">Monitoring</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Features with Icons
    st.markdown("<h2 style='text-align: center; color: white; margin-bottom: 2rem;'> Powerful Features</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card metric-card" style="min-height: 200px;">
                <div class="floating-icon" style="font-size: 3rem; text-align: center;"></div>
                <h3 style="color: white; text-align: center;">Deep Analytics</h3>
                <p style="color: rgba(255,255,255,0.85); text-align: center;">
                    Comprehensive EDA, trend analysis, and performance metrics across all business dimensions
                </p>
                <ul style="color: rgba(255,255,255,0.75); font-size: 0.9rem;">
                    <li>Time-series analysis</li>
                    <li>Product performance</li>
                    <li>Regional insights</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card metric-card" style="min-height: 200px;">
                <div class="floating-icon" style="font-size: 3rem; text-align: center;"></div>
                <h3 style="color: white; text-align: center;">Mistake Detection</h3>
                <p style="color: rgba(255,255,255,0.85); text-align: center;">
                    AI-powered identification of business inefficiencies and lost opportunities
                </p>
                <ul style="color: rgba(255,255,255,0.75); font-size: 0.9rem;">
                    <li>Loss-making products</li>
                    <li>Underperforming regions</li>
                    <li>Inefficient operations</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card metric-card" style="min-height: 200px;">
                <div class="floating-icon" style="font-size: 3rem; text-align: center;"></div>
                <h3 style="color: white; text-align: center;">Root Cause Analysis</h3>
                <p style="color: rgba(255,255,255,0.85); text-align: center;">
                    Understand the "why" behind every metric with AI-driven causal analysis
                </p>
                <ul style="color: rgba(255,255,255,0.75); font-size: 0.9rem;">
                    <li>Correlation analysis</li>
                    <li>Impact assessment</li>
                    <li>Factor identification</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card metric-card" style="min-height: 200px;">
                <div class="floating-icon" style="font-size: 3rem; text-align: center;"></div>
                <h3 style="color: white; text-align: center;">AI Forecasting</h3>
                <p style="color: rgba(255,255,255,0.85); text-align: center;">
                    Predict future trends with confidence intervals using Prophet & XGBoost
                </p>
                <ul style="color: rgba(255,255,255,0.75); font-size: 0.9rem;">
                    <li>Sales predictions</li>
                    <li>Risk assessment</li>
                    <li>Confidence intervals</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="feature-card metric-card" style="min-height: 200px;">
                <div class="floating-icon" style="font-size: 3rem; text-align: center;"></div>
                <h3 style="color: white; text-align: center;">Smart Recommendations</h3>
                <p style="color: rgba(255,255,255,0.85); text-align: center;">
                    Prioritized, actionable strategies with ROI estimates and implementation plans
                </p>
                <ul style="color: rgba(255,255,255,0.75); font-size: 0.9rem;">
                    <li>Priority ranking</li>
                    <li>Impact estimation</li>
                    <li>Action roadmaps</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="feature-card metric-card" style="min-height: 200px;">
                <div class="floating-icon" style="font-size: 3rem; text-align: center;"></div>
                <h3 style="color: white; text-align: center;">Scenario Analysis</h3>
                <p style="color: rgba(255,255,255,0.85); text-align: center;">
                    Simulate strategic decisions and measure impact before implementation
                </p>
                <ul style="color: rgba(255,255,255,0.75); font-size: 0.9rem;">
                    <li>What-if scenarios</li>
                    <li>Strategy simulation</li>
                    <li>Impact modeling</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # How It Works - Using Streamlit columns instead of flex
    st.markdown("""
        <h2 style="color: white; text-align: center; margin-bottom: 2rem;">⚡ How It Works</h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-card" style="text-align: center; min-height: 200px;">
                <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
                <h3 style="color: #667eea;">Step 1</h3>
                <p style="color: white;">Upload your business CSV data</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card" style="text-align: center; min-height: 200px;">
                <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
                <h3 style="color: #764ba2;">Step 2</h3>
                <p style="color: white;">AI automatically analyzes patterns</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card" style="text-align: center; min-height: 200px;">
                <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
                <h3 style="color: #667eea;">Step 3</h3>
                <p style="color: white;">Explore insights & dashboards</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-card" style="text-align: center; min-height: 200px;">
                <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
                <h3 style="color: #764ba2;">Step 4</h3>
                <p style="color: white;">Implement recommendations</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Data Format Info
    with st.expander("Required Data Format", expanded=False):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
                ### Required Columns:
                
                - **Date**: Transaction date (YYYY-MM-DD)
                - **Product**: Product name or identifier
                - **Region**: Geographic region/market
                - **Sales**: Sales amount (numeric)
                - **Cost**: Cost amount (numeric)
                - **Profit**: Profit amount (numeric)
                - **Marketing_Spend**: Marketing expenditure (numeric)
            """)
        
        with col2:
            st.markdown("""
                ### Example Data:
                ```csv
                Date,Product,Region,Sales,Cost,Profit,Marketing_Spend
                2024-01-01,Widget A,North,10000,6000,4000,500
                2024-01-02,Widget B,South,15000,9000,6000,750
                2024-01-03,Widget C,East,12000,7000,5000,600
                ```
                
                **Tip**: More data = better insights!
            """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Call to Action with Animation
    st.markdown("""
        <div style="text-align: center; padding: 2rem; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; margin: 2rem 0;">
            <h2 style="color: white; margin-bottom: 1rem;">Ready to Transform Your Business?</h2>
            <p style="color: white; font-size: 1.1rem; margin-bottom: 2rem;">
                Upload your data now and unlock AI-powered insights in seconds!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(" Upload Data Now", type="primary", width='stretch', key="upload_data_cta"):
            st.session_state.main_menu = 1
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Trust Indicators
    st.markdown("""
        <div style="text-align: center; padding: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
            <p style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">
                 Lightning Fast •  Secure •  Accurate •  Scalable
            </p>
        </div>
    """, unsafe_allow_html=True)
