#!/bin/bash

# FraudGuard Backend Setup Script
# Automates the setup process for the fraud detection backend

echo "======================================"
echo "FraudGuard Backend Setup"
echo "======================================"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✅ Python $python_version detected (>= 3.8 required)"
else
    echo "❌ Python 3.8 or higher is required"
    exit 1
fi

echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p models
mkdir -p logs
echo "✅ Directories created"
echo ""

# Create __init__.py in src
echo "📄 Creating package files..."
touch src/__init__.py
echo "✅ Package files created"
echo ""

# Generate sample data
echo "🎲 Generating sample data..."
python generate_sample_data.py
echo "✅ Sample data generated"
echo ""

# Run initial tests
echo "🧪 Running initial tests..."
python -c "from src.data_processor import DataProcessor; print('✅ DataProcessor imported successfully')"
python -c "from src.model_manager import ModelManager; print('✅ ModelManager imported successfully')"
python -c "from src.fraud_detector import FraudDetector; print('✅ FraudDetector imported successfully')"
echo ""

echo "======================================"
echo "✨ Setup Complete!"
echo "======================================"
echo ""
echo "📝 Next steps:"
echo ""
echo "1️⃣  Start the server:"
echo "   python app.py"
echo ""
echo "2️⃣  Train the model:"
echo "   curl -X POST -F 'file=@training_data.csv' http://localhost:5000/api/train"
echo ""
echo "3️⃣  Test predictions:"
echo "   curl -X POST -F 'file=@test_transactions.csv' http://localhost:5000/api/predict"
echo ""
echo "4️⃣  Check health:"
echo "   curl http://localhost:5000/api/health"
echo ""
echo "======================================"