# 📰 Fake News Detection System

A comprehensive machine learning solution for detecting fake news articles using Natural Language Processing (NLP) and classification algorithms. Built with FastAPI backend and Streamlit frontend.

## ✨ Features

- **High Accuracy Detection**: 99%+ F1-Score on test data
- **Real-time Predictions**: Instant classification of news articles
- **Batch Processing**: Analyze multiple articles at once
- **Interactive Web Interface**: User-friendly Streamlit dashboard
- **RESTful API**: Complete FastAPI backend with full documentation
- **Model Management**: Train, evaluate, and persist models
- **Comprehensive Metrics**: Accuracy, Precision, Recall, and F1-Score tracking
- **Visualization Dashboard**: Plotly charts for model performance and predictions

## 📁 Project Structure

```
news_detection_project/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── train_model.py          # Model training script
│   └── __init__.py
├── frontend/
│   └── app.py                  # Streamlit web interface
├── models/                     # Saved model artifacts
│   ├── news_detection_model.pkl
│   └── tfidf_vectorizer.pkl
├── data/                       # Dataset directory
│   ├── Fake.csv               # Fake news articles
│   └── True.csv               # True news articles
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── .gitignore
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone/Setup Project

```bash
cd /Users/vinaysharma/git_class/news_detection_project
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Prepare Data

Place your CSV files in the `data/` directory:
- `data/Fake.csv` - Should contain fake news articles with a 'text' column
- `data/True.csv` - Should contain true news articles with a 'text' column

## 🚀 Quick Start

### Option 1: Complete Setup (Recommended)

#### Terminal 1 - Train the Model

```bash
# From the project root directory
python backend/train_model.py
```

This will:
- Load Fake.csv and True.csv
- Preprocess the text data
- Train the Logistic Regression model
- Save model and vectorizer to `models/` directory
- Display performance metrics

#### Terminal 2 - Start Backend API

```bash
# From the project root directory
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Endpoint**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

#### Terminal 3 - Start Frontend

```bash
# From the project root directory
cd frontend
streamlit run app.py
```

The web interface will open at: http://localhost:8501

### Option 2: Train Model via API

Instead of running `train_model.py`, you can train the model through the API:

```bash
curl -X POST http://localhost:8000/train
```

## 📖 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```http
GET /health
```
Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2024-03-16T10:30:00"
}
```

#### 2. Single Prediction
```http
POST /predict
Content-Type: application/json

{
  "text": "Your news article text here..."
}
```

Response:
```json
{
  "text": "Your news article text here...",
  "prediction": "TRUE",
  "confidence": 95.50,
  "probability_fake": 0.0450,
  "probability_true": 0.9550,
  "timestamp": "2024-03-16T10:30:00"
}
```

#### 3. Batch Prediction
```http
POST /batch-predict
Content-Type: application/json

[
  {"text": "Article 1..."},
  {"text": "Article 2..."},
  {"text": "Article 3..."}
]
```

Response:
```json
{
  "total_articles": 3,
  "predictions": [
    {
      "text": "Article 1...",
      "prediction": "FAKE",
      "confidence": 87.23,
      "probability_fake": 0.8723,
      "probability_true": 0.1277
    },
    ...
  ],
  "timestamp": "2024-03-16T10:30:00"
}
```

#### 4. Model Information
```http
GET /model-info
```

Response:
```json
{
  "trained": true,
  "accuracy": 0.9912,
  "precision": 0.9915,
  "recall": 0.9908,
  "f1_score": 0.9911,
  "train_size": 4628,
  "test_size": 1158,
  "created_at": "2024-03-16T10:00:00"
}
```

#### 5. Train Model
```http
POST /train
```

This endpoint triggers model training on the dataset.

#### 6. Upload CSV
```http
POST /upload-csv
Content-Type: multipart/form-data

[file: your_file.csv]
```

## 💻 Using the Streamlit Frontend

The web interface provides:

### 🏠 Home Page
- Project overview
- Current model status
- Key statistics
- Quick navigation

### 🔍 Single Article Prediction
- Paste or type a news article
- Get instant prediction
- View confidence scores
- See probability distributions
- Interactive visualizations

