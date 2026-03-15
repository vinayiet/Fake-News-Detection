# 🚀 Fake News Detection System - Setup & Startup Guide

## 📋 Prerequisites

- **Python 3.8+**
- **pip** (comes with Python)
- **Git** (optional, for version control)
- **macOS/Linux/Windows** (all platforms supported)

## 🔧 Step-by-Step Setup

### Step 1: Navigate to Project Directory

```bash
cd /Users/vinaysharma/git_class/news_detection_project
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

**Verify activation**: You should see `(venv)` in your terminal prompt

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (backend)
- Streamlit (frontend)
- scikit-learn & pandas (ML libraries)
- Plotly (visualizations)
- And other dependencies

**Expected time**: 2-5 minutes

### Step 4: Prepare Dataset

Ensure these files exist in the `data/` directory:
- `data/Fake.csv`
- `data/True.csv`

```bash
# Check data files
ls -la data/

# Should output:
# Fake.csv
# True.csv
```

## 🏃 Running the System

### Option A: Quick Start (Automatic)

```bash
# Make script executable (first time only)
chmod +x setup.sh

# Run setup
./setup.sh

# Follow the on-screen instructions
```

### Option B: Manual Setup (Recommended for Understanding)

You'll need **3 terminal windows** open:

#### Terminal 1️⃣: Train the Model

```bash
# Activate virtual environment (if not already)
cd /Users/vinaysharma/git_class/news_detection_project
source venv/bin/activate

# Train the model
python backend/train_model.py
```

**Expected Output**:
```
Starting model training pipeline...
Loading fake news from data/Fake.csv...
Loading true news from data/True.csv...
...
MODEL PERFORMANCE METRICS
==================================================
Accuracy:  0.9912
Precision: 0.9915
Recall:    0.9908
F1-Score:  0.9911
==================================================
✓ Model and vectorizer saved successfully!
```

**Time**: 2-5 minutes depending on dataset size

#### Terminal 2️⃣: Start API Server

```bash
# Navigate to backend directory
cd /Users/vinaysharma/git_class/news_detection_project/backend

# Activate virtual environment
source ../venv/bin/activate

# Start API server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Application startup complete
```

**API Now Available At**:
- Main: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Terminal 3️⃣: Start Frontend

```bash
# Navigate to frontend directory
cd /Users/vinaysharma/git_class/news_detection_project/frontend

# Activate virtual environment
source ../venv/bin/activate

# Start Streamlit
streamlit run app.py
```

**Expected Output**:
```
  You can now view your Streamlit app in your browser.

  URL: http://localhost:8501

  Network URL: http://192.168.x.x:8501
```

**Frontend Now Available At**:
- http://localhost:8501

## ✅ Verify Everything is Working

### 1. Check API Health

Open in browser or terminal:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2024-03-16T10:30:00"
}
```

### 2. Make a Test Prediction

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Scientists discover breakthrough in cancer treatment"
  }'
```

### 3. Open Frontend

Visit http://localhost:8501 in your browser

## 📚 Using the Application

### 🏠 Home Page
- Overview of the project
- Current model status
- Quick navigation buttons

### 🔍 Single Prediction
1. Paste a news article
2. Click "Analyze"
3. View prediction with confidence score
4. See probability distribution charts

### 📊 Batch Prediction
1. Paste multiple articles (separated by delimiter)
2. Or upload a CSV file
3. Click "Analyze Batch"
4. Download results as CSV

### ⚙️ Train Model
1. Click "Start Training"
2. Wait for training to complete
3. View new metrics
4. Model is saved automatically

## 🔌 API Endpoints Quick Reference

### Make Predictions

**Single Article**:
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your article text..."}'
```

**Multiple Articles**:
```bash
curl -X POST "http://localhost:8000/batch-predict" \
  -H "Content-Type: application/json" \
  -d '[
    {"text": "Article 1..."},
    {"text": "Article 2..."}
  ]'
```

### Get Model Info

```bash
curl http://localhost:8000/model-info
```

## 🐛 Troubleshooting

### "Cannot connect to API"
- ✅ Make sure Terminal 2 is running the API server
- ✅ Check that port 8000 is not in use
- ✅ Try: `lsof -i :8000`

### "Model not trained yet"
- ✅ Run `python backend/train_model.py` in Terminal 1
- ✅ Wait for training to complete
- ✅ Check the models/ directory exists

### "Port already in use"

Kill process on port:
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### CSV file issues
- ✅ Ensure CSV has a 'text' column
- ✅ File should be UTF-8 encoded
- ✅ No corrupted data

### Slow predictions
- ✅ Normal for first prediction
- ✅ Model caching after first call
- ✅ Check system resources

## 📦 Project Structure Check

```
news_detection_project/
├── ✅ backend/
│   ├── main.py
│   ├── train_model.py
│   ├── config.py
│   └── __init__.py
├── ✅ frontend/
│   └── app.py
├── ✅ models/
│   ├── news_detection_model.pkl
│   └── tfidf_vectorizer.pkl
├── ✅ data/
│   ├── Fake.csv
│   └── True.csv
├── ✅ requirements.txt
├── ✅ README.md
├── ✅ STARTUP.md (this file)
└── ✅ setup.sh
```

## 🎯 Common Workflows

### Workflow 1: Fresh Start
```bash
# Terminal 1
python backend/train_model.py

# Terminal 2
cd backend && python -m uvicorn main:app --reload

# Terminal 3
cd frontend && streamlit run app.py
```

### Workflow 2: Only Frontend Changes
```bash
# No need to restart API or retrain
# Just rerun Streamlit
cd frontend && streamlit run app.py
```

### Workflow 3: Only API Changes
```bash
# API auto-reloads with --reload flag
# No restart needed for code changes
# If model changes, retrain
```

## 📊 Model Retraining

When to retrain:
- New dataset available
- Want to tune hyperparameters
- Model performance needs improvement

To retrain:
```bash
python backend/train_model.py
```

The new model will be saved to `models/` automatically.

## 🔒 Security Notes for Production

For production deployment:
- ✅ Use environment variables for secrets
- ✅ Add authentication to API endpoints
- ✅ Set CORS properly
- ✅ Use HTTPS/SSL
- ✅ Add rate limiting
- ✅ Validate all inputs

## 📈 Performance Tips

- **First Prediction**: 1-2 seconds (model loading)
- **Subsequent Predictions**: <100ms
- **Batch Predictions**: ~10-20ms per article
- **Model Training**: 2-5 minutes (depends on dataset)

## 🆘 Getting Help

If stuck:
1. Check logs in Terminal output
2. Review API docs: http://localhost:8000/docs
3. Check README.md for detailed information
4. Verify all prerequisites are installed

## 🎉 You're Ready!

Once all three terminals show success messages:
- 🟢 Terminal 1: Model trained
- 🟢 Terminal 2: API running on port 8000
- 🟢 Terminal 3: Streamlit running on port 8501

Visit **http://localhost:8501** and start detecting fake news! 🚀📰

---

**Need help?** Review the troubleshooting section or check the README.md for more details.
