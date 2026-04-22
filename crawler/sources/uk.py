"""
UK price scraper — Tesco Online (tesco.com).

Tesco exposes a JSON API at /groceries/en-GB/search that returns product data.
Prices are in GBP per pack.
"""

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
}

SEARCH_ITEMS: list[tuple[str, str, float]] = [
    ("tomato",     "tomatoes",          500.0),
    ("carrot",     "carrots",           500.0),
    ("potato",     "potatoes",          500.0),
    ("onion",      "onions",            500.0),
    ("broccoli",   "broccoli",          400.0),
    ("cucumber",   "cucumber",          350.0),
    ("garlic",     "garlic bulb",        52.0),
    ("bell_pepper","bell pepper",        160.0),
    ("apple",      "apples",            500.0),
    ("banana",     "bananas",           500.0),
    ("orange",     "oranges",           500.0),
    ("strawberry", "strawberries",      400.0),
    ("grape",      "grapes seedless",   500.0),
]


def _search_price(query: str) -> float | None:
    """Return GBP price for the first Tesco result."""
    try:
        r = requests.get(
            "https://www.tesco.com/groceries/en-GB/search",
            params={"query": query, "count": 5},
            headers=HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("productsByCategory", [{}])[0].get("products", [])
        if results:
            return float(results[0]["price"])
    except Exception as e:
        print(f"  [uk] query '{query}' failed: {e}")
    return None


def get_uk_prices(exchange_rate: int = 1750) -> dict | None:
    results: dict = {}
    for item_key, query, unit_grams in SEARCH_ITEMS:
        gbp = _search_price(query)
        if gbp is None:
            continue
        gbp_per_100g = gbp / unit_grams * 100
        krw_per_100g = round(gbp_per_100g * exchange_rate)
        results[item_key] = {
            "price_krw": krw_per_100g,
            "price_local": round(gbp_per_100g, 2),
            "currency": "GBP",
            "store": "Tesco",
        }
        print(f"  [uk] {item_key}: £{gbp_per_100g:.2f}/100g = ₩{krw_per_100g}")
    return results if results else None
