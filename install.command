#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "===== iMessage Sync App Installer ====="
echo "This script will install the iMessage Sync App on your Mac."
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
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip3 install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
pip3 install py2app

# Generate icon
echo "Generating app icon..."
python3 icon.py

# Build the app
echo "Building the app..."
python3 setup.py py2app

# Move the app to Applications folder
echo "Moving app to Applications folder..."
cp -R dist/iMessage\ Sync.app /Applications/

echo ""
echo "===== Installation Complete ====="
echo "The iMessage Sync app has been installed to your Applications folder."
echo "You can launch it from there or using Spotlight Search."

exit 0 