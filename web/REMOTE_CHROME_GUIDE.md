# 🌐 Remote Chrome Setup for Railway

Use your local Chrome browser with Railway scraper to bypass all container Chrome issues!

## 🚀 Quick Setup

### Step 1: Start Remote Chrome Locally

```bash
cd web
python setup_remote_chrome.py
```

This will:
- ✅ Find your Chrome installation
- ✅ Start Chrome with remote debugging enabled
- ✅ Test the connection
- ✅ Show you the next steps

### Step 2: Expose Chrome to Internet

**Option A: Using ngrok (Recommended)**
```bash
# Install ngrok from https://ngrok.com/download
ngrok http 9222
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

**Option B: Using localtunnel**
```bash
npm install -g localtunnel
lt --port 9222
```

### Step 3: Configure Railway

In your Railway project, add environment variable:
```
REMOTE_CHROME_URL = https://abc123.ngrok.io
```

### Step 4: Test Scraping

1. ✅ Keep Chrome running locally
2. ✅ Keep ngrok/tunnel running  
3. ✅ Deploy to Railway
4. ✅ Start scraping - it will use your local Chrome!

## 🎯 Benefits

- ✅ **No Chrome container issues** - Uses your working local Chrome
- ✅ **Full debugging** - You can see what's happening in your Chrome
- ✅ **Better performance** - Local Chrome is faster than container Chrome
- ✅ **Easy troubleshooting** - Visual feedback in your browser

## 🔧 Troubleshooting

**Chrome not starting?**
- Make sure no other Chrome instances are running on port 9222
- Try closing all Chrome windows first

**Railway can't connect?**
- Check if ngrok URL is correct in Railway environment variables
- Make sure your firewall allows connections
- Test the ngrok URL in your browser: `https://abc123.ngrok.io/json/version`

**Scraping still fails?**
- Check Railway logs for connection messages
- Make sure REMOTE_CHROME_URL is set correctly
- Verify Chrome is still running locally

## 🛡️ Security Notes

- ⚠️ Only use this for testing/development
- ⚠️ Don't leave Chrome exposed permanently
- ⚠️ Stop ngrok when not using the scraper
- ⚠️ Use HTTPS ngrok URLs when possible

## 🎉 Success Indicators

When working correctly, Railway logs will show:
```
🔗 Using Remote Chrome at: https://abc123.ngrok.io
✅ Remote Chrome connection configured
[DEBUG] Successfully connected to remote Chrome!
```

Your local Chrome will show the scraping activity in real-time!
