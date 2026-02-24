"""
Data Upload Page
"""
import streamlit as st
import pandas as pd

from utils import validate_data, clean_data, engineer_features, get_data_summary
from utils.auth import is_logged_in, get_current_user
from database import save_raw_data, save_cleaned_data, generate_batch_id
from ui import render_alert


def process_uploaded_file(uploaded_file):
    """Process uploaded file with caching"""
    df = pd.read_csv(uploaded_file)
    return df


def render():
    """Render data upload page"""
    
    # Check if user is logged in
    if not is_logged_in():
        st.warning(" You must be logged in to upload data")
        st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <h3>Please login to continue</h3>
                <p>You need to be authenticated to upload and analyze data.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button(" Go to Login", width='stretch'):
                st.session_state.show_login = True
                st.session_state.main_menu = 0
                st.rerun()
        with col2:
            if st.button(" Register", width='stretch'):
                st.session_state.show_register = True
                st.session_state.main_menu = 0
                st.rerun()
        with col3:
            if st.button(" Go to Home", width='stretch'):
                st.session_state.main_menu = 0
                st.rerun()
        st.stop()
    
    # Display current user
    user = get_current_user()
    st.info(f"👤 Logged in as: **{user['username']}** ({user['role']})")
    
    st.markdown("""
        <h1 class="gradient-text"> Data Upload & Processing</h1>
        <p style="color: white; font-size: 1.1rem;">Upload your business data to begin analysis</p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file with columns: Date, Product, Region, Sales, Cost, Profit, Marketing_Spend",
        key="data_upload_file"
    )
    
    if uploaded_file is not None:
        try:
            # Read the file
            df = process_uploaded_file(uploaded_file)
            
            st.success(f"✓ File loaded successfully: {len(df)} records")
            
            # Show data preview
            with st.expander(" Data Preview", expanded=True):
                st.dataframe(df.head(10), width='stretch')
                st.info(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
            
            # Validate data
            st.markdown("###  Data Validation")
            is_valid, messages = validate_data(df)
            
            if not is_valid:
                # Separate errors from warnings
                errors = [msg for msg in messages if not msg.startswith('⚠️') and not msg.startswith('ℹ️')]
                warnings = [msg for msg in messages if msg.startswith('⚠️') or msg.startswith('ℹ️')]
                
                render_alert(" Data validation failed:", 'danger')
                for error in errors:
                    st.error(f"• {error}")
                
                if warnings:
                    for warning in warnings:
                        st.warning(warning)
                
                st.stop()
            else:
                # Check if there are any warnings
                warnings = [msg for msg in messages if msg.startswith('⚠️') or msg.startswith('ℹ️')]
                if warnings:
                    st.info("📋 **Data Quality Notes:**")
                    for warning in warnings:
                        st.warning(warning)
                
                render_alert("✓ Data validation passed!", 'success')
            
            # Clean data and process
            st.markdown("###  Data Cleaning & Processing")
            
            with st.spinner("Cleaning and processing data..."):
                cleaned_df, cleaning_report = clean_data(df)
                processed_df = engineer_features(cleaned_df)
            
            st.success(f"✓ Data cleaned and processed: {len(processed_df)} records")
            
            # Show cleaning report if any operations were performed
            if any([cleaning_report['rows_removed'], cleaning_report['nulls_filled'], 
                    cleaning_report['outliers_capped'], cleaning_report['duplicates_removed']]):
                with st.expander("🔧 View Data Cleaning Report", expanded=False):
                    if cleaning_report['rows_removed'] > 0:
                        st.info(f"🗑️ Removed {cleaning_report['rows_removed']} rows with invalid dates")
                    
                    if cleaning_report['nulls_filled']:
                        st.info("📝 **Null Values Handled:**")
                        for col, info in cleaning_report['nulls_filled'].items():
                            if 'value' in info:
                                st.write(f"  • {col}: {info['count']} nulls filled with {info['filled_with']} ({info['value']:.2f})")
                            else:
                                st.write(f"  • {col}: {info['count']} nulls filled with '{info['filled_with']}'")
                    
                    if cleaning_report['duplicates_removed'] > 0:
                        st.info(f"🔄 Removed {cleaning_report['duplicates_removed']} duplicate records")
                    
                    if cleaning_report['outliers_capped']:
                        st.info("📊 **Outliers Capped:**")
                        for col, count in cleaning_report['outliers_capped'].items():
                            st.write(f"  • {col}: {count} outliers capped to reasonable ranges")
            
            # Show data summary
            st.markdown("### Data Summary")
            summary = get_data_summary(processed_df)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Records", f"{summary['total_records']:,}")
            
            with col2:
                st.metric("Products", summary['products'])
            
            with col3:
                st.metric("Regions", summary['regions'])
            
            with col4:
                st.metric("Date Range", f"{summary['date_range']['days']} days")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Sales", f"₹{summary['total_sales']:,.2f}")
            
            with col2:
                st.metric("Total Profit", f"₹{summary['total_profit']:,.2f}")
            
            with col3:
                st.metric("Avg Profit Margin", f"{summary['avg_profit_margin']:.1f}%")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Save to database button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(" Save & Continue", type="primary", width='stretch', key="save_btn"):
                    try:
                        # Generate batch ID
                        batch_id = generate_batch_id()
                        
                        # Save raw data
                        save_raw_data(df, batch_id)
                        
                        # Save cleaned data
                        save_cleaned_data(processed_df, batch_id)
                        
                        # Update session state
                        st.session_state.df = processed_df
                        st.session_state.batch_id = batch_id
                        st.session_state.data_uploaded = True
                        st.session_state.analysis_complete = True
                        st.session_state.main_menu = 2
                        
                        st.success("✓ Data saved successfully!")
                        st.balloons()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f" Error saving data: {str(e)}")
        
        except Exception as e:
            st.error(f" Error processing file: {str(e)}")
            st.info("Please check your file format and try again.")
    
    else:
        # Show upload instructions
        st.markdown("""
            <div class="metric-card">
                <h3 style="color: white;"> Data Format Requirements</h3>
                <p style="color: rgba(255,255,255,0.9);">
                    Your CSV file must contain these columns:
                </p>
                <ul style="color: rgba(255,255,255,0.8);">
                    <li><strong>Date:</strong> Transaction date (YYYY-MM-DD)</li>
                    <li><strong>Product:</strong> Product name</li>
                    <li><strong>Region:</strong> Geographic region</li>
                    <li><strong>Sales:</strong> Sales amount (numeric)</li>
                    <li><strong>Cost:</strong> Cost amount (numeric)</li>
                    <li><strong>Profit:</strong> Profit amount (numeric)</li>
                    <li><strong>Marketing_Spend:</strong> Marketing spend (numeric)</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        # Show sample data
        st.markdown("### Sample Data Format")
        sample_df = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Product': ['Widget A', 'Widget B', 'Widget A'],
            'Region': ['North', 'South', 'East'],
            'Sales': [10000, 15000, 12000],
            'Cost': [6000, 9000, 7000],
            'Profit': [4000, 6000, 5000],
            'Marketing_Spend': [500, 750, 600]
        })
        st.dataframe(sample_df, width='stretch')
