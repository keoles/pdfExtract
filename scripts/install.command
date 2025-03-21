#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Move up to the project root directory
PROJECT_DIR="$( cd "$DIR/.." && pwd )"
cd "$PROJECT_DIR"

echo "===== Art Data Extract Installer ====="
echo "This script will install Art Data Extract on your Mac."
echo "It will create a virtual environment, install dependencies, and build the app."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install it first."
    exit 1
fi

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install it first."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv imessage_pdf_env
source imessage_pdf_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip3 install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
pip3 install py2app

# Generate icon
echo "Generating app icon..."
python3 src/utils/icon.py

# Create extracted_pdfs directory
echo "Creating PDF extraction directory..."
mkdir -p extracted_pdfs

# Build the app
echo "Building the app..."
cd "$PROJECT_DIR"
python3 src/setup.py py2app

# Create the DMG
echo "Creating DMG for distribution..."
hdiutil create -volname "Art Data Extract" -srcfolder dist/Art\ Data\ Extract.app -ov -format UDZO dist/Art_Data_Extract.dmg

# Move the app to Applications folder (optional)
read -p "Would you like to install Art Data Extract to your Applications folder? (y/n) " INSTALL_APP
if [[ $INSTALL_APP == "y" || $INSTALL_APP == "Y" ]]; then
    echo "Moving app to Applications folder..."
    cp -R dist/Art\ Data\ Extract.app /Applications/
    echo "App has been installed to your Applications folder."
else
    echo "App was not installed to Applications folder."
fi

echo ""
echo "===== Installation Complete ====="
echo "You can run Art Data Extract using the scripts/run.command script or from the Applications folder if you chose to install it."
echo "To extract PDFs directly, you can use the scripts/launch_pdf_extractor.command script."

exit 0 