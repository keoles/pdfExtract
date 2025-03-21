#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Move up to the project root directory
PROJECT_DIR="$( cd "$DIR/.." && pwd )"
cd "$PROJECT_DIR"

# Set a custom dock icon using Python
osascript -e 'tell application "Finder" to set comment of (POSIX file "'$DIR'/launch_pdf_extractor.command") to "📑"'

# Activate virtual environment if it exists
if [ -f "$PROJECT_DIR/imessage_pdf_env/bin/activate" ]; then
    source "$PROJECT_DIR/imessage_pdf_env/bin/activate"
else
    echo "Virtual environment not found. Creating one..."
    python3 -m venv imessage_pdf_env
    source imessage_pdf_env/bin/activate
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
fi

# Set the window title
echo -n -e "\033]0;PDF Rescue Squad 🚀\007"

# Create extracted_pdfs directory if it doesn't exist
if [ ! -d "extracted_pdfs" ]; then
    echo "Creating extracted_pdfs directory..."
    mkdir -p extracted_pdfs
fi

# Clear terminal and add some flair
clear
echo "🚀 Launching PDF Rescue Squad..."
echo "💫 Preparing to save your PDFs from iMessage oblivion..."
echo "🔮 Initializing the extraction portal..."
sleep 1

# Run the GUI
python3 "$PROJECT_DIR/src/gui/imessage_pdf_extract_gui.py" 