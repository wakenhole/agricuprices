"""Australia price scraper — Numbeo Sydney"""

from .numbeo import get_city_prices


def get_australia_prices(exchange_rate: int = 890) -> dict | None:
    print("  [au] Fetching Numbeo Sydney...")
    return get_city_prices("Sydney", "AUD", exchange_rate, "Woolworths")
