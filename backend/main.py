import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import stock, predict, market, indicators, watchlist, auth_router

load_dotenv()

app = FastAPI(title="StockAI API", version="1.0.0")

# Setup CORS origins dynamically
origins_env = os.getenv("CORS_ORIGINS", "")
origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
if not origins:
    origins = [
        "http://localhost:4200",
        "https://your-vercel-app.vercel.app"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to create tables
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(stock.router, prefix="/stock", tags=["Stock Data"])
app.include_router(predict.router, prefix="/predict", tags=["Predictions"])
app.include_router(market.router, prefix="/market", tags=["Market Overview"])
app.include_router(indicators.router, prefix="/indicators", tags=["Indicators"])
app.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])
app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])

@app.get("/")
def read_root():
    return {"message": "StockAI API is running", "version": "1.0.0"}
