from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import User, Watchlist
from models.schemas import WatchlistAdd
from auth import get_current_user
from ml.fetch_data import fetch_stock_data

router = APIRouter()

@router.get("/")
def get_watchlist(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """return user's saved stocks with latest prices"""
    items = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).all()
    result = []
    for item in items:
        # Fetch latest price
        try:
            df = fetch_stock_data(item.ticker, period="5d")
            if not df.empty and len(df) >= 2:
                latest = round(df["Close"].iloc[-1], 2)
                prev = round(df["Close"].iloc[-2], 2)
                change = round(latest - prev, 2)
                change_pct = round((change / prev) * 100, 2)
                result.append({
                    "ticker": item.ticker,
                    "price": latest,
                    "change": change,
                    "change_pct": change_pct
                })
            else:
                result.append({
                    "ticker": item.ticker,
                    "price": 0,
                    "change": 0,
                    "change_pct": 0
                })
        except:
             result.append({
                "ticker": item.ticker,
                "price": 0,
                "change": 0,
                "change_pct": 0
            })
    return result

@router.post("/add")
def add_to_watchlist(item: WatchlistAdd, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """add to user's watchlist"""
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.ticker == item.ticker
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Ticker already in watchlist")
        
    new_item = Watchlist(user_id=current_user.id, ticker=item.ticker)
    db.add(new_item)
    db.commit()
    
    return {"message": f"Added {item.ticker} to watchlist"}

@router.delete("/{ticker}")
def remove_from_watchlist(ticker: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """remove from watchlist"""
    item = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.ticker == ticker
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Ticker not found in watchlist")
        
    db.delete(item)
    db.commit()
    
    return {"message": f"Removed {ticker} from watchlist"}
