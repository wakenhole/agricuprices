"""
Korea price scraper — KAMIS (한국농수산식품유통공사) website.

KAMIS shows daily retail prices at https://www.kamis.or.kr
Item code mapping used in the form POST request:
  211 토마토, 214 오이, 215 파프리카, 231 마늘, 232 양파
  233 감자, 221 브로콜리, 225 당근
  412 사과, 414 배, 415 포도, 418 딸기, 420 바나나, 424 오렌지
"""

import re
import requests
from bs4 import BeautifulSoup

ITEM_CODES = {
    "tomato":     "211",
    "cucumber":   "214",
    "bell_pepper":"215",
    "garlic":     "231",
    "onion":      "232",
    "potato":     "233",
    "broccoli":   "221",
    "carrot":     "225",
    "apple":      "412",
    "grape":      "415",
    "strawberry": "418",
    "banana":     "420",
    "orange":     "424",
}

# grams per reported KAMIS unit (KAMIS reports per-item or per-kg)
# Most KAMIS retail prices are reported per 1kg; we convert to per 100g.
UNIT_GRAMS = 1000  # assume kg → 100g factor = 0.1


def _fetch_price(item_code: str) -> float | None:
    """Return KRW price per 100g for a single item, or None on failure."""
    try:
        r = requests.post(
            "https://www.kamis.or.kr/customer/price/retail/item.do",
            data={
                "action": "dailySalesList",
                "itemCategoryCode": "100" if int(item_code) < 400 else "200",
                "itemCode": item_code,
                "kindCode": "01",
                "gradeCode": "06",  # 중품 (medium grade)
                "countyCode": "1101",  # 서울 종로구
                "convert_kg_yn": "Y",
            },
            headers={"Referer": "https://www.kamis.or.kr/"},
            timeout=15,
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        # The price appears in a table cell with class "price" or similar.
        # Try to find the first numeric price value in the response table.
        for td in soup.select("table td"):
            text = td.get_text(strip=True).replace(",", "")
            if re.fullmatch(r"\d{3,6}", text):
                price_per_kg = float(text)
                return round(price_per_kg / 10)  # per 100g
    except Exception as e:
        print(f"  [korea] item {item_code} failed: {e}")
    return None


def get_korea_prices() -> dict | None:
    results: dict = {}
    for item_key, code in ITEM_CODES.items():
        price = _fetch_price(code)
        if price:
            results[item_key] = {
                "price_krw": price,
                "price_local": price,
                "currency": "KRW",
                "store": "이마트",
            }
            print(f"  [korea] {item_key}: ₩{price}/100g")
    return results if results else None
