#!/bin/bash

echo "Installing Dynamic Firewall with AI Deceptive Layer..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating data directories..."
mkdir -p data/{logs,config,training_data,backups}

# Create default config
echo "Creating default configuration..."
python -c "
from app.config import Config
Config.save_config()
print('Default configuration created.')"

echo "Installation complete!"
echo "To start the application, run: source venv/bin/activate && python app/main.py"
