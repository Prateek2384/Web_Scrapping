import re
import os
import requests
from bs4 import BeautifulSoup
import csv
import time
import random

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9'
}
MAX_PAGES = 5
TIMEOUT = 30

CITIES = [
    "Bangalore",
    "Pune",
    "Mumbai",
    "New Delhi",
    "Chennai",
    "Hyderabad"
]

FIELDNAMES = [
    'bhk',
    'area',
    'furnishing',
    'car_parking',
    'bathroom',
    'price',
    'address'
]

def get_page(url, page_num=1):
    for attempt in range(3):
        try:
            params = {'page': page_num} if page_num > 1 else {}
            response = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            text = response.text.lower()
            if "captcha" in text or "access denied" in text:
                print(f"Blocking detected (attempt {attempt + 1}/3). Retrying...")
                time.sleep(random.uniform(10, 15))
                continue
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}/3 failed: {e}")
            time.sleep(random.uniform(5, 10))
    return None

def safe_extract(element, selector=None, attribute=None, default=None):
    try:
        if selector:
            found = element.select_one(selector)
            if not found:
                return default
            if attribute:
                return found.get(attribute, default)
            return found.get_text(strip=True)
        return element.get_text(strip=True) if element else default
    except Exception:
        return default

def parse_price(price_str):
    if not price_str:
        return None

    price_str = price_str.replace("₹", "").replace(",", "").strip()

    if "Cr" in price_str:
        number = re.search(r'([\d.]+)', price_str)
        if number:
            return int(float(number.group(1)) * 1e7)

    if "Lac" in price_str:
        number = re.search(r'([\d.]+)', price_str)
        if number:
            return int(float(number.group(1)) * 1e5)

    number = re.search(r'([\d.]+)', price_str)
    if number:
        return int(float(number.group(1)))

    return None

def extract_bhk_and_address(title):
    bhk = None
    address = None

    bhk_match = re.search(r'(\d+)\s*BHK', title, re.IGNORECASE)
    if bhk_match:
        bhk = bhk_match.group(1).strip()

    addr_match = re.search(r'\bin\s+(.+)', title, re.IGNORECASE)
    if addr_match:
        full_address = addr_match.group(1).strip()
        address_parts = [part.strip() for part in full_address.split(',')]
        city = address_parts[-1] if address_parts else full_address
        address = city

    return bhk, address

def parse_listing(card):
    data = {}

    # BHK and Address
    title_text = safe_extract(card, '.mb-srp__card--title')
    bhk, address = extract_bhk_and_address(title_text)
    if bhk:
        data['bhk'] = bhk
    if address:
        data['address'] = address

    # Price
    price_text = safe_extract(card, '.mb-srp__card__price--amount')
    if price_text:
        numeric_price = parse_price(price_text)
        if numeric_price:
            data['price'] = numeric_price

    # Area
    area = safe_extract(card, 'div[data-summary="carpet-area"] .mb-srp__card__summary--value')
    if not area:
        area = safe_extract(card, 'div[data-summary="super-area"] .mb-srp__card__summary--value')
    if area:
        data['area'] = area.replace('sqft', '').strip()

    # Furnishing
    data['furnishing'] = safe_extract(card, 'div[data-summary="furnishing"] .mb-srp__card__summary--value')

    # Car Parking
    car_parking = safe_extract(card, 'div[data-summary="parking"] .mb-srp__card__summary--value')
    if car_parking:
        data['car_parking'] = car_parking.replace('Covered', '').replace('Open', '').replace(',','').strip()

    # Bathroom
    data['bathroom'] = safe_extract(card, 'div[data-summary="bathroom"] .mb-srp__card__summary--value')

    return {k: v for k, v in data.items() if v}

def scrape_magicbricks(city):
    all_listings = []

    BASE_URL = (
        "https://www.magicbricks.com/property-for-sale/residential-real-estate"
        "?proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,"
        "Studio-Apartment,Residential-House,Villa"
        f"&cityName={city}"
    )

    for page_num in range(1, MAX_PAGES + 1):
        print(f"\nScraping {city} - page {page_num}...")
        html = get_page(BASE_URL, page_num)
        if not html:
            continue

        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.select('.mb-srp__card')

        if not cards:
            print(f"No listings found for {city}.")
            break

        page_count = 0
        for card in cards:
            try:
                listing = parse_listing(card)
                if listing:
                    all_listings.append(listing)
                    page_count += 1
            except Exception as e:
                print(f"Error parsing listing: {e}")
                continue

        print(f"{city} - Page {page_num}: Found {page_count} listings.")
        time.sleep(random.uniform(5, 8))

    return all_listings

def save_to_csv(data, filename='magicbricks.csv'):
    if not data:
        print("No data to save.")
        return

    file_exists = os.path.isfile(filename)

    try:
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if not file_exists:
                writer.writeheader()

            writer.writerows(data)
        print(f"\nAppended {len(data)} listings to {filename}")
    except Exception as e:
        print(f"Error saving CSV: {e}")

if __name__ == "__main__":
    print("Starting MagicBricks multi-city scraper...")
    start_time = time.time()
    if os.path.exists("magicbricks.csv"):
        os.remove("magicbricks.csv")
        print("Deleted old magicbricks.csv")

    total_listings = 0

    for city in CITIES:
        listings = scrape_magicbricks(city)
        save_to_csv(listings)
        total_listings += len(listings)

    print(f"\nDone! Total scraped listings: {total_listings}")
    print(f"Total execution time: {time.time() - start_time:.2f} seconds.")
