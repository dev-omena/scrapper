#!/usr/bin/env python3
"""
Railway startup script for Orizon Google Maps Scraper
This script ensures proper environment setup before starting the Flask app
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Set up environment variables for Railway deployment"""
    print("🚀 Setting up Railway environment...")
    
    # Set production environment
    os.environ['RAILWAY_ENVIRONMENT'] = '1'
    
    # Set Chrome paths for Railway/Nixpacks
    chrome_paths = [
        '/nix/store/*/bin/chromium',
        '/usr/bin/google-chrome',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser'
    ]
    
    chromedriver_paths = [
        '/nix/store/*/bin/chromedriver',
        '/usr/bin/chromedriver',
        '/usr/local/bin/chromedriver'
    ]
    
    # Find Chrome binary
    for path in chrome_paths:
        if os.path.exists(path) or '*' in path:
            os.environ['CHROME_BIN'] = path
            print(f"✅ Chrome binary set to: {path}")
            break
    
    # Find ChromeDriver
    for path in chromedriver_paths:
        if os.path.exists(path) or '*' in path:
            os.environ['CHROMEDRIVER_PATH'] = path
            print(f"✅ ChromeDriver set to: {path}")
            break
    
    # Set Python path
    app_dir = Path(__file__).parent.absolute()
    parent_dir = app_dir.parent
    
    python_path = f"{app_dir}:{parent_dir}/app"
    os.environ['PYTHONPATH'] = python_path
    print(f"✅ Python path set to: {python_path}")
    
    # Set port from Railway
    port = os.environ.get('PORT', '5000')
    print(f"✅ Port set to: {port}")

def start_app():
    """Start the Flask application with Gunicorn"""
    print("🚀 Starting Orizon Google Maps Scraper...")
    
    # Get port from environment
    port = os.environ.get('PORT', '5000')
    
    # Start with Gunicorn
    cmd = [
        'gunicorn',
        '--bind', f'0.0.0.0:{port}',
        '--timeout', '300',
        '--workers', '2',
        '--worker-class', 'sync',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        'app:app'
    ]
    
    print(f"🚀 Executing: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Shutting down...")
        sys.exit(0)

if __name__ == '__main__':
    setup_environment()
    start_app()
