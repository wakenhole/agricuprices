"""
Australia price scraper — Woolworths Online (woolworths.com.au).

Woolworths has a public product search JSON API.
Prices are in AUD per pack.
"""

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-AU,en;q=0.9",
}

SEARCH_ITEMS: list[tuple[str, str, float]] = [
    ("tomato",     "tomatoes",       500.0),
    ("carrot",     "carrots",        500.0),
    ("potato",     "potatoes",       500.0),
    ("onion",      "brown onions",   500.0),
    ("broccoli",   "broccoli",       350.0),
    ("cucumber",   "continental cucumber", 300.0),
    ("garlic",     "garlic bulb",     60.0),
    ("bell_pepper","capsicum",        200.0),
    ("apple",      "pink lady apples", 500.0),
    ("banana",     "cavendish bananas", 500.0),
    ("orange",     "navel oranges",  500.0),
    ("strawberry", "strawberries",   250.0),
    ("grape",      "seedless grapes",500.0),
]


def _search_price(query: str) -> float | None:
    """Return AUD price for the first Woolworths result."""
    try:
        r = requests.post(
            "https://www.woolworths.com.au/apis/ui/Search/products",
            json={"SearchTerm": query, "PageNumber": 1, "PageSize": 5, "SortType": "TraderRelevance"},
            headers={**HEADERS, "Content-Type": "application/json"},
            timeout=15,
        )
        r.raise_for_status()
        products = r.json().get("Products", [])
        if products:
            return float(products[0].get("Price", 0))
    except Exception as e:
        print(f"  [australia] query '{query}' failed: {e}")
    return None


def get_australia_prices(exchange_rate: int = 890) -> dict | None:
    results: dict = {}
    for item_key, query, unit_grams in SEARCH_ITEMS:
        aud = _search_price(query)
        if aud is None:
            continue
        aud_per_100g = aud / unit_grams * 100
        krw_per_100g = round(aud_per_100g * exchange_rate)
        results[item_key] = {
            "price_krw": krw_per_100g,
            "price_local": round(aud_per_100g, 2),
            "currency": "AUD",
            "store": "Woolworths",
        }
        print(f"  [australia] {item_key}: A${aud_per_100g:.2f}/100g = ₩{krw_per_100g}")
    return results if results else None
