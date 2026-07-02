import yfinance as yf
import requests
import os

# Optional HuggingFace token for higher rate limits
HF_API_TOKEN = os.getenv("HF_API_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")

# Financial lexicon for high-quality fallback sentiment analysis
LEXICON = {
    "positive": [
        "profit", "profitability", "gain", "increase", "rise", "surge", "growth", "high", "positive", 
        "bullish", "upgrade", "outperform", "buy", "successful", "expansion", "beat", "strong", "rebound",
        "acquisition", "approve", "approved", "agreement", "partnership", "optimistic", "win", "wins"
    ],
    "negative": [
        "loss", "decline", "fall", "drop", "slump", "negative", "bearish", "downgrade", "sell", 
        "decrease", "fail", "failure", "shrink", "weak", "plunge", "investigation", "court", "lawsuit", 
        "fine", "deficit", "warn", "warning", "debt", "bankruptcy", "disappointing", "miss", "misses"
    ]
}

def analyze_sentiment_lexicon(text: str) -> float:
    """Calculates sentiment score in range [-1.0, 1.0] using a local lexicon."""
    text_lower = text.lower()
    pos_count = sum(1 for word in LEXICON["positive"] if word in text_lower)
    neg_count = sum(1 for word in LEXICON["negative"] if word in text_lower)
    
    total = pos_count + neg_count
    if total == 0:
        return 0.0
    return (pos_count - neg_count) / total

def get_lexicon_label(score: float) -> str:
    if score > 0.15:
        return "Bullish"
    elif score < -0.15:
        return "Bearish"
    return "Neutral"

def get_news_sentiment(ticker: str) -> dict:
    """Fetches stock news from yfinance and calculates sentiment score."""
    try:
        # yfinance expects tickers ending in .NS for NSE
        formatted_ticker = ticker
        if not formatted_ticker.endswith('.NS') and not formatted_ticker.endswith('.BO'):
            formatted_ticker = f"{ticker}.NS"
            
        stock = yf.Ticker(formatted_ticker)
        news_list = stock.news
        
        if not news_list:
            return {
                "score": 0.0,
                "label": "Neutral",
                "articles_analyzed": 0,
                "news": []
            }
            
        articles = []
        scores = []
        
        # We will attempt to run HuggingFace FinBERT API for headlines
        # But we will fall back on lexicon for each article if API fails
        hf_failed = False
        
        for item in news_list[:5]: # Analyze top 5 recent articles
            content = item.get("content", {}) if "content" in item else item
            title = content.get("title", "") or item.get("title", "")
            
            provider = content.get("provider", {}) if isinstance(content.get("provider"), dict) else {}
            publisher = provider.get("displayName", "") or content.get("publisher", "") or item.get("publisher", "")
            
            canonical_url = content.get("canonicalUrl", {}) if isinstance(content.get("canonicalUrl"), dict) else {}
            link = canonical_url.get("url", "") or content.get("link", "") or item.get("link", "")

            
            score = 0.0
            label = "Neutral"
            
            # Try HuggingFace FinBERT
            if not hf_failed:
                try:
                    headers = {}
                    if HF_API_TOKEN:
                        headers["Authorization"] = f"Bearer {HF_API_TOKEN}"
                        
                    # ProsusAI/finbert is the standard financial sentiment model on HF
                    api_url = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
                    response = requests.post(
                        api_url, 
                        json={"inputs": title}, 
                        headers=headers,
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        predictions = response.json()
                        # Output format is usually list of list of dicts: [[{"label": "positive", "score": 0.9}, ...]]
                        if predictions and isinstance(predictions, list) and len(predictions) > 0:
                            scores_list = predictions[0]
                            # Find highest scoring label
                            best_pred = max(scores_list, key=lambda x: x["score"])
                            hf_label = best_pred["label"]
                            hf_score = best_pred["score"]
                            
                            # Map positive -> 1.0, negative -> -1.0, neutral -> 0.0, weighted by prediction confidence
                            if hf_label == "positive":
                                score = hf_score
                                label = "Bullish"
                            elif hf_label == "negative":
                                score = -hf_score
                                label = "Bearish"
                            else:
                                score = 0.0
                                label = "Neutral"
                        else:
                            raise ValueError("Invalid HF response format")
                    else:
                        # Rate limit or loading state, fall back to lexicon
                        hf_failed = True
                        score = analyze_sentiment_lexicon(title)
                        label = get_lexicon_label(score)
                except Exception:
                    # Catch all network/timeout/format issues and fallback to lexicon
                    hf_failed = True
                    score = analyze_sentiment_lexicon(title)
                    label = get_lexicon_label(score)
            else:
                score = analyze_sentiment_lexicon(title)
                label = get_lexicon_label(score)
                
            scores.append(score)
            articles.append({
                "title": title,
                "publisher": publisher,
                "link": link,
                "score": round(score, 2),
                "label": label
            })
            
        avg_score = sum(scores) / len(scores) if scores else 0.0
        final_label = "Bullish" if avg_score > 0.15 else "Bearish" if avg_score < -0.15 else "Neutral"
        
        return {
            "score": round(avg_score, 2),
            "label": final_label,
            "articles_analyzed": len(articles),
            "news": articles
        }
        
    except Exception as e:
        print(f"Sentiment analysis error for {ticker}: {e}")
        return {
            "score": 0.0,
            "label": "Neutral",
            "articles_analyzed": 0,
            "news": [],
            "error": str(e)
        }
