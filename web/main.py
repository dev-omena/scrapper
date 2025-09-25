#!/usr/bin/env python3
"""
Railway-optimized Orizon Google Maps Scraper Web Interface
Full functionality with Railway-friendly startup
"""

import os
import sys
import threading
import time
from datetime import datetime

# Add paths for imports
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/app')

try:
    from flask import Flask, request, jsonify, Response
    from flask_cors import CORS
except ImportError:
    print("❌ Flask modules not found, installing...")
    os.system("pip install flask flask-cors")
    from flask import Flask, request, jsonify, Response
    from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

# Global state
is_production = bool(os.getenv('RAILWAY_ENVIRONMENT')) or bool(os.getenv('RAILWAY_PROJECT_ID'))
scraper_loaded = False
scraper_error = None

# Global scraping progress
scraping_progress = {
    'status': 'idle',
    'progress': 0,
    'message': 'Ready to start scraping',
    'results': None,
    'extracted_data': []
}

# Global web communicator instance
web_communicator = None

print(f"🚀 Starting Orizon Google Maps Scraper (Production: {is_production})")

@app.route('/')
def index():
    """Smart root route - serves web interface for browsers, JSON for health checks"""
    accept_header = request.headers.get('Accept', '')
    user_agent = request.headers.get('User-Agent', '').lower()
    
    # Health check response (for Railway, curl, etc.)
    if ('text/html' not in accept_header or 
        'curl' in user_agent or 
        'healthcheck' in user_agent or
        'railway' in user_agent or
        'bot' in user_agent):
        
        return {
            "status": "healthy",
            "service": "Orizon Google Maps Scraper",
            "message": "Service is running successfully on Railway!",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "environment": "production" if is_production else "development",
            "port": os.getenv('PORT', '5000'),
            "scraper_loaded": scraper_loaded
        }, 200
    
    # Web interface response (for browsers)
    try:
        # Try to serve the full HTML interface
        html_path = os.path.join(os.path.dirname(__file__), 'index.html')
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return Response(html_content, mimetype='text/html')
        else:
            # Fallback HTML interface
            return get_fallback_html()
    except Exception as e:
        print(f"Error serving HTML: {e}")
        return get_fallback_html()

