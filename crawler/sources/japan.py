"""
Japan price scraper — AEON Online Shop (aeon.com/shop).

AEON's product search returns JSON from their internal API.
Prices are in JPY per pack; we divide by estimated pack weight (grams).
"""

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept-Language": "ja,en;q=0.9",
}

# (item_key, search_keyword, estimated_grams_per_unit)
SEARCH_ITEMS: list[tuple[str, str, float]] = [
    ("tomato",     "トマト",       200.0),
    ("carrot",     "にんじん",     200.0),
    ("potato",     "じゃがいも",   150.0),
    ("onion",      "玉ねぎ",       200.0),
    ("broccoli",   "ブロッコリー", 200.0),
    ("cucumber",   "きゅうり",     100.0),
    ("garlic",     "にんにく",      50.0),
    ("bell_pepper","パプリカ",     150.0),
    ("apple",      "りんご",       250.0),
    ("banana",     "バナナ",       100.0),
    ("orange",     "オレンジ",     200.0),
    ("strawberry", "いちご",       100.0),
    ("grape",      "ぶどう",       100.0),
]


def _search_price(keyword: str) -> float | None:
    """Return JPY price per pack from AEON's product API, or None."""
    try:
        r = requests.get(
            "https://shop.aeon.com/api/search",
            params={"keyword": keyword, "limit": 5, "category": "19"},
            headers=HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        items = r.json().get("items", [])
        if items:
            return float(items[0].get("price", 0))
    except Exception as e:
        print(f"  [japan] keyword '{keyword}' failed: {e}")
    return None


def get_japan_prices(exchange_rate: int = 9) -> dict | None:
    results: dict = {}
    for item_key, keyword, unit_grams in SEARCH_ITEMS:
        jpy = _search_price(keyword)
        if jpy is None:
            continue
        jpy_per_100g = jpy / unit_grams * 100
        krw_per_100g = round(jpy_per_100g * exchange_rate)
        results[item_key] = {
            "price_krw": krw_per_100g,
            "price_local": round(jpy_per_100g),
            "currency": "JPY",
            "store": "AEON",
        }
        print(f"  [japan] {item_key}: ¥{jpy_per_100g:.0f}/100g = ₩{krw_per_100g}")
    return results if results else None
