#!/usr/bin/env python3
"""
Minimal Flask app for Railway deployment testing
This ensures the healthcheck passes before loading the full scraper
"""

import os
import sys
from datetime import datetime
from flask import Flask, jsonify

# Create minimal Flask app
app = Flask(__name__)

@app.route('/')
def health_check():
    """Simple health check that always works"""
    return {
        "status": "healthy",
        "service": "Orizon Google Maps Scraper",
        "timestamp": datetime.now().isoformat(),
        "environment": "production" if os.getenv('RAILWAY_ENVIRONMENT') else "development",
        "port": os.getenv('PORT', '5000')
    }

@app.route('/test')
def test():
    """Test endpoint"""
    return health_check()

@app.route('/health')
def health():
    """Health endpoint"""
    return health_check()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting minimal Flask app on port {port}")
    print(f"📍 Health check available at: http://0.0.0.0:{port}/")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
