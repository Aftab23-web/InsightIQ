"""
Main Streamlit Application - InsightIQ
"""
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import APP_CONFIG
from ui import get_custom_css
from database import init_db

# Page configuration
st.set_page_config(
    page_title=APP_CONFIG['title'],
    layout=APP_CONFIG['layout'],
    initial_sidebar_state='expanded'
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize database (optional - for persistence)
try:
    init_db()
except Exception as e:
    # Database not required for basic functionality
    pass

# Initialize session state
if 'data_uploaded' not in st.session_state:
    st.session_state.data_uploaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'batch_id' not in st.session_state:
    st.session_state.batch_id = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'nav_selection' not in st.session_state:
    st.session_state.nav_selection = "Home"
if 'main_menu' not in st.session_state:
    st.session_state.main_menu = 0
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'show_register' not in st.session_state:
    st.session_state.show_register = False

# Check if we need to show login or register page
if st.session_state.show_login:
    from pages import login_page
    login_page.render()
    st.stop()

if st.session_state.show_register:
    from pages import register_page
    register_page.render()
    st.stop()

# Sidebar navigation
with st.sidebar:
    st.markdown(f"<h2 style='text-align: center; color: white; font-size: 1.5rem;'>{APP_CONFIG['title']}</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
    
    # Check if admin user
    user = st.session_state.get('user', {})
    is_admin = user.get('is_admin', False) if user else False
    
    if is_admin:
        # Admin menu
        menu_options = [
            "Home",
            "Admin Dashboard"
        ]
        
        selected = option_menu(
            menu_title="Admin Menu",
            options=menu_options,
            icons=[
                "house-fill",
                "shield-lock-fill"
            ],
            menu_icon="cast",
            default_index=st.session_state.main_menu,
            key="main_menu_widget",
            styles={
                "container": {"padding": "5px", "background-color": "transparent"},
                "icon": {"color": "#667eea", "font-size": "20px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "5px",
                    "color": "white",
                    "border-radius": "10px"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "font-weight": "600"
                },
            }
        )
    else:
        # Regular user menu
        menu_options = [
            "Home",
            "Data Upload",
            "Executive Dashboard",
            "Analytics",
            "Insights & SWOT",
            "Forecasting",
            "Recommendations",
            "Reports"
        ]
        
        selected = option_menu(
            menu_title="Navigation",
            options=menu_options,
            icons=[
                "house-fill",
                "cloud-upload-fill",
                "speedometer2",
                "bar-chart-fill",
                "lightbulb-fill",
                "graph-up-arrow",
                "clipboard-check-fill",
                "file-earmark-text-fill"
            ],
            menu_icon="cast",
            default_index=st.session_state.main_menu,
            key="main_menu_widget",
            styles={
                "container": {"padding": "5px", "background-color": "transparent"},
                "icon": {"color": "#667eea", "font-size": "20px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "5px",
                    "color": "white",
                    "border-radius": "10px"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "font-weight": "600"
                },
            }
        )
    
    # Update session state when menu selection changes
    selected_index = menu_options.index(selected)
    if selected_index != st.session_state.main_menu:
        st.session_state.main_menu = selected_index
        st.session_state.nav_selection = selected
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
    
    # User info if logged in
    if st.session_state.logged_in and st.session_state.user:
        user = st.session_state.user
        st.markdown(f"""
            <div style='padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 10px; margin-bottom: 1rem;'>
                <p style='color: white; margin: 0;'><b>👤 {user['username']}</b></p>
                <p style='color: rgba(255,255,255,0.7); font-size: 0.85rem; margin: 0.25rem 0 0 0;'>{user['role']}</p>
                <p style='color: rgba(255,255,255,0.6); font-size: 0.8rem; margin: 0.25rem 0 0 0;'>🏢 {user['company_name']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Status indicator
    if st.session_state.data_uploaded:
        st.success("✓ Data Loaded")
        if st.session_state.analysis_complete:
            st.success("✓ Analysis Complete")
    else:
        st.info("⚠ No Data Loaded")
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.5); font-size: 0.8rem;'>© 2026 AI Business Intelligence</p>", unsafe_allow_html=True)

# Main content area
if selected == "Home":
    from pages import home_page
    home_page.render()

elif selected == "Admin Dashboard":
    from pages import admin_dashboard_page
    admin_dashboard_page.render()
    
elif selected == "Data Upload":
    from pages import data_upload_page
    data_upload_page.render()
    
elif selected == "Executive Dashboard":
    from pages import executive_dashboard_page
    executive_dashboard_page.render()
    
elif selected == "Analytics":
    from pages import analytics_page
    analytics_page.render()
    
elif selected == "Insights & SWOT":
    from pages import insights_page
    insights_page.render()
    
elif selected == "Forecasting":
    from pages import forecasting_page
    forecasting_page.render()
    
elif selected == "Recommendations":
    from pages import recommendations_page
    recommendations_page.render()
    
elif selected == "Reports":
    from pages import reports_page
    reports_page.render()