def get_fallback_html():
    """Fallback HTML interface if index.html is not available"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Orizon Google Maps Scraper</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #272860 0%, #1a1b4b 100%);
                color: white; min-height: 100vh; padding: 20px;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .title {{ font-size: 2.5rem; color: #f8c800; margin-bottom: 10px; }}
            .subtitle {{ font-size: 1.2rem; color: #e0e0e0; }}
            .card {{ 
                background: rgba(255, 255, 255, 0.1); border-radius: 20px; 
                padding: 40px; backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3); margin-bottom: 30px;
            }}
            .form-group {{ margin-bottom: 25px; }}
            .form-label {{ 
                display: block; font-size: 1.1rem; font-weight: 600;
                color: #f8c800; margin-bottom: 8px;
            }}
            .form-input {{ 
                width: 100%; padding: 15px; font-size: 1rem;
                border: 2px solid rgba(248, 200, 0, 0.3); border-radius: 10px;
                background: rgba(255, 255, 255, 0.1); color: white;
            }}
            .form-input::placeholder {{ color: rgba(255, 255, 255, 0.6); }}
            .start-button {{ 
                width: 100%; padding: 18px; font-size: 1.2rem; font-weight: 700;
                background: linear-gradient(45deg, #f8c800, #ffd700); color: #272860;
                border: none; border-radius: 15px; cursor: pointer;
                text-transform: uppercase; letter-spacing: 1px;
            }}
            .status {{ padding: 20px; margin: 20px 0; border-radius: 10px; }}
            .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
            .info {{ background: #cce7ff; color: #004085; border: 1px solid #b6d7ff; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="title">🚀 Orizon Google Maps Scraper</h1>
                <p class="subtitle">Professional Business Data Extraction Platform</p>
            </div>

            <div class="card">
                <div class="status success">
                    <strong>✅ Service Status:</strong> Running successfully on Railway!<br>
                    <strong>🌐 Environment:</strong> {"Production" if is_production else "Development"}<br>
                    <strong>⏰ Started:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
                </div>

                <form id="scraperForm" onsubmit="startScraping(event)">
                    <div class="form-group">
                        <label class="form-label" for="search_query">Search Query</label>
                        <input type="text" id="search_query" name="search_query" class="form-input" 
                               placeholder="e.g., restaurants in Cairo, Egypt" required>
                    </div>

                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="headless" name="headless" checked>
                            Run in headless mode (recommended)
                        </label>
                    </div>

                    <button type="submit" class="start-button" id="startButton">
                        Start Scraping
                    </button>
                </form>

                <div id="progressSection" style="display: none; margin-top: 30px;">
                    <div class="status info">
                        <strong>🔄 Status:</strong> <span id="statusText">Initializing...</span>
                    </div>
                </div>

                <div id="resultsSection" style="display: none; margin-top: 30px;">
                    <div class="status success">
                        <strong>✅ Complete:</strong> <span id="resultsText">Scraping completed!</span>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function startScraping(event) {{
                event.preventDefault();
                
                const formData = new FormData(event.target);
                const data = {{
                    search_query: formData.get('search_query'),
                    headless: formData.has('headless')
                }};

                document.getElementById('progressSection').style.display = 'block';
                document.getElementById('startButton').disabled = true;
                document.getElementById('startButton').textContent = 'Starting...';
                document.getElementById('statusText').textContent = 'Starting scraper...';

                try {{
                    const response = await fetch('/api/scrape', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(data)
                    }});

                    if (response.ok) {{
                        document.getElementById('statusText').textContent = 'Scraper started successfully!';
                        pollProgress();
                    }} else {{
                        throw new Error('Failed to start scraping');
                    }}
                }} catch (error) {{
                    document.getElementById('statusText').textContent = 'Error: ' + error.message;
                    document.getElementById('startButton').disabled = false;
                    document.getElementById('startButton').textContent = 'Start Scraping';
                }}
            }}

            async function pollProgress() {{
                try {{
                    const response = await fetch('/api/progress');
                    const progress = await response.json();
                    
                    // Update status text
                    document.getElementById('statusText').textContent = progress.message || 'Processing...';
                    
                    // Check status
                    if (progress.status === 'completed') {{
                        document.getElementById('resultsSection').style.display = 'block';
                        document.getElementById('resultsText').textContent = `Scraping completed! Found ${{progress.extracted_data ? progress.extracted_data.length : 0}} businesses.`;
                        document.getElementById('startButton').disabled = false;
                        document.getElementById('startButton').textContent = 'Start Scraping';
                        
                        // Add download button
                        const downloadBtn = document.createElement('a');
                        downloadBtn.href = '/api/download/excel';
                        downloadBtn.textContent = '📊 Download Excel';
                        downloadBtn.style.cssText = 'display: inline-block; margin-top: 10px; padding: 10px 20px; background: #f8c800; color: #272860; text-decoration: none; border-radius: 5px; font-weight: bold;';
                        document.getElementById('resultsSection').appendChild(downloadBtn);
                        
                    }} else if (progress.status === 'error') {{
                        document.getElementById('statusText').textContent = progress.message || 'An error occurred';
                        document.getElementById('startButton').disabled = false;
                        document.getElementById('startButton').textContent = 'Start Scraping';
                    }} else {{
                        // Continue polling
                        setTimeout(pollProgress, 2000);
                    }}
                }} catch (error) {{
                    console.error('Error polling progress:', error);
                    setTimeout(pollProgress, 5000); // Retry after 5 seconds
                }}
            }}
        </script>
    </body>
    </html>
    """, 200

