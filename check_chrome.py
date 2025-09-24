#!/usr/bin/env python3
"""
Chrome Installation Checker for Google Maps Scraper
This script helps diagnose Chrome and ChromeDriver installation issues.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_status(item, status, details=""):
    """Print status with colored output"""
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {item}")
    if details:
        print(f"   └─ {details}")

def check_chrome_installation():
    """Check if Chrome browser is installed"""
    print_header("CHROME BROWSER INSTALLATION CHECK")
    
    system = platform.system().lower()
    chrome_found = False
    chrome_path = None
    
    # Check environment variable
    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin and os.path.exists(chrome_bin):
        print_status("Chrome via CHROME_BIN environment variable", True, chrome_bin)
        chrome_found = True
        chrome_path = chrome_bin
    else:
        print_status("Chrome via CHROME_BIN environment variable", False, "Not set or invalid")
    
    # Check common installation paths
    if system == "windows":
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        which_commands = ['chrome', 'google-chrome']
    else:
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable", 
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/opt/google/chrome/chrome",
            "/snap/bin/chromium"
        ]
        which_commands = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']
    
    for path in possible_paths:
        expanded_path = os.path.expandvars(os.path.expanduser(path))
        if os.path.exists(expanded_path):
            print_status(f"Chrome at {path}", True, expanded_path)
            if not chrome_found:
                chrome_found = True
                chrome_path = expanded_path
        else:
            print_status(f"Chrome at {path}", False)
    
    # Check using which/where command
    which_cmd = 'where' if system == "windows" else 'which'
    for cmd in which_commands:
        try:
            result = subprocess.run([which_cmd, cmd], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                if os.path.exists(path):
                    print_status(f"Chrome via '{which_cmd} {cmd}'", True, path)
                    if not chrome_found:
                        chrome_found = True
                        chrome_path = path
                else:
                    print_status(f"Chrome via '{which_cmd} {cmd}'", False, "Path not found")
            else:
                print_status(f"Chrome via '{which_cmd} {cmd}'", False, "Command not found")
        except Exception as e:
            print_status(f"Chrome via '{which_cmd} {cmd}'", False, f"Error: {e}")
    
    return chrome_found, chrome_path

def check_chromedriver():
    """Check ChromeDriver installation"""
    print_header("CHROMEDRIVER INSTALLATION CHECK")
    
    system = platform.system().lower()
    chromedriver_found = False
    chromedriver_path = None
    
    # Check environment variable
    chromedriver_env = os.environ.get("CHROMEDRIVER_PATH")
    if chromedriver_env and os.path.exists(chromedriver_env):
        print_status("ChromeDriver via CHROMEDRIVER_PATH", True, chromedriver_env)
        chromedriver_found = True
        chromedriver_path = chromedriver_env
    else:
        print_status("ChromeDriver via CHROMEDRIVER_PATH", False, "Not set or invalid")
    
    # Check common paths
    if system == "windows":
        possible_paths = [
            r"C:\chromedriver\chromedriver.exe",
            r"C:\Program Files\chromedriver\chromedriver.exe",
            r"C:\tools\chromedriver\chromedriver.exe"
        ]
    else:
        possible_paths = [
            "/usr/local/bin/chromedriver",
            "/usr/bin/chromedriver",
            "/opt/chromedriver/chromedriver"
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print_status(f"ChromeDriver at {path}", True)
            if not chromedriver_found:
                chromedriver_found = True
                chromedriver_path = path
        else:
            print_status(f"ChromeDriver at {path}", False)
    
    # Check webdriver-manager cache
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        wdm_path = ChromeDriverManager().install()
        if os.path.exists(wdm_path):
            print_status("ChromeDriver via webdriver-manager", True, wdm_path)
            if not chromedriver_found:
                chromedriver_found = True
                chromedriver_path = wdm_path
        else:
            print_status("ChromeDriver via webdriver-manager", False)
    except Exception as e:
        print_status("ChromeDriver via webdriver-manager", False, f"Error: {e}")
    
    return chromedriver_found, chromedriver_path

def check_python_dependencies():
    """Check required Python packages"""
    print_header("PYTHON DEPENDENCIES CHECK")
    
    required_packages = [
        'selenium',
        'webdriver-manager',
        'undetected-chromedriver'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_status(f"Package: {package}", True)
        except ImportError:
            print_status(f"Package: {package}", False, "Not installed")
            all_installed = False
    
    return all_installed

def provide_installation_instructions():
    """Provide installation instructions based on the system"""
    print_header("INSTALLATION INSTRUCTIONS")
    
    system = platform.system().lower()
    
    print("🔧 To fix Chrome installation issues:\n")
    
    if system == "windows":
        print("1. Install Google Chrome:")
        print("   - Download from: https://www.google.com/chrome/")
        print("   - Install to default location")
        print("   - Or set CHROME_BIN environment variable")
        print("\n2. Install Python dependencies:")
        print("   pip install selenium webdriver-manager undetected-chromedriver")
        print("\n3. If running in production, consider using Docker:")
        print("   - Use the provided Dockerfile in web/ directory")
    else:
        print("1. Install Google Chrome:")
        print("   Ubuntu/Debian:")
        print("     wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -")
        print("     echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list")
        print("     sudo apt-get update")
        print("     sudo apt-get install google-chrome-stable")
        print("\n   CentOS/RHEL:")
        print("     sudo yum install google-chrome-stable")
        print("\n2. Install dependencies:")
        print("     sudo apt-get install -y xvfb")
        print("\n3. Set environment variables:")
        print("     export CHROME_BIN=/usr/bin/google-chrome")
        print("     export CHROMEDRIVER_PATH=/usr/bin/chromedriver")
        print("\n4. Install Python dependencies:")
        print("     pip install selenium webdriver-manager undetected-chromedriver")

def test_selenium_initialization():
    """Test if Selenium can initialize Chrome"""
    print_header("SELENIUM INITIALIZATION TEST")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Try webdriver-manager
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get("https://www.google.com")
            driver.quit()
            print_status("Selenium with webdriver-manager", True, "Successfully initialized and tested")
            return True
        except Exception as e:
            print_status("Selenium with webdriver-manager", False, str(e))
        
        # Try without service
        try:
            driver = webdriver.Chrome(options=options)
            driver.get("https://www.google.com")
            driver.quit()
            print_status("Selenium without service", True, "Successfully initialized and tested")
            return True
        except Exception as e:
            print_status("Selenium without service", False, str(e))
        
        return False
        
    except Exception as e:
        print_status("Selenium import", False, str(e))
        return False

def main():
    """Main function to run all checks"""
    print("🔍 Google Maps Scraper - Chrome Installation Checker")
    print("=" * 60)
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    
    # Run all checks
    chrome_ok, chrome_path = check_chrome_installation()
    chromedriver_ok, chromedriver_path = check_chromedriver()
    deps_ok = check_python_dependencies()
    
    # Test Selenium if basic requirements are met
    if chrome_ok and deps_ok:
        selenium_ok = test_selenium_initialization()
    else:
        selenium_ok = False
    
    # Summary
    print_header("SUMMARY")
    print_status("Chrome Browser", chrome_ok, chrome_path or "Not found")
    print_status("ChromeDriver", chromedriver_ok, chromedriver_path or "Will be auto-installed")
    print_status("Python Dependencies", deps_ok)
    print_status("Selenium Test", selenium_ok)
    
    if chrome_ok and deps_ok and selenium_ok:
        print("\n🎉 All checks passed! Your system should work with the Google Maps Scraper.")
    else:
        print("\n⚠️  Some issues found. Please follow the installation instructions below.")
        provide_installation_instructions()

if __name__ == "__main__":
    main()