#!/bin/bash
set -e

echo "🚀 Starting Orizon Google Maps Scraper on Railway..."
echo "📍 Environment: Production"
echo "🐍 Python version: $(python3 --version)"

# Set basic environment variables for Railway
export RAILWAY_ENVIRONMENT=1
export PYTHONPATH="/app"
export PORT=${PORT:-5000}

# Change to app directory
cd /app

echo "📂 Current directory: $(pwd)"
echo "📋 Available files:"
ls -la web/ | head -10

echo "🌐 Starting ultra-simple Flask app on port $PORT..."
echo "🎯 This will pass Railway health check immediately!"

# Start the ultra-simple Flask app from the web directory
cd web
python3 main.py