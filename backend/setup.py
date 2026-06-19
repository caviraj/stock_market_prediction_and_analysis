import os

def main():
    # Create /data/ folder if not exists (for CSV cache)
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    # Create /ml/saved_models/ folder if not exists
    models_dir = os.path.join(os.path.dirname(__file__), "ml", "saved_models")
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        
    # Run database initialization
    from database import Base, engine
    Base.metadata.create_all(engine)
    
    print("Database tables created successfully")
    print("StockAI backend ready. Run: uvicorn main:app --reload")

if __name__ == "__main__":
    main()
