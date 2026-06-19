import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from ml.fetch_data import fetch_stock_data
from ml.preprocess import prepare_rf_features

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "saved_models")

def get_rf_model():
    return RandomForestClassifier(
        n_estimators=200, 
        max_depth=10, 
        random_state=42, 
        class_weight='balanced'
    )

def get_model_path(ticker: str) -> str:
    return os.path.join(MODELS_DIR, f"{ticker}_rf.pkl")

def train_rf(ticker: str):
    print(f"Fetching data for {ticker} (Random Forest)...")
    df = fetch_stock_data(ticker, period="5y")
    
    if df.empty:
        print("No data found")
        return
        
    features_df = prepare_rf_features(df)
    if features_df.empty:
        print("Not enough data to create features")
        return
        
    # Exclude targets from features
    target_col = 'signal'
    exclude_cols = [target_col]
    
    X = features_df.drop(columns=exclude_cols)
    y = features_df[target_col]
    
    # Train-test split 80/20
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    model = get_rf_model()
    print("Training Random Forest model...")
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        
    path = get_model_path(ticker)
    joblib.dump((model, list(X.columns)), path) # Save model and feature names
    print(f"Random Forest model saved to {path}")

def predict_signal(ticker: str, latest_features: pd.DataFrame) -> str:
    path = get_model_path(ticker)
    if not os.path.exists(path):
        return "HOLD" # fallback if no model
        
    model, feature_names = joblib.load(path)
    
    # Ensure columns match training
    X = latest_features[feature_names]
    
    # Predict using the latest row
    pred = model.predict(X.tail(1))[0]
    
    if pred == 1:
        return "BUY"
    elif pred == -1:
        return "SELL"
    else:
        return "HOLD"

def get_feature_importance(ticker: str) -> dict:
    path = get_model_path(ticker)
    if not os.path.exists(path):
        return {}
        
    model, feature_names = joblib.load(path)
    importances = model.feature_importances_
    
    # Create dict and sort by importance
    feat_imp = {feat: float(imp) for feat, imp in zip(feature_names, importances)}
    sorted_feat_imp = dict(sorted(feat_imp.items(), key=lambda item: item[1], reverse=True))
    
    return sorted_feat_imp
