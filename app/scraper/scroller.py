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
                     
                     # Check if page has loaded at all
                     page_loaded = self.driver.execute_script(
                         """
                         return document.querySelector("[role='main']") || 
                                document.querySelector(".m6QErb") ||
                                document.querySelector("[data-value='Directions']") ||
                                document.querySelector("title")
                         """
                     )
                     
                     if page_loaded:
                         Communicator.show_message(message="[DEBUG] Page loaded but no scrollable results found")
                     else:
                         Communicator.show_message(message="[DEBUG] Page may not be loaded yet")
                         
             except Exception as e:
                 Communicator.show_message(message=f"[DEBUG] Error on attempt {attempt + 1}: {str(e)}")
                
        if scrollAbleElement is None:
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


                    