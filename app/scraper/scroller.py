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
                error_msg = str(e)
                Communicator.show_message(message=f"[DEBUG] Error on attempt {attempt + 1}: {error_msg}")
                
                # If we get DevTools disconnection errors in Railway, trigger fallback immediately
                if is_railway and ("disconnected: not connected to DevTools" in error_msg or "DevTools" in error_msg):
                    Communicator.show_message(message="[DEBUG] DevTools disconnection detected in Railway - triggering immediate fallback analysis")
                    
                    # Try to check if driver is still responsive
                    try:
                        current_url = self.driver.current_url
                        Communicator.show_message(message=f"[DEBUG] Driver still responsive, current URL: {current_url[:100]}...")
                    except Exception as driver_error:
                        Communicator.show_message(message=f"[DEBUG] Driver completely unresponsive: {driver_error}")
                        # Driver is dead, can't do much more
                        return
                    
                    break  # Exit the retry loop and go to fallback
                
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
                 
                 # Check if driver is still responsive before trying JavaScript
                 try:
                     driver_responsive = True
                     test_url = self.driver.current_url
                     Communicator.show_message(message=f"[DEBUG] Driver responsive, current URL: {test_url[:100]}...")
                 except Exception as e:
                     driver_responsive = False
                     Communicator.show_message(message=f"[DEBUG] Driver not responsive: {e}")
                 
                 if driver_responsive:
                     # First, let's see what's actually on the page
                     try:
                         page_analysis = self.driver.execute_script(
                             """
                             return {
                                 title: document.title,
                                 url: window.location.href,
                                 bodyText: document.body.innerText.substring(0, 2000),
                                 innerHTML: document.body.innerHTML.substring(0, 3000),
                                 allLinks: Array.from(document.querySelectorAll('a')).slice(0, 50).map(a => ({
                                     href: a.href,
                                     text: a.innerText.substring(0, 100),
                                     hasPlace: a.href.includes('place'),
                                     className: a.className,
                                     id: a.id
                                 })),
                                 divCount: document.querySelectorAll('div').length,
                                 hasNoResults: document.body.innerText.includes('No results') || 
                                                  document.body.innerText.includes('لم يتم العثور') ||
                                                  document.body.innerText.includes('Couldn\\'t find'),
                                 allDivs: Array.from(document.querySelectorAll('div[data-result-index], div[jsaction], div[role], div[aria-label]')).slice(0, 20).map(div => ({
                                     className: div.className,
                                     id: div.id,
                                     role: div.getAttribute('role'),
                                     ariaLabel: div.getAttribute('aria-label'),
                                     dataResultIndex: div.getAttribute('data-result-index'),
                                     jsaction: div.getAttribute('jsaction'),
                                     text: div.innerText.substring(0, 150)
                                 })),
                                 searchResults: Array.from(document.querySelectorAll('[data-result-index], .section-result, [role="article"], .result, [aria-label*="result"]')).slice(0, 10).map(el => ({
                                     tagName: el.tagName,
                                     className: el.className,
                                     id: el.id,
                                     text: el.innerText.substring(0, 200),
                                     innerHTML: el.innerHTML.substring(0, 300)
                                 }))
                             };
                             """
                         )
                     except Exception as js_error:
                         Communicator.show_message(message=f"[DEBUG] JavaScript execution failed: {js_error}")
                         page_analysis = {"error": "JavaScript failed", "title": "Unknown", "url": "Unknown"}
                 else:
                     Communicator.show_message(message="[DEBUG] Driver not responsive - skipping JavaScript analysis")
                     page_analysis = {"error": "Driver not responsive", "title": "Unknown", "url": "Unknown"}
                 
                 Communicator.show_message(message=f"[DEBUG] === DETAILED RAILWAY PAGE ANALYSIS ===")
                 Communicator.show_message(message=f"[DEBUG] Title: {page_analysis.get('title', 'Unknown')}")
                 Communicator.show_message(message=f"[DEBUG] URL: {page_analysis.get('url', 'Unknown')}")
                 Communicator.show_message(message=f"[DEBUG] Has No Results: {page_analysis.get('hasNoResults', False)}")
                 Communicator.show_message(message=f"[DEBUG] Div Count: {page_analysis.get('divCount', 0)}")
                 Communicator.show_message(message=f"[DEBUG] Body Text Sample (first 500 chars): {page_analysis.get('bodyText', '')[:500]}...")
                 Communicator.show_message(message=f"[DEBUG] HTML Sample (first 800 chars): {page_analysis.get('innerHTML', '')[:800]}...")
                 
                 # Show detailed link analysis
                 all_links = page_analysis.get('allLinks', [])
                 place_links = [link for link in all_links if link.get('hasPlace', False)]
                 Communicator.show_message(message=f"[DEBUG] Found {len(place_links)} place links out of {len(all_links)} total links")
                 
                 # Show ALL links for debugging (not just place links)
                 for i, link in enumerate(all_links[:10]):  # Show first 10 links
                     Communicator.show_message(message=f"[DEBUG] Link {i+1}: href='{link.get('href', 'No href')[:100]}' text='{link.get('text', 'No text')[:50]}' class='{link.get('className', 'No class')[:30]}'")
                 
                 # Show search result elements
                 search_results = page_analysis.get('searchResults', [])
                 Communicator.show_message(message=f"[DEBUG] Found {len(search_results)} search result elements")
                 for i, result in enumerate(search_results[:5]):
                     Communicator.show_message(message=f"[DEBUG] Search Result {i+1}: {result.get('tagName', 'Unknown')} class='{result.get('className', 'No class')[:50]}' text='{result.get('text', 'No text')[:100]}'")
                 
                 # Show interesting divs
                 all_divs = page_analysis.get('allDivs', [])
                 Communicator.show_message(message=f"[DEBUG] Found {len(all_divs)} interesting divs")
                 for i, div in enumerate(all_divs[:5]):
                     Communicator.show_message(message=f"[DEBUG] Div {i+1}: class='{div.get('className', 'No class')[:50]}' role='{div.get('role', 'No role')}' aria-label='{div.get('ariaLabel', 'No aria')[:50]}'")
                 
                 # Take a screenshot for debugging
                 try:
                     import tempfile
                     screenshot_path = "/tmp/railway_google_maps_debug.png"
                     self.driver.save_screenshot(screenshot_path)
                     Communicator.show_message(message=f"[DEBUG] Screenshot saved to: {screenshot_path}")
                     
                     # Also save the full page source for analysis
                     page_source_path = "/tmp/railway_google_maps_source.html"
                     with open(page_source_path, 'w', encoding='utf-8') as f:
                         f.write(self.driver.page_source)
                     Communicator.show_message(message=f"[DEBUG] Page source saved to: {page_source_path}")
                     
                 except Exception as e:
                     Communicator.show_message(message=f"[DEBUG] Failed to save screenshot/source: {e}")
                 
                 # More aggressive link extraction
                 visible_results = self.driver.execute_script(
                     """
                     var results = [];
                     var selectors = [
                         'a[data-result-index]',
                         'a[href*="/maps/place/"]',
                         'a[href*="place/"]',
                         'div[data-result-index] a',
                         '.section-result a',
                         '[role="article"] a',
                         'a[jsaction*="click"]',
                         '[data-value] a',
                         '.section-listbox a',
                         '[aria-label*="result"] a'
                     ];
                     
                     selectors.forEach(function(selector, index) {
                         var elements = document.querySelectorAll(selector);
                         console.log('Selector', index, selector, 'found', elements.length, 'elements');
                         for (var i = 0; i < Math.min(elements.length, 5); i++) {
                             var el = elements[i];
                             var href = el.href || '';
                             if (href && (href.includes('maps/place') || href.includes('/place/'))) {
                                 results.push(href);
                             }
                         }
                     });
                     
                     // Also try to find any clickable elements with place-like text
                     var allClickable = document.querySelectorAll('a, [role="button"], [onclick], [jsaction]');
                     for (var j = 0; j < Math.min(allClickable.length, 100); j++) {
                         var el = allClickable[j];
                         var href = el.href || '';
                         var text = (el.innerText || el.textContent || '').toLowerCase();
                         
                         if (href && (href.includes('maps/place') || href.includes('/place/'))) {
                             results.push(href);
                         }
                     }
                     
                     return [...new Set(results)]; // Remove duplicates
                     """
                 )
                 
                 Communicator.show_message(message=f"[DEBUG] Aggressive extraction found {len(visible_results)} results")
                 for i, result in enumerate(visible_results[:3]):
                     Communicator.show_message(message=f"[DEBUG] Extracted Result {i+1}: {result[:100]}...")
                 
                 # If no place links found, try to extract business information directly
                 if not visible_results or len(visible_results) == 0:
                     Communicator.show_message(message="[DEBUG] No place links found, trying direct business extraction...")
                     business_data = self.driver.execute_script(
                         """
                         var businesses = [];
                         var textNodes = [];
                         
                         // Look for text that might be business names or addresses
                         function extractTextFromElement(element, depth) {
                             if (depth > 3) return; // Limit recursion depth
                             
                             var text = element.innerText || element.textContent || '';
                             if (text && text.length > 5 && text.length < 200) {
                                 // Look for patterns that might be business names
                                 if (text.match(/café|coffee|restaurant|shop|store|hotel|مقهى|مطعم|فندق|محل/i)) {
                                     textNodes.push({
                                         text: text.trim(),
                                         tagName: element.tagName,
                                         className: element.className,
                                         parent: element.parentElement ? element.parentElement.tagName : 'none'
                                     });
                                 }
                             }
                             
                             // Recurse through children
                             for (var i = 0; i < element.children.length && i < 10; i++) {
                                 extractTextFromElement(element.children[i], depth + 1);
                             }
                         }
                         
                         // Search the entire document
                         extractTextFromElement(document.body, 0);
                         
                         return {
                             businessTexts: textNodes.slice(0, 10),
                             totalFound: textNodes.length
                         };
                         """
                     )
                     
                     business_texts = business_data.get('businessTexts', [])
                     Communicator.show_message(message=f"[DEBUG] Found {len(business_texts)} potential business texts out of {business_data.get('totalFound', 0)} total")
                     
                     for i, biz in enumerate(business_texts[:5]):
                         Communicator.show_message(message=f"[DEBUG] Business Text {i+1}: '{biz.get('text', 'No text')[:100]}' ({biz.get('tagName', 'Unknown')})")
                 
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


                    