@echo off
echo 🚀 Starting Orizon Google Maps Scraper Web Interface...
echo.
echo ⚙️  Setting up environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Fix Python 3.13 distutils issue first
echo 🔧 Fixing Python 3.13 compatibility issues...
pip install setuptools wheel distlib

REM Install basic dependencies
echo 📦 Installing basic dependencies...
pip install flask flask-cors selenium beautifulsoup4 requests

echo.
echo 📦 Installing Chrome WebDriver...
pip install undetected-chromedriver

echo.
echo 📦 Installing pandas and Excel support...
pip install pandas openpyxl

echo.
echo 🌟 Starting web server...
echo.
echo 📍 Web Interface will be available at: http://localhost:5000
echo 🎨 Orizon branding colors: #272860 (primary), #f8c800 (secondary)
echo.
echo ✨ Using the exact same scraper logic as your desktop version!
echo ⚠️  Note: Make sure Google Chrome is installed for scraping to work
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause