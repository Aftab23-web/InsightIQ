"""
Forecasting Module using Prophet and ARIMA
"""
import pandas as pd
import numpy as np
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')


def prepare_time_series_data(df, metric='Sales'):
    """
    Prepare data for time series forecasting with null handling
    """
    # Ensure no null values in the metric column
    df = df.copy()
    df[metric] = df[metric].fillna(0)
    
    # Aggregate by date
    ts_data = df.groupby('Date')[metric].sum().reset_index()
    ts_data = ts_data.sort_values('Date')
    
    # Remove any remaining null values
    ts_data = ts_data.dropna()
    
    return ts_data


def forecast_with_prophet(df, metric='Sales', periods=12):
    """
    Forecast using Facebook Prophet with null handling
    Returns predictions with confidence intervals
    """
    # Prepare data for Prophet
    ts_data = prepare_time_series_data(df, metric)
    
    # Check if we have enough data
    if len(ts_data) < 2:
        raise ValueError(f"Insufficient data for forecasting. Need at least 2 data points, got {len(ts_data)}")
    
    # Prophet requires columns named 'ds' and 'y'
    prophet_df = ts_data.rename(columns={'Date': 'ds', metric: 'y'})
    
    # Ensure no null or infinite values
    prophet_df = prophet_df.replace([np.inf, -np.inf], np.nan).dropna()
    
    if len(prophet_df) < 2:
        raise ValueError("Data contains too many null or invalid values for forecasting")
    
    # Initialize and fit model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
        interval_width=0.95
    )
    
    model.fit(prophet_df)
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=periods, freq='MS')  # Monthly start
    
    # Make predictions
    forecast = model.predict(future)
    
    # Extract future predictions only
    future_forecast = forecast.iloc[-periods:][['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    future_forecast.columns = ['date', f'predicted_{metric.lower()}', 
                               f'{metric.lower()}_lower', f'{metric.lower()}_upper']
    
    # Calculate model performance on historical data
    historical_forecast = forecast.iloc[:-periods]
    actual_values = prophet_df['y'].values
    predicted_values = historical_forecast['yhat'].values
    
    # Ensure arrays are same length
    min_len = min(len(actual_values), len(predicted_values))
    actual_values = actual_values[-min_len:]
    predicted_values = predicted_values[-min_len:]
    
    mae = mean_absolute_error(actual_values, predicted_values)
    rmse = np.sqrt(mean_squared_error(actual_values, predicted_values))
    mape = np.mean(np.abs((actual_values - predicted_values) / np.maximum(actual_values, 1))) * 100
    
    performance = {
        'mae': float(mae),
        'rmse': float(rmse),
        'mape': float(mape)
    }
    
    return future_forecast, performance, model


def forecast_with_arima(df, metric='Sales', periods=12):
    """
    Forecast using ARIMA model
    """
    ts_data = prepare_time_series_data(df, metric)
    
    # Fit ARIMA model
    try:
        model = ARIMA(ts_data[metric], order=(1, 1, 1))
        fitted_model = model.fit()
        
        # Make predictions
        forecast = fitted_model.forecast(steps=periods)
        
        # Get confidence intervals
        forecast_result = fitted_model.get_forecast(steps=periods)
        conf_int = forecast_result.conf_int()
        
        # Create forecast dataframe
        last_date = ts_data['Date'].max()
        future_dates = pd.date_range(start=last_date, periods=periods + 1, freq='MS')[1:]
        
        forecast_df = pd.DataFrame({
            'date': future_dates,
            f'predicted_{metric.lower()}': forecast,
            f'{metric.lower()}_lower': conf_int.iloc[:, 0],
            f'{metric.lower()}_upper': conf_int.iloc[:, 1]
        })
        
        return forecast_df, fitted_model
    
    except Exception as e:
        print(f"ARIMA forecast failed: {e}")
        return None, None


def generate_forecast(df, periods=12, metric='Sales', method='prophet'):
    """
    Main forecasting function
    """
    if len(df) < 10:
        return {
            'error': 'Insufficient data for forecasting (minimum 10 data points required)'
        }
    
    if method == 'prophet':
        forecast_df, performance, model = forecast_with_prophet(df, metric, periods)
        
        return {
            'method': 'Prophet',
            'metric': metric,
            'forecast': forecast_df.to_dict('records'),
            'performance': performance,
            'model_type': 'Time Series (Prophet)'
        }
    
    elif method == 'arima':
        forecast_df, model = forecast_with_arima(df, metric, periods)
        
        if forecast_df is not None:
            return {
                'method': 'ARIMA',
                'metric': metric,
                'forecast': forecast_df.to_dict('records'),
                'model_type': 'Time Series (ARIMA)'
            }
        else:
            # Fallback to Prophet
            return generate_forecast(df, periods, metric, 'prophet')
    
    else:
        return {'error': f'Unknown method: {method}'}


def forecast_multiple_metrics(df, periods=12):
    """
    Forecast multiple business metrics
    """
    metrics = ['Sales', 'Profit']
    forecasts = {}
    
    for metric in metrics:
        if metric in df.columns:
            result = generate_forecast(df, periods, metric, 'prophet')
            forecasts[metric] = result
    
    return forecasts


def assess_forecast_risk(forecast_df, metric='Sales'):
    """
    Assess risk level in forecast
    """
    pred_col = f'predicted_{metric.lower()}'
    lower_col = f'{metric.lower()}_lower'
    upper_col = f'{metric.lower()}_upper'
    
    # Calculate uncertainty
    forecast_df['uncertainty'] = forecast_df[upper_col] - forecast_df[lower_col]
    forecast_df['uncertainty_pct'] = (forecast_df['uncertainty'] / forecast_df[pred_col] * 100)
    
    avg_uncertainty = forecast_df['uncertainty_pct'].mean()
    
    # Determine risk level
    if avg_uncertainty < 20:
        risk_level = 'Low'
        risk_description = 'Forecast has high confidence with narrow prediction intervals'
    elif avg_uncertainty < 40:
        risk_level = 'Medium'
        risk_description = 'Forecast has moderate uncertainty'
    else:
        risk_level = 'High'
        risk_description = 'Forecast has high uncertainty - use with caution'
    
    # Check for declining trend
    first_pred = forecast_df[pred_col].iloc[0]
    last_pred = forecast_df[pred_col].iloc[-1]
    trend_change = (last_pred - first_pred) / first_pred * 100
    
    if trend_change < -10:
        risk_level = 'High'
        risk_description += '. Forecast shows declining trend.'
    
    return {
        'risk_level': risk_level,
        'avg_uncertainty': float(avg_uncertainty),
        'trend_change_pct': float(trend_change),
        'description': risk_description
    }
