import pandas as pd
from ml.fetch_data import fetch_stock_data

try:
    import pandas_ta as ta
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> dict:
    if not TA_AVAILABLE: return {"value": 50.0, "status": "Neutral"}
    rsi_series = ta.rsi(df['Close'], length=period)
    if rsi_series is None or rsi_series.empty or pd.isna(rsi_series.iloc[-1]):
        return {"value": 50.0, "status": "Neutral"}
        
    latest_rsi = float(rsi_series.iloc[-1])
    status = "Overbought" if latest_rsi > 70 else "Oversold" if latest_rsi < 30 else "Neutral"
    
    return {"value": round(latest_rsi, 2), "status": status}

def calculate_macd(df: pd.DataFrame) -> dict:
    if not TA_AVAILABLE: return {"macd": 0.0, "signal": 0.0, "histogram": 0.0, "trend": "Neutral"}
    macd_df = ta.macd(df['Close'])
    if macd_df is None or macd_df.empty:
        return {"macd": 0.0, "signal": 0.0, "histogram": 0.0, "trend": "Neutral"}
        
    # Columns usually MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
    macd = float(macd_df.iloc[-1, 0])
    histogram = float(macd_df.iloc[-1, 1])
    signal = float(macd_df.iloc[-1, 2])
    
    trend = "Bullish" if macd > signal else "Bearish"
    
    return {
        "macd": round(macd, 2),
        "signal": round(signal, 2),
        "histogram": round(histogram, 2),
        "trend": trend
    }

def calculate_bollinger(df: pd.DataFrame, period: int = 20) -> dict:
    if not TA_AVAILABLE: return {"upper": 0.0, "middle": 0.0, "lower": 0.0, "current_price": 0.0, "position": "Inside"}
    bbands = ta.bbands(df['Close'], length=period)
    if bbands is None or bbands.empty:
        return {"upper": 0.0, "middle": 0.0, "lower": 0.0, "current_price": 0.0, "position": "Inside"}
        
    # Columns typically BBL_20_2.0, BBM_20_2.0, BBU_20_2.0, BBB_20_2.0, BBP_20_2.0
    lower = float(bbands.iloc[-1, 0])
    middle = float(bbands.iloc[-1, 1])
    upper = float(bbands.iloc[-1, 2])
    
    current_price = float(df['Close'].iloc[-1])
    
    if current_price > upper:
        position = "Above Upper"
    elif current_price < lower:
        position = "Below Lower"
    else:
        position = "Inside"
        
    return {
        "upper": round(upper, 2),
        "middle": round(middle, 2),
        "lower": round(lower, 2),
        "current_price": round(current_price, 2),
        "position": position
    }

def calculate_atr(df: pd.DataFrame, period: int = 14) -> dict:
    if not TA_AVAILABLE: return {"atr": 0.0, "volatility_level": "Medium"}
    atr_series = ta.atr(df['High'], df['Low'], df['Close'], length=period)
    if atr_series is None or atr_series.empty or pd.isna(atr_series.iloc[-1]):
        return {"atr": 0.0, "volatility_level": "Medium"}
        
    atr = float(atr_series.iloc[-1])
    current_price = float(df['Close'].iloc[-1])
    
    atr_pct = (atr / current_price) * 100
    if atr_pct > 2.0:
        volatility_level = "High"
    elif atr_pct < 1.0:
        volatility_level = "Low"
    else:
        volatility_level = "Medium"
        
    return {
        "atr": round(atr, 2),
        "volatility_level": volatility_level
    }

def calculate_sma(df: pd.DataFrame, periods: list = [20, 50]) -> dict:
    if not TA_AVAILABLE: return {"sma20": 0.0, "sma50": 0.0, "cross_signal": "Neutral"}
    sma20_series = ta.sma(df['Close'], length=periods[0])
    sma50_series = ta.sma(df['Close'], length=periods[1])
    
    if sma20_series is None or sma50_series is None or sma20_series.empty or sma50_series.empty:
        return {"sma20": 0.0, "sma50": 0.0, "cross_signal": "Neutral"}
        
    sma20 = float(sma20_series.iloc[-1])
    sma50 = float(sma50_series.iloc[-1])
    
    if sma20 > sma50:
        cross_signal = "Golden Cross"
    elif sma20 < sma50:
        cross_signal = "Death Cross"
    else:
        cross_signal = "Neutral"
        
    return {
        "sma20": round(sma20, 2),
        "sma50": round(sma50, 2),
        "cross_signal": cross_signal
    }

def calculate_ema(df: pd.DataFrame, period: int = 20) -> float:
    if not TA_AVAILABLE: return 0.0
    ema_series = ta.ema(df['Close'], length=period)
    if ema_series is None or ema_series.empty or pd.isna(ema_series.iloc[-1]):
        return 0.0
    return round(float(ema_series.iloc[-1]), 2)

def get_all_indicators(ticker: str) -> dict:
    try:
        df = fetch_stock_data(ticker, period="6mo")
        if df.empty:
            return {}
            
        return {
            "rsi": calculate_rsi(df),
            "macd": calculate_macd(df),
            "bollinger": calculate_bollinger(df),
            "atr": calculate_atr(df),
            "sma": calculate_sma(df),
            "ema": calculate_ema(df)
        }
    except Exception as e:
        print(f"Error getting indicators for {ticker}: {e}")
        return {}
