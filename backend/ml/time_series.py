import numpy as np
import pandas as pd
import warnings

# Suppress statsmodels warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

def forecast_exponential_smoothing_fallback(series: pd.Series, steps: int = 30) -> list:
    """Fallback using a double exponential smoothing concept for trend extrapolation."""
    prices = series.values
    if len(prices) < 2:
        return [float(prices[-1])] * steps if len(prices) > 0 else [0.0] * steps
        
    last_val = float(prices[-1])
    
    # Calculate simple trend based on the difference over recent window
    window = min(len(prices), 20)
    recent_trend = (prices[-1] - prices[-window]) / window
    
    forecast = []
    for i in range(1, steps + 1):
        # Dampen the trend to prevent unrealistic runaway values
        dampened_trend = recent_trend * (0.92 ** i)
        forecast.append(round(last_val + (dampened_trend * i), 2))
        
    return forecast

def run_arima(series: pd.Series, steps: int = 30) -> list:
    """ARIMA forecasting."""
    if not STATSMODELS_AVAILABLE:
        return forecast_exponential_smoothing_fallback(series, steps)
        
    try:
        # ARIMA(5, 1, 0) is a robust baseline for stock price sequences
        # We fill missing values and ensure numeric format
        clean_series = series.dropna().astype(float)
        if len(clean_series) < 10:
            return forecast_exponential_smoothing_fallback(series, steps)
            
        model = ARIMA(clean_series, order=(5, 1, 0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=steps)
        return [round(float(val), 2) for val in forecast.values]
    except Exception as e:
        print(f"ARIMA error: {e}. Falling back.")
        return forecast_exponential_smoothing_fallback(series, steps)

def run_sarimax(series: pd.Series, steps: int = 30) -> list:
    """SARIMAX forecasting with a light weekly seasonality order (5 business days)."""
    if not STATSMODELS_AVAILABLE:
        return forecast_exponential_smoothing_fallback(series, steps)
        
    try:
        clean_series = series.dropna().astype(float)
        if len(clean_series) < 15:
            return forecast_exponential_smoothing_fallback(series, steps)
            
        # Fit SARIMAX(1, 1, 1)x(1, 1, 1, 5)
        model = SARIMAX(clean_series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 5), enforce_stationarity=False)
        model_fit = model.fit(disp=False)
        forecast = model_fit.forecast(steps=steps)
        return [round(float(val), 2) for val in forecast.values]
    except Exception as e:
        print(f"SARIMAX error: {e}. Falling back.")
        return forecast_exponential_smoothing_fallback(series, steps)

def run_prophet(df: pd.DataFrame, steps: int = 30) -> list:
    """Prophet forecasting. Expects a DataFrame with 'Close' and DatetimeIndex."""
    if not PROPHET_AVAILABLE:
        return forecast_exponential_smoothing_fallback(df['Close'], steps)
        
    try:
        df_p = pd.DataFrame({
            'ds': df.index,
            'y': df['Close'].values
        })
        
        # Remove timezone info for Prophet compatibility
        if df_p['ds'].dt.tz is not None:
            df_p['ds'] = df_p['ds'].dt.tz_localize(None)
            
        m = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            interval_width=0.8
        )
        m.fit(df_p)
        
        future = m.make_future_dataframe(periods=steps, freq='D') # Daily (will filter to forecast length)
        forecast = m.predict(future)
        forecast_values = forecast['yhat'].values[-steps:]
        
        return [round(float(val), 2) for val in forecast_values]
    except Exception as e:
        print(f"Prophet error: {e}. Falling back.")
        return forecast_exponential_smoothing_fallback(df['Close'], steps)
