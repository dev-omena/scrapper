#!/usr/bin/env python3
"""
Chrome wrapper for Railway deployment
Ensures Chrome starts properly in containerized environment
"""

import os
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def create_chrome_driver():
    """Create a Chrome WebDriver instance optimized for Railway"""
    
    print("🔧 Creating Chrome WebDriver for Railway...")
    
    # Chrome options optimized for containers
    chrome_options = Options()
    
    # Essential headless flags
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # Memory and performance optimizations
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--disable-javascript')  # We'll enable this if needed
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    
    # Window and display settings
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    
    # User agent
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
    
    # Container-specific optimizations
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-default-browser-check')
    
    # Remote debugging
    chrome_options.add_argument('--remote-debugging-port=9222')
    
    # Set binary locations
    chrome_binary = '/usr/bin/google-chrome'
    chromedriver_path = '/usr/bin/chromedriver'
    
    if os.path.exists(chrome_binary):
        chrome_options.binary_location = chrome_binary
        print(f"✅ Chrome binary: {chrome_binary}")
    else:
        print(f"❌ Chrome binary not found: {chrome_binary}")
        return None
    
    if os.path.exists(chromedriver_path):
        service = Service(chromedriver_path)
        print(f"✅ ChromeDriver: {chromedriver_path}")
    else:
        print(f"❌ ChromeDriver not found: {chromedriver_path}")
        return None
    
    try:
        # Create the WebDriver
        print("🚀 Starting Chrome WebDriver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome WebDriver created successfully!")
        return driver
        
    except Exception as e:
        print(f"❌ Failed to create Chrome WebDriver: {e}")
        return None

def test_chrome_driver():
    """Test Chrome WebDriver functionality"""
    driver = create_chrome_driver()
    
    if driver:
        try:
            print("🧪 Testing Chrome WebDriver...")
            driver.get("https://www.google.com")
            title = driver.title
            print(f"✅ Chrome test successful! Page title: {title}")
            driver.quit()
            return True
        except Exception as e:
            print(f"❌ Chrome test failed: {e}")
            try:
                driver.quit()
            except:
                pass
            return False
    else:
        return False

if __name__ == '__main__':
    # Test Chrome setup
    success = test_chrome_driver()
    sys.exit(0 if success else 1)
