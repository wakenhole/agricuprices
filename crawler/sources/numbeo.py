"""
Shared Numbeo scraper — absolute retail food prices by city.
https://www.numbeo.com/food-prices/in/CITY
No API key required.

Numbeo publishes ~15 food items per city. Items not covered by Numbeo
will retain their existing values in prices.json.
"""

import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Numbeo table row label (lowercase) → our item key
# Only items Numbeo reliably publishes
NUMBEO_ITEM_MAP: dict[str, tuple[str, float]] = {
    "tomato (1 kg)":       ("tomato",     1000),
    "potato (1 kg)":       ("potato",     1000),
    "onion (1 kg)":        ("onion",      1000),
    "apple (1 kg)":        ("apple",      1000),
    "banana (1 kg)":       ("banana",     1000),
    "orange (1 kg)":       ("orange",     1000),
    "strawberry (1 kg)":   ("strawberry", 1000),
    "grape (1 kg)":        ("grape",      1000),
    "garlic (1 head)":     ("garlic",      50),
    "green pepper (1 kg)": ("bell_pepper",1000),
    "lettuce (1 head)":    (None,         None),   # not in our item list
}


def get_city_prices(city: str, currency: str, exchange_rate: int, store_label: str) -> dict | None:
    """
    Fetch Numbeo food prices for a city.
    Returns {item_key: price_dict} or None on failure.
    """
    url = f"https://www.numbeo.com/food-prices/in/{city}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()

        if any(w in r.text.lower() for w in ["captcha", "access denied", "cf-error"]):
            print(f"  [numbeo:{city}] bot challenge")
            return None

        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find("table", class_=re.compile(r"table_builder"))
        if not table:
            print(f"  [numbeo:{city}] price table not found")
            return None

        results: dict = {}
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue

            label = cells[0].get_text(strip=True).lower()
            price_text = cells[1].get_text(strip=True).replace(",", "")
            m = re.search(r"\d+\.?\d*", price_text)
            if not m:
                continue
            price = float(m.group())

            for fragment, (item_key, unit_grams) in NUMBEO_ITEM_MAP.items():
                if item_key and fragment in label:
                    price_per_100g = round(price / unit_grams * 100, 3)
                    krw = round(price_per_100g * exchange_rate)
                    results[item_key] = {
                        "price_krw":   krw,
                        "price_local": price_per_100g,
                        "currency":    currency,
                        "store":       store_label,
                    }
                    print(f"  [numbeo:{city}] {item_key}: {currency} {price_per_100g:.3f}/100g = ₩{krw}")
                    break

        return results if results else None

    except Exception as e:
        print(f"  [numbeo:{city}] error: {e}")
        return None
