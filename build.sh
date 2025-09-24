#!/bin/bash
set -e

echo "🔧 Installing Google Chrome for Railway deployment..."

# Update package lists
apt-get update

# Install required dependencies
apt-get install -y wget gnupg2 ca-certificates software-properties-common

# Add Google Chrome repository
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list

# Update package lists again
apt-get update

# Install Google Chrome
apt-get install -y google-chrome-stable

# Install additional dependencies for headless Chrome
apt-get install -y xvfb

# Verify Chrome installation
echo "✅ Chrome installation verification:"
google-chrome --version
which google-chrome

# Create symbolic links if needed
if [ ! -f /usr/bin/google-chrome ]; then
    ln -s /usr/bin/google-chrome-stable /usr/bin/google-chrome
fi

# Set up Xvfb for headless display
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

echo "🎉 Chrome installation completed successfully!"
