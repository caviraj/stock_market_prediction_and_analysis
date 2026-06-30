import os
from tensorflow.keras.models import Sequential, load_model as keras_load_model
from tensorflow.keras.layers import LSTM, GRU, Dropout, Dense
from tensorflow.keras.optimizers import Adam

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "saved_models")

def build_lstm_model():
    model = Sequential()
    model.add(LSTM(units=128, return_sequences=True, input_shape=(60, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=64, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=32))
    model.add(Dense(units=1))
    
    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='mean_squared_error')
    return model

def build_gru_model():
    model = Sequential()
    model.add(GRU(units=128, return_sequences=True, input_shape=(60, 1)))
    model.add(Dropout(0.2))
    model.add(GRU(units=64, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=32))
    model.add(Dense(units=1))
    
    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='mean_squared_error')
    return model

def save_dl_model(model, ticker: str, model_type: str = "lstm"):
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
    path = os.path.join(MODELS_DIR, f"{ticker}_{model_type}.h5")
    model.save(path)
    print(f"{model_type.upper()} model saved to {path}")

def load_dl_model(ticker: str, model_type: str = "lstm"):
    path = os.path.join(MODELS_DIR, f"{ticker}_{model_type}.h5")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{model_type.upper()} model not found at {path}")
    return keras_load_model(path)
