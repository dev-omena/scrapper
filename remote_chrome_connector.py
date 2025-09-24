"""
Remote Chrome Connector
Allows Railway deployment to connect to user's local Chrome browser
"""

import os
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class RemoteChromeConnector:
    def __init__(self):
        self.remote_chrome_url = None
        self.local_chrome_port = 9222
        
    def setup_local_chrome_for_remote_access(self):
        """
        Instructions for user to setup their local Chrome for remote access
        """
        instructions = """
        🔧 SETUP YOUR LOCAL CHROME FOR REMOTE ACCESS:
        
        1. Close all Chrome windows completely
        
        2. Start Chrome with remote debugging enabled:
        
        Windows:
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\\temp\\chrome_remote" --disable-web-security --disable-features=VizDisplayCompositor
        
        Mac:
        /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_remote" --disable-web-security --disable-features=VizDisplayCompositor
        
        Linux:
        google-chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_remote" --disable-web-security --disable-features=VizDisplayCompositor
        
        3. Make your local Chrome accessible from internet:
        
        Option A - Using ngrok (Recommended):
        - Download ngrok from https://ngrok.com/
        - Run: ngrok http 9222
        - Copy the https URL (e.g., https://abc123.ngrok.io)
        
        Option B - Using localtunnel:
        - Install: npm install -g localtunnel
        - Run: lt --port 9222
        - Copy the URL
        
        4. Set the REMOTE_CHROME_URL environment variable in Railway:
        REMOTE_CHROME_URL=https://your-ngrok-url.ngrok.io
        
        5. Your local Chrome will now be used by Railway! 🎉
        """
        
        return instructions
    
    def connect_to_remote_chrome(self, remote_url: str = None):
        """
        Connect to remote Chrome instance
        
        Args:
            remote_url: URL of remote Chrome (e.g., https://abc123.ngrok.io)
        """
        
        if not remote_url:
            remote_url = os.getenv('REMOTE_CHROME_URL')
            
        if not remote_url:
            raise ValueError("No remote Chrome URL provided. Set REMOTE_CHROME_URL environment variable.")
        
        self.remote_chrome_url = remote_url.rstrip('/')
        
        # Test connection
        try:
            response = requests.get(f"{self.remote_chrome_url}/json/version", timeout=10)
            if response.status_code == 200:
                version_info = response.json()
                print(f"✅ Connected to remote Chrome: {version_info.get('Browser', 'Unknown')}")
                return True
            else:
                print(f"❌ Failed to connect to remote Chrome: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Failed to connect to remote Chrome: {e}")
            return False
    
    def create_remote_driver(self):
        """
        Create a Selenium WebDriver connected to remote Chrome
        """
        
        if not self.remote_chrome_url:
            raise ValueError("Not connected to remote Chrome. Call connect_to_remote_chrome() first.")
        
        # Get available tabs/sessions
        try:
            response = requests.get(f"{self.remote_chrome_url}/json")
            tabs = response.json()
            
            if not tabs:
                # Create a new tab
                requests.post(f"{self.remote_chrome_url}/json/new")
                response = requests.get(f"{self.remote_chrome_url}/json")
                tabs = response.json()
            
            # Use the first available tab
            tab = tabs[0]
            websocket_url = tab['webSocketDebuggerUrl']
            
            # Configure Chrome options for remote connection
            options = Options()
            options.add_experimental_option("debuggerAddress", self.remote_chrome_url.replace('https://', '').replace('http://', ''))
            
            # Create driver
            driver = webdriver.Chrome(options=options)
            
            print("✅ Successfully created remote Chrome driver")
            return driver
            
        except Exception as e:
            print(f"❌ Failed to create remote driver: {e}")
            raise
    
    def create_fallback_driver(self):
        """
        Fallback to local Chrome if remote connection fails
        """
        print("🔄 Falling back to local Chrome...")
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        try:
            driver = webdriver.Chrome(options=options)
            print("✅ Created fallback local Chrome driver")
            return driver
        except Exception as e:
            print(f"❌ Fallback driver creation failed: {e}")
            raise

class RemoteChromeManager:
    """
    Manager class to handle remote Chrome connections with fallback
    """
    
    def __init__(self):
        self.connector = RemoteChromeConnector()
        self.driver = None
        
    def get_driver(self):
        """
        Get Chrome driver - tries remote first, then falls back to local
        """
        
        # Try remote Chrome first
        remote_url = os.getenv('REMOTE_CHROME_URL')
        
        if remote_url:
            print(f"🌐 Attempting to connect to remote Chrome: {remote_url}")
            
            try:
                if self.connector.connect_to_remote_chrome(remote_url):
                    self.driver = self.connector.create_remote_driver()
                    print("✅ Using remote Chrome successfully!")
                    return self.driver
            except Exception as e:
                print(f"⚠️ Remote Chrome failed: {e}")
        
        # Fallback to local Chrome
        print("🔄 Using local Chrome as fallback...")
        self.driver = self.connector.create_fallback_driver()
        return self.driver
    
    def close_driver(self):
        """Close the driver"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Driver closed successfully")
            except:
                pass

# Integration function for existing scraper
def get_remote_chrome_driver():
    """
    Function to integrate with existing scraper code
    Returns a Chrome driver (remote if available, local if not)
    """
    
    manager = RemoteChromeManager()
    return manager.get_driver()

if __name__ == "__main__":
    # Show setup instructions
    connector = RemoteChromeConnector()
    print(connector.setup_local_chrome_for_remote_access())
    
    # Test connection if URL is provided
    remote_url = os.getenv('REMOTE_CHROME_URL')
    if remote_url:
        print(f"\n🧪 Testing connection to: {remote_url}")
        manager = RemoteChromeManager()
        
        try:
            driver = manager.get_driver()
            driver.get("https://www.google.com")
            print(f"✅ Successfully loaded Google! Title: {driver.title}")
            manager.close_driver()
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print("\n💡 Set REMOTE_CHROME_URL environment variable to test connection")