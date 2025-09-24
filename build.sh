#!/bin/bash
set -e

echo "🔧 Setting up Chrome for Railway deployment..."

# Ensure required tools are available
apt-get update
apt-get install -y wget unzip curl file

# Install additional dependencies for ChromeDriver
apt-get install -y libc6 libgcc-s1 libstdc++6 libnss3 libatk-bridge2.0-0 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2

# Check if chromium is available (from Nixpacks)
if command -v chromium >/dev/null 2>&1; then
    echo "✅ Chromium found via Nixpacks: $(chromium --version)"
    
    # Create symbolic links for compatibility
    if [ ! -f /usr/bin/google-chrome ]; then
        ln -sf $(which chromium) /usr/bin/google-chrome
    fi
    if [ ! -f /usr/bin/google-chrome-stable ]; then
        ln -sf $(which chromium) /usr/bin/google-chrome-stable
    fi
    
    echo "✅ Chrome symbolic links created"
else
    echo "🔧 Installing Google Chrome stable..."
    
    # Update package lists
    apt-get update
    
    # Install required dependencies
    apt-get install -y wget gnupg2 ca-certificates software-properties-common unzip curl
    
    # Add Google Chrome repository
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list
    
    # Update package lists again
    apt-get update
    
    # Install Google Chrome
    apt-get install -y google-chrome-stable
    
    # Create symbolic links if needed
    if [ ! -f /usr/bin/google-chrome ]; then
        ln -sf /usr/bin/google-chrome-stable /usr/bin/google-chrome
    fi
fi

# Install ChromeDriver
echo "🔧 Installing ChromeDriver..."

# Get Chrome version to match ChromeDriver version
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+')
CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d. -f1)

echo "Chrome version: $CHROME_VERSION"
echo "Chrome major version: $CHROME_MAJOR_VERSION"

# For Chrome 115+, use Chrome for Testing JSON API
if [ "$CHROME_MAJOR_VERSION" -ge 115 ]; then
    echo "🔧 Using Chrome for Testing API for Chrome $CHROME_MAJOR_VERSION..."
    
    # Get the latest ChromeDriver version for this Chrome milestone
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json" | \
        grep -o "\"$CHROME_MAJOR_VERSION\":{[^}]*\"version\":\"[^\"]*\"" | \
        grep -o "\"version\":\"[^\"]*\"" | \
        cut -d'"' -f4)
    
    if [ -z "$CHROMEDRIVER_VERSION" ]; then
        echo "❌ No ChromeDriver version found for Chrome $CHROME_MAJOR_VERSION"
        echo "🔧 Trying stable channel fallback..."
        CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json" | \
            grep -o '"Stable":{[^}]*"version":"[^"]*"' | \
            cut -d'"' -f8)
    fi
    
    echo "ChromeDriver version: $CHROMEDRIVER_VERSION"
    
    # Download ChromeDriver from Chrome for Testing
    DOWNLOAD_URL="https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"
    echo "Download URL: $DOWNLOAD_URL"
    wget -O /tmp/chromedriver.zip "$DOWNLOAD_URL"
else
    echo "🔧 Using legacy API for Chrome $CHROME_MAJOR_VERSION..."
    
    # For Chrome 114 and older, use the legacy API
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR_VERSION}")
    echo "ChromeDriver version: $CHROMEDRIVER_VERSION"
    
    # Download ChromeDriver from legacy endpoint
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
fi

# Extract and install ChromeDriver
unzip /tmp/chromedriver.zip -d /tmp/

# Handle different zip structures
if [ -f /tmp/chromedriver ]; then
    # Legacy structure: chromedriver directly in zip
    echo "🔧 Using legacy ChromeDriver structure"
    chmod +x /tmp/chromedriver
    mv /tmp/chromedriver /usr/bin/chromedriver
elif [ -f /tmp/chromedriver-linux64/chromedriver ]; then
    # Chrome for Testing structure: chromedriver in subdirectory
    echo "🔧 Using Chrome for Testing ChromeDriver structure"
    chmod +x /tmp/chromedriver-linux64/chromedriver
    mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver
else
    echo "❌ ChromeDriver binary not found in expected locations"
    echo "Contents of /tmp after extraction:"
    ls -la /tmp/
    exit 1
fi

# Verify ChromeDriver binary architecture and executability
echo "🔍 Verifying ChromeDriver binary..."
if file /usr/bin/chromedriver | grep -q "ELF 64-bit"; then
    echo "✅ ChromeDriver binary has correct 64-bit architecture"
else
    echo "❌ ChromeDriver binary architecture check failed:"
    file /usr/bin/chromedriver
    exit 1
fi

# Test if ChromeDriver can be executed
if /usr/bin/chromedriver --version >/dev/null 2>&1; then
    echo "✅ ChromeDriver binary is executable"
else
    echo "❌ ChromeDriver binary cannot be executed"
    echo "Checking dependencies:"
    ldd /usr/bin/chromedriver 2>&1 || echo "ldd check failed"
    exit 1
fi

# Verify ChromeDriver installation
echo "🔍 ChromeDriver verification:"
echo "  File exists: $(test -f /usr/bin/chromedriver && echo 'YES' || echo 'NO')"
echo "  File permissions: $(ls -la /usr/bin/chromedriver 2>/dev/null || echo 'FILE NOT FOUND')"
echo "  File type: $(file /usr/bin/chromedriver 2>/dev/null || echo 'CANNOT DETERMINE')"

if command -v chromedriver >/dev/null 2>&1; then
    echo "✅ ChromeDriver command available"
    if chromedriver --version 2>/dev/null; then
        echo "✅ ChromeDriver version check successful"
    else
        echo "❌ ChromeDriver version check failed"
        echo "Trying to run with explicit path:"
        /usr/bin/chromedriver --version 2>&1 || echo "Direct execution failed"
    fi
else
    echo "❌ ChromeDriver command not found in PATH"
    exit 1
fi

# Verify final Chrome installation
echo "✅ Final Chrome verification:"
if command -v google-chrome >/dev/null 2>&1; then
    google-chrome --version
    echo "Chrome path: $(which google-chrome)"
else
    echo "❌ Chrome not found after installation"
    exit 1
fi

echo "🎉 Chrome and ChromeDriver setup completed successfully!"
