#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set a custom dock icon using Python (this is a fun hack!)
osascript -e 'tell application "Finder" to set comment of (POSIX file "'$DIR'/launch_pdf_extractor.command") to "📑"'

# Activate virtual environment if it exists
if [ -f "$DIR/venv/bin/activate" ]; then
    source "$DIR/venv/bin/activate"
fi

# Set the window title
echo -n -e "\033]0;PDF Rescue Squad 🚀\007"

# Clear terminal and add some flair
clear
echo "🚀 Launching PDF Rescue Squad..."
echo "💫 Preparing to save your PDFs from iMessage oblivion..."
echo "🔮 Initializing the extraction portal..."
sleep 1

# Run the GUI
python "$DIR/imessage_pdf_extract_gui.py" 