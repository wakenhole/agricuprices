"""Manual price fallback — reads crawler/manual_prices.yaml"""

from pathlib import Path
import yaml

YAML_PATH = Path(__file__).parent.parent / "manual_prices.yaml"


def get_manual_prices(country_code: str, exchange_rate: int) -> dict | None:
    """
    Load manual prices for a country from manual_prices.yaml.
    Prices in YAML are already per 100g in local currency.
    Returns {item_key: price_dict} or None if country not found.
    """
    try:
        with open(YAML_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"  [manual:{country_code}] failed to load YAML: {e}")
        return None

    entry = data.get(country_code)
    if not entry:
        return None

    currency = entry["currency"]
    store = entry["store"]
    verified = entry.get("verified", "unknown")
    items = entry.get("items", {})

    results: dict = {}
    for item_key, price_local in items.items():
        price_local = float(price_local)
        krw = round(price_local * exchange_rate)
        results[item_key] = {
            "price_krw":   krw,
            "price_local": price_local,
            "currency":    currency,
            "store":       store,
            "source":      f"manual/{verified}",
        }
        print(f"  [manual:{country_code}] {item_key}: {currency} {price_local}/100g = ₩{krw}")

    return results if results else None
