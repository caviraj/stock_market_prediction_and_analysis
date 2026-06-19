from fastapi import APIRouter
from ml.indicators import get_all_indicators

router = APIRouter()

@router.get("/{ticker}")
def get_indicators(ticker: str):
    """Call get_all_indicators(ticker) and return full JSON"""
    return get_all_indicators(ticker)
