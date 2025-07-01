# MagicBricks Web Scraper

A Python-based web scraper to extract residential property listings from MagicBricks.com across multiple Indian cities.

## Features

- Scrapes property details including BHK, area, furnishing, parking, bathrooms, price, and address
- Handles multiple cities (Bangalore, Pune, Mumbai, New Delhi, Chennai, Hyderabad)
- Implements anti-blocking measures:
  - Random delays between requests
  - CAPTCHA detection
  - Retry mechanism for failed requests
- Data cleaning and normalization:
  - Price conversion (Cr/Lac to numeric values)
  - Text normalization
  - Missing value handling
- Saves data to CSV with proper formatting

## Technologies Used

- Python 3
- BeautifulSoup4 (HTML parsing)
- Requests (HTTP requests)
- Regular expressions (data extraction)
- CSV module (data storage)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/magicbricks-scraper.git
   cd magicbricks-scraper
   ```
   or
   Download the file
2. Install the required packages:
   ```bash
   pip install requests beautifulsoup4 lxml
   ```
3. Run:
   ```bash
   python magicbricks_scraper.py
   ```
