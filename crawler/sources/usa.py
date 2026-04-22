"""
USA price scraper — Walmart.com product pages.

Walmart renders prices client-side via __NEXT_DATA__ JSON embedded in HTML.
We search for items by name and parse the first result's price.
"""

import json
import re
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Search queries → (item_key, grams_per_unit)
SEARCH_ITEMS: list[tuple[str, str, float]] = [
    ("tomato",     "roma tomatoes per lb",  453.6),
    ("carrot",     "baby carrots 1lb bag",  453.6),
    ("potato",     "russet potatoes per lb", 453.6),
    ("onion",      "yellow onion per lb",   453.6),
    ("broccoli",   "broccoli crown per lb", 453.6),
    ("cucumber",   "english cucumber each", 300.0),
    ("garlic",     "garlic bulb each",       50.0),
    ("bell_pepper","bell pepper each",       150.0),
    ("apple",      "gala apple per lb",     453.6),
    ("banana",     "bananas per lb",        453.6),
    ("orange",     "navel orange each",     180.0),
    ("strawberry", "strawberries 1lb",      453.6),
    ("grape",      "seedless grapes per lb",453.6),
]

KRW_PER_USD = 1380  # will be overridden by live exchange rate in main crawler


def _search_price(query: str) -> float | None:
    """Return USD price for the first Walmart search result, or None."""
    try:
        url = "https://www.walmart.com/search"
        r = requests.get(url, params={"q": query}, headers=HEADERS, timeout=15)
        r.raise_for_status()

        match = re.search(r'"currentPrice"\s*:\s*(\d+\.?\d*)', r.text)
        if not match:
            # fallback: look for __NEXT_DATA__ JSON
            nd = re.search(r'__NEXT_DATA__\s*=\s*(\{.*?\})\s*;', r.text, re.DOTALL)
            if nd:
                data = json.loads(nd.group(1))
                items = (
                    data.get("props", {})
                    .get("pageProps", {})
                    .get("initialData", {})
                    .get("searchResult", {})
                    .get("itemStacks", [{}])[0]
                    .get("items", [])
                )
                if items:
                    price = items[0].get("price", {}).get("currentPrice")
                    if price:
                        return float(price)
            return None

        return float(match.group(1))
    except Exception as e:
        print(f"  [usa] query '{query}' failed: {e}")
        return None


def get_usa_prices(exchange_rate: int = KRW_PER_USD) -> dict | None:
    results: dict = {}
    for item_key, query, unit_grams in SEARCH_ITEMS:
        usd = _search_price(query)
        if usd is None:
            continue
        usd_per_100g = usd / unit_grams * 100
        krw_per_100g = round(usd_per_100g * exchange_rate)
        results[item_key] = {
            "price_krw": krw_per_100g,
            "price_local": round(usd_per_100g, 2),
            "currency": "USD",
            "store": "Walmart",
        }
        print(f"  [usa] {item_key}: ${usd_per_100g:.2f}/100g = ₩{krw_per_100g}")
    return results if results else None
