#!/bin/bash
set -e

echo "🚀 Starting Google Maps Scraper on Railway..."

# Create debug directory
mkdir -p /tmp/debug

# Set environment variables
export DISPLAY=:99
export PYTHONPATH=/app:/app/app
export RAILWAY_ENVIRONMENT=true

# Detect Chrome installation
if command -v google-chrome >/dev/null 2>&1; then
    export CHROME_BIN=/usr/bin/google-chrome
elif command -v chromium >/dev/null 2>&1; then
    export CHROME_BIN=$(which chromium)
    # Create symbolic link if it doesn't exist
    if [ ! -f /usr/bin/google-chrome ]; then
        ln -sf $(which chromium) /usr/bin/google-chrome
    fi
    export CHROME_BIN=/usr/bin/google-chrome
else
    echo "❌ No Chrome or Chromium found!"
    exit 1
fi

export CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Add Chrome debugging flags
export CHROME_FLAGS="--headless=new --no-sandbox --disable-dev-shm-usage --window-size=1920,1080 --disable-gpu --remote-debugging-port=9222"

# Start Xvfb for headless display (if available)
echo "🖥️ Starting virtual display..."
if command -v Xvfb >/dev/null 2>&1; then
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    # Wait a moment for Xvfb to start
    sleep 2
    echo "✅ Xvfb started"
else
    echo "⚠️ Xvfb not available, continuing without virtual display"
fi

# Verify Chrome is available
echo "🔍 Verifying Chrome installation..."
if command -v google-chrome >/dev/null 2>&1; then
    echo "✅ Chrome found: $(google-chrome --version)"
    echo "Chrome path: $CHROME_BIN"
else
    echo "❌ Chrome not found!"
    exit 1
fi

# Test Chrome before starting app
echo "🧪 Testing Chrome functionality..."
if google-chrome --version && google-chrome --headless --no-sandbox --disable-gpu --dump-dom https://www.google.com > /tmp/test.html; then
    echo "✅ Chrome test successful"
    echo "📄 Test HTML size: $(wc -c < /tmp/test.html) bytes"
else
    echo "❌ Chrome test failed"
    exit 1
fi

# Run the web application with debug mode
echo "🎯 Starting web application with debug mode..."
cd /app
SCRAPER_DEBUG=true python web/app.py