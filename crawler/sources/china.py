"""China price scraper — Numbeo Shanghai"""

from .numbeo import get_city_prices


def get_china_prices(exchange_rate: int = 190) -> dict | None:
    print("  [cn] Fetching Numbeo Shanghai...")
    return get_city_prices("Shanghai", "CNY", exchange_rate, "盒马")
