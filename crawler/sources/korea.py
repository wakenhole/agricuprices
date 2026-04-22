"""
Korea price scraper — KAMIS 공식 API (한국농수산식품유통공사)
API key from https://www.data.go.kr → "KAMIS 농산물유통정보"

Required env vars:
  KAMIS_API_KEY  — p_cert_key (인증키)
  KAMIS_API_ID   — p_cert_id  (기관코드, 발급 시 제공)
"""

import os
from datetime import date

import requests

KAMIS_KEY = os.environ.get("KAMIS_API_KEY", "")
KAMIS_ID  = os.environ.get("KAMIS_API_ID", "")

BASE_URL = "https://www.kamis.or.kr/service/price/xml.do"

# item_code → (category_code, unit_grams)
# 채소류=100, 과일류=200
ITEM_CODES: dict[str, tuple[str, str, int]] = {
    "tomato":      ("100", "211", 1000),
    "cucumber":    ("100", "214", 1000),
    "bell_pepper": ("100", "215", 1000),
    "garlic":      ("100", "231", 1000),
    "onion":       ("100", "232", 1000),
    "potato":      ("100", "233", 1000),
    "broccoli":    ("100", "221", 1000),
    "carrot":      ("100", "225", 1000),
    "apple":       ("200", "412", 1000),
    "grape":       ("200", "415", 1000),
    "strawberry":  ("200", "418", 1000),
    "banana":      ("200", "420", 1000),
    "orange":      ("200", "424", 1000),
}


def _fetch_price(category_code: str, item_code: str) -> float | None:
    today = date.today().strftime("%Y-%m-%d")
    try:
        r = requests.get(
            BASE_URL,
            params={
                "action":              "dailySalesList",
                "p_cert_key":          KAMIS_KEY,
                "p_cert_id":           KAMIS_ID,
                "p_returntype":        "json",
                "p_item_category_code": category_code,
                "p_item_code":         item_code,
                "p_kind_code":         "01",
                "p_grade_code":        "06",   # 중품
                "p_start_day":         today,
                "p_end_day":           today,
                "p_country_code":      "1101", # 서울 종로구
            },
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()

        items = (
            data.get("data", {})
                .get("item", [])
        )
        for entry in items:
            raw = entry.get("dpr1", "").replace(",", "").strip()
            if raw and raw != "-":
                return float(raw)
    except Exception as e:
        print(f"  [korea] item {item_code} error: {e}")
    return None


def get_korea_prices() -> dict | None:
    if not KAMIS_KEY:
        print("  [korea] KAMIS_API_KEY not set — skipping")
        return None

    results: dict = {}
    for item_key, (cat, code, unit_g) in ITEM_CODES.items():
        price_per_unit = _fetch_price(cat, code)
        if price_per_unit is None:
            continue
        price_per_100g = round(price_per_unit / unit_g * 100)
        results[item_key] = {
            "price_krw":   price_per_100g,
            "price_local": price_per_100g,
            "currency":    "KRW",
            "store":       "이마트",
        }
        print(f"  [korea] {item_key}: ₩{price_per_100g}/100g")

    return results if results else None
