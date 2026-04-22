"""
USA price scraper — Kroger 공식 개발자 API
https://developer.kroger.com (무료 가입)

Required env vars:
  KROGER_CLIENT_ID
  KROGER_CLIENT_SECRET

Kroger은 미국 2위 대형마트 체인. API로 실제 매장 가격 제공.
대표 매장: Atlanta, GA (location_id 하드코딩 또는 zip 검색)
"""

import base64
import os
import re

import requests

CLIENT_ID     = os.environ.get("KROGER_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("KROGER_CLIENT_SECRET", "")

TOKEN_URL    = "https://api.kroger.com/v1/connect/oauth2/token"
PRODUCTS_URL = "https://api.kroger.com/v1/products"
LOCATIONS_URL= "https://api.kroger.com/v1/locations"

# Atlanta, GA zip — representative US city
SEARCH_ZIP = "30301"

# (item_key, search_term, fallback_grams)
SEARCH_ITEMS: list[tuple[str, str, float]] = [
    ("tomato",     "roma tomatoes",       453.0),
    ("carrot",     "baby carrots",        453.0),
    ("potato",     "russet potatoes",     907.0),
    ("onion",      "yellow onions",       907.0),
    ("broccoli",   "broccoli crown",      340.0),
    ("cucumber",   "english cucumber",    300.0),
    ("garlic",     "garlic bulb",          52.0),
    ("bell_pepper","bell peppers",        170.0),
    ("apple",      "gala apples",         907.0),
    ("banana",     "bananas",             453.0),
    ("orange",     "navel oranges",       907.0),
    ("strawberry", "strawberries",        453.0),
    ("grape",      "seedless grapes",     907.0),
]


def _parse_grams(size: str) -> float | None:
    """Convert Kroger size string ('10 oz', '1 lb', '500g') to grams."""
    s = size.lower()
    if m := re.search(r"(\d+\.?\d*)\s*oz", s):
        return float(m.group(1)) * 28.35
    if m := re.search(r"(\d+\.?\d*)\s*lb", s):
        return float(m.group(1)) * 453.6
    if m := re.search(r"(\d+\.?\d*)\s*kg", s):
        return float(m.group(1)) * 1000
    if m := re.search(r"(\d+\.?\d*)\s*g\b", s):
        return float(m.group(1))
    return None


def _get_token() -> str:
    creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r = requests.post(
        TOKEN_URL,
        headers={
            "Authorization":  f"Basic {creds}",
            "Content-Type":   "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials", "scope": "product.compact"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def _get_location_id(token: str) -> str:
    """Find the nearest Kroger store to the search zip."""
    r = requests.get(
        LOCATIONS_URL,
        headers={"Authorization": f"Bearer {token}"},
        params={
            "filter.zipCode.near": SEARCH_ZIP,
            "filter.limit":        1,
            "filter.chain":        "Kroger",
        },
        timeout=15,
    )
    r.raise_for_status()
    locations = r.json().get("data", [])
    if not locations:
        raise ValueError("No Kroger locations found near zip")
    return locations[0]["locationId"]


def _search_product(token: str, location_id: str, term: str) -> tuple[float, float] | None:
    """Return (usd_price, grams) for the first matching product, or None."""
    r = requests.get(
        PRODUCTS_URL,
        headers={"Authorization": f"Bearer {token}"},
        params={
            "filter.term":       term,
            "filter.locationId": location_id,
            "filter.limit":      5,
        },
        timeout=15,
    )
    r.raise_for_status()
    products = r.json().get("data", [])

    for product in products:
        for item in product.get("items", []):
            price = item.get("price", {}).get("regular")
            size  = item.get("size", "")
            grams = _parse_grams(size)
            if price and grams and grams > 0:
                return float(price), grams
    return None


def get_usa_prices(exchange_rate: int = 1380) -> dict | None:
    if not CLIENT_ID:
        print("  [usa] KROGER_CLIENT_ID not set — skipping")
        return None

    try:
        token       = _get_token()
        location_id = _get_location_id(token)
        print(f"  [usa] Kroger location: {location_id}")
    except Exception as e:
        print(f"  [usa] Auth/location failed: {e}")
        return None

    results: dict = {}
    for item_key, term, fallback_g in SEARCH_ITEMS:
        try:
            result = _search_product(token, location_id, term)
            if not result:
                continue
            usd, grams = result
            usd_per_100g = usd / grams * 100
            krw_per_100g = round(usd_per_100g * exchange_rate)
            results[item_key] = {
                "price_krw":   krw_per_100g,
                "price_local": round(usd_per_100g, 2),
                "currency":    "USD",
                "store":       "Kroger",
            }
            print(f"  [usa] {item_key}: ${usd_per_100g:.2f}/100g = ₩{krw_per_100g}")
        except Exception as e:
            print(f"  [usa] {item_key} error: {e}")

    return results if results else None
