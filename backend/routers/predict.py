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
