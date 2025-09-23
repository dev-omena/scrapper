# Orizon Google Maps Scraper - Web Interface

A simple, elegant web interface for the Google Maps scraper with Orizon branding.

## 🎨 Orizon Branding
- **Primary Color**: #272860 (Deep Navy Blue)
- **Secondary Color**: #f8c800 (Bright Yellow)
- **Logo**: Orizon full logo and favicon integrated

## ✨ Features

- **Same Functionality**: Identical to the desktop application, no features changed
- **Simple Interface**: Single page with clean, professional design
- **Real-time Progress**: Live progress tracking during scraping
- **File Downloads**: Download results in CSV and JSON formats
- **Responsive Design**: Works on desktop and mobile devices
- **Orizon Branding**: Full integration of Orizon visual identity

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Chrome browser

### Installation & Running

1. **Navigate to the web directory**:
   ```cmd
   cd web
   ```

2. **Run the startup script**:
   ```cmd
   start.cmd
   ```

3. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

### Manual Setup (if needed)

1. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

2. **Start the server**:
   ```cmd
   python app.py
   ```

## 📁 Files Structure

```
web/
├── index.html          # Main web interface with Orizon branding
├── app.py             # Flask backend server
├── requirements.txt   # Python dependencies
├── start.cmd         # Windows startup script
└── README.md         # This file
```

## 🔧 How to Use

1. **Open the web interface** at http://localhost:5000
2. **Enter your search query** (e.g., "restaurants in Cairo, Egypt")
3. **Set parameters**:
   - Total results to scrape
   - Language code (en, ar, fr, etc.)
   - Headless mode option
4. **Click "Start Scraping"**
5. **Monitor progress** in real-time
6. **Download results** when complete

## 📊 Data Extracted

The scraper extracts the same data as the desktop version:
- Business name
- Phone number (with enhanced extraction)
- Email address
- Website URL
- Physical address
- Rating and review count
- Business status
- Operating hours
- GPS coordinates

## 🎨 Visual Design

The web interface features:
- **Gradient background** using Orizon primary color (#272860)
- **Yellow accents** (#f8c800) for buttons and highlights
- **Glassmorphism design** with blur effects
- **Orizon logo** prominently displayed
- **Professional typography** with proper spacing
- **Smooth animations** and hover effects

## 🔗 API Endpoints

- `GET /` - Main web interface
- `POST /api/scrape` - Start scraping job
- `GET /api/progress` - Get scraping progress
- `GET /api/download/csv` - Download CSV file
- `GET /api/download/json` - Download JSON file

## 🛠️ Technical Details

- **Frontend**: Pure HTML, CSS, and JavaScript (no frameworks)
- **Backend**: Flask with CORS enabled
- **Scraping**: Uses existing scraper modules from the desktop app
- **Progress Tracking**: Real-time polling for updates
- **File Handling**: Automatic CSV and JSON generation

## 🎯 Key Differences from Desktop App

| Desktop App | Web Interface |
|-------------|---------------|
| tkinter GUI | Modern web interface |
| Local only | Accessible via browser |
| Manual file save | Automatic download links |
| No progress bar | Real-time progress tracking |
| Basic styling | Orizon branded design |

## 🔧 Customization

### Colors
The Orizon brand colors are defined in the CSS:
```css
--orizon-primary: #272860;
--orizon-secondary: #f8c800;
```

### Logo and Favicon
- Logo: `../Full-logo.png`
- Favicon: `../Fav-icon.png`

## 🌟 Benefits

- **Professional Appearance**: Matches Orizon brand identity
- **User-Friendly**: Simple, intuitive interface
- **No Installation**: Runs in any modern browser
- **Same Reliability**: Uses the proven desktop scraper logic
- **Easy Sharing**: Can be accessed by multiple users
- **Mobile Compatible**: Works on phones and tablets

## 🚀 Ready to Use!

Your Orizon Google Maps Scraper web interface is ready to use. Simply run `start.cmd` and begin scraping with the same reliable functionality in a beautiful, branded web interface.

---

**Built with ❤️ for Orizon** - Transforming business intelligence through elegant web solutions.