

class Communicator:

    __frontend_object = None
    __backend_object = None

    @classmethod
    def show_message(cls, message):
        if cls.__frontend_object is None:
            raise AttributeError("frontend_module attribute of Communicator class is none")
        
        cls.__frontend_object.messageshowing(message)

    @classmethod
    def show_error_message(cls, message, error_code):
        if cls.__frontend_object is None:
            raise AttributeError("frontend_module attribute of Communicator class is none")
        
        message = f"{message} Error code is: {error_code}"
        
        cls.__frontend_object.messageshowing(message)

    @classmethod
    def add_extracted_row(cls, business_data):
        """Send extracted business data to frontend"""
        if cls.__frontend_object is None:
            return  # No frontend to send to
        
        # Check if frontend has the method
        if hasattr(cls.__frontend_object, 'add_extracted_row'):
            cls.__frontend_object.add_extracted_row(business_data)

    @classmethod
    def suppress_error_message(cls, message):
        """Suppress error messages that shouldn't be shown to users"""
        # Don't show connection errors or technical debug messages to users
        error_keywords = [
            'HTTPConnectionPool', 'Max retries exceeded', 'getaddrinfo failed',
            'NameResolutionError', 'Connection refused', 'Failed to resolve',
            'Error in find_mail', 'WebDriver failed', 'urllib3'
        ]
        
        for keyword in error_keywords:
            if keyword in message:
                # Just log to console, don't show to user
                print(f"[SUPPRESSED ERROR] {message}")
                return True
        return False

    

    @classmethod
    def set_frontend_object(cls, frontend_object):
        cls.__frontend_object = frontend_object

    @classmethod
    def end_processing(cls):
        cls.__frontend_object.end_processing()

    @classmethod
    def get_output_format(cls):
        return cls.__frontend_object.outputFormatValue
    
    @classmethod
    def set_backend_object(cls, backend_object):
        cls.__backend_object = backend_object
    
    @classmethod
    def get_search_query(cls):
        return cls.__backend_object.searchquery