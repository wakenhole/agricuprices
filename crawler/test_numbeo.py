"""
Numbeo food price scraper.
https://www.numbeo.com/food-prices/in/CITY

Numbeo is a crowd-sourced cost-of-living database with
absolute retail prices per item per city — no API key needed.
Cities: Berlin (DE), London (UK), Sydney (AU), Tokyo (JP), Shanghai (CN)
"""

import re
import time
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

# city → country_code, currency, exchange_rate_key
CITIES = {
    "Berlin":   ("de", "EUR", "EUR"),
    "London":   ("uk", "GBP", "GBP"),
    "Sydney":   ("au", "AUD", "AUD"),
    "Tokyo":    ("jp", "JPY", "JPY"),
    "Shanghai": ("cn", "CNY", "CNY"),
}

# Numbeo item name fragments → our item keys (lowercase match)
ITEM_MAP = {
    "tomato":                    "tomato",
    "lettuce":                   None,
    "potato":                    "potato",
    "onion":                     "onion",
    "beef round":                None,
    "apple":                     "apple",
    "banana":                    "banana",
    "orange":                    "orange",
    "tomato (1 kg)":             "tomato",
    "potato (1 kg)":             "potato",
    "onion (1 kg)":              "onion",
    "apple (1 kg)":              "apple",
    "banana (1 kg)":             "banana",
    "orange (1 kg)":             "orange",
    "strawberry (1 kg)":        "strawberry",
    "grape (1 kg)":              "grape",
    "garlic (1 head)":           "garlic",
    "green pepper":              "bell_pepper",
    "broccoli (1 head)":        "broccoli",
    "cucumber (1)":              "cucumber",
    "carrot (1 kg)":             "carrot",
}

# Approximate grams per Numbeo unit
UNIT_GRAMS = {
    "1 kg":   1000,
    "500 g":   500,
    "1 head":   80,   # garlic
    "1":       300,   # cucumber
}


def _parse_grams_from_label(label: str) -> float:
    label = label.lower()
    if "1 kg" in label:
        return 1000
    if "500 g" in label:
        return 500
    if "1 head" in label:
        return 80   # garlic bulb
    if "(1)" in label:
        return 300  # cucumber
    return 1000     # default assume 1kg


def fetch_city_prices(city: str) -> dict[str, float] | None:
    """Return {item_key: local_price_per_100g} for a city, or None."""
    url = f"https://www.numbeo.com/food-prices/in/{city}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        if any(w in r.text.lower() for w in ["captcha", "access denied", "cloudflare"]):
            print(f"  [numbeo] {city}: bot challenge detected")
            return None

        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find("table", class_=re.compile(r"table_builder"))
        if not table:
            print(f"  [numbeo] {city}: price table not found")
            print(f"  Page title: {soup.title.string if soup.title else '?'}")
            return None

        results: dict[str, float] = {}
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            label = cells[0].get_text(strip=True).lower()
            price_text = cells[1].get_text(strip=True).replace(",", "")
            try:
                price = float(re.search(r"\d+\.?\d*", price_text).group())
            except Exception:
                continue

            for fragment, item_key in ITEM_MAP.items():
                if item_key and fragment in label:
                    grams = _parse_grams_from_label(label)
                    results[item_key] = round(price / grams * 100, 3)
                    break

        return results if results else None

    except Exception as e:
        print(f"  [numbeo] {city}: {e}")
        return None


# ─── main test ───────────────────────────────────────────────

def section(t): print(f"\n{'='*60}\n  {t}\n{'='*60}")

for city, (code, currency, _) in CITIES.items():
    section(f"Numbeo — {city} ({currency})")
    prices = fetch_city_prices(city)
    if prices:
        print(f"  ✅ {len(prices)} items found")
        for item, p in list(prices.items())[:5]:
            print(f"  {item:15s}: {currency} {p:.3f}/100g")
    else:
        print(f"  ❌ No data")
    time.sleep(2)

print("\n" + "="*60 + "\n  TEST COMPLETE\n" + "="*60)
