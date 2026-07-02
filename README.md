# Stock Market Prediction & Analysis Platform

A full-stack web application designed for real-time stock market data visualization, technical analysis computation, news sentiment evaluation, and machine learning-powered price forecasting.

---

## 🚀 Key Features

*   **Interactive Real-Time Charting:** High-performance candlestick and volume charts powered by the `lightweight-charts` library.
*   **Technical Analysis Engine:** Automated computation of technical indicators including SMA, EMA, RSI, MACD, Bollinger Bands, ATR, ADX, CCI, and Stochastic Oscillator.
*   **Predictive Modeling & ML Pipeline:**
    *   **LSTM Neural Networks:** Deep learning models for time-series forecasting of future stock prices.
    *   **Random Forest Classifiers:** Supervised learning models predicting direction/trend classification (buy/sell signals).
    *   **ARIMA Models:** Classical statistical models for traditional time-series forecasting.
*   **Sentiment Analysis:** News-scraping and text sentiment analysis utilizing VADER to gauge market mood for specific tickers.
*   **Watchlist Management:** Personalized dashboard for tracking favorite stocks, tickers, and predictions.
*   **Secure Authentication:** User sign-up and sign-in operations with JSON Web Tokens (JWT) and encrypted passwords.

---

## 🛠️ Tech Stack

### Backend & Machine Learning
*   **Framework:** FastAPI (Python 3.10+)
*   **Database:** SQLite with SQLAlchemy ORM
*   **Machine Learning / Data Science:** TensorFlow, Scikit-learn, Pandas, NumPy, Joblib, Pandas-TA
*   **Financial Data API:** Yahoo Finance (`yfinance`)
*   **Security:** Passlib (bcrypt), PyJWT

### Frontend
*   **Framework:** Angular 17.3.0
*   **Charting:** TradingView Lightweight Charts (`lightweight-charts`)
*   **Styling:** Vanilla CSS & Angular Materials

---

## 📂 Project Structure

```text
├── backend/                       # Python FastAPI application
│   ├── data/                      # Ticker data store (JSON/CSV cached files)
│   ├── database.py                # SQLite database session configuration
│   ├── db_models.py               # SQLAlchemy database models
│   ├── main.py                    # FastAPI entrypoint and CORS settings
│   ├── ml/                        # ML pipelines (training, preprocessing, inference)
│   │   ├── classical_ml.py        # Classical machine learning utilities
│   │   ├── deep_learning.py       # Neural network architecture helpers
│   │   ├── fetch_data.py          # Data retrieval from financial APIs
│   │   ├── indicators.py          # Tech indicator calculators
│   │   ├── lstm_model.py          # LSTM neural network configuration
│   │   ├── predict_utils.py       # Inference and forecasting pipeline
│   │   ├── sentiment.py           # Sentiment analysis engine
│   │   └── train_all.py           # Master script to train all models
│   ├── models/                    # Pydantic validation schemas
│   ├── requirements.txt           # Python backend dependencies
│   └── routers/                   # API routes (Auth, Stock, Prediction, Watchlist)
│
├── stock-market-app/              # Angular 17 frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/        # Reusable UI elements (Charts, Watchlist, Stock Grid)
│   │   │   ├── pages/             # Layout components (Dashboard, Stock Detail, Auth)
│   │   │   ├── services/          # HTTP service wrappers for communicating with FastAPI
│   │   │   └── app.routes.ts      # Angular app routing configurations
│   │   └── index.html
│   ├── package.json               # NPM package dependencies
│   └── vercel.json                # Vercel deployment configuration
│
├── deployment/                    # Configuration files for hosting services
│   ├── render.yaml                # Render blueprint for backend hosting
│   └── vercel.json                # Alternative vercel hosting configurations
│
└── schema.sql                     # Raw database DDL schema structure
```

---

## ⚙️ Getting Started & Setup

### Prerequisites
*   [Node.js](https://nodejs.org/) (v18 or higher recommended)
*   [Python](https://www.python.org/) (v3.10 or higher recommended)

---

### 1. Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```

2.  Create and activate a virtual environment:
    *   **Windows (PowerShell/CMD):**
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure Environment Variables:
    *   Duplicate `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Open `.env` and fill in the secrets (such as custom database URL, JWT secret key, or third-party API keys).

5.  Initialize database tables:
    ```bash
    python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
    ```

6.  Start the FastAPI development server:
    ```bash
    uvicorn main:app --reload
    ```
    The backend server will run on `http://127.0.0.1:8000`.

---

### 2. Frontend Setup

1.  Navigate to the `stock-market-app` directory:
    ```bash
    cd stock-market-app
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Start the Angular development server:
    ```bash
    npm run start
    ```
    The application will compile and start. Open `http://localhost:4200/` in your browser.

---

## 🔮 Machine Learning Model Training

To retrain the ML forecasting models (LSTM and Random Forest Classifier) with fresh market data:
1.  Navigate to the `backend` directory.
2.  Activate the virtual environment.
3.  Run the master training script:
    ```bash
    python ml/train_all.py
    ```
This will fetch latest data, compute indicators, train models, and serialize the trained weight binaries to the `backend/ml/saved_models/` folder.

---

## 🌐 Deployment

### Frontend (Vercel)
The Angular project contains a `vercel.json` file. You can connect your GitHub repository directly to Vercel and set the Root Directory to `stock-market-app`.

### Backend (Render / Railway)
The backend can be deployed using the Render Blueprints configuration found in `deployment/render.yaml`. Alternatively, host the FastAPI application as a Web Service running:
*   **Build Command:** `pip install -r requirements.txt`
*   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
