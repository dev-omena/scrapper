from flask import Flask, request, jsonify, send_file, Response, send_from_directory
from flask_cors import CORS
import sys
import os
import json
import threading
import time
import pandas as pd
from io import BytesIO
from datetime import datetime

# Add the app directory to the path to import scraper modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

# Fix distutils issue for Python 3.13+
try:
    import distutils
except ImportError:
    try:
        import setuptools
        # Create a fake distutils module to satisfy undetected_chromedriver
        import sys
        from types import ModuleType
        distutils_module = ModuleType('distutils')
        distutils_version = ModuleType('distutils.version')
        
        class LooseVersion:
            def __init__(self, version):
                self.version = str(version)
            def __str__(self):
                return self.version
            def __lt__(self, other):
                return True
            def __le__(self, other):
                return True
            def __gt__(self, other):
                return False
            def __ge__(self, other):
                return False
                
        distutils_version.LooseVersion = LooseVersion
        distutils_module.version = distutils_version
        sys.modules['distutils'] = distutils_module
        sys.modules['distutils.version'] = distutils_version
    except ImportError:
        pass

# Import the exact same scraper logic from desktop version
try:
    from scraper.scraper import Backend
    from scraper.communicator import Communicator
    from scraper.common import Common
    from scraper.email_scraper import EmailScraper
    try:
        from web.web_communicator import WebCommunicator
        from web.web_data_saver import WebDataSaver
        from web.email_web_communicator import email_web_comm
    except ModuleNotFoundError:
        # Fallback for local runs from web/ directory
        from web_communicator import WebCommunicator
        from web_data_saver import WebDataSaver
        from email_web_communicator import email_web_comm
    print("✅ Successfully imported desktop scraper modules and email scraper!")
except Exception as e:
    print(f"❌ Error importing scraper modules: {e}")
    print("🔧 Attempting to install missing dependencies...")
    # Try to install setuptools and retry
    os.system("pip install setuptools")
    try:
        from scraper.scraper import Backend
        from scraper.communicator import Communicator
        from scraper.common import Common
        from scraper.email_scraper import EmailScraper
        from web.web_communicator import WebCommunicator
        from web.web_data_saver import WebDataSaver
        from web.email_web_communicator import email_web_comm
        print("✅ Successfully imported after installing setuptools!")
    except Exception as e2:
        print(f"❌ Still failed: {e2}")
        print("Please run 'pip install setuptools' manually and restart.")
        sys.exit(1)

app = Flask(__name__)
CORS(app)

# Production configuration
if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RENDER'):
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
else:
    app.config['DEBUG'] = True

# Global variable to store scraping progress
scraping_progress = {
    'status': 'idle',
    'progress': 0,
    'message': '',
    'results': None,
    'extracted_rows': [],
    'live_messages': []
}

