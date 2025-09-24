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

## 🚀 Deployment Impact
This fix ensures that:
1. Railway can build the application successfully
2. Chrome is available regardless of installation method (Chromium via Nixpacks or Google Chrome via apt)
3. The scraper works with both Chrome variants
4. Environment variables are properly configured
5. **Health checks pass** - The web application responds to HTTP requests on the correct port
6. **Service starts successfully** - Railway can properly monitor and manage the application

The Google Maps Scraper is now fully compatible with Railway's Nixpacks build system! 🎉