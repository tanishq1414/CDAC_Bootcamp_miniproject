#!/bin/bash

echo "Starting Dynamic Firewall System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running install script..."
    ./scripts/install.sh
fi

# Activate virtual environment
source venv/bin/activate

# Start the application
python app/main.py