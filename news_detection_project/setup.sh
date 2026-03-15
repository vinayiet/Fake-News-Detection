#!/bin/bash

set -e

echo "🚀 Fake News Detection System - Setup Script"
echo "================================================"
echo ""

echo "✓ Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "  Python version: $python_version"

if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found!"
    echo "   Please run this script from the project root directory"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "🔓 Activating virtual environment..."
source venv/bin/activate

echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

echo "📥 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

echo ""
echo "📂 Checking data files..."
if [ ! -f "data/Fake.csv" ]; then
    echo "⚠️  Warning: data/Fake.csv not found"
    echo "   Please ensure Fake.csv is in the data/ directory"
fi

if [ ! -f "data/True.csv" ]; then
    echo "⚠️  Warning: data/True.csv not found"
    echo "   Please ensure True.csv is in the data/ directory"
fi

if [ -f "data/Fake.csv" ] && [ -f "data/True.csv" ]; then
    echo "✓ Data files found"
fi

# Create models directory
mkdir -p models
echo "✓ Models directory ready"

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "📖 Next Steps:"
echo ""
echo "1️⃣  Train the model (Terminal 1):"
echo "   python backend/train_model.py"
echo ""
echo "2️⃣  Start the API server (Terminal 2):"
echo "   cd backend && python -m uvicorn main:app --reload"
echo ""
echo "3️⃣  Start the Streamlit app (Terminal 3):"
echo "   cd frontend && streamlit run app.py"
echo ""
echo "📚 Documentation:"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Web App: http://localhost:8501"
echo ""
echo "💡 Tips:"
echo "   - Make sure you have Fake.csv and True.csv in data/ directory"
echo "   - Use different terminals for API and Streamlit"
echo "   - API must be running before starting Streamlit"
echo ""
echo "Happy detecting! 🎯📰"
echo ""
