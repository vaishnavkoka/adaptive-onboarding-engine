#!/bin/bash
# Setup and Run Script for Adaptive Onboarding Engine

echo "🎯 AI-Adaptive Onboarding Engine - Setup & Run Guide"
echo "=================================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✓ Python: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Print startup info
echo ""
echo "=================================================="
echo "✓ Setup Complete!"
echo "=================================================="
echo ""
echo "To start the application:"
echo "  python app.py"
echo ""
echo "Then open your browser to:"
echo "  http://localhost:5000"
echo ""
echo "API Documentation:"
echo "  POST /api/analyze       - Analyze resume and job"
echo "  GET  /api/health        - Health check"
echo ""
echo "For Docker deployment:"
echo "  docker build -t onboarding-engine ."
echo "  docker run -p 5000:5000 onboarding-engine"
echo ""
