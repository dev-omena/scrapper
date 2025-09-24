from bs4 import BeautifulSoup
try:
    from scraper.error_codes import ERROR_CODES
    from scraper.communicator import Communicator
    from scraper.datasaver import DataSaver
    from scraper.base import Base
    from scraper.common import Common
except ImportError:
    from app.scraper.error_codes import ERROR_CODES
    from app.scraper.communicator import Communicator
    from app.scraper.datasaver import DataSaver
    from app.scraper.base import Base
    from app.scraper.common import Common
import requests
import re


class Parser(Base):

    def __init__(self, driver) -> None:
        self.driver = driver
        self.finalData = []
        self.comparing_tool_tips = {
            "location": "Copy address",
            "phone": "Copy phone number", 
            "website": "Open website",
            "booking": "Open booking link",
        }
        
        # Multilingual keywords for better extraction
        self.multilingual_keywords = {
            "open": ["open", "مفتوح", "فتح", "مفتوحة"],
            "closed": ["closed", "مغلق", "مغلقة", "إغلاق"],
            "hours": ["hours", "ساعات", "مواعيد", "العمل"],
            "phone": ["phone", "tel", "telephone", "هاتف", "تلفون"],
            "email": ["email", "mail", "إيميل", "بريد"],
            "website": ["website", "web", "موقع", "الموقع"],
            "address": ["address", "location", "عنوان", "موقع"],
        }

    def is_valid_phone(self, phone_text):
        """Validate if a text string is a valid phone number"""
        if not phone_text:
            return False
            
        import re
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_text)
        
        # Remove leading + for length check
        digits_only = cleaned.replace('+', '')
        
        # Basic validation rules
        if len(digits_only) < 8 or len(digits_only) > 15:
            return False
            
        # Check if it's likely a postal code (all same digits, sequential, etc.)
        if len(set(digits_only)) == 1:  # All same digit
            return False
            
        # Check for common non-phone patterns
        non_phone_patterns = [
            r'^11111+$',  # Repeated 1s (postal codes)
            r'^12345+$',  # Sequential numbers
            r'^\d{4,5}$'  # Short numbers (likely postal codes)
        ]
        
        for pattern in non_phone_patterns:
            if re.match(pattern, digits_only):
                return False
                
        return True

    def init_data_saver(self):
        self.data_saver = DataSaver()

    def parse(self):
        """Our function to parse the html"""

        """This block will get element details sheet of a business. 
        Details sheet means that business details card when you click on a business in 
        serach results in google maps"""

        infoSheet = self.driver.execute_script(
            """return document.querySelector("[role='main']")"""
        )
        try:
            # Initialize data points
            (
                rating,
                totalReviews,
                address,
                websiteUrl,
                email,
                phone,
                hours,
                category,
                gmapsUrl,
                bookingLink,
                businessStatus,
            ) = (None, None, None, None, None, None, None, None, None, None, None)

            html = infoSheet.get_attribute("outerHTML")
            soup = BeautifulSoup(html, "html.parser")

            # Extract rating
            try:
                # Try multiple selectors for rating
                rating_selectors = [
                    "span.ceNzKf",
                    "[data-value]",
                    "span[aria-label*='stars']",
                    "div.F7nice span:first-child",
                    "span.yi40Hd.YrbPuc"
                ]
                
                for selector in rating_selectors:
                    rating_element = soup.select_one(selector)
                    if rating_element:
                        if rating_element.get("aria-label"):
                            rating = rating_element.get("aria-label")
                            rating = rating.replace("stars", "").replace("نجمة", "").strip()
                        elif rating_element.get("data-value"):
                            rating = rating_element.get("data-value")
                        else:
                            rating = rating_element.get_text(strip=True)
                        break
                        
                if not rating:
                    # Try extracting from review section
                    review_section = soup.find("div", class_="F7nice")
                    if review_section:
                        rating_text = review_section.get_text()
                        import re
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            rating = rating_match.group(1)
            except:
                rating = None

            # Extract total reviews
            try:
                # Try multiple selectors for total reviews
                review_selectors = [
                    "div.F7nice",
                    "button[data-value]", 
                    "span.RDApEe.YrbPuc",
                    "button.HHrUdb.fontTitleSmall.rqjGif"
                ]
                
                for selector in review_selectors:
                    review_element = soup.select_one(selector)
                    if review_element:
                        if selector == "div.F7nice":
                            children = list(review_element.children)
                            if len(children) > 1:
                                totalReviews = children[1].get_text(strip=True)
                                # Clean up the review text
                                totalReviews = totalReviews.replace("(", "").replace(")", "").replace("reviews", "").replace("review", "").strip()
                            else:
                                totalReviews = review_element.get_text(strip=True)
                        else:
                            totalReviews = review_element.get_text(strip=True)
                            totalReviews = totalReviews.replace("(", "").replace(")", "").replace("reviews", "").replace("review", "").strip()
                        
                        # Extract just the number
                        import re
                        review_match = re.search(r'\((\d+[\d,]*)\)', totalReviews) or re.search(r'(\d+[\d,]*)', totalReviews)
                        if review_match:
                            totalReviews = review_match.group(1)
                        break
            except:
                totalReviews = None

            # Extract name
            try:
                # Try multiple selectors for business name
                name_selectors = [
                    ".tAiQdd h1.DUwDvf",
                    "h1.DUwDvf.lfPIob",
                    "h1.x3AX1-LfntMc-header-title-title",
                    "h1[data-attrid='title']",
                    ".SPZz6b h1",
                    "h1.qrShPb.kno-ecr-pt.PZPZlf.q8U8x.VcaUQd.rSWAr",
                    ".tAiQdd .DUwDvf"
                ]
                
                for selector in name_selectors:
                    name_element = soup.select_one(selector)
                    if name_element:
                        name = name_element.get_text(strip=True)
                        if name:  # Make sure we got actual text
                            break
                            
                if not name:
                    # Fallback: try to find the main heading
                    h1_elements = soup.find_all("h1")
                    for h1 in h1_elements:
                        text = h1.get_text(strip=True)
                        if text and len(text) > 1:  # Make sure it's not just whitespace
                            name = text
                            break
            except:
                name = None

            # Extract address, website, phone, and appointment link
            # Try multiple approaches to find contact information
            allInfoBars = soup.find_all("button", class_="CsEnBe")
            
            # Alternative selectors if primary ones don't work
            if not allInfoBars:
                allInfoBars = soup.find_all("button", {"data-tooltip": True})
            if not allInfoBars:
                allInfoBars = soup.find_all("div", class_="rogA2c")
                
            for infoBar in allInfoBars:
                try:
                    data_tooltip = infoBar.get("data-tooltip")
                    text_element = infoBar.find("div", class_="rogA2c")
                    
                    if not text_element:
                        text_element = infoBar.find("div", class_="Io6YTe fontBodyMedium kR99db")
                    if not text_element:
                        text_element = infoBar
                        
                    if text_element:
                        text = text_element.get_text(strip=True)

                        if data_tooltip == self.comparing_tool_tips["location"] or "address" in str(data_tooltip).lower() or "Copy address" in str(data_tooltip):
                            address = text

                        elif data_tooltip == self.comparing_tool_tips["phone"] or "phone" in str(data_tooltip).lower() or "Copy phone" in str(data_tooltip):
                            # Validate that this is actually a phone number, not just any number
                            import re
                            # Check if it looks like a phone number (contains more than just 4-5 digits)
                            if re.search(r'\b\d{3,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}\b', text) or len(text.replace(' ', '').replace('-', '')) >= 8:
                                phone = text.strip()
                except:
                    continue
                    
            # Enhanced phone extraction methods
            if not phone:
                try:
                    # Method 1: Look for phone in specific Google Maps phone sections
                    phone_section_selectors = [
                        "button[data-item-id='phone:tel:']",
                        "a[href^='tel:']",
                        "button[aria-label*='Call']",
                        "div[class*='phone'] span",
                        "span[dir='ltr']"  # Phone numbers are often in LTR direction
                    ]
                    
                    for selector in phone_section_selectors:
                        phone_elements = soup.select(selector)
                        for element in phone_elements:
                            if selector == "a[href^='tel:']":
                                # Extract from tel: link
                                phone_text = element.get('href').replace('tel:', '')
                            else:
                                phone_text = element.get_text(strip=True)
                            
                            # Validate phone number
                            if phone_text and self.is_valid_phone(phone_text):
                                phone = phone_text
                                break
                        if phone:
                            break
                            
                    # Method 2: Look for phone numbers in structured format
                    if not phone:
                        # Look for phone numbers that are clearly formatted as phone numbers
                        all_text_elements = soup.find_all(text=True)
                        import re
                        
                        for text in all_text_elements:
                            text = text.strip()
                            # Egyptian phone number patterns
                            egyptian_patterns = [
                                r'\b01[0-9]{1}[\s\-]?[0-9]{3,4}[\s\-]?[0-9]{3,4}\b',  # Egyptian mobile: 010/011/012/015
                                r'\b0[2-9]{1}[\s\-]?[0-9]{3,4}[\s\-]?[0-9]{3,4}\b',   # Egyptian landline
                                r'\b\+20[\s\-]?1[0-9]{1}[\s\-]?[0-9]{3,4}[\s\-]?[0-9]{3,4}\b'  # International Egyptian
                            ]
                            
                            for pattern in egyptian_patterns:
                                match = re.search(pattern, text)
                                if match:
                                    potential_phone = match.group()
                                    # Make sure it's not part of an address
                                    parent_text = text.lower()
                                    if not any(addr_word in parent_text for addr_word in ['road', 'street', 'avenue', 'building', 'floor', 'apartment', 'حي', 'شارع', 'عمارة', 'طابق']):
                                        phone = potential_phone
                                        break
                            if phone:
                                break
                                
                except Exception as e:
                    print(f"Debug - Phone extraction error: {e}")
                    pass
                    
            # Additional address extraction
            if not address:
                try:
                    # Look for address in different locations
                    address_selectors = [
                        "button[data-item-id='address']",
                        "div[data-attrid='kc:/location/location:address']",
                        ".LrzXr",
                        "span.LrzXr.rdApif"
                    ]
                    
                    for selector in address_selectors:
                        addr_element = soup.select_one(selector)
                        if addr_element:
                            address = addr_element.get_text(strip=True)
                            if address:
                                break
                except:
                    pass

            # Extract website URL
            try:
                # Try multiple approaches for website
                website_selectors = [
                    "a[aria-label*='Website:']",
                    "a[data-tooltip='Open website']",
                    "a[href*='http']:not([href*='google.com']):not([href*='maps.google'])",
                    "button[data-item-id='authority'] a",
                    ".CsEnBe a[href^='http']"
                ]
                
                for selector in website_selectors:
                    websiteTag = soup.select_one(selector)
                    if websiteTag and websiteTag.get("href"):
                        websiteUrl = websiteTag.get("href")
                        # Make sure it's not a Google URL
                        if "google.com" not in websiteUrl and "maps.google" not in websiteUrl:
                            break
                            
                # Additional fallback method
                if not websiteUrl:
                    # Look for website in button tooltips
                    website_buttons = soup.find_all("button")
                    for btn in website_buttons:
                        tooltip = btn.get("data-tooltip", "")
                        if "website" in tooltip.lower():
                            link = btn.find("a")
                            if link and link.get("href"):
                                websiteUrl = link.get("href")
                                break

            except:
                websiteUrl = None
            # Extract Email
            try:
                # First try to find email directly in the Google Maps page
                page_text = soup.get_text()
                import re
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                direct_emails = re.findall(email_pattern, page_text)
                
                if direct_emails:
                    # Filter out common non-business emails
                    filtered_emails = [e for e in direct_emails if not any(domain in e.lower() for domain in ['noreply', 'no-reply', 'donotreply', 'admin', 'test', 'example'])]
                    if filtered_emails:
                        email = ", ".join(filtered_emails[:3])  # Limit to 3 emails
                
                # If no direct email found and we have a website, try scraping the website
                if not email and websiteUrl:
                    email = self.find_mail(websiteUrl)
                    
            except:
                email = None

            # Extract booking link
            try:
                # Try multiple approaches for booking links
                booking_selectors = [
                    "a[aria-label*='Open booking link']",
                    "a[aria-label*='booking']",
                    "button[data-tooltip*='booking'] a",
                    "a[href*='booking']",
                    "a[href*='reservation']",
                    "a[href*='opentable']",
                    "a[href*='resy.com']"
                ]
                
                for selector in booking_selectors:
                    bookingTag = soup.select_one(selector)
                    if bookingTag and bookingTag.get("href"):
                        bookingLink = bookingTag.get("href")
                        break
                        
                # Additional method: look in action buttons
                if not bookingLink:
                    action_buttons = soup.find_all("button", class_="CsEnBe")
                    for btn in action_buttons:
                        tooltip = btn.get("data-tooltip", "")
                        if "booking" in tooltip.lower():
                            link = btn.find("a")
                            if link and link.get("href"):
                                bookingLink = link.get("href")
                                break
            except:
                bookingLink = None

            # Extract hours of operation
            try:
                # Try multiple selectors for hours
                hours_selectors = [
                    "div.t39EBf",
                    "div[data-attrid='kc:/location/location:hours']",
                    "div.OqCZI.fontBodyMedium.WVXvdc",
                    "table.WgFkxc tr",
                    "div.lo7_ob",
                    "button[data-value*='hours'] .fontBodyMedium"
                ]
                
                for selector in hours_selectors:
                    hours_elements = soup.select(selector)
                    if hours_elements:
                        if selector == "table.WgFkxc tr":
                            # Handle table format
                            hours_list = []
                            for row in hours_elements:
                                day_hour = row.get_text(strip=True)
                                if day_hour:
                                    hours_list.append(day_hour)
                            hours = "; ".join(hours_list) if hours_list else None
                        else:
                            # Handle other formats
                            hours = hours_elements[0].get_text(strip=True)
                        if hours:
                            break
                            
                # Try alternative approach - look for "Open" or "Closed" status
                if not hours:
                    status_elements = soup.find_all(text=lambda text: text and any(word in text.lower() for word in ['open', 'closed', 'opens', 'closes']))
                    if status_elements:
                        hours = status_elements[0].strip()
                        
            except:
                hours = None

            # Extract category
            try:
                # Try multiple selectors for business category
                category_selectors = [
                    "button.DkEaL",
                    "button.DkEaL.fontBodyMedium.VuuXrf",
                    "span.YhemCb",
                    "div.LBgpqf",
                    "button[jsaction*='category']",
                    ".DkEaL .fontBodyMedium"
                ]
                
                for selector in category_selectors:
                    category_element = soup.select_one(selector)
                    if category_element:
                        category = category_element.get_text(strip=True)
                        if category:
                            break
                            
                # Fallback: look for category in meta information
                if not category:
                    meta_elements = soup.find_all("span", class_="YhemCb")
                    for element in meta_elements:
                        text = element.get_text(strip=True)
                        if text and not any(char.isdigit() for char in text):  # Avoid ratings/numbers
                            category = text
                            break
                            
            except:
                category = None

            # Extract Google Maps URL
            try:
                gmapsUrl = self.driver.current_url
            except:
                gmapsUrl = None

            # Extract business status
            try:
                # Try multiple approaches for business status
                status_selectors = [
                    "span.ZDu9vd span:first-child",
                    "div.WY6HQe span",
                    "span.WY6HQe",
                    "div.UYsEof span",
                    "span[class*='open'], span[class*='closed']"
                ]
                
                for selector in status_selectors:
                    status_element = soup.select_one(selector)
                    if status_element:
                        businessStatus = status_element.get_text(strip=True)
                        if businessStatus:
                            break
                            
                # Additional check for status in various locations
                if not businessStatus:
                    all_keywords = self.multilingual_keywords["open"] + self.multilingual_keywords["closed"]
                    for text in soup.stripped_strings:
                        text_lower = text.lower()
                        if any(keyword in text_lower for keyword in all_keywords):
                            businessStatus = text
                            break
                            
            except:
                businessStatus = None

            # Reorder data to match desired column structure
            data = {
                "Category": category,
                "Name": name,
                "Phone": phone,
                "Website": websiteUrl,
                "Email": email,
                "Business Status": businessStatus,
                "Address": address,
                "Total Reviews": totalReviews,
                "Booking Links": bookingLink,
                "Rating": rating,
                "Hours": hours,
                "Google Maps URL": gmapsUrl,
            }

            # Debug logging to help identify extraction issues
            print(f"Debug - Extracted data for {name}:")
            for key, value in data.items():
                if value:
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: [NOT FOUND]")
            
            # Special debug for phone extraction
            if not phone:
                print("  Phone Debug: Searching for phone patterns in page...")
                page_text = soup.get_text()
                import re
                all_numbers = re.findall(r'\b\d+[\d\s\-]*\d+\b', page_text)
                print(f"  All numbers found: {all_numbers[:10]}")  # Show first 10 numbers
                
            print("-" * 50)

            self.finalData.append(data)
            
            # Send extracted data to web interface for real-time display
            Communicator.add_extracted_row(data)

        except Exception as e:
            Communicator.show_error_message(
                f"Error occurred while parsing a location. Error is: {str(e)}",
                ERROR_CODES["ERR_WHILE_PARSING_DETAILS"],
            )

    # find email
    def find_mail(self, url):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            }
            source_code = requests.get(url, headers=headers, timeout=(10))
            curr = source_code.url

            original_curr = curr
            plain_text = source_code.text
            match = re.findall(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", plain_text
            )

            if not match:
                urls = [original_curr + "/contact/", original_curr + "/Contact/"]
                for cu in urls:
                    curr = cu
                    source_code = requests.get(url, headers=headers, timeout=(10))
                    plain_text = source_code.text
                    match = re.findall(
                        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", plain_text
                    )

                    if match:
                        break

            if not match:
                match = re.findall(
                    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", original_curr
                )

            if not match:

                if self.driver is None:
                    Communicator.show_message("Error: WebDriver failed to initialize.")
                    return ""

                self.driver.get(original_curr)
                plain_text = self.driver.page_source
                match = re.findall(
                    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", plain_text
                )

                if not match:
                    urls = [original_curr + "/contact/", original_curr + "/Contact/"]
                    for cu in urls:
                        self.driver.get(cu)
                        plain_text = self.driver.page_source
                        match = re.findall(
                            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                            plain_text,
                        )

                        if match:
                            break

                # self.driver.quit()

            match = [
                email
                for email in set(match)
                if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$", email)
            ]
            email = ", ".join(match)
            return email

        except Exception as e:
            error_msg = f"Error in find_mail: {e}"
            # Only show error if it's not a connection/network issue
            if not Communicator.suppress_error_message(error_msg):
                Communicator.show_message(error_msg)
        return ""

    def main(self, allResultsLinks):
        Communicator.show_message(
            "Scrolling is done. Now going to scrape each location"
        )
        try:
            for resultLink in allResultsLinks:
                if Common.close_thread_is_set():
                    self.driver.quit()
                    return

                self.openingurl(url=resultLink)
                self.parse()

        except Exception as e:
            Communicator.show_message(
                f"Error occurred while parsing the locations. Error: {str(e)}"
            )

        finally:
            self.init_data_saver()
            self.data_saver.save(datalist=self.finalData)
