-- ==========================================
-- SQL Schema Definition
-- System: Stock Market Prediction & Analysis
-- Database Dialect: PostgreSQL (compatible with standard SQLite configurations)
-- Description: Sets up tables, constraints, foreign keys, and indexes.
-- ==========================================

-- -----------------------------------------------------
-- Clean-up Phase (Drop tables if they exist in reverse dependency order)
-- -----------------------------------------------------
DROP TABLE IF EXISTS trading_signals CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS watchlists CASCADE;
DROP TABLE IF EXISTS stocks CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- -----------------------------------------------------
-- Table: users
-- Stores user account info and credentials.
-- -----------------------------------------------------
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Constraints
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email)
);

-- Indexes for rapid login credential queries
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_users_email ON users (email);

-- -----------------------------------------------------
-- Table: stocks
-- Caches tracking list of NSE/BSE stocks.
-- -----------------------------------------------------
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    industry VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Constraints
    CONSTRAINT uq_stocks_ticker UNIQUE (ticker)
);

-- Index for searching tickers (e.g., during search autocomplete)
CREATE INDEX idx_stocks_ticker ON stocks (ticker);

-- -----------------------------------------------------
-- Table: watchlists
-- User-specific stock watchlist join table.
-- -----------------------------------------------------
CREATE TABLE watchlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Foreign Keys with cascade deletes
    CONSTRAINT fk_watchlist_user FOREIGN KEY (user_id) 
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_watchlist_stock FOREIGN KEY (stock_id) 
        REFERENCES stocks (id) ON DELETE CASCADE,
        
    -- Constraint to prevent duplicate watchlist entries for same stock/user combination
    CONSTRAINT uq_user_stock UNIQUE (user_id, stock_id)
);

-- -----------------------------------------------------
-- Table: predictions
-- Stores daily ML forecasts (LSTM model outputs, cached for 24 hours).
-- -----------------------------------------------------
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER NOT NULL,
    prediction_date DATE NOT NULL,
    forecast_target_date DATE NOT NULL,
    forecast_price DECIMAL(12, 4) NOT NULL,
    model_version VARCHAR(50) DEFAULT 'LSTM-v1.0' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Foreign Keys
    CONSTRAINT fk_predictions_stock FOREIGN KEY (stock_id) 
        REFERENCES stocks (id) ON DELETE CASCADE
);

-- Composite index to accelerate checking daily predictions cache per stock
CREATE INDEX idx_predictions_stock_date ON predictions (stock_id, prediction_date);

-- -----------------------------------------------------
-- Table: trading_signals
-- Stores daily classification signals (Random Forest model outputs and technical overlays).
-- -----------------------------------------------------
CREATE TABLE trading_signals (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER NOT NULL,
    signal_date DATE NOT NULL,
    signal_type VARCHAR(10) NOT NULL,
    confidence_score DECIMAL(5, 4) NOT NULL,
    rsi DECIMAL(6, 3),
    moving_average_20 DECIMAL(12, 4),
    moving_average_50 DECIMAL(12, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Foreign Keys
    CONSTRAINT fk_signals_stock FOREIGN KEY (stock_id) 
        REFERENCES stocks (id) ON DELETE CASCADE,
        
    -- Check Constraints
    CONSTRAINT chk_signal_type CHECK (signal_type IN ('BUY', 'HOLD', 'SELL')),
    CONSTRAINT chk_confidence CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0)
);

-- Composite index to accelerate checking daily signals cache per stock
CREATE INDEX idx_signals_stock_date ON trading_signals (stock_id, signal_date);
