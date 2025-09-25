import time
import os
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
        
        # Railway-specific optimizations
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT')
        if is_railway:
            Communicator.show_message(message="[DEBUG] Railway environment - using optimized settings")
            max_attempts = 10  # More attempts for Railway
            base_wait_time = 8  # Longer wait time for Railway
        else:
            max_attempts = 6
            base_wait_time = 5
        
        # Wait for Google Maps to load and search results to appear
        scrollAbleElement = None
        
        for attempt in range(max_attempts):
            try:
                Communicator.show_message(message=f"[DEBUG] Attempt {attempt + 1}/{max_attempts} - Checking for feed element...")
                
                # Wait a bit for the page to load (longer for Railway)
                time.sleep(base_wait_time)
                
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
                          
                          # Add comprehensive HTML structure debugging
                          html_debug = self.driver.execute_script(
                              """
                              var debug = {
                                  feedElement: null,
                                  gaBwheElement: null,
                                  allLinks: [],
                                  bodyStructure: '',
                                  feedHTML: '',
                                  gaBwheHTML: ''
                              };
                              
                              // Check feed element
                              var feed = document.querySelector("[role='feed']");
                              if (feed) {
                                  debug.feedElement = {
                                      className: feed.className,
                                      innerHTML: feed.innerHTML.substring(0, 500),
                                      childrenCount: feed.children.length,
                                      scrollHeight: feed.scrollHeight,
                                      clientHeight: feed.clientHeight
                                  };
                                  debug.feedHTML = feed.outerHTML.substring(0, 1000);
                              }
                              
                              // Check gaBwhe element
                              var gaBwhe = document.querySelector(".gaBwhe");
                              if (gaBwhe) {
                                  debug.gaBwheElement = {
                                      className: gaBwhe.className,
                                      innerHTML: gaBwhe.innerHTML.substring(0, 500),
                                      childrenCount: gaBwhe.children.length,
                                      scrollHeight: gaBwhe.scrollHeight,
                                      clientHeight: gaBwhe.clientHeight,
                                      parentClassName: gaBwhe.parentElement ? gaBwhe.parentElement.className : 'no-parent'
                                  };
                                  debug.gaBwheHTML = gaBwhe.outerHTML.substring(0, 1000);
                              }
                              
                              // Find all links
                              var allLinks = document.querySelectorAll('a');
                              debug.allLinks = Array.from(allLinks).slice(0, 10).map(function(link) {
                                  return {
                                      href: link.href,
                                      text: link.textContent.substring(0, 50),
                                      className: link.className
                                  };
                              });
                              
                              // Get body structure overview
                              var bodyChildren = Array.from(document.body.children).map(function(child) {
                                  return child.tagName + '.' + child.className.split(' ').join('.');
                              });
                              debug.bodyStructure = bodyChildren.join(', ');
                              
                              return debug;
                              """
                          )
                          
                          Communicator.show_message(message=f"[DEBUG] === DETAILED HTML ANALYSIS ===")
                          if html_debug.get('feedElement'):
                              Communicator.show_message(message=f"[DEBUG] Feed Element: {html_debug['feedElement']}")
                          else:
                              Communicator.show_message(message=f"[DEBUG] Feed Element: NOT FOUND")
                              
                          if html_debug.get('gaBwheElement'):
                              Communicator.show_message(message=f"[DEBUG] GaBwhe Element: {html_debug['gaBwheElement']}")
                          else:
                              Communicator.show_message(message=f"[DEBUG] GaBwhe Element: NOT FOUND")
                              
                          Communicator.show_message(message=f"[DEBUG] All Links (first 10): {html_debug.get('allLinks', [])}")
                          Communicator.show_message(message=f"[DEBUG] Body Structure: {html_debug.get('bodyStructure', 'Unknown')}")
                          
                          if html_debug.get('feedHTML'):
                              Communicator.show_message(message=f"[DEBUG] Feed HTML Sample: {html_debug['feedHTML'][:200]}...")
                          if html_debug.get('gaBwheHTML'):
                              Communicator.show_message(message=f"[DEBUG] GaBwhe HTML Sample: {html_debug['gaBwheHTML'][:200]}...")
                          
                          # Take a screenshot for debugging (only on first attempt)
                          if attempt == 0:
                              try:
                                  screenshot_path = f"/tmp/railway_debug_screenshot_{attempt + 1}.png"
                                  self.driver.save_screenshot(screenshot_path)
                                  Communicator.show_message(message=f"[DEBUG] Screenshot saved to: {screenshot_path}")
                                  
                                  # Also get page source sample
                                  page_source = self.driver.page_source
                                  source_sample = page_source[:2000] if page_source else "No page source"
                                  Communicator.show_message(message=f"[DEBUG] Page Source Sample: {source_sample}...")
                                  
                              except Exception as e:
                                  Communicator.show_message(message=f"[DEBUG] Screenshot failed: {e}")
                    
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
             
             # Railway fallback - try to extract any visible results without scrolling
             if is_railway:
                 Communicator.show_message(message="[DEBUG] Railway fallback - attempting to extract visible results...")
                 visible_results = self.driver.execute_script(
                     """
                     var results = [];
                     var selectors = [
                         'a[data-result-index]',
                         'a[href*="/maps/place/"]',
                         'div[data-result-index]',
                         '.section-result',
                         '[role="article"]',
                         'a[jsaction*="click"]'
                     ];
                     
                     selectors.forEach(function(selector) {
                         var elements = document.querySelectorAll(selector);
                         for (var i = 0; i < Math.min(elements.length, 10); i++) {
                             var el = elements[i];
                             var href = el.href || (el.querySelector('a') ? el.querySelector('a').href : '');
                             if (href && href.includes('maps/place')) {
                                 results.push(href);
                             }
                         }
                     });
                     
                     return [...new Set(results)]; // Remove duplicates
                     """
                 )
                 
                 if visible_results and len(visible_results) > 0:
                     Communicator.show_message(message=f"[DEBUG] Found {len(visible_results)} visible results without scrolling")
                     self.__allResultsLinks = visible_results
                     self.__init_parser()
                     self.start_parsing()
                     return
                 else:
                     Communicator.show_message(message="[DEBUG] No visible results found in Railway fallback")
             
             Communicator.show_message(message="We are sorry but, No results found for your search query on googel maps....")

        else:
            Communicator.show_message(message="Starting scrolling")
            
            # Debug the scrollable element we're about to use
            element_debug = self.driver.execute_script(
                """
                var element = arguments[0];
                return {
                    tagName: element.tagName,
                    className: element.className,
                    id: element.id,
                    scrollHeight: element.scrollHeight,
                    clientHeight: element.clientHeight,
                    innerHTML: element.innerHTML.substring(0, 300),
                    childrenCount: element.children.length,
                    hasLinks: element.querySelectorAll('a').length,
                    hasPlaceLinks: element.querySelectorAll('a[href*="/maps/place/"]').length
                };
                """, 
                scrollAbleElement
            )
            
            Communicator.show_message(message=f"[DEBUG] === SCROLLING ELEMENT DEBUG ===")
            Communicator.show_message(message=f"[DEBUG] Element Info: {element_debug}")

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


                    