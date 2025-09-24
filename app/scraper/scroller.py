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

                """again finding element to avoid StaleElementReferenceException"""
                scrollAbleElement = self.driver.execute_script(
                """return document.querySelector("[role='feed']")"""
            )
                self.driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
                    scrollAbleElement,
                )
                time.sleep(2)


                # get new scroll height and compare with last scroll height.
                new_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight", scrollAbleElement
                )
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
                    allResultsListSoup = BeautifulSoup(
                    scrollAbleElement.get_attribute('outerHTML'), 'html.parser')

                    allResultsAnchorTags = allResultsListSoup.find_all(
                        'a', class_='hfpxzc')

                    """all the links of results"""
                    self.__allResultsLinks = [anchorTag.get(
                        'href') for anchorTag in allResultsAnchorTags]
                    
                    Communicator.show_message(f"Total locations scrolled: {len(self.__allResultsLinks)}")

            self.start_parsing()


                    