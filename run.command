#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "===== Running iMessage Sync App ====="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install it first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
else
    source venv/bin/activate
fi

# Generate icon if it doesn't exist
if [ ! -f "icon.png" ]; then
    echo "Generating app icon..."
    python3 icon.py
fi

# Run the app
echo "Starting iMessage Sync App..."
python3 messages_sync_app.py

exit 0 