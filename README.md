# Orizon- Google Maps Scraper

## Version: 3.2.0



## Features
- Designed to be highly user-friendly for **beginners**.
- User-friendly graphical interface for easy navigation and interaction. 😊
- Scrapes various data from Google Maps, such as:
  - **Category**
  - **Name**
  - **Phone Number**
  - **Google Maps URL**
  - **Website**
  - **Email**
  - **Address**
  - **Total Reviews**
  - **Rating**
  - **Business Status**
  - **Booking Links**
  - **Hours**
- Fast and efficient 🚀




## Note: 
**Our all scrapers are working, if you find any issue or bug please open an issue with the detail of issue. We will try to resolve it quickly for you.**

<img src="Readme assets/Orizongoogle maps scraper.jpg" alt="Orizonopen sourced google maps scraper">

Welcome to the OrizonGitHub Google Maps Scraper repository, an open-source GUI tool built in Python. This tool allows you to extract data from Google Maps using a user-friendly interface.
Documentation can be found at this [link](https://zubdata.com/docs/google-maps-scraper/getting-started/installation/) 🔗

## Sample Data
    {
        "Category":"Shopping mall",
        "Name":"Packages Mall",
        "Phone":"(042) 111 696 255",
        "Google Maps URL":"https:\/\/www.google.com\/maps\/place\/Packages+Mall\/data=!4m7!3m6!1s0x39190680e8f2d445:0x32ba63a1571efb2a!8m2!3d31.4715199!4d74.3555422!16s%2Fg%2F11gmxj94jy!19sChIJRdTy6IAGGTkRKvseV6FjujI?authuser=0&hl=en&rclk=1",
        "Website":"http:\/\/www.packagesmall.com\/",
        "email":"careers@packagesmall.com, info@packagesmall.com",
        "Business Status":"Open\u22c5 Closes 10\u202fpm",
        "Address":"Main Walton Rd, Shahrah-E-Roomi Nishtar Town, Lahore, Punjab 54750",
        "Total Reviews":"(67,295)",
        "Booking Links":null,
        "Rating":"4.6",
        "Hours":"Sunday11\u202fam\u201310\u202fpm\ue14dMonday11\u202fam\u201310\u202fpm\ue14dTuesday11\u202fam\u201310\u202fpm\ue14dWednesday11\u202fam\u201310\u202fpm\ue14dThursday11\u202fam\u201310\u202fpm\ue14dFriday11\u202fam\u201310\u202fpm\ue14dSaturday11\u202fam\u201310\u202fpm\ue14dSuggest new hours"
    }

## Getting Started

To get started with the Google Maps Scraper, follow these steps:

### 1. Clone the repository to your local machine:

   ```shell
   git clone https://github.com/Zubdata/Google-Maps-Scraper.git
   ```

### 2. Setup the Environment for Scraper

- For Windows, run:
  ```bash
  ./setup_win.cmd
   ```
- For Linux, run:
   ```
   ./setup_linux.sh
   ```

   It will auto install the dependencies

## 3. Install the Driver

   - If you already have a driver compatible with your Chrome browser, specify the driver path in `app/settings.py`.
   - If you don't have a driver, the scraper will automatically install it.
   - If the automatic installation fails, download the driver from the [Chrome Official Page](https://googlechromelabs.github.io/chrome-for-testing/#stable) and specify the driver path in `app/settings.py`. And then re-run the scraper.

### 3. Run the scraper:
   ```shell
   python app/run.py
   ```
