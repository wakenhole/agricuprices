"""
AgricuPrices — Main crawler
Run daily via GitHub Actions (.github/workflows/crawl.yml)

Data collection strategy:
  🇰🇷 Korea    : KAMIS official API          (env: KAMIS_API_KEY, KAMIS_API_ID)
  🇺🇸 USA      : Kroger official API         (env: KROGER_CLIENT_ID, KROGER_CLIENT_SECRET)
  🇬🇧 UK       : Aldi UK Playwright → Numbeo London
  🇩🇪 Germany  : Numbeo Berlin
  🇯🇵 Japan    : Numbeo Tokyo
  🇨🇳 China    : Numbeo Shanghai
  🇦🇺 Australia: Numbeo Sydney

Prices that fail to fetch retain their previous values in prices.json.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from sources.exchange_rates import get_exchange_rates
from sources.korea       import get_korea_prices
from sources.usa         import get_usa_prices
from sources.uk          import get_uk_prices
from sources.germany     import get_germany_prices
from sources.japan       import get_japan_prices
from sources.china       import get_china_prices
from sources.australia   import get_australia_prices

DATA_FILE = Path(__file__).parent.parent / "public" / "data" / "prices.json"


def load_data() -> dict:
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def apply_prices(data: dict, country_code: str, prices: dict | None, exchange_rate: int) -> int:
    if not prices:
        return 0
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    updated = 0
    for item_key, price_data in prices.items():
        if item_key not in data["items"]:
            continue
        if price_data["currency"] != "KRW":
            price_data["price_krw"] = round(price_data["price_local"] * exchange_rate)
        price_data["fetched_at"] = today
        data["items"][item_key]["countries"][country_code] = price_data
        updated += 1
    return updated


def main() -> None:
    print("=== AgricuPrices Crawler ===")
    data = load_data()

    # ── 1. Exchange rates ────────────────────────────────────
    print("\n[1/8] Exchange rates (frankfurter.app)...")
    rates = get_exchange_rates()
    if rates:
        data["exchange_rates"] = rates
        print(f"  {rates}")
    else:
        rates = data["exchange_rates"]
        print(f"  Using cached: {rates}")

    # ── 2. Country scrapers ──────────────────────────────────
    scrapers = [
        ("kr", get_korea_prices,    rates.get("KRW", 1),    "[2/8] 🇰🇷 Korea    (KAMIS API)"),
        ("us", get_usa_prices,      rates.get("USD", 1471), "[3/8] 🇺🇸 USA      (Kroger API)"),
        ("uk", get_uk_prices,       rates.get("GBP", 2000), "[4/8] 🇬🇧 UK       (Aldi → Numbeo)"),
        ("de", get_germany_prices,  rates.get("EUR", 1724), "[5/8] 🇩🇪 Germany  (Numbeo Berlin)"),
        ("jp", get_japan_prices,    rates.get("JPY", 9),    "[6/8] 🇯🇵 Japan    (Numbeo Tokyo)"),
        ("cn", get_china_prices,    rates.get("CNY", 216),  "[7/8] 🇨🇳 China    (Numbeo Shanghai)"),
        ("au", get_australia_prices,rates.get("AUD", 1053), "[8/8] 🇦🇺 Australia(Numbeo Sydney)"),
    ]

    total = 0
    for code, scraper, rate, label in scrapers:
        print(f"\n{label}...")
        try:
            prices = scraper(rate) if code != "kr" else scraper()
            n = apply_prices(data, code, prices, rate)
            print(f"  → {n} items updated")
            total += n
        except Exception as e:
            print(f"  → ERROR: {e}")

    # ── 3. Save ──────────────────────────────────────────────
    data["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"
    if total > 0:
        data["is_sample"] = False
    save_data(data)
    print(f"\n✅ Done — {total} records updated → {DATA_FILE.name}")


if __name__ == "__main__":
    main()
