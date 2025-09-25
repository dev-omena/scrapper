#!/usr/bin/env python3
"""
Remote Chrome Setup for Railway
This script helps you start Chrome locally with remote debugging enabled
so Railway can connect to your local Chrome browser.
"""

import subprocess
import sys
import os
import platform
import time
import requests
import json

def find_chrome_executable():
    """Find Chrome executable on different operating systems"""
    system = platform.system().lower()
    
    if system == "windows":
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
    elif system == "darwin":  # macOS
        possible_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium"
        ]
    else:  # Linux
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser"
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def start_remote_chrome(port=9222):
    """Start Chrome with remote debugging enabled"""
    chrome_path = find_chrome_executable()
    
    if not chrome_path:
        print("❌ Chrome not found! Please install Google Chrome.")
        return False
    
    print(f"🔍 Found Chrome: {chrome_path}")
    
    # Chrome flags for remote debugging
    chrome_args = [
        chrome_path,
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",  # Allow connections from Railway
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--disable-extensions",
        "--no-first-run",
        "--no-default-browser-check",
        "--user-data-dir=" + os.path.expanduser("~/chrome-remote-profile")
    ]
    
    print(f"🚀 Starting Chrome with remote debugging on port {port}...")
    print("🌐 Chrome will be accessible for Railway connections")
    
    try:
        # Start Chrome process
        if platform.system().lower() == "windows":
            # On Windows, use CREATE_NEW_CONSOLE to run in background
            process = subprocess.Popen(chrome_args, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # On Unix systems, redirect output
            process = subprocess.Popen(chrome_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait a moment for Chrome to start
        time.sleep(3)
        
        # Test if Chrome is accessible
        try:
            response = requests.get(f"http://localhost:{port}/json/version", timeout=5)
            if response.status_code == 200:
                version_info = response.json()
                print(f"✅ Chrome started successfully!")
                print(f"📋 Chrome Version: {version_info.get('Browser', 'Unknown')}")
                print(f"🔗 WebSocket URL: {version_info.get('webSocketDebuggerUrl', 'Not available')}")
                return True
            else:
                print(f"❌ Chrome not responding on port {port}")
                return False
        except requests.RequestException as e:
            print(f"❌ Failed to connect to Chrome: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start Chrome: {e}")
        return False

def get_public_url(port=9222):
    """Get instructions for exposing Chrome to Railway"""
    print(f"\n🌐 EXPOSING CHROME TO RAILWAY:")
    print(f"=" * 50)
    print(f"Your Chrome is running on localhost:{port}")
    print(f"To allow Railway to connect, you need to expose this port to the internet.")
    print(f"")
    print(f"📋 OPTION 1 - Using ngrok (Recommended):")
    print(f"1. Install ngrok: https://ngrok.com/download")
    print(f"2. Run: ngrok http {port}")
    print(f"3. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)")
    print(f"4. Set Railway environment variable: REMOTE_CHROME_URL=https://abc123.ngrok.io")
    print(f"")
    print(f"📋 OPTION 2 - Using localtunnel:")
    print(f"1. Install: npm install -g localtunnel")
    print(f"2. Run: lt --port {port}")
    print(f"3. Copy the URL and set REMOTE_CHROME_URL in Railway")
    print(f"")
    print(f"📋 OPTION 3 - Port forwarding:")
    print(f"1. Configure your router to forward port {port}")
    print(f"2. Use your public IP: http://YOUR_PUBLIC_IP:{port}")
    print(f"3. Set REMOTE_CHROME_URL=http://YOUR_PUBLIC_IP:{port}")
    print(f"")
    print(f"⚠️  SECURITY NOTE: Only use this for testing. Don't expose Chrome permanently!")

def main():
    """Main function"""
    print("🚀 Remote Chrome Setup for Railway")
    print("=" * 40)
    
    port = 9222
    
    # Check if Chrome is already running
    try:
        response = requests.get(f"http://localhost:{port}/json/version", timeout=2)
        if response.status_code == 200:
            print(f"✅ Chrome already running on port {port}")
            version_info = response.json()
            print(f"📋 Chrome Version: {version_info.get('Browser', 'Unknown')}")
        else:
            # Start Chrome
            if not start_remote_chrome(port):
                sys.exit(1)
    except requests.RequestException:
        # Chrome not running, start it
        if not start_remote_chrome(port):
            sys.exit(1)
    
    # Show instructions for exposing to Railway
    get_public_url(port)
    
    print(f"\n✅ Setup complete!")
    print(f"🔄 Keep this Chrome instance running while using Railway scraper")
    print(f"🛑 Press Ctrl+C to stop")
    
    try:
        # Keep the script running
        while True:
            time.sleep(10)
            # Check if Chrome is still running
            try:
                requests.get(f"http://localhost:{port}/json/version", timeout=2)
            except requests.RequestException:
                print("❌ Chrome connection lost!")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping remote Chrome setup...")
        print("✅ You can now close Chrome manually")

if __name__ == "__main__":
    main()
