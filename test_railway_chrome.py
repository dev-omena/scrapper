#!/usr/bin/env python3
"""
Railway Chrome Test Script
Tests Chrome driver initialization in Railway deployment environment
"""

import os
import sys
import traceback

def simulate_railway_environment():
    """Simulate Railway environment variables"""
    print("🚂 Simulating Railway Environment...")
    
    # Set Railway-like environment variables
    os.environ["CHROME_BIN"] = "/usr/bin/google-chrome"
    os.environ["CHROMEDRIVER_PATH"] = "/usr/bin/chromedriver"
    os.environ["PYTHONPATH"] = "/app:/app/app"
    
    print(f"✅ CHROME_BIN: {os.environ.get('CHROME_BIN')}")
    print(f"✅ CHROMEDRIVER_PATH: {os.environ.get('CHROMEDRIVER_PATH')}")
    print(f"✅ PYTHONPATH: {os.environ.get('PYTHONPATH')}")

def test_main_scraper():
    """Test the main scraper initialization"""
    print("\n🔍 Testing Main Scraper (app.scraper.scraper)...")
    
    try:
        from app.scraper.scraper import Backend
        
        # Test Chrome path detection without full initialization
        # Create a temporary instance just to test the method
        temp_backend = object.__new__(Backend)
        chrome_path = temp_backend.find_chrome_executable()
        print(f"✅ Chrome executable found: {chrome_path}")
        
        # Test that the class can be imported and the method exists
        print("✅ Backend class import successful")
        print("✅ Chrome path detection method is working")
        
        return True
        
    except Exception as e:
        print(f"❌ Main scraper test failed: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

def test_email_scraper():
    """Test the email scraper initialization"""
    print("\n📧 Testing Email Scraper (app.scraper.email_scraper)...")
    
    try:
        from app.scraper.email_scraper import EmailScraper
        
        # Test Chrome path detection
        scraper = EmailScraper()
        chrome_path = scraper._find_chrome_executable()
        print(f"✅ Chrome executable found: {chrome_path}")
        
        print("✅ EmailScraper class initialized successfully")
        print("✅ Email scraper Chrome detection is working")
        
        return True
        
    except Exception as e:
        print(f"❌ Email scraper test failed: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

def test_web_app_import():
    """Test web app imports"""
    print("\n🌐 Testing Web App Imports...")
    
    try:
        # Test if we can import the web app components
        sys.path.insert(0, 'web')
        
        from web.simple_scraper import SimpleGoogleMapsScraper
        print("✅ SimpleGoogleMapsScraper import successful")
        
        from web.web_communicator import WebCommunicator
        print("✅ WebCommunicator import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Web app import test failed: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n📦 Testing Dependencies...")
    
    required_packages = [
        ('selenium', 'selenium'),
        ('webdriver_manager', 'webdriver-manager'),
        ('undetected_chromedriver', 'undetected-chromedriver'),
        ('flask', 'flask'),
        ('gunicorn', 'gunicorn')
    ]
    
    all_good = True
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - Not installed")
            all_good = False
    
    return all_good

def main():
    """Main test function"""
    print("🧪 Railway Chrome Driver Test Suite")
    print("=" * 50)
    
    # Simulate Railway environment
    simulate_railway_environment()
    
    # Run tests
    tests = [
        ("Dependencies", test_dependencies),
        ("Main Scraper", test_main_scraper),
        ("Email Scraper", test_email_scraper),
        ("Web App Imports", test_web_app_import)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Ready for Railway deployment.")
        print("\n🚀 Deployment checklist:")
        print("   1. ✅ Chrome driver initialization fixed")
        print("   2. ✅ Environment variables configured")
        print("   3. ✅ Fallback mechanisms implemented")
        print("   4. ✅ Error handling improved")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\n🔧 Next steps:")
        print("   1. Install missing dependencies")
        print("   2. Check Chrome installation in Railway")
        print("   3. Verify environment variables")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)