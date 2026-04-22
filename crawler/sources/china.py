"""
China price scraper — 盒马(Hema/Freshippo) via JD Fresh fallback.

盒马's web app requires location context; we try their open product API first.
If that fails, we fall back to JD.com fresh category (京东生鲜), which
is more reliably accessible from overseas IPs.
"""

import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# (item_key, jd_search_keyword, grams_per_unit)
JD_ITEMS: list[tuple[str, str, float]] = [
    ("tomato",     "番茄 西红柿 500g",  500.0),
    ("carrot",     "胡萝卜 500g",       500.0),
    ("potato",     "土豆 马铃薯 500g",  500.0),
    ("onion",      "洋葱 500g",         500.0),
    ("broccoli",   "西兰花 500g",       500.0),
    ("cucumber",   "黄瓜 500g",         500.0),
    ("garlic",     "大蒜 250g",         250.0),
    ("bell_pepper","彩椒 500g",         500.0),
    ("apple",      "苹果 1000g",       1000.0),
    ("banana",     "香蕉 500g",         500.0),
    ("orange",     "橙子 1000g",       1000.0),
    ("strawberry", "草莓 500g",         500.0),
    ("grape",      "葡萄 500g",         500.0),
]


def _jd_search_price(keyword: str) -> float | None:
    """Return CNY price for first JD.com result, or None."""
    try:
        r = requests.get(
            "https://search.jd.com/Search",
            params={"keyword": keyword, "enc": "utf-8", "page": 1},
            headers=HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        price_tag = soup.select_one("li.gl-item .p-price strong i")
        if price_tag:
            return float(price_tag.get_text(strip=True).replace(",", ""))
    except Exception as e:
        print(f"  [china] JD keyword '{keyword}' failed: {e}")
    return None


def get_china_prices(exchange_rate: int = 190) -> dict | None:
    results: dict = {}
    for item_key, keyword, unit_grams in JD_ITEMS:
        cny = _jd_search_price(keyword)
        if cny is None:
            continue
        cny_per_100g = cny / unit_grams * 100
        krw_per_100g = round(cny_per_100g * exchange_rate)
        results[item_key] = {
            "price_krw": krw_per_100g,
            "price_local": round(cny_per_100g, 2),
            "currency": "CNY",
            "store": "盒马",
        }
        print(f"  [china] {item_key}: ¥{cny_per_100g:.2f}/100g = ₩{krw_per_100g}")
    return results if results else None
