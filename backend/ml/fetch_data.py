import yfinance as yf
import pandas as pd
from fastapi import HTTPException
import os
import time
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

def _format_ticker(ticker: str) -> str:
    if not ticker.endswith('.NS') and not ticker.endswith('.BO'):
        # Assuming NSE by default as per prompt
        return f"{ticker}.NS"
    return ticker

def _get_cache_filepath(ticker: str, period: str) -> str:
    return os.path.join(CACHE_DIR, f"{ticker}_{period}_cache.csv")

def _is_cache_valid(filepath: str, max_age_hours: int = 1) -> bool:
    if not os.path.exists(filepath):
        return False
    file_mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
    return datetime.now() - file_mod_time < timedelta(hours=max_age_hours)

def _parse_twelvedata_symbol(ticker: str):
    ticker = ticker.upper()
    if ticker.endswith('.NS'):
        return ticker[:-3], "NSE"
    elif ticker.endswith('.BO'):
        return ticker[:-3], "BSE"
    return ticker, None

def _get_twelvedata_outputsize(period: str) -> int:
    if period == "1d":
        return 5
    elif period == "5d":
        return 10
    elif period == "1mo":
        return 35
    elif period == "3mo":
        return 90
    elif period == "6mo":
        return 180
    elif period == "1y":
        return 365
    elif period == "2y":
        return 730
    elif period == "5y":
        return 1825
    elif period == "10y":
        return 3650
    return 1000  # default

def _fetch_from_twelvedata(ticker: str, period: str) -> pd.DataFrame:
    if not TWELVEDATA_API_KEY:
        raise ValueError("TWELVEDATA_API_KEY is not set")
        
    symbol, exchange = _parse_twelvedata_symbol(ticker)
    outputsize = _get_twelvedata_outputsize(period)
    
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": "1day",
        "outputsize": outputsize,
        "apikey": TWELVEDATA_API_KEY
    }
    if exchange:
        params["exchange"] = exchange
        
    response = requests.get(url, params=params, timeout=10)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Twelve Data HTTP Error {response.status_code}")
        
    data = response.json()
    if "status" in data and data["status"] == "error":
        raise ValueError(f"Twelve Data API Error: {data.get('message')}")
        
    values = data.get("values")
    if not values:
        raise ValueError(f"No values returned by Twelve Data for {ticker}")
        
    df = pd.DataFrame(values)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    
    df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)
    
    for col in ['Open', 'High', 'Low', 'Close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0).astype(int)
    
    df.sort_index(ascending=True, inplace=True)
    return df

def fetch_stock_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    formatted_ticker = _format_ticker(ticker)
    cache_filepath = _get_cache_filepath(formatted_ticker, period)
    
    if _is_cache_valid(cache_filepath):
        try:
            df = pd.read_csv(cache_filepath, index_col=0, parse_dates=True)
            if not df.empty:
                return df
        except Exception:
            pass # fallback
            
    # Try Twelve Data first if API key is set
    if TWELVEDATA_API_KEY:
        try:
            df = _fetch_from_twelvedata(formatted_ticker, period)
            if not df.empty:
                df.to_csv(cache_filepath)
                return df
        except Exception as e:
            print(f"Twelve Data failed for {formatted_ticker}: {e}. Falling back to yfinance.")
            
    # Fallback to yfinance
    try:
        stock = yf.Ticker(formatted_ticker)
        df = stock.history(period=period)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Stock data not found for ticker: {formatted_ticker}")
            
        # Ensure we keep specific columns
        cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if 'Adj Close' in df.columns:
            cols.append('Adj Close')
        df = df[cols]
        
        # Save to cache
        df.to_csv(cache_filepath)
        return df
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error fetching data for {formatted_ticker}: {str(e)}")

def fetch_multiple(tickers: list, period: str = "1y") -> dict:
    results = {}
    for t in tickers:
        try:
            results[t] = fetch_stock_data(t, period=period)
        except HTTPException:
            # Skip failures in batch fetch
            pass
    return results

