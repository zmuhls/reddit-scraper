#!/bin/bash

# Setup script for pushing Reddit Scraper to Hugging Face

echo "==== Reddit Scraper: Hugging Face Setup ===="
echo ""

# Check for required tools
echo "Checking for required tools..."

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git before continuing."
    exit 1
else
    echo "✅ Git installed"
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3 before continuing."
    exit 1
else
    echo "✅ Python 3 installed"
fi

if ! command -v pip3 &> /dev/null; then
    echo "❌ pip not found. Please install pip before continuing."
    exit 1
else
    echo "✅ pip installed"
fi

if ! command -v huggingface-cli &> /dev/null; then
    echo "⚠️ Hugging Face CLI not installed. Installing now..."
    pip install huggingface_hub
    if ! command -v huggingface-cli &> /dev/null; then
        echo "❌ Failed to install Hugging Face CLI. Please install manually: pip install huggingface_hub"
        exit 1
    else
        echo "✅ Hugging Face CLI installed"
    fi
else
    echo "✅ Hugging Face CLI installed"
fi

echo ""
echo "Verifying project files..."

# Check for required files
required_files=("app.py" "requirements.txt" "enhanced_scraper.py" "advanced_scraper_ui.py" "README-HF.md")
missing_files=0

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        missing_files=$((missing_files+1))
    else
        echo "✅ Found $file"
    fi
done

if [ $missing_files -gt 0 ]; then
    echo ""
    echo "❌ Some required files are missing. Please make sure all project files exist."
    exit 1
fi

echo ""
echo "All required files are present."
echo ""

# Check for Hugging Face login
echo "Checking Hugging Face login status..."
huggingface-cli whoami &> /dev/null
if [ $? -ne 0 ]; then
    echo "You need to login to Hugging Face first."
    echo "Run the following command and follow the instructions:"
    echo ""
    echo "huggingface-cli login"
    echo ""
    exit 1
else
    echo "✅ Already logged in to Hugging Face"
fi

echo ""
echo "==== Ready to push to Hugging Face! ===="
echo ""
echo "To create a new Hugging Face Space and push your code:"
echo ""
echo "1. Go to https://huggingface.co/new-space"
echo "2. Choose a Space name (e.g., 'reddit-scraper')"
echo "3. Select 'Streamlit' as the SDK"
echo "4. Create the Space"
echo ""
echo "Then run the following commands to push your code:"
echo ""
echo "git init"
echo "git add ."
echo "git commit -m \"Initial commit of Reddit Scraper\""
echo "git branch -M main"
echo "git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/reddit-scraper"
echo "git push -u origin main"
echo ""
echo "Replace YOUR_USERNAME with your Hugging Face username."
echo ""
echo "Remember to set up your Reddit API credentials in the Space settings!"
echo ""
