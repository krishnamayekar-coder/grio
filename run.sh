#!/bin/bash
# Run script for Griot Backend

# Exit on any error
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "Starting Griot Backend..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