# Global web communicator instance
web_communicator = None

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files like images, CSS, JS"""
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), filename)

@app.route('/test')
def test():
    """Simple test route"""
    return "<h1>Flask App is Working!</h1><p>If you see this, the Flask server is running correctly.</p>"

@app.route('/')
def index():
    """Serve the main HTML page"""
    try:
        html_path = os.path.join(os.path.dirname(__file__), 'index.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Return HTML content with proper headers
        return Response(html_content, mimetype='text/html')
    except FileNotFoundError:
        return "Web interface not found. Please ensure index.html exists.", 404

@app.route('/api/scrape', methods=['POST'])
def scrape():
    """Handle scraping requests"""
    global scraping_progress
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('search_query'):
            return jsonify({'error': 'Search query is required'}), 400
        
        # Reset progress
        scraping_progress = {
            'status': 'running',
            'progress': 0,
            'message': 'Starting scraper...',
            'results': None
        }
        
        # Start scraping in a separate thread
        thread = threading.Thread(target=run_scraper, args=(data,))
        thread.daemon = True
        thread.start()
        
        return jsonify({'message': 'Scraping started', 'status': 'running'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/complete', methods=['GET', 'POST'])
def manual_complete():
    """Manually trigger completion status for debugging"""
    global scraping_progress, web_communicator
    
    if web_communicator and web_communicator.extracted_rows:
        scraping_progress['status'] = 'completed'
        scraping_progress['progress'] = 100
        scraping_progress['extracted_data'] = web_communicator.extracted_rows
        scraping_progress['message'] = f'Scraping completed! Found {len(web_communicator.extracted_rows)} businesses.'
        scraping_progress['results'] = {
            'total_results': len(web_communicator.extracted_rows),
            'excel_file': '/api/download/excel'
        }
        return jsonify({'success': True, 'message': 'Completion triggered manually'})
    else:
        return jsonify({'success': False, 'message': 'No extracted data found'})

@app.route('/debug')
def debug():
    """Debug route to check app status"""
    global scraping_progress
    return jsonify({
        'message': 'Debug endpoint working',
        'scraping_progress': scraping_progress,
        'web_communicator_status': web_communicator is not None
    })

@app.route('/api/progress')
def get_progress():
    """Get current scraping progress with real-time updates"""
    global scraping_progress, web_communicator
    
    try:
        if web_communicator:
            # Update progress from communicator
            scraping_progress['progress'] = web_communicator.get_progress()
            scraping_progress['message'] = web_communicator.get_latest_message()
            
            # Add processing phase indicator
            latest_message = web_communicator.get_latest_message()
            if "scrolling" in latest_message.lower():
                scraping_progress['phase'] = 'scrolling'
            elif "parsing" in latest_message.lower() or "scrape each location" in latest_message.lower():
                scraping_progress['phase'] = 'extracting'
            elif "saving" in latest_message.lower():
                scraping_progress['phase'] = 'saving'
            else:
                scraping_progress['phase'] = 'initializing'
            
            # Get live messages (including extracted rows)
            all_messages = web_communicator.get_all_messages()
            
            # Filter extracted row messages
            extracted_messages = [msg for msg in all_messages if msg.startswith('EXTRACTED_ROW:')]
            latest_extracted = extracted_messages  # Show ALL extracted businesses
            
            # Regular status messages
            status_messages = [msg for msg in all_messages if not msg.startswith('EXTRACTED_ROW:')]
            latest_status = status_messages[-1] if status_messages else scraping_progress['message']
            
            scraping_progress['live_messages'] = latest_extracted
            scraping_progress['message'] = latest_status
            
            # Add extraction progress stats
            scraping_progress['extracted_count'] = len(web_communicator.extracted_rows)
            scraping_progress['total_locations'] = web_communicator.total_locations
            
            # Check if scraping is completed
            if (web_communicator.get_progress() >= 100 or 
                "successfully saved" in latest_message.lower() or 
                "closing the driver" in latest_message.lower()):
                scraping_progress['status'] = 'completed'
                scraping_progress['progress'] = 100
            
        return jsonify(scraping_progress)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/excel')
def download_excel():
    """Generate and download Excel file with current scraped data"""
    try:
        global scraping_progress
        
        # Get the extracted data
        extracted_data = scraping_progress.get('extracted_data', [])
        
        if not extracted_data:
            return jsonify({'error': 'No data available to download. Please run a scraping operation first.'}), 404
        
        # Create Excel file in memory
        # Convert data to DataFrame
        df = pd.DataFrame(extracted_data)
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Scraped Data', index=False)
        
        output.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        search_query = scraping_progress.get('search_query', 'google_maps_data')
        # Clean search query for filename
        clean_query = "".join(c for c in search_query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_query = clean_query.replace(' ', '_')[:50]  # Limit length
        
        filename = f"Google_Maps_Scraper_{clean_query}_{timestamp}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Error generating Excel file: {str(e)}'}), 500

@app.route('/api/data')
def get_extracted_data():
    """Get the extracted data for display in table"""
    global scraping_progress
    
    try:
        if 'extracted_data' in scraping_progress:
            return jsonify({
                'success': True,
                'data': scraping_progress['extracted_data']
            })
        else:
            return jsonify({'error': 'No data available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_scraper(data):
    """Run the scraper in a separate thread using the exact same Backend class"""
    global scraping_progress, web_communicator
    
    try:
        # Create web communicator
        web_communicator = WebCommunicator()
        web_communicator.set_search_query(data['search_query'])
        web_communicator.set_output_format('excel')  # Changed to excel
        
        # Set the web communicator as the frontend object
        Communicator.set_frontend_object(web_communicator)
        
        # Reset progress
        scraping_progress = {
            'status': 'running',
            'progress': 0,
            'message': 'Initializing...',
            'results': None,
            'extracted_rows': [],
            'live_messages': []
        }
        
        # Use the exact same Backend class from desktop version
        search_query = data['search_query']
        output_format = 'excel'  # Changed to excel
        headless_mode = 1 if data.get('headless', True) else 0
        
        # Initialize the backend (same as desktop version)
        backend = Backend(
            searchquery=search_query,
            outputformat=output_format,
            healdessmode=headless_mode
        )
        
        # Run the main scraping method
        backend.mainscraping()
        
        # Get the extracted data from the backend
        extracted_data = getattr(backend, 'finalData', []) or web_communicator.extracted_rows
        
        scraping_progress['message'] = 'Scraping completed successfully!'
        scraping_progress['progress'] = 100
        scraping_progress['status'] = 'completed'
        
        # Store the data for display
        scraping_progress['extracted_data'] = extracted_data
        scraping_progress['search_query'] = search_query  # Store search query for filename
        
        # Mark as completed
        scraping_progress['status'] = 'completed'
        scraping_progress['progress'] = 100
        scraping_progress['message'] = f'Scraping completed successfully! Found {len(extracted_data)} businesses.'
        
        # Get the scraped data from the backend
        scraping_progress['results'] = {
            'total_results': len(extracted_data) if extracted_data else 0,
            'excel_file': '/api/download/excel'
        }
        
        # End processing in communicator
        if web_communicator:
            web_communicator.end_processing()
        
    except Exception as e:
        scraping_progress['status'] = 'error'
        scraping_progress['message'] = f'Error: {str(e)}'
        scraping_progress['progress'] = 0
        print(f"❌ Scraping error: {e}")


# Email Scraping Routes
@app.route('/api/email/scrape', methods=['POST'])
def start_email_scraping():
    """Start email scraping for a domain"""
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        include_patterns = data.get('include_patterns', True)
        
        if not domain:
            return jsonify({'error': 'Domain is required'}), 400
        
        # Clean domain (remove http/https and www)
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        
        if email_web_comm.is_running():
            return jsonify({'error': 'Email scraping is already running'}), 400
        
        # Start scraping in background thread
        def run_email_scraping():
            try:
                email_web_comm.reset()
                email_web_comm.start_extraction(domain)
                
                # Initialize email scraper
                scraper = EmailScraper(headless=True)
                
                # Step 1: Direct crawling
                email_web_comm.update_step("Crawling domain pages", 1, 
                                         "Scanning website pages for contact emails...")
                
                crawl_results = scraper.crawl_domain_pages(domain)
                for result in crawl_results:
                    email_web_comm.add_found_email(result)
                
                # Step 2: Enhanced Google searches
                email_web_comm.update_step("Enhanced Google searches", 2,
                                         "Searching Google for LinkedIn and directory listings...")
                
                search_results = scraper.search_google_for_emails(domain)
                for result in search_results:
                    email_web_comm.add_found_email(result)
                
                # Step 3: LinkedIn profiles
                email_web_comm.update_step("LinkedIn company profiles", 3,
                                         "Searching LinkedIn for company information...")
                
                linkedin_results = scraper.search_linkedin_profiles(domain)
                for result in linkedin_results:
                    email_web_comm.add_found_email(result)
                
                # Step 4: Business directories
                email_web_comm.update_step("Business directories", 4,
                                         "Checking Crunchbase, Apollo, and other directories...")
                
                directory_results = scraper.search_business_directories(domain)
                for result in directory_results:
                    email_web_comm.add_found_email(result)
                
                # Step 5: Social media
                email_web_comm.update_step("Social media platforms", 5,
                                         "Searching Twitter, Facebook, and other platforms...")
                
                social_results = scraper.search_social_media(domain)
                for result in social_results:
                    email_web_comm.add_found_email(result)
                
                # Step 6: Press and news
                email_web_comm.update_step("Press releases and news", 6,
                                         "Finding press contacts and media information...")
                
                press_results = scraper.search_press_and_news(domain)
                for result in press_results:
                    email_web_comm.add_found_email(result)
                
                # Step 7: Finalization and pattern generation (if needed)
                if include_patterns:
                    email_web_comm.update_step("Finalizing results", 7,
                                             "Processing results and adding patterns if needed...")
                else:
                    email_web_comm.update_step("Finalizing results", 7,
                                             "Processing and deduplicating results...")
                
                # Get full results with comprehensive extraction
                full_results = scraper.scrape_emails(domain, include_patterns)
                
                if full_results['success']:
                    email_web_comm.set_completed(full_results['results'], full_results['statistics'])
                else:
                    email_web_comm.set_error(full_results.get('error', 'Unknown error'))
                    
            except Exception as e:
                email_web_comm.set_error(str(e))
                print(f"Email scraping error: {e}")
        
        # Start background thread
        thread = threading.Thread(target=run_email_scraping)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Email scraping started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/email/progress', methods=['GET'])
def get_email_progress():
    """Get email scraping progress"""
    try:
        progress = email_web_comm.get_progress()
        return jsonify(progress)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/email/results', methods=['GET'])
def get_email_results():
    """Get email scraping results"""
    try:
        if not email_web_comm.is_completed():
            return jsonify({'error': 'Email scraping not completed yet'}), 400
        
        results = email_web_comm.get_results()
        
        # Convert results to dictionary format
        if results:
            from scraper.email_scraper import EmailScraper
            scraper = EmailScraper()
            export_data = scraper.export_to_dict(results)
        else:
            export_data = []
        
        return jsonify({
            'success': True,
            'total_results': len(results),
            'results': export_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/email/download/excel', methods=['GET'])
def download_email_excel():
    """Download email results as Excel file"""
    try:
        if not email_web_comm.is_completed():
            return jsonify({'error': 'Email scraping not completed yet'}), 400
        
        results = email_web_comm.get_results()
        
        if not results:
            return jsonify({'error': 'No email results to download'}), 400
        
        # Convert results to DataFrame
        from scraper.email_scraper import EmailScraper
        scraper = EmailScraper()
        export_data = scraper.export_to_dict(results)
        
        df = pd.DataFrame(export_data)
        
        # Create Excel file in memory
        excel_buffer = BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Email Results', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Email Results']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        excel_buffer.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = email_web_comm.get_progress().get('current_domain', 'unknown')
        filename = f"email_results_{domain}_{timestamp}.xlsx"
        
        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Starting Orizon Google Maps Scraper Web Server...")
    print("📍 Web Interface: http://localhost:5000")
    print("🔧 API Endpoint: http://localhost:5000/api/scrape")
    print("📊 Progress API: http://localhost:5000/api/progress")
    print("📧 Email Scraper: http://localhost:5000/api/email/scrape")
    print("💾 Download API: http://localhost:5000/api/download/<file_type>")
    print("✨ Orizon branding colors: #272860 (primary), #f8c800 (secondary)")
    
    # Get port from environment (for production deployment)
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0' if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RENDER') else '127.0.0.1'
    
    app.run(host=host, port=port, debug=app.config['DEBUG'])
    print("💾 Download API: http://localhost:5000/api/download/<file_type>")
    print("\n✨ Orizon branding colors: #272860 (primary), #f8c800 (secondary)")
    
    app.run(debug=False, host='0.0.0.0', port=5000)