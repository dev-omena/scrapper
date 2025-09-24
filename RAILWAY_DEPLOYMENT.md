# Railway Deployment Guide for Google Maps Scraper

This guide provides comprehensive instructions for deploying the Google Maps Scraper on Railway.app with proper Chrome driver support.

## 🚀 Quick Deployment

### 1. Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

Or manually:
1. Fork this repository
2. Connect your Railway account to GitHub
3. Create a new Railway project from your fork
4. Railway will automatically detect the configuration and deploy

### 2. Environment Variables

The following environment variables are automatically set via `railway.toml`:

```bash
PYTHONPATH=/app:/app/app
CHROME_BIN=/usr/bin/google-chrome
CHROMEDRIVER_PATH=/usr/bin/chromedriver
DISPLAY=:99
DEBIAN_FRONTEND=noninteractive
```

## 📁 Configuration Files

### `nixpacks.toml`
Configures the build environment and Chrome installation:

```toml
[phases.setup]
nixPkgs = ["python3", "python3Packages.pip", "chromium", "xorg.xvfb"]

[phases.install]
cmds = [
    "chmod +x ./build.sh",
    "./build.sh"
]

[phases.build]
cmds = [
    "python3 -m pip install -r requirements.txt"
]
```

**Note**: `python3-pip` is not needed as pip is automatically included with Python 3 in Nixpacks.

### `railway.toml`
Configures Railway deployment settings:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "chmod +x ./start.sh && ./start.sh"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[variables]
PYTHONPATH = "/app:/app/app"
CHROME_BIN = "/usr/bin/google-chrome"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
DISPLAY = ":99"
DEBIAN_FRONTEND = "noninteractive"
```

### `build.sh`
Installs Chrome and dependencies during build:

```bash
#!/bin/bash
set -e

echo "🔧 Installing Google Chrome for Railway deployment..."

# Update and install dependencies
apt-get update
apt-get install -y wget gnupg2 ca-certificates software-properties-common

# Add Google Chrome repository and install
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable xvfb

# Verify installation
google-chrome --version
which google-chrome

# Create symbolic links if needed
if [ ! -f /usr/bin/google-chrome ]; then
    ln -s /usr/bin/google-chrome-stable /usr/bin/google-chrome
fi

echo "🎉 Chrome installation completed successfully!"
```

### `start.sh`
Initializes the runtime environment:

```bash
#!/bin/bash
set -e

echo "🚀 Starting Google Maps Scraper on Railway..."

# Set environment variables
export DISPLAY=:99
export CHROME_BIN=/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/usr/bin/chromedriver
export PYTHONPATH=/app:/app/app

# Start Xvfb for headless display
echo "🖥️ Starting virtual display..."
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Wait for Xvfb to start
sleep 2

# Verify Chrome installation
echo "🔍 Verifying Chrome installation..."
if command -v google-chrome >/dev/null 2>&1; then
    echo "✅ Chrome found: $(google-chrome --version)"
else
    echo "❌ Chrome not found!"
    exit 1
fi

