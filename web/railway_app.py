#!/usr/bin/env python3
"""
Railway-optimized Flask app with progressive loading
Starts fast for healthcheck, loads scraper modules after
"""

import os
import sys
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, Response

# Create Flask app immediately
app = Flask(__name__)

# Global state
scraper_loaded = False
scraper_error = None
is_production = bool(os.getenv('RAILWAY_ENVIRONMENT')) or bool(os.getenv('RAILWAY_PROJECT_ID'))

print(f"🚀 Starting Railway Flask app (Production: {is_production})")

@app.route('/')
def index():
    """Smart root route for health checks and web interface"""
    accept_header = request.headers.get('Accept', '')
    user_agent = request.headers.get('User-Agent', '').lower()
    
    # Health check response (for Railway and curl)
    if ('text/html' not in accept_header or 
        'curl' in user_agent or 
        'healthcheck' in user_agent or
        'railway' in user_agent):
        
        return {
            "status": "healthy",
            "service": "Orizon Google Maps Scraper",
            "version": "2.0.0",
            "production": is_production,
            "scraper_loaded": scraper_loaded,
            "timestamp": datetime.now().isoformat(),
            "port": os.getenv('PORT', '5000')
        }, 200
    
    # Web interface response
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Orizon Google Maps Scraper</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .status { padding: 20px; border-radius: 5px; margin: 20px 0; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
            .loading { background: #cce7ff; color: #004085; border: 1px solid #b6d7ff; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Orizon Google Maps Scraper</h1>
                <p>Professional Business Data Extraction</p>
            </div>
            
            <div id="status" class="status loading">
                <strong>⚡ Service Status:</strong> Starting up...
            </div>
            
            <div class="status success">
                <strong>✅ Health Check:</strong> Service is running successfully on Railway!
            </div>
            
            <p><strong>Available Endpoints:</strong></p>
            <ul>
                <li><a href="/test">Health Check</a> - Service status</li>
                <li><a href="/health">Alternative Health Check</a></li>
            </ul>
            
            <p><em>Full scraper interface will be available once all modules are loaded.</em></p>
        </div>
        
        <script>
            // Check scraper status
            fetch('/test')
                .then(r => r.json())
                .then(data => {
                    const status = document.getElementById('status');
                    if (data.scraper_loaded) {
                        status.className = 'status success';
                        status.innerHTML = '<strong>✅ Fully Ready:</strong> All scraper modules loaded successfully!';
                    } else {
                        status.className = 'status warning';
                        status.innerHTML = '<strong>⚡ Loading:</strong> Scraper modules are still loading...';
                    }
                })
                .catch(() => {
                    const status = document.getElementById('status');
                    status.className = 'status success';
                    status.innerHTML = '<strong>✅ Service Running:</strong> Basic health check passed!';
                });
        </script>
    </body>
    </html>
    """, 200

@app.route('/test')
@app.route('/health')
def health_check():
    """Dedicated health check endpoint"""
    return {
        "status": "healthy",
        "service": "Orizon Google Maps Scraper",
        "version": "2.0.0",
        "production": is_production,
        "scraper_loaded": scraper_loaded,
        "scraper_error": scraper_error,
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time(),
        "port": os.getenv('PORT', '5000'),
        "environment": {
            "RAILWAY_ENVIRONMENT": os.getenv('RAILWAY_ENVIRONMENT'),
            "RAILWAY_PROJECT_ID": os.getenv('RAILWAY_PROJECT_ID'),
            "CHROME_BIN": os.getenv('CHROME_BIN'),
            "CHROMEDRIVER_PATH": os.getenv('CHROMEDRIVER_PATH')
        }
    }, 200

def load_scraper_modules():
    """Load scraper modules in background after app starts"""
    global scraper_loaded, scraper_error
    
    try:
        print("📦 Loading scraper modules...")
        time.sleep(2)  # Give Flask time to start
        
        # Add paths for imports
        sys.path.append('/app')
        sys.path.append('/app/app')
        
        # Set Chrome paths for production
        if is_production:
            os.environ['CHROME_BIN'] = '/usr/bin/google-chrome'
            os.environ['CHROMEDRIVER_PATH'] = '/usr/bin/chromedriver'
        
        # Import scraper modules (this might take time)
        from scraper.scraper import Backend
        from scraper.communicator import Communicator
        print("✅ Scraper modules loaded successfully!")
        scraper_loaded = True
        
    except Exception as e:
        print(f"❌ Failed to load scraper modules: {e}")
        scraper_error = str(e)
        scraper_loaded = False

if __name__ == '__main__':
    # Start scraper loading in background
    if is_production:
        loading_thread = threading.Thread(target=load_scraper_modules, daemon=True)
        loading_thread.start()
    
    # Start Flask app immediately
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"🌐 Starting Flask server on {host}:{port}")
    print(f"📍 Health check: http://{host}:{port}/")
    
    app.run(
        host=host,
        port=port,
        debug=False,
        threaded=True
    )
