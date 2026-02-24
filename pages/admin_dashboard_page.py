"""
Admin Dashboard Page
"""
import streamlit as st
import pandas as pd
from database.models import User, RawData, CleanedData, get_session
from utils.auth import is_user_admin
from datetime import datetime, timedelta
from sqlalchemy import func


def get_all_companies():
    """Get all registered companies"""
    session = get_session()
    try:
        users = session.query(User).all()
        companies_data = []
        for user in users:
            companies_data.append({
                'Username': user.username,
                'Email': user.email,
                'Role': user.role,
                'Company Name': user.company_name,
                'Company ID': user.company_id,
                'Contact': user.contact_number,
                'Created At': user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'N/A',
                'Last Login': user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
                'Status': 'Active' if user.is_active else 'Inactive'
            })
        return pd.DataFrame(companies_data)
    except Exception as e:
        st.error(f"Error fetching companies: {e}")
        return pd.DataFrame()
    finally:
        session.close()


def get_usage_statistics():
    """Get usage statistics"""
    session = get_session()
    try:
        total_users = session.query(User).count()
        active_users = session.query(User).filter(User.is_active == True).count()
        total_data_uploads = session.query(RawData.batch_id).distinct().count()
        total_records = session.query(RawData).count()
        
        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_users = session.query(User).filter(User.created_at >= thirty_days_ago).count()
        
        # Recent logins (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_logins = session.query(User).filter(User.last_login >= seven_days_ago).count()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_data_uploads': total_data_uploads,
            'total_records': total_records,
            'recent_users': recent_users,
            'recent_logins': recent_logins
        }
    except Exception as e:
        st.error(f"Error fetching statistics: {e}")
        return {}
    finally:
        session.close()


def render():
    """Render admin dashboard"""
    
    # Check if user is admin
    if not is_user_admin():
        st.error(" Access Denied: Admin privileges required")
        st.info("This page is only accessible to system administrators.")
        if st.button(" Go to Home"):
            st.session_state.main_menu = 0
            st.rerun()
        st.stop()
    
    st.markdown("""
        <h1 class="gradient-text"> Admin Dashboard</h1>
        <p style="color: white; font-size: 1.1rem;">System Overview & Company Management</p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Get statistics
    stats = get_usage_statistics()
    
    # Overview Statistics
    st.markdown("### System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-card" style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;">
                <div style="font-size: 2.5rem; font-weight: bold; color: white;">{}</div>
                <p style="color: white; font-size: 1rem; margin-top: 0.5rem;">Total Companies</p>
            </div>
        """.format(stats.get('total_users', 0)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card" style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border-radius: 10px;">
                <div style="font-size: 2.5rem; font-weight: bold; color: white;">{}</div>
                <p style="color: white; font-size: 1rem; margin-top: 0.5rem;">Active Users</p>
            </div>
        """.format(stats.get('active_users', 0)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card" style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); border-radius: 10px;">
                <div style="font-size: 2.5rem; font-weight: bold; color: white;">{}</div>
                <p style="color: white; font-size: 1rem; margin-top: 0.5rem;">Data Uploads</p>
            </div>
        """.format(stats.get('total_data_uploads', 0)), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-card" style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 10px;">
                <div style="font-size: 2.5rem; font-weight: bold; color: white;">{:,}</div>
                <p style="color: white; font-size: 1rem; margin-top: 0.5rem;">Total Records</p>
            </div>
        """.format(stats.get('total_records', 0)), unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Recent Activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label=" New Registrations (Last 30 Days)",
            value=stats.get('recent_users', 0),
            delta=f"{stats.get('recent_users', 0)} new companies"
        )
    
    with col2:
        st.metric(
            label=" Active Logins (Last 7 Days)",
            value=stats.get('recent_logins', 0),
            delta=f"{stats.get('recent_logins', 0)} active users"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Company Management Section
    st.markdown("###  Registered Companies")
    
    companies_df = get_all_companies()
    
    if not companies_df.empty:
        st.dataframe(
            companies_df,
            width='stretch',
            height=400
        )
        
        # Download option
        csv = companies_df.to_csv(index=False)
        st.download_button(
            label=" Download Companies Data (CSV)",
            data=csv,
            file_name=f"companies_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No companies registered yet.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # System Info
    st.markdown("### System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Admin User:** Administrator  
        **Email:** {st.session_state.user['email']}  
        **Access Level:** Full System Access  
        **Dashboard:** Real-time Monitoring
        """)
    
    with col2:
        st.success(f"""
        **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
        **Database:** Connected  
        **Status:**  All Systems Operational  
        **Version:** 1.0.0
        """)
