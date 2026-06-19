import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
try:
    import pandas_ta as ta
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False

def prepare_lstm_data(df: pd.DataFrame, lookback: int = 60):
    if df.empty or len(df) <= lookback:
        raise ValueError("DataFrame is too short to create LSTM sequences")
        
    data = df.filter(['Close']).values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i, 0])
        y.append(scaled_data[i, 0])
        
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    
    train_size = int(len(X) * 0.8)
    X_train, y_train = X[:train_size], y[:train_size]
    X_test, y_test = X[train_size:], y[train_size:]
    
    return X_train, y_train, X_test, y_test, scaler

def prepare_rf_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
        
    df = df.copy()
    
    # Add technical indicators using pandas-ta
    if TA_AVAILABLE:
        df['SMA_20'] = ta.sma(df['Close'], length=20)
        df['SMA_50'] = ta.sma(df['Close'], length=50)
        df['EMA_20'] = ta.ema(df['Close'], length=20)
        df['RSI_14'] = ta.rsi(df['Close'], length=14)
        
        macd = ta.macd(df['Close'])
        if macd is not None and not macd.empty:
            df['MACD'] = macd[macd.columns[0]]
            df['MACD_signal'] = macd[macd.columns[2]]
        else:
            df['MACD'] = np.nan
            df['MACD_signal'] = np.nan
    else:
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['RSI_14'] = 50.0  # Dummy if TA not available
        df['MACD'] = 0.0
        df['MACD_signal'] = 0.0

    # Custom features
    df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
    df['price_change_pct'] = df['Close'].pct_change()
    df['high_low_range'] = df['High'] - df['Low']
    
    # Target creation: Next day's percentage change
    df['next_day_change'] = df['Close'].pct_change().shift(-1)
    
    def generate_signal(change):
        if pd.isna(change):
            return np.nan
        if change > 0.005:
            return 1   # BUY
        elif change < -0.005:
            return -1  # SELL
        else:
            return 0   # HOLD
            
    df['signal'] = df['next_day_change'].apply(generate_signal)
    
    # Drop rows with NaN values created by moving averages/shifts
    df.dropna(inplace=True)
    
    # Drop intermediate columns if needed, but keeping them is fine for feature set
    df.drop(columns=['next_day_change'], inplace=True, errors='ignore')
    
    return df