### 📊 Batch Prediction
- Analyze multiple articles
- Upload CSV files
- Download results
- Summary statistics
- Distribution charts

### 📈 Model Information
- View all performance metrics
- Visualize model accuracy
- See dataset statistics
- Radar charts for performance comparison

### ⚙️ Train Model
- Retrain the model
- Monitor training progress
- View training results immediately

## 🔧 Advanced Usage

### Training with Custom Parameters

Edit `backend/train_model.py` and modify:

```python
def train_model(df, test_size=0.2, random_state=42):
    # Modify test_size, random_state, etc.
    
    vectorizer = TfidfVectorizer(
        max_features=5000,      # Change feature count
        stop_words='english',
        min_df=5,               # Minimum document frequency
        max_df=0.7              # Maximum document frequency
    )
```

### Using the Model Programmatically

```python
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Load model and vectorizer
with open('models/news_detection_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('models/tfidf_vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# Make predictions
text = "Your news article..."
text_tfidf = vectorizer.transform([text])
prediction = model.predict(text_tfidf)[0]
confidence = model.predict_proba(text_tfidf)[0]

print(f"Prediction: {'TRUE' if prediction == 1 else 'FAKE'}")
print(f"Confidence: {confidence[prediction]*100:.2f}%")
```

## 📊 Model Performance

The trained model achieves:
- **Accuracy**: ~99.12%
- **Precision**: ~99.15%
- **Recall**: ~99.08%
- **F1-Score**: ~99.11%

Based on testing on ~1,158 test articles.

## 🧹 Data Preprocessing Steps

1. **Text Cleaning**
   - Convert to lowercase
   - Remove special characters (keep only letters and spaces)

2. **Feature Extraction**
   - TF-IDF Vectorization with max 5,000 features
   - English stop words removal
   - Minimum document frequency: 5
   - Maximum document frequency: 0.7

3. **Train-Test Split**
   - Training: 80%
   - Testing: 20%
   - Stratified split to maintain label distribution

## 🐛 Troubleshooting

### API Not Connecting
```bash
# Make sure API is running
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Model Not Found Error
```bash
# Train the model first
python backend/train_model.py
```

### Streamlit Connection Issues
```bash
# Make sure ports are available
# Kill process on port 8000 (API) and 8501 (Streamlit) if needed
lsof -ti:8000 | xargs kill -9  # macOS/Linux
lsof -ti:8501 | xargs kill -9
```

### CSV File Issues
- Ensure CSV has a 'text' column
- Check for special encodings (use UTF-8)
- Verify file is not corrupted

## 📦 Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI web server
- **Streamlit**: Interactive data app framework
- **scikit-learn**: Machine learning library
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **Requests**: HTTP library for API calls

## 🔐 Security Considerations

For production deployment:

1. **API Key Authentication**: Add authentication to FastAPI endpoints
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **HTTPS**: Use SSL/TLS certificates
4. **Input Validation**: Validate all user inputs
5. **CORS**: Configure CORS appropriately for your domain

Example:
```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/predict")
def predict(article: NewsArticle, credentials: HTTPAuthCredentials = Depends(security)):
    # Validate credentials
    pass
```

## 🚀 Deployment

### Local Testing
```bash
# Terminal 1
cd backend && python -m uvicorn main:app --reload

# Terminal 2
cd frontend && streamlit run app.py
```

### Docker Deployment
Create a `Dockerfile` for containerized deployment.

### Cloud Deployment
- Heroku
- AWS (EC2, Lambda)
- Google Cloud
- Azure
- DigitalOcean

## 📝 Example Usage

### Python Script
```python
import requests

# Single prediction
response = requests.post(
    'http://localhost:8000/predict',
    json={'text': 'Your news article text...'}
)
result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}%")
```

### cURL
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your news article text here..."}'
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [Pandas Documentation](https://pandas.pydata.org/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Developed as a comprehensive machine learning project for fake news detection.

## 📞 Support

For issues and questions:
1. Check the Troubleshooting section
2. Review API documentation at http://localhost:8000/docs
3. Check logs for error messages

---

**Happy Detecting! 🎯📰**
