import pandas as pd
import numpy as np
import re
import pickle
import os
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z ]", "", text)
    return text

def load_data(fake_csv_path, true_csv_path):
    logger.info(f"Loading fake news from {fake_csv_path}...")
    fake_df = pd.read_csv(fake_csv_path, engine="python", on_bad_lines="skip")
    
    logger.info(f"Loading true news from {true_csv_path}...")
    true_df = pd.read_csv(true_csv_path, engine="python", on_bad_lines="skip")
    
    logger.info(f"Fake news shape: {fake_df.shape}")
    logger.info(f"True news shape: {true_df.shape}")
    
    # Add labels
    fake_df['label'] = 0
    true_df['label'] = 1
    
    # Check if 'text' column exists, if not use 'content' or first column
    if 'text' not in fake_df.columns:
        text_col = 'content' if 'content' in fake_df.columns else fake_df.columns[3]
        fake_df = fake_df.rename(columns={text_col: 'text'})
    
    if 'text' not in true_df.columns:
        text_col = 'content' if 'content' in true_df.columns else true_df.columns[3]
        true_df = true_df.rename(columns={text_col: 'text'})
    
    # Combine datasets
    df = pd.concat([fake_df, true_df], axis=0, ignore_index=True)
    
    logger.info(f"Combined dataset shape: {df.shape}")
    logger.info(f"Label distribution:\n{df['label'].value_counts()}")
    
    # Select only text and label columns
    df = df[["text", "label"]]
    
    # Shuffle dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    logger.info("Dataset shuffled successfully")
    
    return df

def preprocess_text(df):
    logger.info("Preprocessing text data...")
    df["text"] = df["text"].apply(clean_text)
    
    # Remove rows with empty text after cleaning
    df = df[df["text"].str.len() > 0]
    
    logger.info(f"Preprocessed dataset shape: {df.shape}")
    
    return df

def train_model(df, test_size=0.2, random_state=42):
    logger.info("Preparing training data...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["label"],
        test_size=test_size,
        random_state=random_state,
        stratify=df["label"]
    )
    
    logger.info(f"Training set size: {len(X_train)}")
    logger.info(f"Test set size: {len(X_test)}")
    logger.info(f"Training set label distribution:\n{y_train.value_counts()}")
    
    # Vectorize text
    logger.info("Creating TF-IDF vectors...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        min_df=5,
        max_df=0.7
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    logger.info(f"TF-IDF shape - Train: {X_train_tfidf.shape}, Test: {X_test_tfidf.shape}")
    
    # Train model
    logger.info("Training Logistic Regression model...")
    model = LogisticRegression(
        max_iter=1000,
        random_state=random_state,
        solver='lbfgs',
        n_jobs=-1
    )
    model.fit(X_train_tfidf, y_train)
    
    # Evaluate
    logger.info("Evaluating model...")
    y_pred = model.predict(X_test_tfidf)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
        "confusion_matrix": confusion_matrix(y_test, y_pred),
        "classification_report": classification_report(y_test, y_pred, target_names=["FAKE", "TRUE"])
    }
    
    # Print metrics
    logger.info("=" * 50)
    logger.info("MODEL PERFORMANCE METRICS")
    logger.info("=" * 50)
    logger.info(f"Accuracy:  {metrics['accuracy']:.4f}")
    logger.info(f"Precision: {metrics['precision']:.4f}")
    logger.info(f"Recall:    {metrics['recall']:.4f}")
    logger.info(f"F1-Score:  {metrics['f1_score']:.4f}")
    logger.info("\nConfusion Matrix:")
    logger.info(metrics['confusion_matrix'])
    logger.info("\nClassification Report:")
    logger.info(metrics['classification_report'])
    logger.info("=" * 50)
    
    return model, vectorizer, metrics

def save_model(model, vectorizer, output_dir="models"):
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, "news_detection_model.pkl")
    vectorizer_path = os.path.join(output_dir, "tfidf_vectorizer.pkl")
    
    logger.info(f"Saving model to {model_path}...")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    logger.info(f"Saving vectorizer to {vectorizer_path}...")
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    logger.info("Model and vectorizer saved successfully!")

def main(fake_csv_path, true_csv_path, output_dir="models"):
    logger.info("Starting model training pipeline...")
    
    # Validate input files
    if not os.path.exists(fake_csv_path):
        logger.error(f"File not found: {fake_csv_path}")
        return
    
    if not os.path.exists(true_csv_path):
        logger.error(f"File not found: {true_csv_path}")
        return
    
    try:
        # Load data
        df = load_data(fake_csv_path, true_csv_path)
        
        # Preprocess text
        df = preprocess_text(df)
        
        # Train model
        model, vectorizer, metrics = train_model(df)
        
        # Save model
        save_model(model, vectorizer, output_dir)
        
        logger.info("Training pipeline completed successfully!")
        
        return model, vectorizer, metrics
    
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise

if __name__ == "__main__":
    import sys
    
    # Get paths from command line arguments or use defaults
    if len(sys.argv) > 2:
        fake_csv = sys.argv[1]
        true_csv = sys.argv[2]
    else:
        # Use relative paths from project structure
        project_root = Path(__file__).parent.parent
        fake_csv = project_root / "data" / "Fake.csv"
        true_csv = project_root / "data" / "True.csv"
        fake_csv = str(fake_csv)
        true_csv = str(true_csv)
    
    output_dir = Path(__file__).parent.parent / "models"
    
    logger.info(f"Fake CSV: {fake_csv}")
    logger.info(f"True CSV: {true_csv}")
    logger.info(f"Output directory: {output_dir}")
    
    main(fake_csv, true_csv, str(output_dir))
