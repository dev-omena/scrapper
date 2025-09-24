# Nixpacks Configuration Fix

## 🐛 Problem
Railway deployment was failing with the error:
```
error: undefined variable 'python3-pip'
at /app/.nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix:19:26:
```

## 🔍 Root Cause
The `nixpacks.toml` configuration included `python3-pip` in the `nixPkgs` array, but this is not a valid package name in the Nix package manager. In Nixpacks, pip is automatically included with Python 3.

## ✅ Solution

### Before (Broken):
```toml
[phases.setup]
nixPkgs = ["python3", "python3-pip", "chromium", "xorg.xvfb"]
```

### After (Fixed):
```toml
[phases.setup]
nixPkgs = ["python3", "chromium", "xorg.xvfb"]
```

## 🔧 **Solution Applied**

1. **Removed Invalid Package**: Deleted `python3-pip` from `nixPkgs` in `nixpacks.toml`
2. **Added Manual Pip Installation**: Install pip using `curl -sS https://bootstrap.pypa.io/get-pip.py | python3 - --break-system-packages` in build phase
3. **Updated Package List**: Now uses: `["python3", "curl", "chromium", "xorg.xvfb"]`
4. **Fixed Pip Command**: Changed `pip install` to `python3 -m pip install --break-system-packages` in build phase
5. **Added System Override**: Used `--break-system-packages` flag to bypass externally managed environment restrictions
6. **Enhanced Build Script**: Improved Chrome/Chromium detection and installation
7. **Optimized Start Script**: Better runtime environment configuration
8. **Fixed Healthcheck Issue**: Updated start script to run web application instead of desktop GUI

## 🔧 Additional Improvements

### Enhanced Build Script
Updated `build.sh` to handle both Chromium (from Nixpacks) and Google Chrome installations:

```bash
# Check if chromium is available (from Nixpacks)
if command -v chromium >/dev/null 2>&1; then
    echo "✅ Chromium found via Nixpacks: $(chromium --version)"
    
    # Create symbolic links for compatibility
    if [ ! -f /usr/bin/google-chrome ]; then
        ln -sf $(which chromium) /usr/bin/google-chrome
    fi
    if [ ! -f /usr/bin/google-chrome-stable ]; then
        ln -sf $(which chromium) /usr/bin/google-chrome-stable
    fi
    
    echo "✅ Chrome symbolic links created"
else
    # Fallback to installing Google Chrome stable
    # ... (existing installation logic)
fi
```

### Enhanced Start Script
Updated `start.sh` to detect and handle both Chrome installations:

```bash
# Detect Chrome installation
if command -v google-chrome >/dev/null 2>&1; then
    export CHROME_BIN=/usr/bin/google-chrome
elif command -v chromium >/dev/null 2>&1; then
    export CHROME_BIN=$(which chromium)
    # Create symbolic link if it doesn't exist
    if [ ! -f /usr/bin/google-chrome ]; then
        ln -sf $(which chromium) /usr/bin/google-chrome
    fi
    export CHROME_BIN=/usr/bin/google-chrome
else
    echo "❌ No Chrome or Chromium found!"
    exit 1
fi
```

## 🧪 Testing
Created `test_nixpacks.py` to verify:
- Nixpacks packages are installed correctly
- Chrome/Chromium is available
- Symbolic links are created properly
- Environment variables are set

## 📊 Results
- ✅ Nixpacks build now succeeds
- ✅ Chrome/Chromium detection works
- ✅ Symbolic links provide compatibility
- ✅ All existing tests still pass

## 🚀 Healthcheck Fix

### Problem
After resolving the pip installation issues, the application was building successfully but failing health checks:
```
Healthcheck failed! 1/1 replicas never became healthy!
```

### Root Cause
The `start.sh` script was running the desktop GUI application (`app/run.py`) instead of the web application (`web/app.py`). Railway expects a web service that responds to HTTP requests, not a Tkinter GUI application.

### Solution
Updated `start.sh` to:
1. Set `RAILWAY_ENVIRONMENT=true` environment variable
2. Run `python web/app.py` instead of `python app/run.py`
3. The web application automatically detects Railway environment and binds to `0.0.0.0` with the correct PORT

### Fixed start.sh:
```bash
# Set environment variables
export DISPLAY=:99
export PYTHONPATH=/app:/app/app
export RAILWAY_ENVIRONMENT=true

# Run the web application
echo "🎯 Starting web application..."
cd /app
python web/app.py
```

## 🔧 ChromeDriver Fix

### Problem
After resolving the healthcheck issues, the web application was starting successfully but scraping was failing with ChromeDriver errors:
```
Service unexpectedly exited. Status code was: 127
```

### Root Cause
- Status code 127 indicates "command not found" or "exec format error"
- Runtime-downloaded ChromeDriver binaries were incompatible with Railway's Linux container architecture
- The scraper was attempting to download ChromeDriver at runtime using webdriver-manager, but these binaries didn't match the container environment

### Solution
1. **Updated build.sh** to install ChromeDriver during the build phase:
   - Detects the installed Chrome version
   - Downloads the matching ChromeDriver version for Linux 64-bit
   - Installs ChromeDriver to `/usr/bin/chromedriver` with proper permissions

2. **Updated start.sh** to set the ChromeDriver path:
   ```bash
   export CHROMEDRIVER_PATH=/usr/bin/chromedriver
   ```

3. **Updated scraper code** to prioritize system-installed ChromeDriver:
   - Check `CHROMEDRIVER_PATH` environment variable first
   - Fall back to common system paths (`/usr/bin/chromedriver`, `/usr/local/bin/chromedriver`)
   - Only use webdriver-manager as a last resort

### Fixed build.sh ChromeDriver installation:
```bash
# Install ChromeDriver
echo "📦 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+')
CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d. -f1)

# For Chrome 115+, use Chrome for Testing JSON API
if [ "$CHROME_MAJOR_VERSION" -ge 115 ]; then
    echo "🔧 Using Chrome for Testing API for Chrome $CHROME_MAJOR_VERSION..."
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json" | \
        grep -o "\"$CHROME_MAJOR_VERSION\":{[^}]*\"version\":\"[^\"]*\"" | \
        grep -o "\"version\":\"[^\"]*\"" | cut -d'"' -f4)
    
    wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"
    unzip /tmp/chromedriver.zip -d /tmp/
    mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver
else
    # For Chrome 114 and older, use legacy API
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR_VERSION}")
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
    unzip /tmp/chromedriver.zip -d /tmp/
    mv /tmp/chromedriver /usr/bin/chromedriver
fi

chmod +x /usr/bin/chromedriver
echo "✅ ChromeDriver installed: $(/usr/bin/chromedriver --version)"
```

## 🚀 Deployment Impact
This comprehensive fix ensures that:
1. Railway can build the application successfully
2. Chrome is available regardless of installation method (Chromium via Nixpacks or Google Chrome via apt)
3. **ChromeDriver is properly installed** during the build phase with correct architecture compatibility
4. The scraper works with both Chrome variants and uses system-installed ChromeDriver
5. Environment variables are properly configured
6. **Health checks pass** - The web application responds to HTTP requests on the correct port
7. **Service starts successfully** - Railway can properly monitor and manage the application
8. **Scraping functionality works** - ChromeDriver initializes correctly and can perform web scraping

The Google Maps Scraper is now fully compatible with Railway's Nixpacks build system! 🎉