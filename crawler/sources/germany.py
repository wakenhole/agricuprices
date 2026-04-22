"""
Germany price scraper — REWE Online Shop (rewe.de).

REWE's product search API returns JSON at /api/products/search.
Prices are in EUR per pack; we divide by pack weight.
"""

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "de-DE,de;q=0.9",
}

SEARCH_ITEMS: list[tuple[str, str, float]] = [
    ("tomato",     "Tomaten",      500.0),
    ("carrot",     "Karotten",     500.0),
    ("potato",     "Kartoffeln",   500.0),
    ("onion",      "Zwiebeln",     500.0),
    ("broccoli",   "Brokkoli",     500.0),
    ("cucumber",   "Salatgurke",   400.0),
    ("garlic",     "Knoblauch",     80.0),
    ("bell_pepper","Paprika",       200.0),
    ("apple",      "Apfel",        500.0),
    ("banana",     "Bananen",      500.0),
    ("orange",     "Orangen",      500.0),
    ("strawberry", "Erdbeeren",    500.0),
    ("grape",      "Weintrauben",  500.0),
]


def _search_price(query: str) -> float | None:
    """Return EUR price for the first REWE search result."""
    try:
        r = requests.get(
            "https://shop.rewe.de/api/products",
            params={"search": query, "page": 0, "pageSize": 5, "market": "3600530"},
            headers=HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        items = r.json().get("_embedded", {}).get("products", [])
        if items:
            return float(items[0]["listing"]["price"]["value"]) / 100  # price in cents
    except Exception as e:
        print(f"  [germany] query '{query}' failed: {e}")
    return None


def get_germany_prices(exchange_rate: int = 1490) -> dict | None:
    results: dict = {}
    for item_key, query, unit_grams in SEARCH_ITEMS:
        eur = _search_price(query)
        if eur is None:
            continue
        eur_per_100g = eur / unit_grams * 100
        krw_per_100g = round(eur_per_100g * exchange_rate)
        results[item_key] = {
            "price_krw": krw_per_100g,
            "price_local": round(eur_per_100g, 2),
            "currency": "EUR",
            "store": "REWE",
        }
        print(f"  [germany] {item_key}: €{eur_per_100g:.2f}/100g = ₩{krw_per_100g}")
    return results if results else None
