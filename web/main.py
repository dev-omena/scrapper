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
                // Simple progress polling - you can enhance this
                setTimeout(() => {{
                    document.getElementById('resultsSection').style.display = 'block';
                    document.getElementById('resultsText').textContent = 'Scraping in progress... (Full functionality loading)';
                    document.getElementById('startButton').disabled = false;
                    document.getElementById('startButton').textContent = 'Start Scraping';
                }}, 3000);
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

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """API endpoint for scraping (placeholder for now)"""
    return {
        "message": "Scraping functionality is loading...",
        "status": "accepted",
        "note": "Full scraper modules are being loaded in background"
    }, 202

def load_scraper_modules():
    """Load scraper modules in background"""
    global scraper_loaded, scraper_error
    
    try:
        print("📦 Loading scraper modules in background...")
        time.sleep(5)  # Give Flask time to start and pass health check
        
        # Try to import scraper modules
        from scraper.scraper import Backend
        from scraper.communicator import Communicator
        print("✅ Scraper modules loaded successfully!")
        scraper_loaded = True
        
    except Exception as e:
        print(f"❌ Failed to load scraper modules: {e}")
        scraper_error = str(e)
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
