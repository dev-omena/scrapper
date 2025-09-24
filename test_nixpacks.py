#!/usr/bin/env python3
"""
Nixpacks Configuration Test
Tests the Nixpacks setup for Railway deployment.
"""

import os
import subprocess
import sys

def test_nixpacks_packages():
    """Test that Nixpacks packages are available"""
    print("🔧 Testing Nixpacks Package Installation")
    print("=" * 50)
    
    # Test Python
    print(f"✅ Python: {sys.version}")
    
    # Test Chromium
    try:
        result = subprocess.run(['chromium', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Chromium: {result.stdout.strip()}")
        else:
            print(f"❌ Chromium not working: {result.stderr}")
    except FileNotFoundError:
        print("❌ Chromium not found")
    except Exception as e:
        print(f"❌ Chromium test failed: {e}")
    
    # Test Xvfb
    try:
        result = subprocess.run(['Xvfb', '-help'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 or "Xvfb" in result.stderr:
            print("✅ Xvfb available")
        else:
            print("❌ Xvfb not working")
    except FileNotFoundError:
        print("❌ Xvfb not found")
    except Exception as e:
        print(f"❌ Xvfb test failed: {e}")
    
    print()

def test_chrome_setup():
    """Test Chrome setup after build script"""
    print("🌐 Testing Chrome Setup")
    print("=" * 50)
    
    # Test google-chrome command
    try:
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ google-chrome: {result.stdout.strip()}")
        else:
            print(f"❌ google-chrome not working: {result.stderr}")
    except FileNotFoundError:
        print("❌ google-chrome command not found")
    except Exception as e:
        print(f"❌ google-chrome test failed: {e}")
    
    # Check symbolic links
    chrome_paths = ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable']
    for path in chrome_paths:
        if os.path.exists(path):
            if os.path.islink(path):
                target = os.readlink(path)
                print(f"✅ {path} -> {target}")
            else:
                print(f"✅ {path} (regular file)")
        else:
            print(f"❌ {path} not found")
    
    print()

def test_environment():
    """Test environment variables"""
    print("🔧 Testing Environment Variables")
    print("=" * 50)
    
    env_vars = ['CHROME_BIN', 'CHROMEDRIVER_PATH', 'DISPLAY', 'PYTHONPATH']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    print()

def main():
    """Run all tests"""
    print("🧪 Nixpacks Configuration Test")
    print("=" * 50)
    
    test_nixpacks_packages()
    test_chrome_setup()
    test_environment()
    
    print("🎯 Nixpacks test completed!")

if __name__ == "__main__":
    main()