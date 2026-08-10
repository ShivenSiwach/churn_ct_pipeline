from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import xgboost as xgb
import os

app = FastAPI(title="Churn Prediction API", version="1.0")

# 1. Define the Expected Payload
class CustomerData(BaseModel):
    Tenure: float
    MonthlyCharges: float
    TotalCharges: float

# 2. Global Model Variable
model = None

# 3. Load the model on startup
@app.on_event("startup")
def load_model():
    global model
    model_path = "data/model.pkl" # In a full MLflow setup, this pulls from the registry
    
    if os.path.exists(model_path):
        model = xgb.XGBClassifier()
        model.load_model(model_path)
        print(" Model loaded successfully.")
    else:
        print(" Warning: No model found at startup. Waiting for first CT pipeline run.")

# 4. The Health Check Endpoint (Crucial for Blue/Green Deployment)
@app.get("/health")
def health_check():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")
    return {"status": "healthy", "model_version": "champion"}

# 5. The Prediction Endpoint
@app.post("/predict")
def predict_churn(data: CustomerData):
    if model is None:
        raise HTTPException(status_code=503, detail="Model is currently unavailable.")
    
    # Convert incoming JSON payload to DataFrame
    df = pd.DataFrame([data.model_dump()])
    
    # Generate prediction
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]
    
    return {
        "churn_prediction": int(prediction),
        "churn_probability": float(probability)
    }