"""
This module contain the code for backend,
that will handle scraping process
"""

from time import sleep
from scraper.base import Base
from scraper.scroller import Scroller
import os
import subprocess
from settings import DRIVER_EXECUTABLE_PATH
from scraper.communicator import Communicator

# Try importing undetected_chromedriver first, fallback to selenium
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager


class Backend(Base):
    
    def __init__(self, searchquery, outputformat, healdessmode):
        """
        params:

        search query: it is the value that user will enter in search query entry 
        outputformat: output format of file , selected by user
        outputpath: directory path where file will be stored after scraping
        headlessmode: it's value can be 0 and 1, 0 means unchecked box and 1 means checked
        """

        self.searchquery = searchquery  # search query that user will enter
        self.headlessMode = healdessmode

        self.init_driver()
        self.scroller = Scroller(driver=self.driver)
        self.init_communicator()

    def init_communicator(self):
        Communicator.set_backend_object(self)

    def find_chrome_executable(self):
        """Find Chrome executable in different possible locations"""
        possible_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable", 
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/opt/google/chrome/chrome"
        ]
        
        # Check environment variable first
        chrome_bin = os.environ.get("CHROME_BIN")
        if chrome_bin and os.path.exists(chrome_bin):
            print(f"[DEBUG] Found Chrome via CHROME_BIN: {chrome_bin}")
            return chrome_bin
        
        # Check possible paths
        for path in possible_paths:
            if os.path.exists(path):
                print(f"[DEBUG] Found Chrome at: {path}")
                return path
        
        # Try to find using which command
        try:
            for cmd in ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']:
                result = subprocess.run(['which', cmd], capture_output=True, text=True)
                if result.returncode == 0:
                    path = result.stdout.strip()
                    print(f"[DEBUG] Found Chrome via 'which {cmd}': {path}")
                    return path
        except Exception as e:
            print(f"[DEBUG] 'which' command failed: {e}")
        
        print("[DEBUG] Chrome executable not found")
        return None

    def init_driver(self):
        chrome_path = self.find_chrome_executable()
        
        if UC_AVAILABLE:
            self._init_undetected_chrome(chrome_path)
        else:
            self._init_regular_chrome(chrome_path)

    def _init_undetected_chrome(self, chrome_path):
        """Initialize undetected chrome driver"""
        options = uc.ChromeOptions()
        
        # Essential options for deployment
        if self.headlessMode == 1:
            options.headless = True
            
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        
        # Disable images for faster loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        if chrome_path:
            options.binary_location = chrome_path

        Communicator.show_message("Wait checking for driver...\nIf you don't have webdriver in your machine it will install it")

        try:
            if DRIVER_EXECUTABLE_PATH is not None:
                self.driver = uc.Chrome(
                    driver_executable_path=DRIVER_EXECUTABLE_PATH, 
                    options=options
                )
            else:
                self.driver = uc.Chrome(options=options)
                
        except Exception as e:
            print(f"[DEBUG] Undetected Chrome failed: {e}")
            # Fallback to regular Chrome
            self._init_regular_chrome(chrome_path)

    def _init_regular_chrome(self, chrome_path):
        """Initialize regular selenium chrome driver"""
        options = Options()
        
        # Essential options for deployment
        if self.headlessMode == 1:
            options.add_argument("--headless")
            
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--window-size=1920,1080")
        
        # Disable images for faster loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        if chrome_path:
            options.binary_location = chrome_path

        Communicator.show_message("Wait checking for driver...\nIf you don't have webdriver in your machine it will install it")

        try:
            # Try to use webdriver-manager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"[DEBUG] webdriver-manager failed: {e}")
            # Try without service
            try:
                self.driver = webdriver.Chrome(options=options)
            except Exception as e2:
                print(f"[DEBUG] Regular Chrome failed: {e2}")
                raise RuntimeError(f"Could not initialize Chrome driver: {e2}")

        Communicator.show_message("Opening browser...")
        try:
            if not self.headlessMode:
                self.driver.maximize_window()
        except:
            pass  # In headless mode, maximize might fail
            
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
            error_msg = f"❌ Scraping error: \n---------------------\n{str(e)}\n---------------------"
            if "browser executable" in str(e).lower():
                error_msg += ("\nMake sure your browser is installed in the default location (path).\n"
                             "If you are sure about the browser executable, you can specify it using\n"
                             "the `browser_executable_path='/path/to/browser/executable` parameter.")
            
            Communicator.show_message(error_msg)
            print(f"[ERROR] {error_msg}")

        finally:
            try:
                Communicator.show_message("Closing the driver")
                if hasattr(self, 'driver'):
                    self.driver.close()
                    self.driver.quit()
            except:  # if browser is always closed due to error
                pass

            Communicator.end_processing()
            Communicator.show_message("Now you can start another session")