import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

def prepare_lag_features(series: pd.Series, lags: int = 5):
    """Creates tabular features for training recursive regression models."""
    df = pd.DataFrame({'y': series.values})
    for i in range(1, lags + 1):
        df[f'lag_{i}'] = df['y'].shift(i)
    df.dropna(inplace=True)
    
    X = df[[f'lag_{i}' for i in range(1, lags + 1)]].values
    y = df['y'].values
    return X, y

def forecast_recursive(model, last_known_lags: list, steps: int = 30, scaler=None) -> list:
    """Predicts next steps recursively using lag features."""
    current_lags = list(last_known_lags)
    forecast = []
    
    for _ in range(steps):
        # Format input features (lags must be in chronological order, e.g., lag_1, lag_2...)
        # In our case, lag_1 is close at t-1, lag_2 at t-2, etc.
        # So we feed current_lags in order [lag_1, lag_2, lag_3, lag_4, lag_5]
        # Which is [last, last-1, last-2, last-3, last-4]
        X_in = np.array(current_lags).reshape(1, -1)
        
        if scaler:
            X_in_scaled = scaler.transform(X_in)
            pred_scaled = model.predict(X_in_scaled)[0]
            pred = float(pred_scaled) # SVR is scaled
        else:
            pred = float(model.predict(X_in)[0])
            
        forecast.append(round(pred, 2))
        
        # Shift lags: new prediction becomes lag_1, old lag_1 becomes lag_2, etc.
        current_lags = [pred] + current_lags[:-1]
        
    return forecast

def run_linear_regression(series: pd.Series, steps: int = 30) -> list:
    """Trains and forecasts using Linear Regression."""
    try:
        X, y = prepare_lag_features(series)
        if len(X) < 10:
            return [float(series.iloc[-1])] * steps
            
        model = LinearRegression()
        model.fit(X, y)
        
        # Last known lags: [lag_1, lag_2, lag_3, lag_4, lag_5]
        last_lags = list(series.values[-5:])[::-1]
        return forecast_recursive(model, last_lags, steps)
    except Exception as e:
        print(f"Linear Regression forecast error: {e}")
        return [float(series.iloc[-1])] * steps

def run_random_forest_regressor(series: pd.Series, steps: int = 30) -> list:
    """Trains and forecasts using Random Forest Regressor."""
    try:
        X, y = prepare_lag_features(series)
        if len(X) < 10:
            return [float(series.iloc[-1])] * steps
            
        model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
        model.fit(X, y)
        
        last_lags = list(series.values[-5:])[::-1]
        return forecast_recursive(model, last_lags, steps)
    except Exception as e:
        print(f"Random Forest Regressor error: {e}")
        return [float(series.iloc[-1])] * steps

def run_xgboost(series: pd.Series, steps: int = 30) -> list:
    """Trains and forecasts using XGBoost (falls back to Gradient Boosting if missing)."""
    try:
        X, y = prepare_lag_features(series)
        if len(X) < 10:
            return [float(series.iloc[-1])] * steps
            
        if XGB_AVAILABLE:
            model = xgb.XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42)
        else:
            # Fallback to sklearn GradientBoosting
            model = GradientBoostingRegressor(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42)
            
        model.fit(X, y)
        
        last_lags = list(series.values[-5:])[::-1]
        return forecast_recursive(model, last_lags, steps)
    except Exception as e:
        print(f"XGBoost error: {e}")
        return [float(series.iloc[-1])] * steps

def run_svr(series: pd.Series, steps: int = 30) -> list:
    """Trains and forecasts using SVR (uses scaling for stabilization)."""
    try:
        X, y = prepare_lag_features(series)
        if len(X) < 10:
            return [float(series.iloc[-1])] * steps
            
        # Scale features for SVR
        scaler_X = StandardScaler()
        X_scaled = scaler_X.fit_transform(X)
        
        # We don't necessarily need to scale Y, but it's simpler if we don't
        model = SVR(kernel='rbf', C=1e3, gamma=0.1)
        model.fit(X_scaled, y)
        
        last_lags = list(series.values[-5:])[::-1]
        return forecast_recursive(model, last_lags, steps, scaler=scaler_X)
    except Exception as e:
        print(f"SVR error: {e}")
        return [float(series.iloc[-1])] * steps
