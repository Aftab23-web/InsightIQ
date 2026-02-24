"""
Database Utility Functions
"""
import pandas as pd
from sqlalchemy.orm import Session
from database.models import (
    RawData, CleanedData, KPI, Prediction, 
    Insight, Recommendation, Anomaly, get_session
)
from datetime import datetime
import uuid


def generate_batch_id():
    """Generate unique batch ID for data uploads"""
    return f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def save_raw_data(df, batch_id=None):
    """Save raw data to database with NaN handling"""
    session = get_session()
    
    if batch_id is None:
        batch_id = generate_batch_id()
    
    # Ensure no NaN values before saving
    df = df.copy()
    df = df.fillna(0)  # Replace all NaN with 0
    
    try:
        for _, row in df.iterrows():
            record = RawData(
                date=row['Date'],
                product=str(row['Product']) if pd.notna(row['Product']) else 'Unknown',
                region=str(row['Region']) if pd.notna(row['Region']) else 'Unknown',
                sales=float(row['Sales']) if pd.notna(row['Sales']) else 0.0,
                cost=float(row['Cost']) if pd.notna(row['Cost']) else 0.0,
                profit=float(row['Profit']) if pd.notna(row['Profit']) else 0.0,
                marketing_spend=float(row['Marketing_Spend']) if pd.notna(row['Marketing_Spend']) else 0.0,
                batch_id=batch_id
            )
            session.add(record)
        
        session.commit()
        return batch_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def save_cleaned_data(df, batch_id):
    """Save cleaned data to database with NaN handling"""
    session = get_session()
    
    # Ensure no NaN values before saving
    df = df.copy()
    # Replace NaN in numeric columns with 0
    numeric_cols = ['Sales', 'Cost', 'Profit', 'Marketing_Spend', 'Year', 'Month', 'Quarter', 
                    'Profit_Margin', 'ROI', 'Cost_Ratio']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    
    # Replace NaN in string columns with 'Unknown'
    string_cols = ['Product', 'Region']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')
    
    try:
        for _, row in df.iterrows():
            record = CleanedData(
                date=row['Date'],
                product=str(row['Product']) if pd.notna(row['Product']) else 'Unknown',
                region=str(row['Region']) if pd.notna(row['Region']) else 'Unknown',
                sales=float(row['Sales']) if pd.notna(row['Sales']) else 0.0,
                cost=float(row['Cost']) if pd.notna(row['Cost']) else 0.0,
                profit=float(row['Profit']) if pd.notna(row['Profit']) else 0.0,
                marketing_spend=float(row['Marketing_Spend']) if pd.notna(row['Marketing_Spend']) else 0.0,
                year=int(row.get('Year', 0)) if pd.notna(row.get('Year')) else None,
                month=int(row.get('Month', 0)) if pd.notna(row.get('Month')) else None,
                quarter=int(row.get('Quarter', 0)) if pd.notna(row.get('Quarter')) else None,
                profit_margin=float(row.get('Profit_Margin', 0)) if pd.notna(row.get('Profit_Margin')) else 0.0,
                roi=float(row.get('ROI', 0)) if pd.notna(row.get('ROI')) else 0.0,
                cost_ratio=float(row.get('Cost_Ratio', 0)) if pd.notna(row.get('Cost_Ratio')) else 0.0,
                batch_id=batch_id
            )
            session.add(record)
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def save_kpis(kpi_data, batch_id):
    """Save KPI metrics to database"""
    session = get_session()
    
    try:
        kpi = KPI(
            batch_id=batch_id,
            total_sales=kpi_data.get('total_sales'),
            total_profit=kpi_data.get('total_profit'),
            total_cost=kpi_data.get('total_cost'),
            avg_profit_margin=kpi_data.get('avg_profit_margin'),
            sales_growth=kpi_data.get('sales_growth'),
            profit_growth=kpi_data.get('profit_growth'),
            cost_efficiency=kpi_data.get('cost_efficiency'),
            roi=kpi_data.get('roi'),
            health_score=kpi_data.get('health_score'),
            health_status=kpi_data.get('health_status')
        )
        session.add(kpi)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def save_predictions(predictions_df, batch_id, model_type='Prophet'):
    """Save forecast predictions to database"""
    session = get_session()
    
    try:
        for _, row in predictions_df.iterrows():
            pred = Prediction(
                batch_id=batch_id,
                prediction_date=row['date'],
                predicted_sales=row.get('predicted_sales'),
                predicted_profit=row.get('predicted_profit'),
                sales_lower=row.get('sales_lower'),
                sales_upper=row.get('sales_upper'),
                profit_lower=row.get('profit_lower'),
                profit_upper=row.get('profit_upper'),
                model_type=model_type,
                confidence_level=0.95
            )
            session.add(pred)
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def save_insights(insights_list, batch_id):
    """Save business insights to database"""
    session = get_session()
    
    try:
        for insight_data in insights_list:
            insight = Insight(
                batch_id=batch_id,
                insight_type=insight_data.get('type'),
                category=insight_data.get('category'),
                title=insight_data.get('title'),
                description=insight_data.get('description'),
                impact=insight_data.get('impact'),
                severity=insight_data.get('severity'),
                metric_name=insight_data.get('metric_name'),
                metric_value=insight_data.get('metric_value')
            )
            session.add(insight)
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def save_recommendations(recommendations_list, batch_id):
    """Save recommendations to database"""
    session = get_session()
    
    try:
        for rec_data in recommendations_list:
            rec = Recommendation(
                batch_id=batch_id,
                priority=rec_data.get('priority'),
                category=rec_data.get('category'),
                title=rec_data.get('title'),
                description=rec_data.get('description'),
                action_items=rec_data.get('action_items'),
                estimated_impact=rec_data.get('estimated_impact'),
                implementation_effort=rec_data.get('implementation_effort')
            )
            session.add(rec)
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def save_anomalies(anomalies_list, batch_id):
    """Save detected anomalies to database"""
    session = get_session()
    
    try:
        for anomaly_data in anomalies_list:
            anomaly = Anomaly(
                batch_id=batch_id,
                detection_date=anomaly_data.get('date'),
                anomaly_type=anomaly_data.get('type'),
                severity=anomaly_data.get('severity'),
                description=anomaly_data.get('description'),
                affected_metric=anomaly_data.get('metric'),
                expected_value=anomaly_data.get('expected_value'),
                actual_value=anomaly_data.get('actual_value'),
                deviation_percent=anomaly_data.get('deviation_percent')
            )
            session.add(anomaly)
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_cleaned_data(batch_id=None):
    """Retrieve cleaned data from database"""
    session = get_session()
    
    try:
        query = session.query(CleanedData)
        if batch_id:
            query = query.filter(CleanedData.batch_id == batch_id)
        
        results = query.all()
        
        data = [{
            'Date': r.date,
            'Product': r.product,
            'Region': r.region,
            'Sales': r.sales,
            'Cost': r.cost,
            'Profit': r.profit,
            'Marketing_Spend': r.marketing_spend,
            'Year': r.year,
            'Month': r.month,
            'Quarter': r.quarter,
            'Profit_Margin': r.profit_margin,
            'ROI': r.roi,
            'Cost_Ratio': r.cost_ratio
        } for r in results]
        
        return pd.DataFrame(data)
    finally:
        session.close()


def get_latest_batch_id():
    """Get the most recent batch ID"""
    session = get_session()
    
    try:
        result = session.query(CleanedData.batch_id)\
            .order_by(CleanedData.processed_timestamp.desc())\
            .first()
        
        return result[0] if result else None
    finally:
        session.close()
