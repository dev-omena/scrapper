"""
Email Scraper Module for finding emails from specific domains
Supports multiple search methods: search engines, direct crawling, and pattern matching
"""

import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from dataclasses import dataclass
from typing import List, Dict, Set, Optional


@dataclass
class EmailResult:
    """Data class for email extraction results"""
    email: str
    source_url: str
    email_type: str  # 'contact', 'info', 'admin', 'sales', 'support', 'ceo', 'hr', etc.
    confidence_score: float  # 0.0 to 1.0
    extraction_method: str  # 'search_engine', 'direct_crawl', 'pattern_match'


class EmailScraper:
    """
    Email scraper for finding emails associated with a specific domain
    """
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Common email patterns for different roles
        self.email_patterns = {
            'ceo': ['ceo', 'chief', 'president', 'founder'],
            'contact': ['contact', 'info', 'hello', 'inquiries'],
            'sales': ['sales', 'business', 'partnerships'],
            'support': ['support', 'help', 'service', 'customer'],
            'hr': ['hr', 'careers', 'jobs', 'recruitment'],
            'admin': ['admin', 'webmaster', 'postmaster'],
            'marketing': ['marketing', 'pr', 'media'],
            'general': ['office', 'main', 'general']
        }
        
        # Email regex pattern
        self.email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Common pages to check for emails
        self.target_pages = [
            '', '/', '/contact', '/contact-us', '/about', '/about-us', 
            '/team', '/staff', '/leadership', '/management', '/careers',
            '/support', '/help', '/info', '/press'
        ]

    def setup_driver(self):
        """Setup Selenium WebDriver"""
        if self.driver is None:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            import os
            chrome_bin = os.environ.get("CHROME_BIN")
            if not chrome_bin or not isinstance(chrome_bin, str):
                raise RuntimeError("CHROME_BIN environment variable is not set or not a string")
            chrome_options.binary_location = chrome_bin

            self.driver = webdriver.Chrome(options=chrome_options)

    def close_driver(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def validate_email(self, email: str, target_domain: str) -> bool:
        """Validate if email belongs to target domain and has valid format"""
        if not email or '@' not in email:
            return False
            
        # Check if email belongs to target domain
        email_domain = email.split('@')[1].lower()
        target_domain = target_domain.lower().replace('www.', '')
        
        return email_domain == target_domain

    def classify_email_type(self, email: str) -> str:
        """Classify email type based on local part"""
        local_part = email.split('@')[0].lower()
        
        for email_type, patterns in self.email_patterns.items():
            for pattern in patterns:
                if pattern in local_part:
                    return email_type
                    
        return 'other'

    def calculate_confidence_score(self, email: str, source_url: str, context: str = "") -> float:
        """Calculate confidence score for found email"""
        score = 0.5  # Base score
        
        local_part = email.split('@')[0].lower()
        
        # Higher score for common business emails
        if any(pattern in local_part for patterns in self.email_patterns.values() for pattern in patterns):
            score += 0.3
            
        # Higher score if found on official pages
        if any(page in source_url.lower() for page in ['/contact', '/about', '/team']):
            score += 0.2
            
        # Lower score for generic emails
        if local_part in ['noreply', 'no-reply', 'donotreply']:
            score -= 0.4
            
        # Context bonus
        if context and any(word in context.lower() for word in ['contact', 'email', 'reach']):
            score += 0.1
            
        return min(1.0, max(0.1, score))

    def search_google_for_emails(self, domain: str, max_results: int = 20) -> List[EmailResult]:
        """Search Google for emails from the domain across multiple sources"""
        results = []
        
        try:
            self.setup_driver()
            
            # Enhanced search queries targeting professional platforms and business directories
            search_queries = [
                # LinkedIn and professional networks
                f'site:linkedin.com "{domain}" email',
                f'site:linkedin.com/company/{domain.replace(".", "-")}',
                f'site:linkedin.com "{domain}" contact',
                
                # Business directories and professional sites
                f'site:crunchbase.com "{domain}" email',
                f'site:bloomberg.com "{domain}" contact',
                f'site:pitchbook.com "{domain}"',
                f'site:apollo.io "{domain}"',
                f'site:zoominfo.com "{domain}"',
                
                # Social media and company profiles
                f'site:twitter.com "{domain}" email',
                f'site:facebook.com "{domain}" contact',
                f'site:instagram.com "{domain}"',
                
                # Domain-specific searches
                f'"{domain}" CEO email contact',
                f'"{domain}" founder email',
                f'"{domain}" contact information',
                f'site:{domain} "@{domain}"',
                f'intext:"@{domain}" contact',
                f'"{domain}" team email',
                f'"{domain}" press contact',
                f'"{domain}" business development',
                
                # Business listing sites
                f'site:yelp.com "{domain}"',
                f'site:yellowpages.com "{domain}"',
                f'site:bbb.org "{domain}"',
                
                # News and press mentions
                f'"{domain}" press release email',
                f'"{domain}" media contact',
                f'news "{domain}" contact'
            ]
            
            for i, query in enumerate(search_queries[:12]):  # Process first 12 queries
                try:
                    print(f"🔍 Searching Google with query {i+1}/{min(12, len(search_queries))}: {query}")
                    self.driver.get(f"https://www.google.com/search?q={query}")
                    time.sleep(random.uniform(3, 6))
                    
                    # Get page source and extract emails directly from search results
                    page_source = self.driver.page_source
                    emails_found = self.email_regex.findall(page_source)
                    
                    for email in emails_found:
                        if self.validate_email(email, domain):
                            email_type = self.classify_email_type(email)
                            confidence = self.calculate_confidence_score(email, f"google_search_{query}", page_source)
                            
                            # Boost confidence based on source
                            if 'linkedin.com' in query:
                                confidence += 0.3  # LinkedIn is very reliable
                            elif any(site in query for site in ['crunchbase.com', 'bloomberg.com', 'apollo.io']):
                                confidence += 0.25  # Business directories are reliable
                            elif 'CEO' in query or 'founder' in query:
                                confidence += 0.2  # Executive searches are valuable
                            
                            result = EmailResult(
                                email=email.lower(),
                                source_url=f"Google Search: {query}",
                                email_type=email_type,
                                confidence_score=min(confidence, 0.95),  # Cap at 0.95
                                extraction_method='search_engine'
                            )
                            results.append(result)
                            print(f"✓ Found email via Google: {email} (confidence: {confidence:.2f})")
                    
                    # Also check search result links for additional context
                    try:
                        links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="http"]')
                        for link in links[:5]:  # Check first 5 results
                            try:
                                url = link.get_attribute('href')
                                if url and any(platform in url for platform in ['linkedin.com', 'crunchbase.com', 'apollo.io', domain]):
                                    if 'google.com' not in url and url.startswith('http'):
                                        print(f"🔗 Checking search result: {url}")
                                        page_results = self.extract_emails_from_url(url, domain)
                                        for result in page_results:
                                            if 'linkedin.com' in url:
                                                result.confidence_score += 0.2
                                                result.source_url = f"LinkedIn: {url}"
                                            elif 'crunchbase.com' in url:
                                                result.confidence_score += 0.15
                                                result.source_url = f"Crunchbase: {url}"
                                        results.extend(page_results)
                                        
                            except Exception as e:
                                print(f"Error checking link: {e}")
                                continue
                    except Exception as e:
                        print(f"Error getting search result links: {e}")
                        
                    time.sleep(random.uniform(2, 5))
                    
                except Exception as e:
                    print(f"Error searching Google with query '{query}': {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in Google search: {e}")
            
        return results

    def search_linkedin_profiles(self, domain: str) -> List[EmailResult]:
        """Search LinkedIn for company profiles and employee emails"""
        results = []
        
        try:
            print("🔍 Searching LinkedIn for company profiles...")
            
            # LinkedIn company search URLs
            company_name = domain.split('.')[0]  # Extract company name from domain
            linkedin_urls = [
                f"https://www.linkedin.com/company/{company_name}",
                f"https://www.linkedin.com/company/{domain.replace('.', '-')}",
                f"https://www.linkedin.com/search/results/companies/?keywords={company_name}",
            ]
            
            for url in linkedin_urls:
                try:
                    print(f"🔗 Checking LinkedIn URL: {url}")
                    page_results = self.extract_emails_from_url(url, domain)
                    for result in page_results:
                        result.confidence_score += 0.25  # LinkedIn boost
                        result.source_url = f"LinkedIn: {url}"
                        result.extraction_method = 'linkedin_search'
                    results.extend(page_results)
                    time.sleep(random.uniform(3, 5))
                    
                except Exception as e:
                    print(f"Error checking LinkedIn URL {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in LinkedIn search: {e}")
            
        return results

    def search_business_directories(self, domain: str) -> List[EmailResult]:
        """Search business directories and databases"""
        results = []
        
        try:
            print("🔍 Searching business directories...")
            
            company_name = domain.split('.')[0]
            directory_urls = [
                # Crunchbase
                f"https://www.crunchbase.com/organization/{company_name}",
                f"https://www.crunchbase.com/search/organizations/field/organizations/short_description/{company_name}",
                
                # Apollo.io (email finder)
                f"https://app.apollo.io/companies?q={domain}",
                
                # ZoomInfo
                f"https://www.zoominfo.com/c/{company_name}",
                
                # Business listings
                f"https://www.yelp.com/biz/{company_name}",
                f"https://www.yellowpages.com/search?search_terms={company_name}",
                
                # Company information sites
                f"https://www.bloomberg.com/search?query={company_name}",
                f"https://pitchbook.com/profiles/company/{company_name}",
            ]
            
            for url in directory_urls:
                try:
                    print(f"🔗 Checking directory: {url}")
                    page_results = self.extract_emails_from_url(url, domain)
                    for result in page_results:
                        result.confidence_score += 0.2  # Directory boost
                        if 'crunchbase.com' in url:
                            result.source_url = f"Crunchbase: {url}"
                        elif 'apollo.io' in url:
                            result.source_url = f"Apollo.io: {url}"
                            result.confidence_score += 0.1  # Extra boost for Apollo
                        elif 'zoominfo.com' in url:
                            result.source_url = f"ZoomInfo: {url}"
                        else:
                            result.source_url = f"Directory: {url}"
                        result.extraction_method = 'business_directory'
                    results.extend(page_results)
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    print(f"Error checking directory {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in business directory search: {e}")
            
        return results

    def search_social_media(self, domain: str) -> List[EmailResult]:
        """Search social media platforms for business contact information"""
        results = []
        
        try:
            print("🔍 Searching social media platforms...")
            
            company_name = domain.split('.')[0]
            social_urls = [
                # Twitter/X
                f"https://twitter.com/{company_name}",
                f"https://twitter.com/search?q={domain}",
                
                # Facebook
                f"https://www.facebook.com/{company_name}",
                f"https://www.facebook.com/search/top?q={company_name}",
                
                # Instagram
                f"https://www.instagram.com/{company_name}",
                
                # GitHub (for tech companies)
                f"https://github.com/{company_name}",
                
                # AngelList
                f"https://angel.co/company/{company_name}",
            ]
            
            for url in social_urls:
                try:
                    print(f"🔗 Checking social media: {url}")
                    page_results = self.extract_emails_from_url(url, domain)
                    for result in page_results:
                        result.confidence_score += 0.15  # Social media boost
                        if 'twitter.com' in url:
                            result.source_url = f"Twitter: {url}"
                        elif 'facebook.com' in url:
                            result.source_url = f"Facebook: {url}"
                        elif 'instagram.com' in url:
                            result.source_url = f"Instagram: {url}"
                        elif 'github.com' in url:
                            result.source_url = f"GitHub: {url}"
                            result.confidence_score += 0.1  # Extra boost for GitHub
                        else:
                            result.source_url = f"Social Media: {url}"
                        result.extraction_method = 'social_media'
                    results.extend(page_results)
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    print(f"Error checking social media {url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in social media search: {e}")
            
        return results

    def search_press_and_news(self, domain: str) -> List[EmailResult]:
        """Search press releases and news articles for contact information"""
        results = []
        
        try:
            print("🔍 Searching press releases and news...")
            
            # Use Google to find press releases and news articles
            company_name = domain.split('.')[0]
            press_queries = [
                f'"{domain}" press release contact',
                f'"{company_name}" press contact email',
                f'"{domain}" media contact',
                f'"{company_name}" news contact information',
                f'site:prnewswire.com "{domain}"',
                f'site:businesswire.com "{domain}"',
                f'site:globenewswire.com "{domain}"',
            ]
            
            for query in press_queries:
                try:
                    print(f"🔍 Press search: {query}")
                    self.driver.get(f"https://www.google.com/search?q={query}")
                    time.sleep(random.uniform(2, 4))
                    
                    # Extract emails from search results
                    page_source = self.driver.page_source
                    emails_found = self.email_regex.findall(page_source)
                    
                    for email in emails_found:
                        if self.validate_email(email, domain):
                            email_type = self.classify_email_type(email)
                            confidence = self.calculate_confidence_score(email, f"press_search_{query}", page_source)
                            confidence += 0.2  # Press contacts are usually real
                            
                            result = EmailResult(
                                email=email.lower(),
                                source_url=f"Press Search: {query}",
                                email_type=email_type,
                                confidence_score=min(confidence, 0.9),
                                extraction_method='press_search'
                            )
                            results.append(result)
                            print(f"✓ Found press contact: {email}")
                    
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    print(f"Error in press search '{query}': {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in press search: {e}")
            
        return results

    def crawl_domain_pages(self, domain: str) -> List[EmailResult]:
        """Crawl domain pages directly for emails"""
        results = []
        base_url = f"https://{domain}" if not domain.startswith('http') else domain
        
        # Enhanced list of pages to check
        pages_to_check = [
            '', '/', '/contact', '/contact-us', '/about', '/about-us', 
            '/team', '/staff', '/leadership', '/management', '/careers',
            '/support', '/help', '/info', '/press', '/media',
            '/contact.html', '/about.html', '/team.html'
        ]
        
        for page in pages_to_check:
            try:
                url = urljoin(base_url, page)
                print(f"Crawling page: {url}")
                page_results = self.extract_emails_from_url(url, domain)
                
                # Boost confidence for emails found on official pages
                for result in page_results:
                    if any(contact_page in page.lower() for contact_page in ['/contact', '/about', '/team']):
                        result.confidence_score += 0.2
                        
                results.extend(page_results)
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"Error crawling {url}: {e}")
                continue
                
        return results

    def extract_emails_from_url(self, url: str, target_domain: str) -> List[EmailResult]:
        """Extract emails from a specific URL"""
        results = []
        
        try:
            print(f"Extracting emails from: {url}")
            
            # Try with requests first (faster)
            try:
                response = self.session.get(url, timeout=15, allow_redirects=True)
                if response.status_code == 200:
                    content = response.text
                    print(f"Successfully fetched {url} with requests (status: {response.status_code})")
                else:
                    print(f"Failed to fetch {url} with requests (status: {response.status_code})")
                    return results
                    
            except Exception as requests_error:
                print(f"Requests failed for {url}: {requests_error}")
                # Fallback to Selenium if requests fails
                try:
                    if not self.driver:
                        self.setup_driver()
                        
                    self.driver.get(url)
                    time.sleep(3)  # Give time for page to load
                    content = self.driver.page_source
                    print(f"Successfully fetched {url} with Selenium")
                except Exception as selenium_error:
                    print(f"Both requests and Selenium failed for {url}: {selenium_error}")
                    return results
            
            # Extract emails using regex
            emails_found = self.email_regex.findall(content)
            print(f"Found {len(emails_found)} potential emails in {url}")
            
            # Create soup for context extraction
            try:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                    
                text_content = soup.get_text()
                
                # Look for specific email patterns in visible text
                visible_emails = self.email_regex.findall(text_content)
                emails_found.extend(visible_emails)
                
            except Exception as soup_error:
                print(f"BeautifulSoup parsing failed for {url}: {soup_error}")
                text_content = content
            
            # Process found emails
            processed_emails = set()  # Avoid duplicates within the same page
            
            for email in emails_found:
                email_clean = email.lower().strip()
                
                if email_clean in processed_emails:
                    continue
                    
                if self.validate_email(email_clean, target_domain):
                    email_type = self.classify_email_type(email_clean)
                    
                    # Enhanced confidence scoring
                    confidence = self.calculate_confidence_score(email_clean, url, text_content)
                    
                    # Extra confidence boosts for real finds
                    if email_clean in text_content.lower():
                        confidence += 0.1  # Found in visible text
                        
                    if any(keyword in text_content.lower() for keyword in ['contact', 'email', 'reach out', 'get in touch']):
                        confidence += 0.1  # Context suggests it's a real contact
                        
                    result = EmailResult(
                        email=email_clean,
                        source_url=url,
                        email_type=email_type,
                        confidence_score=min(confidence, 1.0),  # Cap at 1.0
                        extraction_method='direct_crawl'
                    )
                    results.append(result)
                    processed_emails.add(email_clean)
                    print(f"✓ Valid email found: {email_clean} (confidence: {confidence:.2f})")
        
        except Exception as e:
            print(f"Error extracting emails from {url}: {e}")
        
        return results

    def generate_potential_emails(self, domain: str) -> List[EmailResult]:
        """Generate potential emails based on common patterns"""
        results = []
        
        # Common email prefixes
        prefixes = [
            'info', 'contact', 'hello', 'support', 'sales', 'admin',
            'ceo', 'president', 'founder', 'owner', 'manager',
            'hr', 'careers', 'jobs', 'marketing', 'press'
        ]
        
        for prefix in prefixes:
            email = f"{prefix}@{domain}"
            result = EmailResult(
                email=email,
                source_url=f"https://{domain}",
                email_type=self.classify_email_type(email),
                confidence_score=0.3,  # Lower confidence for generated emails
                extraction_method='pattern_match'
            )
            results.append(result)
            
        return results

    def scrape_emails(self, domain: str, include_patterns: bool = True, max_crawl_pages: int = 10) -> Dict:
        """
        Main method to scrape emails for a domain from multiple sources
        
        Args:
            domain: Target domain (e.g., 'example.com')
            include_patterns: Whether to include pattern-generated emails
            max_crawl_pages: Maximum pages to crawl
            
        Returns:
            Dictionary with results and statistics
        """
        print(f"🚀 Starting comprehensive email scraping for domain: {domain}")
        
        all_results = []
        
        try:
            # Method 1: Direct domain crawling (most reliable for official emails)
            print("� Step 1: Crawling domain pages...")
            crawl_results = self.crawl_domain_pages(domain)
            all_results.extend(crawl_results)
            print(f"   Found {len(crawl_results)} emails from direct crawling")
            
            # Method 2: Enhanced Google searches (LinkedIn, business directories, etc.)
            print("🔍 Step 2: Enhanced Google searches...")
            search_results = self.search_google_for_emails(domain)
            all_results.extend(search_results)
            print(f"   Found {len(search_results)} emails from Google searches")
            
            # Method 3: LinkedIn profiles
            print("💼 Step 3: LinkedIn company profiles...")
            linkedin_results = self.search_linkedin_profiles(domain)
            all_results.extend(linkedin_results)
            print(f"   Found {len(linkedin_results)} emails from LinkedIn")
            
            # Method 4: Business directories
            print("� Step 4: Business directories...")
            directory_results = self.search_business_directories(domain)
            all_results.extend(directory_results)
            print(f"   Found {len(directory_results)} emails from business directories")
            
            # Method 5: Social media platforms
            print("📱 Step 5: Social media platforms...")
            social_results = self.search_social_media(domain)
            all_results.extend(social_results)
            print(f"   Found {len(social_results)} emails from social media")
            
            # Method 6: Press releases and news
            print("📰 Step 6: Press releases and news...")
            press_results = self.search_press_and_news(domain)
            all_results.extend(press_results)
            print(f"   Found {len(press_results)} emails from press/news")
            
            # Count real emails found so far
            real_emails = [r for r in all_results if r.extraction_method != 'pattern_match' and r.confidence_score > 0.4]
            print(f"\n📈 Total real emails found so far: {len(real_emails)}")
            
            # Method 7: Pattern-based generation (only if insufficient real emails and user opted in)
            if include_patterns and len(real_emails) < 3:
                print("� Step 7: Generating potential email patterns...")
                pattern_results = self.generate_potential_emails(domain)
                # Only include a subset of the most likely patterns
                high_priority_patterns = ['info', 'contact', 'hello', 'support', 'admin', 'sales']
                filtered_patterns = [
                    r for r in pattern_results 
                    if any(pattern in r.email.split('@')[0] for pattern in high_priority_patterns)
                ]
                all_results.extend(filtered_patterns[:6])  # Limit to 6 most common patterns
                print(f"   Added {len(filtered_patterns[:6])} pattern-based emails as fallback")
            elif len(real_emails) >= 3:
                print("✅ Sufficient real emails found, skipping pattern generation")
            
            # Enhanced deduplication with prioritization
            unique_emails = {}
            for result in all_results:
                email_key = result.email.lower()
                if email_key not in unique_emails:
                    unique_emails[email_key] = result
                else:
                    # Prioritize based on extraction method and confidence
                    existing = unique_emails[email_key]
                    
                    # Method priority: linkedin > business_directory > direct_crawl > search_engine > social_media > press_search > pattern_match
                    method_priority = {
                        'linkedin_search': 6,
                        'business_directory': 5,
                        'direct_crawl': 4,
                        'search_engine': 3,
                        'social_media': 2,
                        'press_search': 2,
                        'pattern_match': 1
                    }
                    
                    existing_priority = method_priority.get(existing.extraction_method, 0)
                    new_priority = method_priority.get(result.extraction_method, 0)
                    
                    # Keep the better one based on method priority and confidence
                    if (new_priority > existing_priority or 
                        (new_priority == existing_priority and result.confidence_score > existing.confidence_score)):
                        unique_emails[email_key] = result
            
            final_results = list(unique_emails.values())
            
            # Sort by priority and confidence
            def sort_key(result):
                method_priority = {
                    'linkedin_search': 6,
                    'business_directory': 5,
                    'direct_crawl': 4,
                    'search_engine': 3,
                    'social_media': 2,
                    'press_search': 2,
                    'pattern_match': 1
                }
                return (method_priority.get(result.extraction_method, 0), result.confidence_score)
            
            final_results.sort(key=sort_key, reverse=True)
            
            # Enhanced statistics
            stats = {
                'total_found': len(final_results),
                'by_type': {},
                'by_method': {},
                'by_source': {},
                'high_confidence': len([r for r in final_results if r.confidence_score > 0.7]),
                'medium_confidence': len([r for r in final_results if 0.4 <= r.confidence_score <= 0.7]),
                'low_confidence': len([r for r in final_results if r.confidence_score < 0.4]),
                'real_emails': len([r for r in final_results if r.extraction_method != 'pattern_match']),
                'pattern_emails': len([r for r in final_results if r.extraction_method == 'pattern_match']),
                'linkedin_emails': len([r for r in final_results if r.extraction_method == 'linkedin_search']),
                'directory_emails': len([r for r in final_results if r.extraction_method == 'business_directory']),
                'social_emails': len([r for r in final_results if r.extraction_method == 'social_media'])
            }
            
            for result in final_results:
                stats['by_type'][result.email_type] = stats['by_type'].get(result.email_type, 0) + 1
                stats['by_method'][result.extraction_method] = stats['by_method'].get(result.extraction_method, 0) + 1
                
                # Track source platforms
                if 'LinkedIn' in result.source_url:
                    stats['by_source']['LinkedIn'] = stats['by_source'].get('LinkedIn', 0) + 1
                elif 'Crunchbase' in result.source_url:
                    stats['by_source']['Crunchbase'] = stats['by_source'].get('Crunchbase', 0) + 1
                elif 'Apollo' in result.source_url:
                    stats['by_source']['Apollo.io'] = stats['by_source'].get('Apollo.io', 0) + 1
                elif 'Twitter' in result.source_url:
                    stats['by_source']['Twitter'] = stats['by_source'].get('Twitter', 0) + 1
                elif 'Facebook' in result.source_url:
                    stats['by_source']['Facebook'] = stats['by_source'].get('Facebook', 0) + 1
            
            print(f"\n🎯 Email extraction completed:")
            print(f"   📧 Total: {stats['total_found']} emails")
            print(f"   ✅ Real emails: {stats['real_emails']}")
            print(f"   🔤 Pattern emails: {stats['pattern_emails']}")
            print(f"   💼 LinkedIn: {stats['linkedin_emails']}")
            print(f"   📊 Directories: {stats['directory_emails']}")
            print(f"   📱 Social Media: {stats['social_emails']}")
            print(f"   🎖️ High confidence: {stats['high_confidence']}")
            
            return {
                'success': True,
                'domain': domain,
                'results': final_results,
                'statistics': stats,
                'total_found': len(final_results)
            }
            
        except Exception as e:
            print(f"❌ Error in email scraping: {e}")
            return {
                'success': False,
                'domain': domain,
                'error': str(e),
                'results': [],
                'total_found': 0
            }
            
        finally:
            self.close_driver()

    def export_to_dict(self, results: List[EmailResult]) -> List[Dict]:
        """Export results to dictionary format for JSON/Excel export"""
        return [
            {
                'Email': result.email,
                'Email Type': result.email_type.title(),
                'Source URL': result.source_url,
                'Confidence Score': f"{result.confidence_score:.2f}",
                'Extraction Method': result.extraction_method.replace('_', ' ').title(),
                'Domain': result.email.split('@')[1]
            }
            for result in results
        ]


if __name__ == "__main__":
    # Test the email scraper
    scraper = EmailScraper(headless=True)
    
    test_domain = "example.com"
    print(f"Testing email scraper with domain: {test_domain}")
    
    results = scraper.scrape_emails(test_domain, include_patterns=True)
    
    if results['success']:
        print(f"\nFound {results['total_found']} emails:")
        for result in results['results'][:10]:  # Show first 10
            print(f"  {result.email} ({result.email_type}) - Confidence: {result.confidence_score:.2f}")
            
        print(f"\nStatistics:")
        print(f"  High confidence: {results['statistics']['high_confidence']}")
        print(f"  Medium confidence: {results['statistics']['medium_confidence']}")
        print(f"  Low confidence: {results['statistics']['low_confidence']}")
    else:
        print(f"Error: {results.get('error', 'Unknown error')}")