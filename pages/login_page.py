"""
Login Page
"""
import streamlit as st
from utils.auth import login_user


def render():
    """Render login page"""
    
    # Header
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; 
                       -webkit-text-fill-color: transparent;
                       font-size: 3rem; font-weight: bold;'>
                 Login
            </h1>
            <p style='color: #888; font-size: 1.2rem;'>Welcome back! Please login to your account</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Login Form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("###  Enter your Details")
            
            username = st.text_input("Username or Email", placeholder="Enter your username or email", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Submit button
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                submit = st.form_submit_button(" Login", width='stretch')
            
            if submit:
                if not username or not password:
                    st.error(" Please enter both username and password")
                else:
                    # Attempt login
                    success, result = login_user(username, password)
                    
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = result
                        st.session_state.show_login = False
                        st.session_state.show_register = False
                        
                        # Set menu based on user role
                        if result.get('is_admin', False):
                            st.session_state.main_menu = 1  # Admin Dashboard
                            st.success(f" Welcome back, Admin {result['username']}!")
                            st.info(" Redirecting to Admin Dashboard...")
                        else:
                            st.session_state.main_menu = 0  # Home page
                            st.success(f" Welcome back, {result['username']}!")
                            st.info(" Redirecting to home page...")
                        
                        st.balloons()
                        
                        # Small delay for user to see the message
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        # Check if user doesn't exist
                        if result == "USER_NOT_FOUND":
                            st.warning(f" User '{username}' not found. Looks like you're new here!")
                            st.info(" Redirecting to registration page...")
                            import time
                            time.sleep(2)
                            st.session_state.show_register = True
                            st.session_state.show_login = False
                            st.rerun()
                        else:
                            st.error(f" {result}")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Link to registration
        st.markdown("""
            <div style='text-align: center;'>
                <p>Don't have an account?</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_x, col_y, col_z = st.columns([1, 2, 1])
        with col_y:
            if st.button(" Register Here", width='stretch'):
                st.session_state.show_register = True
                st.rerun()
