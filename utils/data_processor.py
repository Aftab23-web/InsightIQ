"""
Data Processing and Cleaning Module
"""
import pandas as pd
import numpy as np
from datetime import datetime
from config import REQUIRED_COLUMNS


def validate_data(df):
    """
    Validate uploaded data structure and content
    Returns: (is_valid, errors_list)
    """
    errors = []
    warnings = []
    
    # Check required columns
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")
    
    if errors:
        return False, errors
    
    # Check for null values in all columns
    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    total_nulls = null_counts.sum()
    
    if total_nulls > 0:
        warnings.append(f"⚠️ Found {total_nulls} null/missing values across dataset:")
        for col, count in null_counts.items():
            if count > 0:
                percentage = (count / len(df)) * 100
                warnings.append(f"  • {col}: {count} null values ({percentage:.1f}%)")
        warnings.append("ℹ️ Null values will be automatically handled during data cleaning")
    
    # Check data types and ranges
    try:
        # Validate Date column - handle multiple date formats
        df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=True, errors='coerce')
        
        # Check for invalid dates
        if df['Date'].isnull().any():
            invalid_count = df['Date'].isnull().sum()
            errors.append(f"Found {invalid_count} invalid date(s). Please use format: DD-MM-YYYY, YYYY-MM-DD, or MM/DD/YYYY")
        
        # Validate numeric columns
        numeric_cols = ['Sales', 'Cost', 'Profit', 'Marketing_Spend']
        for col in numeric_cols:
            if not pd.api.types.is_numeric_dtype(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # Check if conversion created new NaN values
                    new_nulls = df[col].isnull().sum()
                    if new_nulls > 0:
                        warnings.append(f"⚠️ Converted {new_nulls} non-numeric values in '{col}' to null")
                except:
                    errors.append(f"Column {col} must contain numeric values")
        
        # Check for negative values where inappropriate
        if (df['Sales'] < 0).any():
            errors.append("Sales cannot be negative")
        if (df['Cost'] < 0).any():
            errors.append("Cost cannot be negative")
        if (df['Marketing_Spend'] < 0).any():
            errors.append("Marketing Spend cannot be negative")
            
    except Exception as e:
        errors.append(f"Data validation error: {str(e)}")
    
    # Return validation result with both errors and warnings
    return len(errors) == 0, errors + warnings


def clean_data(df):
    """
    Clean and preprocess data with comprehensive null handling
    Returns: (cleaned_df, cleaning_report)
    """
    df = df.copy()
    
    # Convert all categorical columns to object type to avoid category errors
    for col in df.columns:
        if pd.api.types.is_categorical_dtype(df[col]):
            df[col] = df[col].astype('object')
    
    cleaning_report = {
        'rows_removed': 0,
        'nulls_filled': {},
        'outliers_capped': {},
        'duplicates_removed': 0
    }
    
    initial_rows = len(df)
    
    # Convert Date to datetime - handle multiple date formats
    df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=True, errors='coerce')
    
    # Remove rows with invalid dates
    invalid_dates = df['Date'].isnull().sum()
    df = df.dropna(subset=['Date'])
    if invalid_dates > 0:
        cleaning_report['rows_removed'] += invalid_dates
    
    # Handle missing values in numeric columns
    # Fill with median (robust to outliers)
    numeric_cols = ['Sales', 'Cost', 'Profit', 'Marketing_Spend']
    for col in numeric_cols:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            # Use median for better robustness
            median_val = df[col].median()
            # If median is NaN (all values are null), use 0
            if pd.isna(median_val):
                median_val = 0
            df[col].fillna(median_val, inplace=True)
            cleaning_report['nulls_filled'][col] = {'count': null_count, 'filled_with': 'median', 'value': float(median_val)}
    
    # For categorical columns, fill with 'Unknown'
    categorical_cols = ['Product', 'Region']
    for col in categorical_cols:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            # Already converted to object type at start, but double-check
            df[col].fillna('Unknown', inplace=True)
            cleaning_report['nulls_filled'][col] = {'count': null_count, 'filled_with': 'Unknown'}
    
    # Remove duplicates
    duplicates = df.duplicated().sum()
    df = df.drop_duplicates()
    cleaning_report['duplicates_removed'] = int(duplicates)
    
    # Handle outliers using IQR method
    for col in numeric_cols:
        if len(df) > 0:  # Check if dataframe is not empty
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            # Count outliers before capping
            outliers_count = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            
            # Cap outliers instead of removing
            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
            
            if outliers_count > 0:
                cleaning_report['outliers_capped'][col] = int(outliers_count)
    
    # Sort by date
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Final check: ensure no NaN values remain
    remaining_nulls = df.isnull().sum().sum()
    if remaining_nulls > 0:
        # Fill any remaining nulls with 0 for numeric and 'Unknown' for categorical
        for col in df.columns:
            if df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col].fillna(0, inplace=True)
                else:
                    # Already converted to object type at start
                    df[col].fillna('Unknown', inplace=True)
    
    return df, cleaning_report


