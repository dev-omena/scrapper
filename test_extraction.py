#!/usr/bin/env python3
"""
Test script to verify enhanced data extraction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from scraper.parser import Parser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

def test_extraction():
    """Test the enhanced extraction capabilities"""
    
    print("Testing enhanced Google Maps scraper...")
    
    # Set up Chrome driver with options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Initialize driver
        driver = uc.Chrome(options=chrome_options)
        
        # Test with a sample Google Maps URL
        test_url = "https://www.google.com/maps/place/Cairo+Hotel/@30.0444,31.2357,17z/data=!3m1!4b1!4m6!3m5!1s0x0:0x0!8m2!3d30.0444!4d31.2357!16s%2Fg%2F1234567"
        
        print(f"Testing with URL: {test_url}")
        
        # Initialize parser
        parser = Parser(driver)
        
        # Navigate to the URL
        driver.get(test_url)
        
        # Wait a bit for the page to load
        import time
        time.sleep(5)
        
        # Test the extraction
        parser.parse()
        
        # Print results
        if parser.finalData:
            print("\n=== EXTRACTION RESULTS ===")
            for i, data in enumerate(parser.finalData):
                print(f"\nBusiness {i+1}:")
                for key, value in data.items():
                    status = "✓" if value else "✗"
                    print(f"  {status} {key}: {value}")
        else:
            print("No data extracted")
            
    except Exception as e:
        print(f"Error during testing: {e}")
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_extraction()