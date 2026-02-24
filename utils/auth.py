"""
Authentication Utilities
"""
import hashlib
import streamlit as st
from database.models import User, get_session
from datetime import datetime

# Admin credentials
ADMIN_EMAIL = "aftabshah2309@gmail.com"
ADMIN_PASSWORD = "admin2309"


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash


def is_admin(email, password):
    """Check if credentials are admin credentials"""
    return email == ADMIN_EMAIL and password == ADMIN_PASSWORD


def register_user(username, email, password, role, company_name, company_id, contact_number):
    """Register a new user"""
    session = get_session()
    
    try:
        # Check if username or email already exists
        existing_user = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                return False, "Username already exists"
            else:
                return False, "Email already exists"
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=role,
            company_name=company_name,
            company_id=company_id,
            contact_number=contact_number
        )
        
        session.add(new_user)
        session.commit()
        return True, "Registration successful"
        
    except Exception as e:
        session.rollback()
        return False, f"Registration failed: {str(e)}"
    finally:
        session.close()


def login_user(username, password):
    """Authenticate user login"""
    # Check if admin login
    if username == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        return True, {
            'id': 0,
            'username': 'Admin',
            'email': ADMIN_EMAIL,
            'role': 'Administrator',
            'company_name': 'System Admin',
            'company_id': 'ADMIN',
            'contact_number': 'N/A',
            'is_admin': True
        }
    
    session = get_session()
    
    try:
        user = session.query(User).filter(User.username == username).first()
        
        if not user:
            # User doesn't exist
            return False, "USER_NOT_FOUND"
        
        if verify_password(password, user.password_hash):
            if user.is_active:
                # Update last login
                user.last_login = datetime.utcnow()
                session.commit()
                
                return True, {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'company_name': user.company_name,
                    'company_id': user.company_id,
                    'contact_number': user.contact_number,
                    'is_admin': False
                }
            else:
                return False, "Account is deactivated"
        else:
            return False, "Invalid password"
            
    except Exception as e:
        return False, f"Login failed: {str(e)}"
    finally:
        session.close()


def logout_user():
    """Logout current user"""
    if 'user' in st.session_state:
        del st.session_state.user
    if 'logged_in' in st.session_state:
        del st.session_state.logged_in


def is_user_admin():
    """Check if current user is admin"""
    user = get_current_user()
    return user and user.get('is_admin', False)


def is_logged_in():
    """Check if user is logged in"""
    return st.session_state.get('logged_in', False)


def get_current_user():
    """Get current logged in user"""
    return st.session_state.get('user', None)


def require_auth():
    """Decorator to require authentication for a page"""
    if not is_logged_in():
        st.warning(" Please login to access this page")
        st.stop()
