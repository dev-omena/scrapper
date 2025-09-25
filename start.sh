#!/bin/bash
set -e

echo "🚀 Starting Orizon Google Maps Scraper on Railway..."
echo "📍 Environment: Production"
echo "🐍 Python version: $(python3 --version)"

# Set basic environment variables for Railway
export RAILWAY_ENVIRONMENT=1
export PYTHONPATH="/app"
export PORT=${PORT:-5000}

# Setup display for headless Chrome
export DISPLAY=:99

# Start Xvfb for headless display (if available)
echo "🖥️ Setting up virtual display for Chrome..."
if command -v Xvfb >/dev/null 2>&1; then
    echo "Starting Xvfb on display :99..."
    Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
    sleep 2
    echo "✅ Xvfb started successfully"
else
    echo "⚠️ Xvfb not available - Chrome will run without virtual display"
fi

# Verify Chrome installation
echo "🔍 Verifying Chrome installation..."
if command -v google-chrome >/dev/null 2>&1; then
    echo "✅ Chrome found: $(google-chrome --version 2>/dev/null || echo 'Version check failed')"
    echo "Chrome path: $(which google-chrome)"
else
    echo "❌ Chrome not found in PATH"
fi

# Verify ChromeDriver
if command -v chromedriver >/dev/null 2>&1; then
    echo "✅ ChromeDriver found: $(chromedriver --version 2>/dev/null || echo 'Version check failed')"
    echo "ChromeDriver path: $(which chromedriver)"
else
    echo "❌ ChromeDriver not found in PATH"
fi

# Change to app directory
cd /app

echo "📂 Current directory: $(pwd)"
echo "📋 Available files:"
ls -la web/ | head -10

echo "🌐 Starting Flask app with Chrome support on port $PORT..."

# Start the Flask app from the web directory
cd web
python3 main.py