@app.route('/test')
@app.route('/health')
def health_check():
    """Dedicated health check endpoints"""
    return {
        "status": "healthy",
        "service": "Orizon Google Maps Scraper",
        "version": "2.0.0",
        "production": is_production,
        "scraper_loaded": scraper_loaded,
        "timestamp": datetime.now().isoformat(),
        "port": os.getenv('PORT', '5000')
    }, 200

@app.route('/api/status')
def api_status():
    """Get detailed scraper status"""
    global scraper_loaded, scraper_error
    return {
        "scraper_loaded": scraper_loaded,
        "scraper_error": scraper_error,
        "production": is_production,
        "timestamp": datetime.now().isoformat(),
        "remote_chrome_url": os.environ.get('REMOTE_CHROME_URL', 'Not set')
    }, 200

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """API endpoint for scraping"""
    global scraper_loaded, scraper_error
    
    if not scraper_loaded:
        error_msg = f"Scraper modules are still loading. Please try again in a few seconds."
        if scraper_error:
            error_msg += f" Error: {scraper_error}"
        
        return {
            "error": error_msg,
            "scraper_loaded": False,
            "status": "loading",
            "scraper_error": scraper_error
        }, 503
    
    try:
        data = request.get_json()
        search_query = data.get('search_query', '').strip()
        
        if not search_query:
            return {"error": "Search query is required"}, 400
        
        # Start scraping in background thread
        import threading
        
        def run_scraping():
            global scraping_progress, web_communicator
            
            try:
                scraping_progress['status'] = 'running'
                scraping_progress['message'] = 'Starting scraper...'
                scraping_progress['progress'] = 0
                
                from scraper.scraper import Backend
                from web_communicator import WebCommunicator
                from scraper.communicator import Communicator
                
                # Create web communicator
                web_communicator = WebCommunicator()
                web_communicator.set_search_query(search_query)
                web_communicator.set_output_format('excel')
                
                # Set the web communicator as the frontend object
                Communicator.set_frontend_object(web_communicator)
                
                scraping_progress['message'] = 'Initializing browser...'
                scraping_progress['progress'] = 10
                
                # Setup Chrome environment - use remote Chrome connection for Railway
                if is_production:
                    print("🌐 Setting up Remote Chrome connection for Railway...")
                    
                    # Check if user provided remote Chrome URL
                    remote_chrome_url = os.environ.get('REMOTE_CHROME_URL')
                    if remote_chrome_url:
                        print(f"🔗 Using Remote Chrome at: {remote_chrome_url}")
                        os.environ['REMOTE_CHROME_URL'] = remote_chrome_url
                        print("✅ Remote Chrome connection configured")
                    else:
                        print("⚠️ No REMOTE_CHROME_URL provided - falling back to local Railway Chrome")
                        # Set environment variables for the scraper
                        os.environ['CHROME_BIN'] = '/usr/bin/google-chrome'
                        os.environ['CHROMEDRIVER_PATH'] = '/usr/bin/chromedriver'
                        os.environ['DISPLAY'] = ':99'
                        print("🔧 Railway Chrome environment configured as fallback")
                
                # Initialize the backend
                backend = Backend(
                    searchquery=search_query,
                    outputformat='excel',
                    healdessmode=1  # Always headless in production
                )
                
                scraping_progress['message'] = 'Starting scraping process...'
                scraping_progress['progress'] = 20
                
                # Add timeout using threading Timer (works in background threads)
                import threading
                import time
                
                scraping_completed = threading.Event()
                scraping_error_occurred = False
                scraping_exception = None
                
                def scraping_with_timeout():
                    nonlocal scraping_error_occurred, scraping_exception
                    try:
                        # Run scraping
                        backend.mainscraping()
                        scraping_completed.set()
                    except Exception as e:
                        scraping_error_occurred = True
                        scraping_exception = e
                        scraping_completed.set()
                
                # Start scraping in a separate thread
                scraping_thread = threading.Thread(target=scraping_with_timeout, daemon=True)
                scraping_thread.start()
                
                # Wait for completion or timeout (5 minutes) with progress updates
                timeout_seconds = 300  # 5 minutes
                check_interval = 10   # Check every 10 seconds
                elapsed = 0
                
                while elapsed < timeout_seconds:
                    if scraping_completed.wait(timeout=check_interval):
                        if scraping_error_occurred:
                            raise scraping_exception
                        # Scraping completed successfully
                        break
                    
                    elapsed += check_interval
                    minutes_elapsed = elapsed // 60
                    seconds_elapsed = elapsed % 60
                    scraping_progress['message'] = f'Scraping in progress... ({minutes_elapsed}m {seconds_elapsed}s elapsed)'
                    scraping_progress['progress'] = min(90, 20 + (elapsed / timeout_seconds) * 70)  # Progress from 20% to 90%
                    print(f"⏰ Scraping progress: {elapsed}s elapsed")
                    
                else:
                    # Timeout occurred
                    scraping_progress['status'] = 'error'
                    scraping_progress['message'] = 'Scraping timed out after 5 minutes. This may be due to Google Maps loading issues in Railway.'
                    print("❌ Scraping timed out")
                    return
                
                # Get extracted data from multiple possible sources
                extracted_data = []
                
                # Try to get data from backend
                if hasattr(backend, 'finalData') and backend.finalData:
                    extracted_data = backend.finalData
                    print(f"[DEBUG] Got {len(extracted_data)} results from backend.finalData")
                
                # Try to get data from scroller/parser
                elif hasattr(backend, 'scroller') and hasattr(backend.scroller, 'parser') and hasattr(backend.scroller.parser, 'finalData'):
                    extracted_data = backend.scroller.parser.finalData
                    print(f"[DEBUG] Got {len(extracted_data)} results from scroller.parser.finalData")
                
                # Try web communicator as fallback
                elif web_communicator and hasattr(web_communicator, 'extracted_rows'):
                    extracted_data = web_communicator.extracted_rows
                    print(f"[DEBUG] Got {len(extracted_data)} results from web_communicator.extracted_rows")
                
                print(f"[DEBUG] Final extracted_data length: {len(extracted_data)}")
                if extracted_data:
                    print(f"[DEBUG] Sample data: {extracted_data[0] if extracted_data else 'None'}")
                
                scraping_progress['status'] = 'completed'
                scraping_progress['progress'] = 100
                scraping_progress['message'] = f'Scraping completed! Found {len(extracted_data)} businesses.'
                scraping_progress['extracted_data'] = extracted_data
                
                print(f"✅ Scraping completed for: {search_query} - Found {len(extracted_data)} results")
                
            except Exception as e:
                scraping_progress['status'] = 'error'
                scraping_progress['message'] = f'Error: {str(e)}'
                scraping_progress['progress'] = 0
                print(f"❌ Scraping error: {e}")
        
        # Start scraping thread
        scraping_thread = threading.Thread(target=run_scraping, daemon=True)
        scraping_thread.start()
        
        return {
            "message": "Scraping started successfully!",
            "search_query": search_query,
            "status": "started"
        }, 200
        
    except Exception as e:
        return {"error": f"Failed to start scraping: {str(e)}"}, 500

