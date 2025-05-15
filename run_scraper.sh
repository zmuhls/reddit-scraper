#!/bin/bash

# Script to run the Reddit web scraper UI

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but could not be found. Please install Python 3."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is required but could not be found. Please install pip."
    exit 1
fi

# Check for virtual environment
if [[ ! -d "venv" ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install or update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the Reddit scraper UI
echo "Starting Reddit scraper UI..."
streamlit run advanced_scraper_ui.py

# Deactivate virtual environment on exit
deactivate
