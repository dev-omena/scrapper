#!/bin/bash
echo "🚀 Starting Orizon Google Maps Scraper (Railway Deployment)"
echo "📍 Environment: Production"
echo "🐍 Python version: $(python3 --version)"
echo "📦 Starting Flask web server..."

# Set environment variables for Railway
export RAILWAY_ENVIRONMENT=1
export PYTHONPATH="/app"
export PORT=${PORT:-5000}

# Change to the web directory where our Flask app is located
cd /app

echo "📂 Current directory: $(pwd)"
echo "📋 Files in directory:"
ls -la

echo "🌐 Starting Flask app on port $PORT..."

# Start the ultra-simple Flask app
python3 main.py
