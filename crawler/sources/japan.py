"""Japan price scraper — Numbeo Tokyo"""

from .numbeo import get_city_prices


def get_japan_prices(exchange_rate: int = 9) -> dict | None:
    print("  [jp] Fetching Numbeo Tokyo...")
    return get_city_prices("Tokyo", "JPY", exchange_rate, "AEON")
