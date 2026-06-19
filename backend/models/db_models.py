from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Float, BigInteger, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    watchlists = relationship("Watchlist", back_populates="user")

class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticker = Column(String(20), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('user_id', 'ticker', name='_user_ticker_uc'),)

    user = relationship("User", back_populates="watchlists")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(20), nullable=False)
    signal = Column(String(10), nullable=False)  # BUY/HOLD/SELL
    forecast_json = Column(Text)  # store 7-day forecast as JSON string
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(20))

class PriceCache(Base):
    __tablename__ = "price_cache"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)

    __table_args__ = (UniqueConstraint('ticker', 'date', name='_ticker_date_uc'),)
