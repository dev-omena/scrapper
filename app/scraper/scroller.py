import time
try:
    from scraper.communicator import Communicator
    from scraper.common import Common
    from scraper.parser import Parser
except ImportError:
    from app.scraper.communicator import Communicator
    from app.scraper.common import Common
    from app.scraper.parser import Parser
from bs4 import BeautifulSoup
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Scroller:

    def __init__(self, driver) -> None:
        self.driver = driver
    
    def __init_parser(self):
        self.parser = Parser(self.driver)


    def start_parsing(self):
        self.__init_parser() # init parser object on fly

        self.parser.main(self.__allResultsLinks)
        

    
    def scroll(self):
        """In case search results are not available"""

        Communicator.show_message(message="[DEBUG] Starting scroll method...")
        
        # Wait for Google Maps to load and search results to appear
        scrollAbleElement = None
        max_attempts = 6
        
        for attempt in range(max_attempts):
            try:
                Communicator.show_message(message=f"[DEBUG] Attempt {attempt + 1}/{max_attempts} - Checking for feed element...")
                
                # Wait a bit for the page to load
                time.sleep(5)
                
                # Try multiple selectors for the scrollable search results area
                scrollAbleElement = self.driver.execute_script(
                    """
                    // Try multiple selectors for Google Maps search results
                    var selectors = [
                        "[role='feed']",                    // Primary selector
                        ".m6QErb",                          // Common Google Maps class
                        "[data-value='Search results']",    // Alternative data attribute
                        ".section-layout-root",             // Layout container
                        ".section-scrollbox",               // Scrollbox container
                        "[jsaction*='scroll']",             // Elements with scroll actions
                        ".section-result",                  // Result section
                        "[role='main'] [role='region']",    // Main region
                        ".section-listbox",                 // Listbox container
                        "[aria-label*='Results']"           // Aria label containing "Results"
                    ];
                    
                    for (var i = 0; i < selectors.length; i++) {
                        var element = document.querySelector(selectors[i]);
                        if (element && element.scrollHeight > element.clientHeight) {
                            console.log("Found scrollable element with selector: " + selectors[i]);
                            return element;
                        }
                    }
                    return null;
                    """
                )
                
                if scrollAbleElement is not None:
                    Communicator.show_message(message="[DEBUG] Scrollable element found! Starting to scroll...")
                    break
                else:
                    Communicator.show_message(message=f"[DEBUG] No scrollable element found on attempt {attempt + 1}")
                    
                    # Comprehensive page analysis
                    page_analysis = self.driver.execute_script(
                        """
                        var analysis = {
                            title: document.title,
                            url: window.location.href,
                            hasResults: false,
                            elements: [],
                            possibleContainers: []
                        };
                        
                        // Check for common Google Maps elements
                        var commonSelectors = [
                            "[role='main']", ".m6QErb", "[data-value='Directions']", 
                            ".section-layout", ".section-result", ".section-listbox",
                            "[role='region']", "[role='feed']", ".section-scrollbox"
                        ];
                        
                        commonSelectors.forEach(function(selector) {
                            var elements = document.querySelectorAll(selector);
                            if (elements.length > 0) {
                                analysis.elements.push(selector + ": " + elements.length);
                            }
                        });
                        
                        // Look for any scrollable divs
                        var allDivs = document.querySelectorAll('div');
                        for (var i = 0; i < Math.min(allDivs.length, 50); i++) {
                            var div = allDivs[i];
                            if (div.scrollHeight > div.clientHeight && div.clientHeight > 100) {
                                var classes = div.className || 'no-class';
                                var id = div.id || 'no-id';
                                analysis.possibleContainers.push('scrollable-div: ' + classes.substring(0, 50) + ' id:' + id);
                            }
                        }
                        
                        // Check if there are any search results indicators
                        var resultIndicators = document.querySelectorAll('[data-result-index], .section-result, [aria-label*="result"]');
                        analysis.hasResults = resultIndicators.length > 0;
                        
                        return analysis;
                        """
                    )
                    
                    if page_analysis:
                        Communicator.show_message(message=f"[DEBUG] Page Analysis:")
                        Communicator.show_message(message=f"[DEBUG] Title: {page_analysis.get('title', 'Unknown')}")
                        Communicator.show_message(message=f"[DEBUG] URL: {page_analysis.get('url', 'Unknown')}")
                        Communicator.show_message(message=f"[DEBUG] Has Results: {page_analysis.get('hasResults', False)}")
                        Communicator.show_message(message=f"[DEBUG] Elements found: {page_analysis.get('elements', [])}")
                        Communicator.show_message(message=f"[DEBUG] Scrollable containers: {page_analysis.get('possibleContainers', [])}")
                    
                    # Try to find ANY scrollable element as a last resort
                    if attempt >= 3:  # After 3 attempts, try more aggressive approach
                        any_scrollable = self.driver.execute_script(
                            """
                            var allElements = document.querySelectorAll('*');
                            for (var i = 0; i < allElements.length; i++) {
                                var el = allElements[i];
                                if (el.scrollHeight > el.clientHeight && el.clientHeight > 200) {
                                    return el;
                                }
                            }
                            return null;
                            """
                        )
                        
                        if any_scrollable:
                            Communicator.show_message(message="[DEBUG] Found ANY scrollable element as fallback")
                            scrollAbleElement = any_scrollable
                            break
                        
            except Exception as e:
                Communicator.show_message(message=f"[DEBUG] Error on attempt {attempt + 1}: {str(e)}")
                
        if scrollAbleElement is None:
            # Final check - maybe Google Maps itself is showing no results
            google_no_results = self.driver.execute_script(
                """
                var noResultsIndicators = [
                    'No results found',
                    'لم يتم العثور على نتائج',
                    'Couldn\\'t find',
                    'Try a different search',
                    'No places found'
                ];
                
                var pageText = document.body.innerText || '';
                for (var i = 0; i < noResultsIndicators.length; i++) {
                    if (pageText.includes(noResultsIndicators[i])) {
                        return 'Google Maps shows: ' + noResultsIndicators[i];
                    }
                }
                
                // Check if we're on the right page
                if (!window.location.href.includes('google.com/maps')) {
                    return 'Not on Google Maps page';
                }
                
                return 'Unknown issue - page loaded but no scrollable results';
                """
            )
            
            Communicator.show_message(message=f"[DEBUG] Final diagnosis: {google_no_results}")
            Communicator.show_message(message="We are sorry but, No results found for your search query on googel maps....")

        else:
            Communicator.show_message(message="Starting scrolling")

            last_height = 0

            while True:
                if Common.close_thread_is_set():
                    self.driver.quit()
                    return

                """Use the same logic that found the scrollable element initially"""
                current_scrollable = self.driver.execute_script(
                    """
                    // Try the same selectors that worked before
                    var selectors = [
                        "[role='feed']",
                        ".m6QErb",
                        ".gaBwhe",  // This was found on Railway
                        "[data-value='Search results']",
                        ".section-layout-root",
                        ".section-scrollbox",
                        "[jsaction*='scroll']",
                        ".section-result",
                        "[role='main'] [role='region']",
                        ".section-listbox",
                        "[aria-label*='Results']"
                    ];
                    
                    for (var i = 0; i < selectors.length; i++) {
                        var element = document.querySelector(selectors[i]);
                        if (element && element.scrollHeight > element.clientHeight) {
                            return element;
                        }
                    }
                    
                    // Fallback to any scrollable element
                    var allElements = document.querySelectorAll('*');
                    for (var j = 0; j < allElements.length; j++) {
                        var el = allElements[j];
                        if (el.scrollHeight > el.clientHeight && el.clientHeight > 200) {
                            return el;
                        }
                    }
                    return null;
                    """
                )
                
                if current_scrollable is None:
                    Communicator.show_message(message="[DEBUG] Lost scrollable element, breaking scroll loop")
                    break
                    
                scrollAbleElement = current_scrollable
                # More aggressive scrolling for Railway
                self.driver.execute_script(
                    """
                    arguments[0].scrollTo(0, arguments[0].scrollHeight);
                    // Also try scrolling the window
                    window.scrollTo(0, document.body.scrollHeight);
                    """,
                    scrollAbleElement,
                )
                
                # Longer wait for Railway's slower loading
                time.sleep(4)
                
                # Try to trigger more results loading
                self.driver.execute_script(
                    """
                    // Trigger scroll events that might load more results
                    var event = new Event('scroll', { bubbles: true });
                    arguments[0].dispatchEvent(event);
                    window.dispatchEvent(event);
                    """,
                    scrollAbleElement,
                )


                # get new scroll height and compare with last scroll height.
                new_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight", scrollAbleElement
                )
                
                # Check current result count
                current_results = self.driver.execute_script(
                    """
                    var links = document.querySelectorAll('a[href*="/maps/place/"], a.hfpxzc');
                    return links.length;
                    """
                )
                
                Communicator.show_message(f"[DEBUG] Current height: {new_height}, Last height: {last_height}, Results found: {current_results}")
                
                if new_height == last_height:
                    """checking if we have reached end of the list"""

                    script = f"""
                    const endingElement = document.querySelector(".PbZDve ");
                    return endingElement;
                    """

                    endAlertElement = self.driver.execute_script(
                        script)  # to know that we are at end of list or not

                    if endAlertElement is None:
                        """if it returns empty list its mean we are not at the end of list"""
                        try:  # sometimes google maps load results when a result is clicked
                            self.driver.execute_script(
                                "array=document.getElementsByClassName('hfpxzc');array[array.length-1].click();"
                            )
                        except JavascriptException:
                            pass
                    else:

                        break
                else:
                    last_height = new_height
                    
                    # Get the HTML content for parsing
                    allResultsListSoup = BeautifulSoup(
                        scrollAbleElement.get_attribute('outerHTML'), 'html.parser')

                    # Try multiple selectors for result links
                    allResultsAnchorTags = []
                    
                    # Primary selector
                    primary_results = allResultsListSoup.find_all('a', class_='hfpxzc')
                    if primary_results:
                        allResultsAnchorTags = primary_results
                        Communicator.show_message(f"[DEBUG] Found {len(primary_results)} results with primary selector")
                    else:
                        # Try alternative selectors
                        alternative_selectors = [
                            ('a[href*="/maps/place/"]', 'href contains /maps/place/'),
                            ('a[data-value="Directions"]', 'data-value="Directions"'),
                            ('a[role="link"]', 'role="link"'),
                            ('div[role="article"] a', 'article links'),
                            ('div[data-result-index] a', 'data-result-index links'),
                            ('[jsaction*="click"] a', 'jsaction click links')
                        ]
                        
                        for selector, description in alternative_selectors:
                            try:
                                alt_results = allResultsListSoup.select(selector)
                                if alt_results:
                                    allResultsAnchorTags = alt_results
                                    Communicator.show_message(f"[DEBUG] Found {len(alt_results)} results with {description}")
                                    break
                            except Exception as e:
                                Communicator.show_message(f"[DEBUG] Selector {selector} failed: {e}")
                                continue
                    
                    # Extract links
                    if allResultsAnchorTags:
                        self.__allResultsLinks = []
                        for anchorTag in allResultsAnchorTags:
                            href = anchorTag.get('href')
                            if href and '/maps/place/' in href:
                                self.__allResultsLinks.append(href)
                        
                        Communicator.show_message(f"Total locations scrolled: {len(self.__allResultsLinks)}")
                        Communicator.show_message(f"[DEBUG] Sample links: {self.__allResultsLinks[:2] if self.__allResultsLinks else 'None'}")
                    else:
                        Communicator.show_message("[DEBUG] No result links found with any selector")
                        # Debug: show what elements are actually present
                        all_links = allResultsListSoup.find_all('a')
                        Communicator.show_message(f"[DEBUG] Total <a> tags found: {len(all_links)}")
                        if all_links:
                            sample_classes = [link.get('class', []) for link in all_links[:5]]
                            Communicator.show_message(f"[DEBUG] Sample link classes: {sample_classes}")

            self.start_parsing()


                    