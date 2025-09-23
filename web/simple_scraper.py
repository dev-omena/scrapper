"""
Simple Google Maps Scraper for Web Interface
Uses Selenium with undetected Chrome driver
"""

import time
import json
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

class SimpleGoogleMapsScraper:
    def __init__(self, headless=True, lang_code='en'):
        self.headless = headless
        self.lang_code = lang_code
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'--lang={self.lang_code}')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"Error setting up driver: {e}")
            return False
    
    def scrape(self, search_query, total_results=10):
        """Scrape Google Maps for business data"""
        if not self.setup_driver():
            return []
        
        try:
            # Navigate to Google Maps
            maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            self.driver.get(maps_url)
            
            # Wait for results to load
            time.sleep(3)
            
            results = []
            processed_count = 0
            
            # Scroll and collect results
            while processed_count < total_results:
                # Find business listings
                business_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-result-index]')
                
                if not business_elements:
                    break
                
                for element in business_elements:
                    if processed_count >= total_results:
                        break
                    
                    try:
                        # Click on the business to get details
                        element.click()
                        time.sleep(2)
                        
                        # Extract business data
                        business_data = self.extract_business_data()
                        if business_data:
                            results.append(business_data)
                            processed_count += 1
                            
                    except Exception as e:
                        print(f"Error processing business: {e}")
                        continue
                
                # Scroll down for more results
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Break if no new results
                new_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-result-index]')
                if len(new_elements) <= len(business_elements):
                    break
            
            return results
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return []
    
    def extract_business_data(self):
        """Extract data from business detail panel"""
        try:
            data = {}
            
            # Business name
            try:
                name_element = self.driver.find_element(By.CSS_SELECTOR, 'h1[data-value="title"]')
                data['name'] = name_element.text.strip()
            except:
                data['name'] = ''
            
            # Phone number
            data['phone'] = self.extract_phone()
            
            # Website
            try:
                website_element = self.driver.find_element(By.CSS_SELECTOR, 'a[data-value="website"]')
                data['website'] = website_element.get_attribute('href')
            except:
                data['website'] = ''
            
            # Address
            try:
                address_element = self.driver.find_element(By.CSS_SELECTOR, 'button[data-value="directions"]')
                data['address'] = address_element.get_attribute('aria-label', '').replace('Address: ', '')
            except:
                data['address'] = ''
            
            # Rating
            try:
                rating_element = self.driver.find_element(By.CSS_SELECTOR, 'span.MW4etd')
                data['rating'] = rating_element.text.strip()
            except:
                data['rating'] = ''
            
            # Reviews count
            try:
                reviews_element = self.driver.find_element(By.CSS_SELECTOR, 'span.UY7F9')
                data['reviews_count'] = reviews_element.text.strip()
            except:
                data['reviews_count'] = ''
            
            # Business status and hours
            data['business_status'] = 'Unknown'
            data['hours'] = ''
            
            # Email (basic extraction)
            data['email'] = self.extract_email()
            
            # Coordinates (if available)
            data['latitude'] = ''
            data['longitude'] = ''
            
            return data
            
        except Exception as e:
            print(f"Error extracting business data: {e}")
            return None
    
    def extract_phone(self):
        """Extract phone number with improved selectors"""
        phone_selectors = [
            'button[data-value="phone"]',
            'span[data-value="phone"]',
            'a[href^="tel:"]',
            'button[aria-label*="phone"]',
            'span:contains("+")',
        ]
        
        for selector in phone_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and self.is_valid_phone(text):
                        return text
                    
                    # Check href attribute for tel: links
                    href = element.get_attribute('href')
                    if href and href.startswith('tel:'):
                        phone = href.replace('tel:', '').strip()
                        if self.is_valid_phone(phone):
                            return phone
            except:
                continue
        
        return ''
    
    def extract_email(self):
        """Extract email address"""
        try:
            # Look for email patterns in page source
            page_source = self.driver.page_source
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, page_source)
            
            # Filter out common non-business emails
            excluded_domains = ['google.com', 'gmail.com', 'maps.google.com']
            for email in emails:
                domain = email.split('@')[1].lower()
                if domain not in excluded_domains:
                    return email
                    
        except:
            pass
        
        return ''
    
    def is_valid_phone(self, text):
        """Check if text looks like a phone number"""
        # Remove common non-digit characters
        cleaned = re.sub(r'[^\d+]', '', text)
        
        # Check if it has reasonable length and starts with + or digit
        if len(cleaned) >= 8 and len(cleaned) <= 15:
            if cleaned.startswith('+') or cleaned.isdigit():
                return True
        
        return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

def save_to_csv(data, filename):
    """Save data to CSV file"""
    if not data:
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def save_to_json(data, filename):
    """Save data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, ensure_ascii=False)