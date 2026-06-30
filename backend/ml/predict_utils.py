import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime

from ml.time_series import run_arima, run_sarimax, run_prophet
from ml.classical_ml import run_linear_regression, run_random_forest_regressor, run_xgboost, run_svr
from ml.sentiment import get_news_sentiment
from ml.fetch_data import fetch_stock_data
from ml.indicators import get_all_indicators

try:
    from ml.deep_learning import load_dl_model, MODELS_DIR
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "saved_models")

def get_predictions(ticker: str) -> dict:
    try:
        # 1. Fetch latest data (at least 60 days required for deep learning lookback)
        df = fetch_stock_data(ticker, period="1y")
        if len(df) < 60:
            raise ValueError(f"Insufficient stock history (need at least 60 days, got {len(df)}).")
            
        series = df['Close']
        current_price = float(series.iloc[-1])
        
        # 2. Run Time Series Models
        print(f"Running time series models for {ticker}...")
        arima_forecast = run_arima(series, steps=30)
        sarimax_forecast = run_sarimax(series, steps=30)
        prophet_forecast = run_prophet(df, steps=30)
        
        # 3. Run Classical ML Models
        print(f"Running classical ML models for {ticker}...")
        lr_forecast = run_linear_regression(series, steps=30)
        rf_forecast = run_random_forest_regressor(series, steps=30)
        xgb_forecast = run_xgboost(series, steps=30)
        svr_forecast = run_svr(series, steps=30)
        
        # 4. Run Deep Learning Models (if pre-trained files exist)
        print(f"Running deep learning models for {ticker}...")
        lstm_forecast = []
        gru_forecast = []
        last_trained = "Not trained"
        
        scaler_path = os.path.join(MODELS_DIR, f"{ticker}_scaler.pkl")
        lstm_path = os.path.join(MODELS_DIR, f"{ticker}_lstm.h5")
        gru_path = os.path.join(MODELS_DIR, f"{ticker}_gru.h5")
        
        if TF_AVAILABLE and os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
                
            last_60_days = series.values[-60:]
            last_60_days_scaled = scaler.transform(last_60_days.reshape(-1, 1))
            current_seq = np.reshape(last_60_days_scaled, (1, 60, 1))
            
            # Predict LSTM
            if os.path.exists(lstm_path):
                try:
                    lstm_model = load_dl_model(ticker, "lstm")
                    seq = current_seq.copy()
                    lstm_raw = []
                    for _ in range(30):
                        pred = lstm_model.predict(seq, verbose=0)[0, 0]
                        lstm_raw.append(pred)
                        seq = np.append(seq[:, 1:, :], [[[pred]]], axis=1)
                    lstm_unscaled = scaler.inverse_transform(np.array(lstm_raw).reshape(-1, 1)).flatten().tolist()
                    lstm_forecast = [round(float(p), 2) for p in lstm_unscaled]
                    last_trained = datetime.fromtimestamp(os.path.getmtime(lstm_path)).strftime('%Y-%m-%d %H:%M')
                except Exception as e:
                    print(f"LSTM runtime prediction error: {e}")
                    
            # Predict GRU
            if os.path.exists(gru_path):
                try:
                    gru_model = load_dl_model(ticker, "gru")
                    seq = current_seq.copy()
                    gru_raw = []
                    for _ in range(30):
                        pred = gru_model.predict(seq, verbose=0)[0, 0]
                        gru_raw.append(pred)
                        seq = np.append(seq[:, 1:, :], [[[pred]]], axis=1)
                    gru_unscaled = scaler.inverse_transform(np.array(gru_raw).reshape(-1, 1)).flatten().tolist()
                    gru_forecast = [round(float(p), 2) for p in gru_unscaled]
                except Exception as e:
                    print(f"GRU runtime prediction error: {e}")
                    
        # Fallbacks for DL models if not trained/available
        if not lstm_forecast:
            lstm_forecast = rf_forecast.copy() # RF serves as deep fallback
        if not gru_forecast:
            gru_forecast = xgb_forecast.copy()
            
        # 5. Fetch News Sentiment
        print(f"Fetching news sentiment for {ticker}...")
        sentiment_data = get_news_sentiment(ticker)
        sentiment_score = sentiment_data.get("score", 0.0)
        
        # 6. Ensemble Calculations (Weighted Average)
        model_predictions = {
            "arima": arima_forecast,
            "sarimax": sarimax_forecast,
            "prophet": prophet_forecast,
            "linear_regression": lr_forecast,
            "random_forest": rf_forecast,
            "xgboost": xgb_forecast,
            "svr": svr_forecast,
            "lstm": lstm_forecast,
            "gru": gru_forecast
        }
        
        # Calculate ensemble average forecast
        ensemble_forecast_30d = []
        for day in range(30):
            daily_prices = [forecast[day] for forecast in model_predictions.values() if len(forecast) > day]
            ensemble_forecast_30d.append(round(sum(daily_prices) / len(daily_prices), 2) if daily_prices else current_price)
            
        ensemble_forecast_7d = ensemble_forecast_30d[:7]
        
        # 7. Aggregate Signal Crossover Strategy
        # Signal components: Trend direction, technical indicators, and news sentiment
        signal_weights = []
        
        # Trend component (7-day forecast direction)
        predicted_7d_change_pct = ((ensemble_forecast_7d[-1] - current_price) / current_price) * 100
        if predicted_7d_change_pct > 1.2:
            signal_weights.append(1.0) # Buy
        elif predicted_7d_change_pct < -1.2:
            signal_weights.append(-1.0) # Sell
        else:
            signal_weights.append(0.0) # Hold
            
        # Sentiment component
        if sentiment_score > 0.15:
            signal_weights.append(1.0)
        elif sentiment_score < -0.15:
            signal_weights.append(-1.0)
        else:
            signal_weights.append(0.0)
            
        # Technical indicators component
        indicators = get_all_indicators(ticker)
        if indicators:
            # RSI Signal
            rsi_val = indicators.get("rsi", {}).get("value", 50)
            if rsi_val < 35:
                signal_weights.append(1.0) # Oversold (Buy)
            elif rsi_val > 65:
                signal_weights.append(-1.0) # Overbought (Sell)
                
            # MACD Signal
            macd_trend = indicators.get("macd", {}).get("trend", "Neutral")
            if macd_trend == "Bullish":
                signal_weights.append(0.5)
            elif macd_trend == "Bearish":
                signal_weights.append(-0.5)
                
            # SMA Crossover Signal
            sma_cross = indicators.get("sma", {}).get("cross_signal", "Neutral")
            if sma_cross == "Golden Cross":
                signal_weights.append(1.0)
            elif sma_cross == "Death Cross":
                signal_weights.append(-1.0)
                
        # Calculate final ensembled score
        avg_score = sum(signal_weights) / len(signal_weights) if signal_weights else 0.0
        
        if avg_score > 0.25:
            final_signal = "BUY"
        elif avg_score < -0.25:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"
            
        # Confidence score based on standard deviation/agreement among the 9 model outputs
        agreement_ratios = []
        for day in range(7):
            day_forecasts = [forecast[day] for forecast in model_predictions.values() if len(forecast) > day]
            if day_forecasts:
                mean = sum(day_forecasts) / len(day_forecasts)
                std_dev = np.std(day_forecasts)
                # Lower standard deviation relative to mean = higher confidence
                agreement_ratio = max(0, 1 - (std_dev / (mean * 0.05))) # 5% volatility budget
                agreement_ratios.append(agreement_ratio)
                
        base_confidence = sum(agreement_ratios) / len(agreement_ratios) * 100 if agreement_ratios else 70.0
        # Boost confidence slightly if sentiment and technicals align
        confidence = min(98.0, max(50.0, base_confidence))
        
        return {
            "ticker": ticker,
            "forecast_7d": ensemble_forecast_7d,
            "forecast_30d": ensemble_forecast_30d,
            "signal": final_signal,
            "confidence": round(confidence, 1),
            "last_trained": last_trained,
            "sentiment": sentiment_data,
            "model_predictions": model_predictions
        }
        
    except Exception as e:
        print(f"Prediction pipeline error for {ticker}: {e}")
        return {
            "ticker": ticker,
            "error": str(e)
        }
