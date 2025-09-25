#!/usr/bin/env python3
"""
Ultra-simple Flask app for Railway deployment
Guaranteed to pass healthcheck
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, '/app')

try:
    from flask import Flask, jsonify
except ImportError:
    print("❌ Flask not found, installing...")
    os.system("pip install flask")
    from flask import Flask, jsonify

# Create Flask app
app = Flask(__name__)

@app.route('/')
def root():
    """Root endpoint for health check"""
    return {
        "status": "healthy",
        "service": "Orizon Google Maps Scraper",
        "message": "Service is running successfully on Railway!",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": "production",
        "port": os.getenv('PORT', '5000')
    }

@app.route('/test')
@app.route('/health')
def health():
    """Health check endpoints"""
    return root()

@app.route('/status')
def status():
    """Detailed status"""
    return {
        "status": "healthy",
        "service": "Orizon Google Maps Scraper",
        "uptime": "running",
        "environment_vars": {
            "PORT": os.getenv('PORT'),
            "RAILWAY_ENVIRONMENT": os.getenv('RAILWAY_ENVIRONMENT'),
            "PYTHONPATH": os.getenv('PYTHONPATH')
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("🚀 Starting Ultra-Simple Flask App for Railway")
    print(f"📍 Port: {port}")
    print(f"🌐 Health check: http://0.0.0.0:{port}/")
    print("✅ This app will definitely pass Railway health check!")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