@app.route('/api/progress')
def api_progress():
    """Get scraping progress"""
    global scraping_progress, web_communicator
    
    try:
        if web_communicator:
            # Update progress from communicator
            scraping_progress['progress'] = web_communicator.get_progress()
            scraping_progress['message'] = web_communicator.get_latest_message()
            
            # Check if completed
            if web_communicator.get_progress() >= 100:
                scraping_progress['status'] = 'completed'
                scraping_progress['extracted_data'] = web_communicator.extracted_rows
        
        return jsonify(scraping_progress)
    except Exception as e:
        return {"error": f"Failed to get progress: {str(e)}"}, 500

@app.route('/api/download/excel')
def download_excel():
    """Download Excel file with scraped data"""
    try:
        import pandas as pd
        from io import BytesIO
        from flask import send_file
        import glob
        import os
        
        # Try to get data from multiple sources
        extracted_data = []
        
        # First try from scraping progress
        if scraping_progress.get('extracted_data'):
            extracted_data = scraping_progress.get('extracted_data', [])
            print(f"[DEBUG] Found {len(extracted_data)} records in scraping_progress")
        
        # Try from web communicator
        if not extracted_data and web_communicator and hasattr(web_communicator, 'extracted_rows'):
            extracted_data = web_communicator.extracted_rows or []
            print(f"[DEBUG] Found {len(extracted_data)} records in web_communicator")
        
        # Try to find saved Excel files in output directory
        if not extracted_data:
            try:
                # Look for Excel files in various locations
                search_paths = [
                    '/tmp/*GMS output*.xlsx',
                    '*GMS output*.xlsx', 
                    'output/*GMS output*.xlsx',
                    '../output/*GMS output*.xlsx'
                ]
                
                excel_files = []
                for path_pattern in search_paths:
                    excel_files.extend(glob.glob(path_pattern))
                
                if excel_files:
                    # Return the most recent Excel file
                    latest_file = max(excel_files, key=os.path.getctime)
                    print(f"[DEBUG] Found existing Excel file: {latest_file}")
                    
                    return send_file(
                        latest_file,
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True,
                        download_name=f'google_maps_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
                    )
            except Exception as file_error:
                print(f"[DEBUG] File search failed: {file_error}")
        
        if not extracted_data:
            return {"error": "No data available to download. Please run a scraping operation first."}, 404
        
        # Create Excel file from extracted data
        df = pd.DataFrame(extracted_data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Scraped Data', index=False)
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'google_maps_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
    except Exception as e:
        return {"error": f"Failed to generate Excel file: {str(e)}"}, 500

def setup_chrome_for_railway():
    """Setup Chrome environment for Railway container"""
    if is_production:
        print("🔧 Setting up Chrome for Railway container...")
        
        # Set Chrome binary and driver paths
        os.environ['CHROME_BIN'] = '/usr/bin/google-chrome'
        os.environ['CHROMEDRIVER_PATH'] = '/usr/bin/chromedriver'
        
        # Set display for headless mode
        os.environ['DISPLAY'] = ':99'
        
        # Chrome flags optimized for Railway containers
        chrome_flags = [
            '--headless=new',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-images',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--remote-debugging-port=9222',
            '--window-size=1920,1080',
            '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-background-networking'
        ]
        
        os.environ['CHROME_FLAGS'] = ' '.join(chrome_flags)
        print(f"✅ Chrome configured with {len(chrome_flags)} optimization flags")

def load_scraper_modules():
    """Load scraper modules in background"""
    global scraper_loaded, scraper_error
    
    try:
        print("📦 Loading scraper modules in background...")
        time.sleep(5)  # Give Flask time to start and pass health check
        
        # Setup Chrome for production environment
        if is_production:
            setup_chrome_for_railway()
        
        # Try to import scraper modules one by one for better error reporting
        print("📦 Importing Backend...")
        from scraper.scraper import Backend
        print("✅ Backend imported successfully")
        
        print("📦 Importing Communicator...")
        from scraper.communicator import Communicator
        print("✅ Communicator imported successfully")
        
        print("📦 Importing WebCommunicator...")
        from web_communicator import WebCommunicator
        print("✅ WebCommunicator imported successfully")
        
        print("✅ All scraper modules loaded successfully!")
        scraper_loaded = True
        scraper_error = None
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Failed to load scraper modules: {e}")
        print(f"❌ Full error details: {error_details}")
        scraper_error = f"{str(e)} | {error_details}"
        scraper_loaded = False

if __name__ == '__main__':
    # Start scraper loading in background (only in production)
    if is_production:
        loading_thread = threading.Thread(target=load_scraper_modules, daemon=True)
        loading_thread.start()
    
    # Start Flask app immediately
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌐 Starting Orizon Google Maps Scraper Web Interface")
    print(f"📍 URL: http://0.0.0.0:{port}")
    print(f"🎯 Health check: http://0.0.0.0:{port}/test")
    print("✅ Web interface ready!")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
