import argparse
import os
import pickle
import numpy as np

try:
    from tensorflow.keras.callbacks import EarlyStopping
    from ml.deep_learning import build_lstm_model, build_gru_model, save_dl_model, MODELS_DIR
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "saved_models")

from ml.fetch_data import fetch_stock_data
from ml.preprocess import prepare_lstm_data

def train_dl_model(ticker: str, model_type: str, X_train, y_train, X_test, y_test, scaler):
    if not TF_AVAILABLE:
        print(f"Skipping {model_type.upper()} training. TensorFlow is not installed.")
        return 0.0
        
    print(f"\n--- Training {model_type.upper()} model for {ticker} ---")
    if model_type == "lstm":
        model = build_lstm_model()
    else:
        model = build_gru_model()
        
    early_stop = EarlyStopping(monitor='val_loss', patience=6, restore_best_weights=True)
    
    # Train
    model.fit(
        X_train, y_train,
        epochs=15, 
        batch_size=32,
        validation_data=(X_test, y_test),
        callbacks=[early_stop],
        verbose=1
    )
    
    # Evaluate
    y_pred_scaled = model.predict(X_test)
    y_pred = scaler.inverse_transform(y_pred_scaled)
    y_test_true = scaler.inverse_transform(y_test.reshape(-1, 1))
    
    rmse = np.sqrt(np.mean(((y_pred - y_test_true) ** 2)))
    print(f"{model_type.upper()} Test RMSE: {rmse:.2f}")
    
    save_dl_model(model, ticker, model_type)
    return rmse

def main():
    parser = argparse.ArgumentParser(description='Train Deep Learning models for stock prediction')
    parser.add_argument('--ticker', type=str, required=True, help='Stock ticker (e.g. TCS)')
    args = parser.parse_args()
    ticker = args.ticker

    if not TF_AVAILABLE:
        print(f"TensorFlow is not available. Skipping deep learning training for {ticker}.")
        return

    print(f"Fetching data for {ticker} (using 5y period)...")
    df = fetch_stock_data(ticker, period="5y")
    
    if df.empty:
        print(f"No data found for {ticker}")
        return

    print("Preprocessing sequence data...")
    try:
        X_train, y_train, X_test, y_test, scaler = prepare_lstm_data(df, lookback=60)
    except Exception as e:
        print(f"Preprocessing error: {e}")
        return

    # Train LSTM
    lstm_rmse = train_dl_model(ticker, "lstm", X_train, y_train, X_test, y_test, scaler)
    
    # Train GRU
    gru_rmse = train_dl_model(ticker, "gru", X_train, y_train, X_test, y_test, scaler)
    
    # Save the common scaler
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
    scaler_path = os.path.join(MODELS_DIR, f"{ticker}_scaler.pkl")
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
        
    print(f"\nTraining completed for {ticker}!")
    print(f"LSTM RMSE: {lstm_rmse:.2f} | GRU RMSE: {gru_rmse:.2f}")
    print(f"Scaler saved to {scaler_path}")

if __name__ == "__main__":
    main()
