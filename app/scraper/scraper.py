"""
This module contain the code for backend,
that will handle scraping process
"""

from time import sleep
from scraper.base import Base
from scraper.scroller import Scroller
import undetected_chromedriver as uc
from settings import DRIVER_EXECUTABLE_PATH
from scraper.communicator import Communicator


class Backend(Base):
    

    def __init__(self, searchquery, outputformat,  healdessmode):
        """
        params:

        search query: it is the value that user will enter in search query entry 
        outputformat: output format of file , selected by user
        outputpath: directory path where file will be stored after scraping
        headlessmode: it's value can be 0 and 1, 0 means unchecked box and 1 means checked

        """


        self.searchquery = searchquery  # search query that user will enter
        
        # it is a function used as api for transfering message form this backend to frontend

        self.headlessMode = healdessmode

        self.init_driver()
        self.scroller = Scroller(driver=self.driver)
        self.init_communicator()

    def init_communicator(self):
        Communicator.set_backend_object(self)


    def init_driver(self):
        options = uc.ChromeOptions()
        if self.headlessMode == 1:
            options.headless = True

        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        import os
        chrome_bin = os.environ.get("CHROME_BIN")
        print(f"[DEBUG] CHROME_BIN env: {chrome_bin}")
        if not chrome_bin or not isinstance(chrome_bin, str):
            # Fallback for local Windows development
            if os.name == "nt":
                chrome_bin = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
            else:
                raise RuntimeError("CHROME_BIN environment variable is not set or not a string")
        # Check if the chrome_bin path exists
        if not os.path.exists(chrome_bin):
            print(f"[DEBUG] Chrome binary not found at {chrome_bin}")
            # Try fallback to /usr/bin/chromium
            if os.path.exists("/usr/bin/chromium"):
                print("[DEBUG] Falling back to /usr/bin/chromium")
                chrome_bin = "/usr/bin/chromium"
            else:
                print("[DEBUG] /usr/bin/chromium also not found")
            # Print /usr/bin directory listing for debugging
            print("[DEBUG] /usr/bin directory listing:")
            try:
                print(os.listdir("/usr/bin"))
            except Exception as e:
                print(f"[DEBUG] Could not list /usr/bin: {e}")
        else:
            print(f"[DEBUG] Chrome binary found at {chrome_bin}")
        options.binary_location = chrome_bin
        print(f"[DEBUG] Using Chrome binary: {chrome_bin}")
        # Also pass browser_executable_path to uc.Chrome below

        Communicator.show_message("Wait checking for driver...\nIf you don't have webdriver in your machine it will install it")

        try:
            uc_kwargs = {"options": options, "browser_executable_path": chrome_bin}
            if DRIVER_EXECUTABLE_PATH is not None:
                uc_kwargs["driver_executable_path"] = DRIVER_EXECUTABLE_PATH
            self.driver = uc.Chrome(**uc_kwargs)

        except NameError:
            self.driver = uc.Chrome(options=options)
        
        
        

        Communicator.show_message("Opening browser...")
        self.driver.maximize_window()
        self.driver.implicitly_wait(self.timeout)



    def mainscraping(self):

        try:
            querywithplus = "+".join(self.searchquery.split())

            """
            link of page variable contains the link of page of google maps that user wants to scrape.
            We have make it by inserting search query in it
            """

            link_of_page = f"https://www.google.com/maps/search/{querywithplus}/"

            # ==========================================

            self.openingurl(url=link_of_page)

            Communicator.show_message("Working start...")

            sleep(1)

            self.scroller.scroll()
            

        except Exception as e:
            """
            Handling all errors.If any error occurs like user has closed the self.driver and if 'no such window' error occurs
            """
            Communicator.show_message(f"Error occurred while scraping. Error: {str(e)}")


        finally:
            try:
                Communicator.show_message("Closing the driver")
                self.driver.close()
                self.driver.quit()
            except:  # if browser is always closed due to error
                pass

            Communicator.end_processing()
            Communicator.show_message("Now you can start another session")



