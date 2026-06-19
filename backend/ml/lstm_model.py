import os
from tensorflow.keras.models import Sequential, load_model as keras_load_model
from tensorflow.keras.layers import LSTM, Dropout, Dense
from tensorflow.keras.optimizers import Adam

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "saved_models")

def build_lstm_model():
    model = Sequential()
    
    # Layer 1
    model.add(LSTM(units=128, return_sequences=True, input_shape=(60, 1)))
    # Layer 2
    model.add(Dropout(0.2))
    # Layer 3
    model.add(LSTM(units=64, return_sequences=False))
    # Layer 4
    model.add(Dropout(0.2))
    # Layer 5
    model.add(Dense(units=32))
    # Layer 6
    model.add(Dense(units=1))
    
    # Compile
    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='mean_squared_error')
    
    return model

def save_model(model, ticker: str):
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
    path = os.path.join(MODELS_DIR, f"{ticker}_lstm.h5")
    # Using the standard keras save method
    model.save(path)
    print(f"Model saved to {path}")

def load_model(ticker: str):
    path = os.path.join(MODELS_DIR, f"{ticker}_lstm.h5")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found at {path}")
    return keras_load_model(path)
