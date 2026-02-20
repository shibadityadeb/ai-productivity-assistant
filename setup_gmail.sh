#!/bin/bash
# Gmail Integration Setup Helper

echo "=================================="
echo "Gmail Integration - Setup Helper"
echo "=================================="
echo ""

# Check if credentials directory exists
if [ ! -d "credentials" ]; then
    echo "📁 Creating credentials directory..."
    mkdir -p credentials
    echo "✓ Created credentials/"
fi

# Check if credentials file exists
if [ ! -f "credentials/gmail_credentials.json" ]; then
    echo ""
    echo "⚠️  Gmail credentials not found!"
    echo ""
    echo "📋 Setup Steps:"
    echo "1. Go to: https://console.cloud.google.com/"
    echo "2. Create a new project (or select existing)"
    echo "3. Enable Gmail API"
    echo "4. Configure OAuth consent screen"
    echo "5. Create OAuth2 credentials (Desktop app)"
    echo "6. Download the credentials JSON file"
    echo "7. Save it as: credentials/gmail_credentials.json"
    echo ""
    echo "📖 Detailed guide: integrations/GMAIL_SETUP.md"
    echo ""
    exit 1
else
    echo "✓ Credentials file found: credentials/gmail_credentials.json"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "✓ Virtual environment found"
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Create with: python -m venv venv"
fi

# Check required packages
echo ""
echo "📦 Checking required packages..."
python -c "import google.auth; import google_auth_oauthlib; import googleapiclient" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ All required packages installed"
else
    echo "⚠️  Missing packages. Installing..."
    pip install google-auth google-auth-oauthlib google-api-python-client
fi

# Run quickstart
echo ""
echo "🚀 Running Gmail quickstart..."
echo ""
python integrations/gmail_quickstart.py
