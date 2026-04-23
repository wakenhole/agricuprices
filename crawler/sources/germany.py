"""Germany price scraper — Numbeo Berlin"""

from .numbeo import get_city_prices


def get_germany_prices(exchange_rate: int = 1490) -> dict | None:
    print("  [de] Fetching Numbeo Berlin...")
    return get_city_prices("Berlin", "EUR", exchange_rate, "REWE")
