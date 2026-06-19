import os
import pickle
import numpy as np
from datetime import datetime
from ml.rf_classifier import predict_signal
from ml.fetch_data import fetch_stock_data
from ml.preprocess import prepare_rf_features

try:
    from ml.lstm_model import load_model as load_lstm_model, MODELS_DIR
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "saved_models")

def get_predictions(ticker: str) -> dict:
    try:
        forecast_7d_rounded = [0] * 7
        forecast_30d_rounded = [0] * 30
        last_trained = "Not trained"
        
        # Load LSTM model and scaler
        if TF_AVAILABLE:
            lstm_model = load_lstm_model(ticker)
            scaler_path = os.path.join(MODELS_DIR, f"{ticker}_scaler.pkl")
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    scaler = pickle.load(f)
                    
            model_path = os.path.join(MODELS_DIR, f"{ticker}_lstm.h5")
            if os.path.exists(model_path):
                last_trained = datetime.fromtimestamp(os.path.getmtime(model_path)).strftime('%Y-%m-%d %H:%M')
            
        # Fetch latest data for prediction
        df = fetch_stock_data(ticker, period="3mo")
        if len(df) < 60:
            raise ValueError("Not enough data for prediction (need 60 days)")
            
        if TF_AVAILABLE and 'scaler' in locals():
            # Prepare data for LSTM
            last_60_days = df['Close'].values[-60:]
            last_60_days_scaled = scaler.transform(last_60_days.reshape(-1, 1))
            
            # Predict 7 days
            X_pred = np.reshape(last_60_days_scaled, (1, 60, 1))
            forecast_7d = []
            current_seq = X_pred.copy()
            
            for _ in range(7):
                pred_price = lstm_model.predict(current_seq, verbose=0)[0, 0]
                forecast_7d.append(pred_price)
                current_seq = np.append(current_seq[:, 1:, :], [[[pred_price]]], axis=1)
                
            forecast_7d_unscaled = scaler.inverse_transform(np.array(forecast_7d).reshape(-1, 1)).flatten().tolist()
            forecast_7d_rounded = [round(float(p), 2) for p in forecast_7d_unscaled]
            
            # Predict 30 days
            forecast_30d = []
            current_seq_30 = X_pred.copy()
            for _ in range(30):
                pred_price = lstm_model.predict(current_seq_30, verbose=0)[0, 0]
                forecast_30d.append(pred_price)
                current_seq_30 = np.append(current_seq_30[:, 1:, :], [[[pred_price]]], axis=1)
                
            forecast_30d_unscaled = scaler.inverse_transform(np.array(forecast_30d).reshape(-1, 1)).flatten().tolist()
            forecast_30d_rounded = [round(float(p), 2) for p in forecast_30d_unscaled]
        
        # Random forest signal
        features_df = prepare_rf_features(df)
        if not features_df.empty:
            signal = predict_signal(ticker, features_df)
        else:
            signal = "HOLD"
            
        return {
            "ticker": ticker,
            "forecast_7d": forecast_7d_rounded,
            "forecast_30d": forecast_30d_rounded,
            "signal": signal,
            "confidence": 85.5, # Dummy confidence for now
            "last_trained": last_trained
        }
        
    except Exception as e:
        print(f"Prediction error for {ticker}: {e}")
        return {
            "ticker": ticker,
            "error": str(e)
        }
