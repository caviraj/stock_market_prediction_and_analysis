from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import Prediction
from ml.fetch_data import fetch_stock_data

router = APIRouter()

@router.get("/list/latest")
def get_multiple_latest(tickers: str, db: Session = Depends(get_db)):
    """Fetch latest price, change, change_pct, and cached signal for multiple tickers"""
    ticker_list = [t.strip() for t in tickers.split(",") if t.strip()]
    results = []
    for ticker in ticker_list:
        try:
            df = fetch_stock_data(ticker, period="5d")
            if not df.empty and len(df) >= 2:
                latest_price = round(float(df["Close"].iloc[-1]), 2)
                prev_price = round(float(df["Close"].iloc[-2]), 2)
                change = round(latest_price - prev_price, 2)
                change_pct = round((change / prev_price) * 100, 2)
                
                pred = db.query(Prediction).filter(Prediction.ticker == ticker).order_by(Prediction.created_at.desc()).first()
                signal = pred.signal if pred else "HOLD"
                
                results.append({
                    "ticker": ticker,
                    "price": latest_price,
                    "change": change,
                    "change_pct": change_pct,
                    "signal": signal
                })
            else:
                results.append({
                    "ticker": ticker,
                    "price": 0.0,
                    "change": 0.0,
                    "change_pct": 0.0,
                    "signal": "HOLD"
                })
        except Exception:
            results.append({
                "ticker": ticker,
                "price": 0.0,
                "change": 0.0,
                "change_pct": 0.0,
                "signal": "HOLD"
            })
    return results

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
