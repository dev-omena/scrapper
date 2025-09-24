#!/usr/bin/env python3
"""
Railway Deployment Test Script
Tests Chrome installation and environment setup for Railway deployment.
"""

import os
import sys
import subprocess
import platform

def test_environment():
    """Test environment variables and setup"""
    print("🔧 Testing Railway Environment Setup")
    print("=" * 50)
    
    # Test environment variables
    env_vars = {
        'CHROME_BIN': '/usr/bin/google-chrome',
        'CHROMEDRIVER_PATH': '/usr/bin/chromedriver',
        'DISPLAY': ':99',
        'PYTHONPATH': '/app:/app/app'
    }
    
    for var, expected in env_vars.items():
        actual = os.environ.get(var)
        status = "✅" if actual else "❌"
        print(f"{status} {var}: {actual or 'Not set'}")
        if expected and actual != expected:
            print(f"   Expected: {expected}")
    
    print()

def test_chrome_installation():
    """Test Chrome installation"""
    print("🌐 Testing Chrome Installation")
    print("=" * 50)
    
    # Test Chrome executable
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser'
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome found at: {path}")
            chrome_found = True
            
            # Test Chrome version
            try:
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"   Version: {result.stdout.strip()}")
                else:
                    print(f"   ❌ Failed to get version: {result.stderr}")
            except Exception as e:
                print(f"   ❌ Version check failed: {e}")
            break
    
    if not chrome_found:
        print("❌ Chrome not found in any expected location")
    
    print()

def test_display():
    """Test display setup"""
    print("🖥️ Testing Display Setup")
    print("=" * 50)
    
    display = os.environ.get('DISPLAY')
    if display:
        print(f"✅ DISPLAY set to: {display}")
        
        # Test if Xvfb is running
        try:
            result = subprocess.run(['pgrep', 'Xvfb'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Xvfb is running")
            else:
                print("❌ Xvfb not running")
        except Exception as e:
            print(f"❌ Failed to check Xvfb: {e}")
    else:
        print("❌ DISPLAY not set")
    
    print()

def test_python_imports():
    """Test Python imports"""
    print("🐍 Testing Python Imports")
    print("=" * 50)
    
    imports = [
        'selenium',
        'webdriver_manager',
        'undetected_chromedriver',
        'bs4',
        'flask',
        'gunicorn'
    ]
    
    for module in imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
    
    print()

def test_scraper_import():
    """Test scraper module import"""
    print("🔍 Testing Scraper Import")
    print("=" * 50)
    
    try:
        # Add app directory to path
        sys.path.insert(0, '/app')
        sys.path.insert(0, '/app/app')
        
        from app.scraper.scraper import Backend
        print("✅ Backend class imported successfully")
        
        # Test Chrome detection without initialization
        backend = Backend.__new__(Backend)  # Create without calling __init__
        chrome_path = backend.find_chrome_executable()
        if chrome_path:
            print(f"✅ Chrome detected at: {chrome_path}")
        else:
            print("❌ Chrome not detected by scraper")
            
    except Exception as e:
        print(f"❌ Scraper import failed: {e}")
    
    print()

def main():
    """Run all tests"""
    print("🚀 Railway Deployment Test Suite")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print()
    
    test_environment()
    test_chrome_installation()
    test_display()
    test_python_imports()
    test_scraper_import()
    
    print("🎯 Test completed!")

if __name__ == "__main__":
    main()