#!/bin/bash
set -e

echo "🔧 Setting up Chrome for Railway deployment..."

# Ensure required tools are available
apt-get update
apt-get install -y wget unzip curl

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
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR_VERSION}")

echo "Chrome version: $CHROME_VERSION"
echo "Chrome major version: $CHROME_MAJOR_VERSION"
echo "ChromeDriver version: $CHROMEDRIVER_VERSION"

# Download and install ChromeDriver
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /tmp/
chmod +x /tmp/chromedriver
mv /tmp/chromedriver /usr/bin/chromedriver

# Verify ChromeDriver installation
if command -v chromedriver >/dev/null 2>&1; then
    echo "✅ ChromeDriver installed: $(chromedriver --version)"
else
    echo "❌ ChromeDriver installation failed"
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
