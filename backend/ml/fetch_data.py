import yfinance as yf
import pandas as pd
from fastapi import HTTPException
import os
import time
from datetime import datetime, timedelta

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

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

def fetch_stock_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    formatted_ticker = _format_ticker(ticker)
    cache_filepath = _get_cache_filepath(formatted_ticker, period)
    
    if _is_cache_valid(cache_filepath):
        try:
            df = pd.read_csv(cache_filepath, index_col=0, parse_dates=True)
            if not df.empty:
                return df
        except Exception:
            pass # fallback to yfinance
            
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
