#!/bin/bash
# Combined Vehicle Data API - Run Script

echo "🚀 Starting Combined Vehicle Data API..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if unified_vehicle_api.py exists
if [ ! -f "unified_vehicle_api.py" ]; then
    echo "❌ unified_vehicle_api.py not found!"
    exit 1
fi

# Start the API
echo "✅ Starting API on http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop"
echo ""

python unified_vehicle_api.py 