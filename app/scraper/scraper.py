"""
This module contain the code for backend,
that will handle scraping process
"""


from time import sleep
try:
    from scraper.base import Base
    from scraper.scroller import Scroller
    from settings import DRIVER_EXECUTABLE_PATH
    from scraper.communicator import Communicator
except ImportError:
    from app.scraper.base import Base
    from app.scraper.scroller import Scroller
    from app.settings import DRIVER_EXECUTABLE_PATH
    from app.scraper.communicator import Communicator
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests

# Try importing undetected_chromedriver first
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False

# Try importing remote chrome connector
try:
    from remote_chrome_connector import RemoteChromeManager
    REMOTE_CHROME_AVAILABLE = True
except ImportError:
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from remote_chrome_connector import RemoteChromeManager
        REMOTE_CHROME_AVAILABLE = True
    except ImportError:
        REMOTE_CHROME_AVAILABLE = False


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
        import platform
        system = platform.system().lower()
        
        if system == "windows":
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
                r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\chrome.exe"
            ]
            which_commands = ['chrome', 'google-chrome']
        else:
            possible_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable", 
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/opt/google/chrome/chrome",
                "/snap/bin/chromium",
                "/usr/local/bin/chrome"
            ]
            which_commands = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']
        
        # Check environment variable first
        chrome_bin = os.environ.get("CHROME_BIN")
        if chrome_bin and os.path.exists(chrome_bin):
            print(f"[DEBUG] Found Chrome via CHROME_BIN: {chrome_bin}")
            return chrome_bin
        
        # Check possible paths
        for path in possible_paths:
            expanded_path = os.path.expandvars(os.path.expanduser(path))
            if os.path.exists(expanded_path):
                print(f"[DEBUG] Found Chrome at: {expanded_path}")
                return expanded_path
        
        # Try to find using which/where command
        try:
            which_cmd = 'where' if system == "windows" else 'which'
            for cmd in which_commands:
                try:
                    result = subprocess.run([which_cmd, cmd], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        path = result.stdout.strip().split('\n')[0]  # Take first result
                        if os.path.exists(path):
                            print(f"[DEBUG] Found Chrome via '{which_cmd} {cmd}': {path}")
                            return path
                except subprocess.TimeoutExpired:
                    print(f"[DEBUG] '{which_cmd} {cmd}' command timed out")
                    continue
                except Exception as e:
                    print(f"[DEBUG] '{which_cmd} {cmd}' command failed: {e}")
                    continue
        except Exception as e:
            print(f"[DEBUG] Command search failed: {e}")
        
        print("[DEBUG] Chrome executable not found")
        return None

    def init_driver(self):
        """Initialize Chrome driver with multiple fallback options"""
        
        # First priority: Try remote Chrome connection (user's local Chrome)
        if REMOTE_CHROME_AVAILABLE and os.getenv('REMOTE_CHROME_URL'):
            try:
                print("[DEBUG] Attempting to connect to user's remote Chrome...")
                remote_manager = RemoteChromeManager()
                self.driver = remote_manager.get_driver()
                print("[DEBUG] Successfully connected to remote Chrome!")
                
                # Set up driver properties
                self.driver.implicitly_wait(self.timeout)
                Communicator.show_message("Opening browser...")
                if not self.headlessMode:
                    try:
                        self.driver.maximize_window()
                    except:
                        pass
                return
            except Exception as e:
                print(f"[DEBUG] Remote Chrome connection failed: {e}")
        
        # Second priority: Local Chrome initialization
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
            
        # Core stability options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--window-size=1920,1080")
        
        # Additional stability options for Railway
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-translate")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--mute-audio")
        options.add_argument("--no-first-run")
        options.add_argument("--safebrowsing-disable-auto-update")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-permissions-api")
        options.add_argument("--disable-presentation-api")
        options.add_argument("--disable-print-preview")
        options.add_argument("--disable-speech-api")
        options.add_argument("--disable-file-system")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-prompt-on-repost")
        
        # Memory management
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=4096")
        options.add_argument("--single-process")  # Use single process to avoid crashes
        
        # Network and timeout settings
        options.add_argument("--aggressive-cache-discard")
        options.add_argument("--disable-hang-monitor")
        
        # Use US-based user agent to avoid EU consent requirements
        options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
        
        # Disable images and other resources for faster loading and less memory usage
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.cookies": 1,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        options.add_experimental_option("prefs", prefs)

        if chrome_path:
            options.binary_location = chrome_path

        Communicator.show_message("Wait checking for driver...\nIf you don't have webdriver in your machine it will install it")

        try:
            if DRIVER_EXECUTABLE_PATH is not None and os.path.exists(DRIVER_EXECUTABLE_PATH):
                self.driver = uc.Chrome(
                    driver_executable_path=DRIVER_EXECUTABLE_PATH, 
                    options=options
                )
            else:
                self.driver = uc.Chrome(options=options)
            
            print("[DEBUG] Successfully initialized undetected Chrome")
                
        except Exception as e:
            print(f"[DEBUG] Undetected Chrome failed: {e}")
            # Check if it's a binary location error
            if "Binary Location Must be a String" in str(e) or "binary location" in str(e).lower():
                print("[DEBUG] Binary location error detected, trying without custom path")
                try:
                    # Try without custom binary location
                    options.binary_location = None
                    self.driver = uc.Chrome(options=options)
                    print("[DEBUG] Successfully initialized undetected Chrome without custom binary")
                    return
                except Exception as e2:
                    print(f"[DEBUG] Undetected Chrome retry failed: {e2}")
            
            # Fallback to regular Chrome
            print("[DEBUG] Falling back to regular Chrome driver")
            self._init_regular_chrome(chrome_path)

    def _init_regular_chrome(self, chrome_path):
        """Initialize regular selenium chrome driver"""
        options = Options()
        
        # Essential options for deployment
        if self.headlessMode == 1:
            options.add_argument("--headless=new")  # Use new headless mode
            
        # Core stability options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Additional stability options for Railway
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-translate")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--mute-audio")
        options.add_argument("--no-first-run")
        options.add_argument("--safebrowsing-disable-auto-update")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-permissions-api")
        options.add_argument("--disable-presentation-api")
        options.add_argument("--disable-print-preview")
        options.add_argument("--disable-speech-api")
        options.add_argument("--disable-file-system")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-prompt-on-repost")
        
        # Memory management
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=4096")
        options.add_argument("--single-process")  # Use single process to avoid crashes
        
        # Network and timeout settings
        options.add_argument("--aggressive-cache-discard")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-prompt-on-repost")
        
        # Use US-based user agent to avoid EU consent requirements
        options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Disable images and other resources for faster loading and less memory usage
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.cookies": 1,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        options.add_experimental_option("prefs", prefs)

        if chrome_path:
            options.binary_location = chrome_path

        Communicator.show_message("Wait checking for driver...\nIf you don't have webdriver in your machine it will install it")

        # Try multiple initialization methods (prioritize system chromedriver for Railway)
        initialization_methods = [
            ("system chromedriver", self._try_system_chromedriver),
            ("webdriver-manager", self._try_webdriver_manager),
            ("default chrome", self._try_default_chrome)
        ]
        
        last_error = None
        for method_name, method in initialization_methods:
            try:
                print(f"[DEBUG] Trying {method_name}...")
                self.driver = method(options)
                print(f"[DEBUG] Successfully initialized with {method_name}")
                break
            except Exception as e:
                print(f"[DEBUG] {method_name} failed: {e}")
                last_error = e
                continue
        else:
            # If all methods failed
            error_msg = self._generate_chrome_error_message(chrome_path, last_error)
            raise RuntimeError(error_msg)

        Communicator.show_message("Opening browser...")
        try:
            if not self.headlessMode:
                self.driver.maximize_window()
        except:
            pass  # In headless mode, maximize might fail
            
        self.driver.implicitly_wait(self.timeout)

    def _try_webdriver_manager(self, options):
        """Try to initialize using webdriver-manager"""
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def _try_system_chromedriver(self, options):
        """Try to use system-installed chromedriver"""
        # Check environment variable first
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
        if chromedriver_path and os.path.exists(chromedriver_path):
            print(f"[DEBUG] Using CHROMEDRIVER_PATH: {chromedriver_path}")
            service = Service(chromedriver_path)
            return webdriver.Chrome(service=service, options=options)
        
        # Try common system paths (prioritize /usr/bin for Railway)
        import platform
        system = platform.system().lower()
        if system == "windows":
            possible_paths = [
                r"C:\chromedriver\chromedriver.exe",
                r"C:\Program Files\chromedriver\chromedriver.exe",
                r"C:\tools\chromedriver\chromedriver.exe"
            ]
        else:
            possible_paths = [
                "/usr/bin/chromedriver",  # Railway/Docker standard location
                "/usr/local/bin/chromedriver",
                "/opt/chromedriver/chromedriver"
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"[DEBUG] Using system chromedriver: {path}")
                service = Service(path)
                return webdriver.Chrome(service=service, options=options)
        
        raise Exception("No system chromedriver found")
    
    def _try_default_chrome(self, options):
        """Try to initialize without explicit service"""
        return webdriver.Chrome(options=options)
    
    def _generate_chrome_error_message(self, chrome_path, last_error):
        """Generate a helpful error message for Chrome initialization failures"""
        import platform
        system = platform.system().lower()
        
        error_msg = f"Could not initialize Chrome driver: {last_error}\n\n"
        error_msg += "🔧 TROUBLESHOOTING STEPS:\n"
        error_msg += "=" * 50 + "\n"
        
        if system == "windows":
            error_msg += "1. Install Google Chrome from: https://www.google.com/chrome/\n"
            error_msg += "2. Make sure Chrome is installed in the default location\n"
            error_msg += "3. Try running as Administrator\n"
            error_msg += "4. Check Windows Defender/Antivirus settings\n"
        else:
            error_msg += "1. Install Google Chrome:\n"
            error_msg += "   Ubuntu/Debian: sudo apt-get install google-chrome-stable\n"
            error_msg += "   CentOS/RHEL: sudo yum install google-chrome-stable\n"
            error_msg += "   Or download from: https://www.google.com/chrome/\n"
            error_msg += "2. Install dependencies:\n"
            error_msg += "   sudo apt-get install -y xvfb\n"
            error_msg += "3. Set environment variables:\n"
            error_msg += "   export CHROME_BIN=/usr/bin/google-chrome\n"
        
        error_msg += f"\n📍 Chrome path searched: {chrome_path or 'Not found'}\n"
        error_msg += "💡 For deployment, check the DEPLOYMENT_GUIDE.md file\n"
        
        return error_msg

    def handle_consent_page(self):
        """Handle Google's consent page if it appears"""
        try:
            # Check if we're on a consent page
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            Communicator.show_message(f"[DEBUG] Current URL: {current_url}")
            Communicator.show_message(f"[DEBUG] Page Title: {page_title}")
            
            if "consent.google.com" in current_url or "consent" in page_title.lower():
                Communicator.show_message("[DEBUG] Detected Google consent page, attempting to handle...")
                
                # Try to find and click accept buttons
                consent_handled = self.driver.execute_script(
                    """
                    // Try multiple strategies to handle consent
                    var acceptButtons = [
                        'button[aria-label*="Accept"]',
                        'button[aria-label*="Accepteren"]',  // Dutch
                        'button[aria-label*="Akzeptieren"]', // German
                        'button[aria-label*="Accepter"]',    // French
                        '[data-value="accept"]',
                        '[role="button"][aria-label*="accept"]'
                    ];
                    
                    // First try specific selectors
                    for (var i = 0; i < acceptButtons.length; i++) {
                        var buttons = document.querySelectorAll(acceptButtons[i]);
                        for (var j = 0; j < buttons.length; j++) {
                            var button = buttons[j];
                            if (button && button.offsetParent !== null) {
                                button.click();
                                return 'Clicked: ' + acceptButtons[i];
                            }
                        }
                    }
                    
                    // Try to find any button with "accept" text
                    var allButtons = document.querySelectorAll('button, div[role="button"], [role="button"]');
                    for (var k = 0; k < allButtons.length; k++) {
                        var btn = allButtons[k];
                        var text = (btn.textContent || btn.innerText || '').toLowerCase();
                        var ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                        
                        if (text.includes('accept') || text.includes('accepteren') || 
                            text.includes('alles accepteren') || text.includes('alle accepteren') ||
                            ariaLabel.includes('accept') || ariaLabel.includes('accepteren')) {
                            btn.click();
                            return 'Clicked button with text: ' + (btn.textContent || btn.innerText || btn.getAttribute('aria-label'));
                        }
                    }
                    
                    // Try common Google consent button patterns
                    var commonPatterns = [
                        'button[jsname]',  // Google often uses jsname attributes
                        'div[jsname][role="button"]',
                        'button[data-ved]',  // Google tracking attributes
                        'div[data-ved][role="button"]'
                    ];
                    
                    for (var p = 0; p < commonPatterns.length; p++) {
                        var patternButtons = document.querySelectorAll(commonPatterns[p]);
                        for (var q = 0; q < patternButtons.length; q++) {
                            var pBtn = patternButtons[q];
                            var pText = (pBtn.textContent || pBtn.innerText || '').toLowerCase();
                            if (pText.includes('accept') || pText.includes('accepteren') || pText.includes('alles')) {
                                pBtn.click();
                                return 'Clicked Google pattern button: ' + pText;
                            }
                        }
                    }
                    
                    return 'No accept button found';
                    """
                )
                
                Communicator.show_message(f"[DEBUG] Consent handling result: {consent_handled}")
                
                # If no button was found, try a more aggressive approach
                if "No accept button found" in consent_handled:
                    Communicator.show_message("[DEBUG] Trying alternative consent handling...")
                    
                    # Try to find and analyze all clickable elements
                    alternative_result = self.driver.execute_script(
                        """
                        // Log all buttons for debugging
                        var allClickable = document.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"]');
                        var buttonInfo = [];
                        
                        for (var i = 0; i < Math.min(allClickable.length, 10); i++) {
                            var el = allClickable[i];
                            var info = {
                                tag: el.tagName,
                                text: (el.textContent || el.innerText || '').trim().substring(0, 50),
                                ariaLabel: el.getAttribute('aria-label') || '',
                                className: el.className || '',
                                id: el.id || ''
                            };
                            buttonInfo.push(info);
                            
                            // Try clicking anything that looks like accept
                            var combinedText = (info.text + ' ' + info.ariaLabel).toLowerCase();
                            if (combinedText.includes('accept') || combinedText.includes('alles') || 
                                combinedText.includes('akkoord') || combinedText.includes('toestemming')) {
                                el.click();
                                return 'Clicked alternative: ' + info.text + ' / ' + info.ariaLabel;
                            }
                        }
                        
                        return 'Found buttons: ' + JSON.stringify(buttonInfo);
                        """
                    )
                    
                    Communicator.show_message(f"[DEBUG] Alternative consent result: {alternative_result}")
                
                # Wait a moment for the redirect
                sleep(5)
                
                # Check if we're now on Google Maps
                new_url = self.driver.current_url
                new_title = self.driver.title
                
                Communicator.show_message(f"[DEBUG] After consent - URL: {new_url}")
                Communicator.show_message(f"[DEBUG] After consent - Title: {new_title}")
                
                if "google.com/maps" in new_url:
                    Communicator.show_message("[DEBUG] Successfully redirected to Google Maps!")
                else:
                    Communicator.show_message("[DEBUG] Still not on Google Maps, may need manual intervention")
                    
            else:
                Communicator.show_message("[DEBUG] No consent page detected, proceeding normally")
                
        except Exception as e:
            Communicator.show_message(f"[DEBUG] Error handling consent page: {str(e)}")

    def mainscraping(self):
        try:
            querywithplus = "+".join(self.searchquery.split())

            """
            link of page variable contains the link of page of google maps that user wants to scrape.
            We have make it by inserting search query in it
            """

            # Use URL parameters to bypass consent page on Railway
            link_of_page = f"https://www.google.com/maps/search/{querywithplus}/?hl=en&gl=US&consent=PENDING&continue=https://www.google.com/maps"

            # ==========================================

            Communicator.show_message(f"[DEBUG] Opening URL: {link_of_page}")
            self.openingurl(url=link_of_page)

            # Check if we're on a consent page and handle it
            self.handle_consent_page()

            Communicator.show_message("Working start...")
            Communicator.show_message("[DEBUG] About to start scrolling...")

            self.scroller.scroll()
            
            Communicator.show_message("[DEBUG] Scrolling completed")
            
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