# 🚀 Deployment Guide - Orizon Multi-Purpose Scraper

## 🎯 Quick Deploy Options

### 🥇 Option 1: Railway.app (RECOMMENDED)

**Why Railway?**
- ✅ Perfect for Python + Selenium apps
- ✅ Built-in Chrome support
- ✅ Simple Git deployment
- ✅ Affordable ($5-20/month)
- ✅ Custom domains

**Steps:**

1. **Prepare Repository**
   ```bash
   cd d:\orizon\Google-Maps-Scraper
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Connect your GitHub account
   - Select "Google-Maps-Scraper" repository
   - Railway will auto-detect it's a Python app
   - Click "Deploy"

3. **Environment Variables** (Set in Railway dashboard)
   ```
   PYTHONPATH=/app:/app/app
   CHROME_BIN=/usr/bin/google-chrome
   CHROMEDRIVER_PATH=/usr/bin/chromedriver
   ```

4. **Custom Domain** (Optional)
   - In Railway dashboard: Settings → Domains
   - Add your custom domain (e.g., scraper.orizon.com)

---

### 🥈 Option 2: Render.com

**Steps:**

1. **Create render.yaml**
   ```bash
   # Already created in web/render.yaml
   ```

2. **Deploy to Render**
   - Go to [render.com](https://render.com)
   - Click "New Web Service"
   - Connect GitHub → Select repository
   - Build command: `pip install -r web/requirements-deploy.txt`
   - Start command: `cd web && gunicorn app:app --bind 0.0.0.0:$PORT`

---

### 🥉 Option 3: Heroku

**Steps:**

1. **Install Heroku CLI**
   ```bash
   # Download from heroku.com/cli
   ```

2. **Deploy**
   ```bash
   cd web
   heroku create orizon-scraper
   heroku buildpacks:add heroku/python
   heroku buildpacks:add https://github.com/heroku/heroku-buildpack-chromedriver
   heroku buildpacks:add https://github.com/heroku/heroku-buildpack-google-chrome
   git subtree push --prefix=web heroku main
   ```

---

### 🐳 Option 4: Docker (Any Cloud Provider)

**Steps:**

1. **Build Docker Image**
   ```bash
   cd web
   docker build -t orizon-scraper .
   docker run -p 5000:5000 orizon-scraper
   ```

2. **Deploy to Cloud**
   - **Google Cloud Run**: `gcloud run deploy`
   - **AWS ECS**: Use the Dockerfile
   - **Azure Container Instances**: `az container create`

---

## 🔧 Production Optimizations

### Performance Settings
```python
# Already configured in app.py
- gunicorn with 2 workers
- 300s timeout for long scraping jobs
- Health check endpoint (/test)
```

### Security Features
```python
# Recommended additions:
- API rate limiting
- Request authentication
- CORS restrictions
- Input validation
```

### Monitoring
```python
# Add to requirements-deploy.txt:
sentry-sdk[flask]==1.32.0

# Add to app.py:
import sentry_sdk
sentry_sdk.init(dsn="YOUR_SENTRY_DSN")
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Plan | Chrome Support | Custom Domain |
|----------|-----------|-----------|----------------|---------------|
| Railway | No | $5-20/mo | ✅ Excellent | ✅ Yes |
| Render | 750hrs/mo | $7/mo | ✅ Good | ✅ Yes |
| Heroku | No | $7/mo | ✅ With buildpacks | ✅ Yes |
| PythonAnywhere | Limited | $5/mo | ❌ Limited | ✅ Yes |

---

## 🎯 RECOMMENDED DEPLOYMENT STEPS

### 1. Railway Deployment (Easiest)

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy to Railway"
git push origin main

# 2. Deploy on Railway
# - Connect GitHub repo
# - Auto-deploys from main branch
# - Get URL: https://your-app.railway.app
```

### 2. Custom Domain Setup

```bash
# 1. In Railway Dashboard:
# Settings → Domains → Add Domain
# Point your domain to Railway

# 2. Update DNS:
# CNAME record: scraper.yourdomain.com → your-app.railway.app
```

### 3. Production URL

Your scraper will be live at:
- Railway: `https://your-app.railway.app`
- Custom: `https://scraper.yourdomain.com`

---

## 📋 Pre-Deployment Checklist

- ✅ All files in `web/` directory
- ✅ `requirements-deploy.txt` created
- ✅ `Procfile` configured
- ✅ `railway.toml` settings
- ✅ Environment variables set
- ✅ Repository pushed to GitHub
- ✅ Chrome/Selenium dependencies handled

**🚀 Ready to deploy! Choose Railway for the smoothest experience.**