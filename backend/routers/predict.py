from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from ml.predict_utils import get_predictions
import subprocess
import os
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import Prediction as DB_Prediction

router = APIRouter()

@router.get("/{ticker}")
def predict_stock(ticker: str, db: Session = Depends(get_db)):
    """load LSTM model for ticker, run prediction (with caching)"""
    # Check cache (valid for 4 hours)
    cache_limit = datetime.utcnow() - timedelta(hours=4)
    cached = db.query(DB_Prediction).filter(
        DB_Prediction.ticker == ticker,
        DB_Prediction.created_at > cache_limit
    ).order_by(DB_Prediction.created_at.desc()).first()
    
    if cached:
        try:
            data = json.loads(cached.forecast_json)
            data["ticker"] = ticker
            data["signal"] = cached.signal
            data["confidence"] = cached.confidence
            return data
        except Exception as e:
            print(f"Error reading cached prediction: {e}")
            
    # Calculate new predictions
    result = get_predictions(ticker)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    # Save/update cache
    try:
        # Delete old predictions to avoid table bloat
        db.query(DB_Prediction).filter(DB_Prediction.ticker == ticker).delete()
        
        db_pred = DB_Prediction(
            ticker=ticker,
            signal=result.get("signal", "HOLD"),
            confidence=result.get("confidence", 50.0),
            forecast_json=json.dumps(result),
            created_at=datetime.utcnow()
        )
        db.add(db_pred)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error caching prediction: {e}")
        
    return result

def train_models_task(ticker: str):
    ml_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml")
    
    # Locate venv Python interpreter dynamically
    python_exe = "python"
    venv_python = os.path.join(os.path.dirname(ml_dir), "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        python_exe = venv_python
        
    from ml.predict_utils import TF_AVAILABLE
    if TF_AVAILABLE:
        subprocess.run([python_exe, "train_all.py", "--ticker", ticker], cwd=ml_dir)
    else:
        print(f"Skipping training for {ticker} because TensorFlow is not installed.")

@router.post("/train/{ticker}")
def train_models(ticker: str, background_tasks: BackgroundTasks):
    """trigger model training for a ticker"""
    background_tasks.add_task(train_models_task, ticker)
    return {"message": f"Training started for {ticker} in the background."}
