from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import pickle
import os
import re
import logging
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fake News Detection API",
    description="An API to detect fake news using machine learning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
vectorizer = None
model_info = {
    "trained": False,
    "accuracy": 0,
    "precision": 0,
    "recall": 0,
    "f1_score": 0,
    "train_size": 0,
    "test_size": 0,
    "created_at": None
}

class NewsArticle(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    text: str
    prediction: str
    confidence: float
    probability_fake: float
    probability_true: float
    timestamp: str

class ModelMetrics(BaseModel):
    trained: bool
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    train_size: int
    test_size: int
    created_at: Optional[str]

class TrainingProgress(BaseModel):
    status: str
    message: str
    progress: int

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-zA-Z ]", "", text)
    return text

def load_model():
    global model, vectorizer
    model_path = os.path.join(os.path.dirname(__file__), "../models/news_detection_model.pkl")
    vectorizer_path = os.path.join(os.path.dirname(__file__), "../models/tfidf_vectorizer.pkl")
    
    try:
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            with open(vectorizer_path, 'rb') as f:
                vectorizer = pickle.load(f)
            model_info["trained"] = True
            logger.info("Model and vectorizer loaded successfully")
            return True
        return False
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

def save_model():
    model_dir = os.path.join(os.path.dirname(__file__), "../models")
    os.makedirs(model_dir, exist_ok=True)
    
    try:
        model_path = os.path.join(model_dir, "news_detection_model.pkl")
        vectorizer_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)
        
        logger.info("Model and vectorizer saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        return False

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Fake News Detection API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "batch_predict": "/batch-predict",
            "model_info": "/model-info",
            "train": "/train"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_info["trained"],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict", response_model=PredictionResponse)
def predict(article: NewsArticle):
    if not model_info["trained"] or model is None or vectorizer is None:
        raise HTTPException(
            status_code=400,
            detail="Model not trained yet. Please train the model first."
        )
    
    try:
        cleaned_text = clean_text(article.text)
        text_tfidf = vectorizer.transform([cleaned_text])
        
        prediction = model.predict(text_tfidf)[0]
        probabilities = model.predict_proba(text_tfidf)[0]
        
        label = "TRUE" if prediction == 1 else "FAKE"
        confidence = float(probabilities[prediction]) * 100
        
        return PredictionResponse(
            text=article.text[:200] + "..." if len(article.text) > 200 else article.text,
            prediction=label,
            confidence=round(confidence, 2),
            probability_fake=round(float(probabilities[0]), 4),
            probability_true=round(float(probabilities[1]), 4),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/batch-predict")
def batch_predict(articles: List[NewsArticle]):
    if not model_info["trained"] or model is None or vectorizer is None:
        raise HTTPException(
            status_code=400,
            detail="Model not trained yet. Please train the model first."
        )
    
    try:
        predictions = []
        for article in articles:
            cleaned_text = clean_text(article.text)
            text_tfidf = vectorizer.transform([cleaned_text])
            
            prediction = model.predict(text_tfidf)[0]
            probabilities = model.predict_proba(text_tfidf)[0]
            
            label = "TRUE" if prediction == 1 else "FAKE"
            confidence = float(probabilities[prediction]) * 100
            
            predictions.append({
                "text": article.text[:100] + "..." if len(article.text) > 100 else article.text,
                "prediction": label,
                "confidence": round(confidence, 2),
                "probability_fake": round(float(probabilities[0]), 4),
                "probability_true": round(float(probabilities[1]), 4)
            })
        
        return {
            "total_articles": len(articles),
            "predictions": predictions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in batch prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

@app.get("/model-info", response_model=ModelMetrics)
def get_model_info():
    """Get information about the trained model"""
    return ModelMetrics(**model_info)

@app.post("/train")
def train_model(fake_csv: Optional[str] = None, true_csv: Optional[str] = None):
    """
    Train the news detection model using provided CSV files
    
    Args:
        fake_csv: Path to fake news CSV file
        true_csv: Path to true news CSV file
        
    Returns:
        Training status and metrics
    """
    global model, vectorizer
    
    try:
        # Use default paths if not provided
        if not fake_csv:
            fake_csv = os.path.join(os.path.dirname(__file__), "../data/Fake.csv")
        if not true_csv:
            true_csv = os.path.join(os.path.dirname(__file__), "../data/True.csv")
        
        # Check if files exist
        if not os.path.exists(fake_csv) or not os.path.exists(true_csv):
            raise HTTPException(
                status_code=400,
                detail="CSV files not found. Please provide valid paths to Fake.csv and True.csv"
            )
        
        logger.info("Starting model training...")
        
        # Load data
        fake_df = pd.read_csv(fake_csv, engine="python", on_bad_lines="skip")
        true_df = pd.read_csv(true_csv, engine="python", on_bad_lines="skip")
        
        # Add labels
        fake_df['label'] = 0
        true_df['label'] = 1
        
        # Combine and shuffle
        df = pd.concat([fake_df, true_df], axis=0)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        df = df[["text", "label"]]
        
        # Clean text
        df["text"] = df["text"].apply(clean_text)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            df["text"], 
            df["label"],
            test_size=0.2,
            random_state=42
        )
        
        logger.info(f"Training set size: {len(X_train)}, Test set size: {len(X_test)}")
        
        # Vectorize text
        vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        X_train_tfidf = vectorizer.fit_transform(X_train)
        X_test_tfidf = vectorizer.transform(X_test)
        
        # Train model
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X_train_tfidf, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_tfidf)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        # Update model info
        model_info["trained"] = True
        model_info["accuracy"] = round(accuracy, 4)
        model_info["precision"] = round(precision, 4)
        model_info["recall"] = round(recall, 4)
        model_info["f1_score"] = round(f1, 4)
        model_info["train_size"] = len(X_train)
        model_info["test_size"] = len(X_test)
        model_info["created_at"] = datetime.now().isoformat()
        
        # Save model
        save_model()
        
        logger.info("Model training completed successfully")
        
        return {
            "status": "success",
            "message": "Model trained successfully",
            "metrics": {
                "accuracy": model_info["accuracy"],
                "precision": model_info["precision"],
                "recall": model_info["recall"],
                "f1_score": model_info["f1_score"],
                "train_size": model_info["train_size"],
                "test_size": model_info["test_size"]
            },
            "timestamp": model_info["created_at"]
        }
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        data_dir = os.path.join(os.path.dirname(__file__), "../data")
        os.makedirs(data_dir, exist_ok=True)
        
        file_path = os.path.join(data_dir, file.filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"File {file.filename} uploaded successfully")
        
        return {
            "status": "success",
            "message": f"File {file.filename} uploaded successfully",
            "file_path": file_path,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Fake News Detection API...")
    load_model()
    logger.info("API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Fake News Detection API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
