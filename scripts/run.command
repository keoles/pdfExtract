#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Move up to the project root directory
PROJECT_DIR="$( cd "$DIR/.." && pwd )"
cd "$PROJECT_DIR"

echo "===== Running Art Data Extract ====="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install it first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "imessage_pdf_env" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv imessage_pdf_env
    source imessage_pdf_env/bin/activate
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
else
    source imessage_pdf_env/bin/activate
fi

# Generate icon if it doesn't exist
if [ ! -f "resources/icon.png" ]; then
    echo "Generating app icon..."
    python3 src/utils/icon.py
fi

# Create extracted_pdfs directory if it doesn't exist
if [ ! -d "extracted_pdfs" ]; then
    echo "Creating extracted_pdfs directory..."
    mkdir -p extracted_pdfs
fi

# Run the app
echo "Starting Art Data Extract..."
python3 src/gui/messages_sync_app.py

exit 0 