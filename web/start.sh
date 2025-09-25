#!/bin/bash
echo "🚀 Starting Orizon Google Maps Scraper (Railway Deployment)"
echo "📍 Environment: Production"
echo "🐍 Python version: $(python3 --version)"
echo "📦 Starting ultra-simple Flask app..."

# Set environment variables
export RAILWAY_ENVIRONMENT=1
export PYTHONPATH="/app"

# Start the ultra-simple app that will definitely work
python3 main.py
