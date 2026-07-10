from fastapi import APIRouter
from ml.fetch_data import fetch_stock_data

router = APIRouter()

def get_index_data(ticker: str):
    try:
        df = fetch_stock_data(ticker, period="5d")
        if len(df) < 2:
            return {"value": 0, "change": 0, "change_pct": 0}
        
        latest = round(df["Close"].iloc[-1], 2)
        prev = round(df["Close"].iloc[-2], 2)
        change = round(latest - prev, 2)
        change_pct = round((change / prev) * 100, 2)
        
        return {"value": latest, "change": change, "change_pct": change_pct}
    except:
        return {"value": 0, "change": 0, "change_pct": 0}

def get_ticker_live_data(ticker: str, fallback: dict):
    try:
        df = fetch_stock_data(ticker, period="5d")
        if len(df) < 2:
            return fallback
        latest = round(float(df["Close"].iloc[-1]), 2)
        prev = round(float(df["Close"].iloc[-2]), 2)
        change = round(latest - prev, 2)
        change_pct = round((change / prev) * 100, 2)
        return {"ticker": ticker, "price": latest, "change": change, "change_pct": change_pct}
    except Exception:
        return fallback

@router.get("/overview")
def get_market_overview():
    sensex = get_index_data("^BSESN")
    nifty50 = get_index_data("^NSEI")
    bank_nifty = get_index_data("^NSEBANK")
    nifty_it = get_index_data("^CNXIT")
    
    top_gainers = [
        get_ticker_live_data("TATASTEEL.NS", {"ticker": "TATASTEEL.NS", "price": 165.40, "change": 5.4, "change_pct": 3.3}),
        get_ticker_live_data("M&M.NS", {"ticker": "M&M.NS", "price": 1890.20, "change": 42.1, "change_pct": 2.2}),
    ]
    
    top_losers = [
        get_ticker_live_data("HDFCBANK.NS", {"ticker": "HDFCBANK.NS", "price": 1432.10, "change": -25.5, "change_pct": -1.7}),
        get_ticker_live_data("ITC.NS", {"ticker": "ITC.NS", "price": 412.30, "change": -8.1, "change_pct": -1.9}),
    ]

    return {
        "sensex": sensex,
        "nifty50": nifty50,
        "bank_nifty": bank_nifty,
        "nifty_it": nifty_it,
        "top_gainers": top_gainers,
        "top_losers": top_losers
    }
