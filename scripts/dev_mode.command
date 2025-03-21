#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Move up to the project root directory
PROJECT_DIR="$( cd "$DIR/.." && pwd )"
cd "$PROJECT_DIR"

echo "===== Art Data Extract - Development Mode ====="

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

# Check if watchdog is installed
if ! pip3 show watchdog &> /dev/null; then
    echo "Installing watchdog for file monitoring..."
    pip3 install watchdog
fi

# Run the development mode script
echo "Starting development mode..."
python3 "$DIR/dev_mode.py" 