"""
Web communicator for Flask interface - replaces the desktop GUI communicator
"""

class WebCommunicator:
    def __init__(self):
        self.messages = []
        self.is_processing = True
        self.output_format = "excel"  # Default format
        self.search_query = ""
        self.extracted_rows = []  # Store extracted business data
        self.current_progress = 0
        self.total_locations = 0  # Track total locations found during scrolling
        self.parsing_started = False
        
    def messageshowing(self, message):
        """Store messages for web interface"""
        print(f"[SCRAPER] {message}")  # Also print to console
        self.messages.append(message)
        
        # Update progress based on message content
        if "Wait checking for driver" in message:
            self.current_progress = 5
        elif "Opening browser" in message:
            self.current_progress = 10
        elif "Working start" in message:
            self.current_progress = 20
        elif "Starting scrolling" in message:
            self.current_progress = 30
        elif "Total locations scrolled" in message:
            # Extract number and calculate progress
            try:
                import re
                numbers = re.findall(r'\d+', message)
                if numbers:
                    count = int(numbers[-1])
                    self.total_locations = count  # Store total for parsing progress
                    # Progress from 30 to 60 based on scrolled locations
                    self.current_progress = min(30 + (count * 1), 60)
            except:
                pass
        elif "Scrolling is done" in message:
            self.current_progress = 65
        elif "Starting parsing" in message or "Now going to scrape each location" in message:
            self.parsing_started = True
            self.current_progress = 70
        elif "Saving the scraped data" in message:
            self.current_progress = 90
        elif "Scraped data successfully saved" in message or "Total records saved:" in message:
            self.current_progress = 100
        elif "Closing the driver" in message:
            self.current_progress = 100
        
    def add_extracted_row(self, business_data):
        """Add a newly extracted business row"""
        self.extracted_rows.append(business_data)
        
        # Update parsing progress based on extracted rows
        if self.parsing_started and self.total_locations > 0:
            extracted_count = len(self.extracted_rows)
            # Progress from 70 to 85 based on extraction progress
            parsing_progress = min(15 * (extracted_count / self.total_locations), 15)
            self.current_progress = 70 + parsing_progress
        
        # Format the data for display
        formatted_data = self.format_business_data(business_data)
        
        # Add to messages for real-time display
        self.messages.append(f"EXTRACTED_ROW:{formatted_data}")
        print(f"[EXTRACTED] {formatted_data}")
        
    def format_business_data(self, data):
        """Format business data for display"""
        try:
            # The parser uses capitalized keys
            name = data.get('Name', 'Unknown')
            phone = data.get('Phone', '[NOT FOUND]')
            website = data.get('Website', '[NOT FOUND]')
            email = data.get('Email', '[NOT FOUND]')
            address = data.get('Address', '[NOT FOUND]')
            rating = data.get('Rating', '[NOT FOUND]')
            category = data.get('Category', '[NOT FOUND]')
            business_status = data.get('Business Status', '[NOT FOUND]')
            
            return f"""
Extracted data for {name}:
  Category: {category}
  Name: {name}
  Phone: {phone}
  Website: {website}
  Email: {email}
  Business Status: {business_status}
  Address: {address}
  Rating: {rating}
--------------------------------------------------"""
        except:
            return f"Extracted business data: {str(data)[:100]}..."
        
    def end_processing(self):
        """End the processing"""
        self.is_processing = False
        self.current_progress = 100
        
    def get_latest_message(self):
        """Get the latest message"""
        if self.messages:
            return self.messages[-1]
        return "Initializing..."
        
    def get_all_messages(self):
        """Get all messages"""
        return self.messages
        
    def get_progress(self):
        """Get current progress percentage"""
        return self.current_progress
        
    def clear_messages(self):
        """Clear all messages"""
        self.messages = []
        self.extracted_rows = []
        self.current_progress = 0
        self.total_locations = 0
        self.parsing_started = False
        
    @property
    def outputFormatValue(self):
        """Return output format for compatibility"""
        return self.output_format
        
    def set_output_format(self, format_type):
        """Set output format"""
        self.output_format = format_type
        
    def set_search_query(self, query):
        """Set search query"""
        self.search_query = query