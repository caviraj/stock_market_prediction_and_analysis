from fastapi import APIRouter, HTTPException
from typing import Optional
from ml.fetch_data import fetch_stock_data

router = APIRouter()

@router.get("/{ticker}")
def get_stock_data(ticker: str, period: str = "1y"):
    """Fetch OHLCV data, return list of {date, open, high, low, close, volume}"""
    try:
        df = fetch_stock_data(ticker, period=period)
        if df.empty:
            raise HTTPException(status_code=404, detail="Stock data not found")
            
        ohlcv = []
        for index, row in df.iterrows():
            ohlcv.append({
                "date": index.strftime('%Y-%m-%d'),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })
        return {"ticker": ticker, "data": ohlcv}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{ticker}/latest")
def get_latest_price(ticker: str):
    """Return latest price, change amount, change percent, last_updated"""
    try:
        # We need at least 5 days to get yesterday's close safely
        df = fetch_stock_data(ticker, period="5d")
        if len(df) < 2:
            raise HTTPException(status_code=404, detail="Not enough data")
            
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        latest_price = round(latest["Close"], 2)
        prev_price = round(previous["Close"], 2)
        
        change = round(latest_price - prev_price, 2)
        change_pct = round((change / prev_price) * 100, 2)
        
        return {
            "ticker": ticker,
            "price": latest_price,
            "change": change,
            "change_pct": change_pct,
            "last_updated": df.index[-1].strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=400, detail=str(e))