def engineer_features(df):
    """
    Create additional features from existing data with null-safe operations
    """
    df = df.copy()
    
    # Convert categorical columns to object type to avoid category errors
    categorical_cols = ['Product', 'Region']
    for col in categorical_cols:
        if col in df.columns and pd.api.types.is_categorical_dtype(df[col]):
            df[col] = df[col].astype('object')
    
    # Time-based features
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Quarter'] = df['Date'].dt.quarter
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['WeekOfYear'] = df['Date'].dt.isocalendar().week
    
    # Business metrics with null-safe operations
    # Replace inf, -inf, and NaN with 0
    df['Profit_Margin'] = (df['Profit'] / df['Sales'] * 100).replace([np.inf, -np.inf], np.nan).fillna(0)
    df['Cost_Ratio'] = (df['Cost'] / df['Sales']).replace([np.inf, -np.inf], np.nan).fillna(0)
    df['ROI'] = ((df['Profit'] - df['Marketing_Spend']) / df['Marketing_Spend'] * 100).replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Marketing efficiency
    df['Marketing_Efficiency'] = (df['Sales'] / df['Marketing_Spend']).replace([np.inf, -np.inf], np.nan).fillna(0)
    df['Profit_Per_Marketing'] = (df['Profit'] / df['Marketing_Spend']).replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Growth indicators (compare with previous period)
    df = df.sort_values(['Product', 'Region', 'Date'])
    df['Sales_Growth'] = df.groupby(['Product', 'Region'])['Sales'].pct_change() * 100
    df['Profit_Growth'] = df.groupby(['Product', 'Region'])['Profit'].pct_change() * 100
    
    # Fill NaN values from growth calculations (including inf values)
    df['Sales_Growth'] = df['Sales_Growth'].replace([np.inf, -np.inf], np.nan).fillna(0)
    df['Profit_Growth'] = df['Profit_Growth'].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Performance categories with null handling
    df['Profit_Category'] = pd.cut(
        df['Profit_Margin'],
        bins=[-np.inf, 0, 10, 20, np.inf],
        labels=['Loss', 'Low', 'Medium', 'High']
    )
    # Convert to object type before filling NaN to avoid categorical errors
    if pd.api.types.is_categorical_dtype(df['Profit_Category']):
        df['Profit_Category'] = df['Profit_Category'].astype('object')
    # Fill any NaN categories with 'Unknown'
    df['Profit_Category'] = df['Profit_Category'].fillna('Unknown')
    
    # Seasonal indicators
    df['Is_Holiday_Season'] = df['Month'].isin([11, 12]).astype(int)
    
    # Final comprehensive check: ensure NO NaN or inf values remain anywhere
    for col in df.columns:
        if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
            # Replace inf/-inf with NaN first, then fill with 0
            df[col] = df[col].replace([np.inf, -np.inf], np.nan).fillna(0)
        elif df[col].dtype == 'object':
            # Fill string/object columns with 'Unknown'
            df[col] = df[col].fillna('Unknown')
    
    return df


