import argparse
import os
import pickle
import numpy as np
from tensorflow.keras.callbacks import EarlyStopping
from fetch_data import fetch_stock_data
from preprocess import prepare_lstm_data
from lstm_model import build_lstm_model, save_model, MODELS_DIR

def main():
    parser = argparse.ArgumentParser(description='Train LSTM model for stock prediction')
    parser.add_argument('--ticker', type=str, required=True, help='Stock ticker (e.g. TCS)')
    args = parser.parse_args()
    ticker = args.ticker

    print(f"Fetching data for {ticker}...")
    df = fetch_stock_data(ticker, period="5y") # More data helps training
    
    if df.empty:
        print(f"No data found for {ticker}")
        return

    print("Preparing data for LSTM...")
    try:
        X_train, y_train, X_test, y_test, scaler = prepare_lstm_data(df, lookback=60)
    except ValueError as e:
        print(f"Error: {e}")
        return
        
    print("Building model...")
    model = build_lstm_model()
    
    # Early stopping callback
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    print("Training model...")
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_test, y_test),
        callbacks=[early_stop],
        verbose=1
    )
    
    print("Evaluating model...")
    # Predict and inverse transform to calculate true RMSE
    y_pred_scaled = model.predict(X_test)
    y_pred = scaler.inverse_transform(y_pred_scaled)
    y_test_true = scaler.inverse_transform(y_test.reshape(-1, 1))
    
    rmse = np.sqrt(np.mean(((y_pred - y_test_true) ** 2)))
    
    # Save model and scaler
    save_model(model, ticker)
    
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
    scaler_path = os.path.join(MODELS_DIR, f"{ticker}_scaler.pkl")
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
        
    print(f"Model saved. Test RMSE: {rmse:.2f}")

if __name__ == "__main__":
    main()
