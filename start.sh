#!/bin/bash
set -e

echo "🚀 Starting Google Maps Scraper on Railway..."

# Set environment variables
export DISPLAY=:99
export CHROME_BIN=/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/usr/bin/chromedriver
export PYTHONPATH=/app:/app/app

# Start Xvfb for headless display
echo "🖥️ Starting virtual display..."
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Wait a moment for Xvfb to start
sleep 2

# Verify Chrome is available
echo "🔍 Verifying Chrome installation..."
if command -v google-chrome >/dev/null 2>&1; then
    echo "✅ Chrome found: $(google-chrome --version)"
else
    echo "❌ Chrome not found!"
    exit 1
fi

# Run the application
echo "🎯 Starting application..."
cd /app
python app/run.py