def calculate_data_quality_score(df):
    """
    Calculate overall data quality score (0-100)
    """
    scores = {}
    
    # Completeness (no missing values)
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    scores['completeness'] = (1 - missing_cells / total_cells) * 100
    
    # Consistency (valid ranges and relationships)
    consistency_checks = []
    
    # Check if Profit = Sales - Cost (with small tolerance)
    profit_check = np.abs(df['Profit'] - (df['Sales'] - df['Cost'])) < 0.01
    consistency_checks.append(profit_check.mean())
    
    # Check if Sales >= 0
    consistency_checks.append((df['Sales'] >= 0).mean())
    
    # Check if Cost >= 0
    consistency_checks.append((df['Cost'] >= 0).mean())
    
    scores['consistency'] = np.mean(consistency_checks) * 100
    
    # Uniqueness (no duplicate records)
    duplicate_ratio = df.duplicated().sum() / len(df)
    scores['uniqueness'] = (1 - duplicate_ratio) * 100
    
    # Validity (proper data types and formats)
    validity_checks = []
    validity_checks.append(pd.api.types.is_datetime64_any_dtype(df['Date']))
    validity_checks.append(pd.api.types.is_numeric_dtype(df['Sales']))
    validity_checks.append(pd.api.types.is_numeric_dtype(df['Cost']))
    validity_checks.append(pd.api.types.is_numeric_dtype(df['Profit']))
    
    scores['validity'] = np.mean(validity_checks) * 100
    
    # Overall quality score (weighted average)
    overall_score = (
        scores['completeness'] * 0.3 +
        scores['consistency'] * 0.3 +
        scores['uniqueness'] * 0.2 +
        scores['validity'] * 0.2
    )
    
    scores['overall'] = overall_score
    
    return scores


def detect_data_issues(df):
    """
    Detect specific data quality issues
    """
    issues = []
    
    # Missing values
    missing = df.isnull().sum()
    for col, count in missing.items():
        if count > 0:
            issues.append({
                'type': 'Missing Values',
                'severity': 'Medium',
                'description': f"Column '{col}' has {count} missing values ({count/len(df)*100:.1f}%)"
            })
    
    # Negative values where inappropriate
    if (df['Sales'] < 0).any():
        count = (df['Sales'] < 0).sum()
        issues.append({
            'type': 'Invalid Values',
            'severity': 'High',
            'description': f"Found {count} negative sales values"
        })
    
    # Zero sales
    zero_sales = (df['Sales'] == 0).sum()
    if zero_sales > 0:
        issues.append({
            'type': 'Unusual Pattern',
            'severity': 'Low',
            'description': f"Found {zero_sales} records with zero sales"
        })
    
    # Profit inconsistency
    profit_diff = np.abs(df['Profit'] - (df['Sales'] - df['Cost']))
    inconsistent = (profit_diff > 0.01).sum()
    if inconsistent > 0:
        issues.append({
            'type': 'Data Inconsistency',
            'severity': 'High',
            'description': f"Found {inconsistent} records where Profit ≠ Sales - Cost"
        })
    
    # Duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        issues.append({
            'type': 'Duplicate Records',
            'severity': 'Medium',
            'description': f"Found {duplicates} duplicate records"
        })
    
    # Very high profit margins (potential data errors)
    high_margin = (df['Profit_Margin'] > 80).sum() if 'Profit_Margin' in df.columns else 0
    if high_margin > 0:
        issues.append({
            'type': 'Unusual Pattern',
            'severity': 'Low',
            'description': f"Found {high_margin} records with profit margin > 80%"
        })
    
    return issues


def get_data_summary(df):
    """
    Generate comprehensive data summary
    """
    summary = {
        'total_records': len(df),
        'date_range': {
            'start': df['Date'].min().strftime('%Y-%m-%d'),
            'end': df['Date'].max().strftime('%Y-%m-%d'),
            'days': (df['Date'].max() - df['Date'].min()).days
        },
        'products': df['Product'].nunique(),
        'regions': df['Region'].nunique(),
        'total_sales': float(df['Sales'].sum()),
        'total_profit': float(df['Profit'].sum()),
        'total_cost': float(df['Cost'].sum()),
        'avg_profit_margin': float(df['Profit'].sum() / df['Sales'].sum() * 100) if df['Sales'].sum() > 0 else 0
    }
    
    return summary