# Run the application
echo "🎯 Starting application..."
cd /app
python app/run.py
```

## 🔧 Chrome Driver Configuration

The scraper includes robust Chrome driver initialization with multiple fallback strategies:

### 1. Undetected Chrome Driver
- Primary method for anti-detection
- Uses environment variables for Chrome path
- Includes retry logic for binary location errors

### 2. Regular Chrome Driver
- Fallback when undetected Chrome fails
- Supports both webdriver-manager and system chromedriver
- Comprehensive Chrome path detection

### 3. Chrome Path Detection
The scraper automatically detects Chrome in these locations:
- `/usr/bin/google-chrome` (Railway default)
- `/usr/bin/google-chrome-stable`
- `/usr/bin/chromium`
- `/usr/bin/chromium-browser`
- Environment variable `CHROME_BIN`

## 🧪 Testing Deployment

### Local Testing
Run the Railway deployment test:

```bash
python test_railway_deployment.py
```

This tests:
- Environment variables
- Chrome installation
- Display setup (Xvfb)
- Python imports
- Scraper module import

### Railway Testing
After deployment, check the logs for:
- Chrome installation verification
- Xvfb startup
- Application startup
- Any error messages

## 🐛 Troubleshooting

### Common Issues

#### 1. Chrome Not Found
**Error**: `Chrome executable not found`

**Solution**:
- Verify `build.sh` executed successfully
- Check Railway build logs for Chrome installation
- Ensure `CHROME_BIN` environment variable is set

#### 2. Service Unexpectedly Exited
**Error**: `Service unexpectedly exited. Status code was: 127`

**Solution**:
- This usually means Chrome dependencies are missing
- Verify Xvfb is running: `pgrep Xvfb`
- Check that `DISPLAY=:99` is set
- Ensure all Chrome dependencies are installed

#### 3. Binary Location Must be a String
**Error**: `Binary Location Must be a String`

**Solution**:
- This is handled by the retry logic in the scraper
- The scraper will fall back to regular Chrome driver
- Ensure `CHROME_BIN` points to a valid executable

#### 4. Import Errors
**Error**: `ModuleNotFoundError: No module named 'scraper'`

**Solution**:
- Verify `PYTHONPATH` includes `/app` and `/app/app`
- Check that all Python dependencies are installed
- Ensure the application structure is correct

#### 2. Nixpacks Build Errors

**Error**: `undefined variable 'python3-pip'`
- **Solution**: Remove `python3-pip` from `nixPkgs` in `nixpacks.toml`
- **Reason**: `pip` is automatically included with Python 3 in Nixpacks

**Error**: `pip: command not found`
- **Solution**: Use `python3 -m pip` instead of `pip` in build commands
- **Reason**: In Nixpacks environment, pip should be invoked through Python module

**Error**: `No module named pip`
- **Solution**: Add `python3Packages.pip` to `nixPkgs` in `nixpacks.toml`
- **Reason**: Nixpacks Python 3 doesn't include pip by default
- Use only: `nixPkgs = ["python3", "chromium", "xorg.xvfb"]`

### Debug Commands

Add these to your Railway service for debugging:

```bash
# Check Chrome installation
google-chrome --version
which google-chrome

# Check environment variables
env | grep -E "(CHROME|DISPLAY|PYTHON)"

# Check running processes
ps aux | grep -E "(chrome|xvfb)"

# Test Chrome headless
google-chrome --headless --no-sandbox --disable-dev-shm-usage --version
```

## 📊 Performance Optimization

### Resource Limits
Railway provides:
- 512MB RAM (Hobby plan)
- 1GB RAM (Pro plan)
- Shared CPU

### Optimization Tips
1. **Headless Mode**: Always run Chrome in headless mode
2. **Memory Management**: Use `--disable-dev-shm-usage` flag
3. **Process Limits**: Limit concurrent scraping operations
4. **Timeout Settings**: Set appropriate timeouts for requests

### Chrome Options
The scraper uses these optimized Chrome options:

```python
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-plugins")
options.add_argument("--disable-images")
options.add_argument("--disable-javascript")
```

## 🔒 Security Considerations

1. **No Sandbox**: Required for Railway environment
2. **Environment Variables**: Sensitive data should use Railway's secret management
3. **Rate Limiting**: Implement rate limiting to avoid being blocked
4. **User Agents**: Rotate user agents for better anonymity

## 📈 Monitoring

### Health Checks
Railway automatically monitors the application via:
- Health check endpoint: `/`
- Timeout: 100 seconds
- Restart policy: ON_FAILURE
- Max retries: 3

### Logging
Monitor these log patterns:
- `✅ Chrome found:` - Successful Chrome detection
- `🖥️ Starting virtual display` - Xvfb initialization
- `🎯 Starting application` - App startup
- `❌` - Error indicators

## 🆘 Support

If you encounter issues:

1. Check Railway build and deployment logs
2. Run `test_railway_deployment.py` locally
3. Verify all configuration files are present
4. Check Chrome installation in Railway console
5. Review environment variables

For additional support, refer to:
- [Railway Documentation](https://docs.railway.app/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Chrome Driver Documentation](https://chromedriver.chromium.org/)

## 🎉 Success Indicators

Your deployment is successful when you see:
- ✅ All dependencies installed
- ✅ Chrome installation verified
- ✅ Xvfb running
- ✅ Application started
- ✅ Health check passing

The scraper is now ready to handle Google Maps scraping requests on Railway!