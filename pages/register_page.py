"""
Registration Page
"""
import streamlit as st
from utils.auth import register_user
import re


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""


def render():
    """Render registration page"""
    
    # Header
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       -webkit-background-clip: text; 
                       -webkit-text-fill-color: transparent;
                       font-size: 3rem; font-weight: bold;'>
                 Register
            </h1>
            <p style='color: #888; font-size: 1.2rem;'>Create your account to get started</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Registration Form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("registration_form", clear_on_submit=False):
            st.markdown("###  Company Information")
            
            name = st.text_input("Name *", placeholder="Enter your name")
            username = st.text_input("Username *", placeholder="Enter your username")
            email = st.text_input("Company Email *", placeholder="Enter your company email address")
            password = st.text_input("Password *", type="password", placeholder="Enter your password")
            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Re-enter your password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            role = st.selectbox(
                "Role *",
                options=[
                    "Company_Manager",
                    "Data Analytics",
                    "Vice President",
                    "CEO",
                    "Owner"
                ],
                index=0
            )
            
            company_name = st.text_input("Company Name *", placeholder="Enter your company name")
            company_id = st.text_input("Company ID *", placeholder="Enter your company ID")
            contact_number = st.text_input("Contact Number (Company) *", placeholder="Enter company contact number")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Submit button
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                submit = st.form_submit_button(" Register", width='stretch')
            
            if submit:
                # Validation
                errors = []
                
                if not username or not email or not password or not confirm_password:
                    errors.append(" All fields marked with * are required")
                
                if not company_name or not company_id or not contact_number:
                    errors.append(" All company fields are required")
                
                if username and len(username) < 3:
                    errors.append(" Username must be at least 3 characters long")
                
                if email and not validate_email(email):
                    errors.append(" Invalid email format")
                
                if password:
                    is_valid, msg = validate_password(password)
                    if not is_valid:
                        errors.append(f" {msg}")
                
                if password != confirm_password:
                    errors.append(" Passwords do not match")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Register user
                    success, message = register_user(
                        username=username,
                        email=email,
                        password=password,
                        role=role,
                        company_name=company_name,
                        company_id=company_id,
                        contact_number=contact_number
                    )
                    
                    if success:
                        st.success(" " + message)
                        st.balloons()
                        
                        # Auto-login the newly registered user
                        from utils.auth import login_user
                        login_success, user_data = login_user(username, password)
                        
                        if login_success:
                            st.session_state.logged_in = True
                            st.session_state.user = user_data
                            st.session_state.show_register = False
                            st.session_state.show_login = False
                            st.session_state.main_menu = 0
                            st.info(" Redirecting to home page...")
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Auto-redirect to home page after 1 second
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.info(" Redirecting to login page...")
                            import time
                            time.sleep(2)
                            st.session_state.show_register = False
                            st.session_state.show_login = True
                            st.rerun()
                    else:
                        st.error(" " + message)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Link to login
        st.markdown("""
            <div style='text-align: center;'>
                <p>Already have an account?</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_x, col_y, col_z = st.columns([1, 2, 1])
        with col_y:
            if st.button(" Login Here", width='stretch'):
                st.session_state.show_register = False
                st.rerun()
