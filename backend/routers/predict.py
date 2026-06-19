from fastapi import APIRouter, HTTPException, BackgroundTasks
from ml.predict_utils import get_predictions
import subprocess
import os

router = APIRouter()

@router.get("/{ticker}")
def predict_stock(ticker: str):
    """load LSTM model for ticker, run prediction"""
    result = get_predictions(ticker)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

def train_models_task(ticker: str):
    ml_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml")
    
    # Train LSTM if TF is available
    from ml.predict_utils import TF_AVAILABLE
    if TF_AVAILABLE:
        subprocess.run(["python", "train_lstm.py", "--ticker", ticker], cwd=ml_dir)
    else:
        print(f"Skipping LSTM training for {ticker} because TensorFlow is not installed.")
    
    # Train RF
    subprocess.run(["python", "train_rf.py", "--ticker", ticker], cwd=ml_dir)

@router.post("/train/{ticker}")
def train_models(ticker: str, background_tasks: BackgroundTasks):
    """trigger model training for a ticker"""
    background_tasks.add_task(train_models_task, ticker)
    return {"message": f"Training started for {ticker} in the background."}
