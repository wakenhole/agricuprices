import requests


def get_exchange_rates() -> dict[str, int] | None:
    """
    Fetch KRW-per-1-unit rates for USD, JPY, CNY, EUR, GBP, AUD
    using the free frankfurter.app ECB data feed.
    Returns e.g. {"USD": 1380, "JPY": 9, ...} or None on failure.
    """
    try:
        r = requests.get(
            "https://api.frankfurter.app/latest",
            params={"from": "KRW", "to": "USD,JPY,CNY,EUR,GBP,AUD"},
            timeout=10,
        )
        r.raise_for_status()
        rates_from_krw: dict[str, float] = r.json()["rates"]
        # invert: 1 KRW = 0.000725 USD  →  1 USD = 1380 KRW
        return {k: round(1 / v) for k, v in rates_from_krw.items()}
    except Exception as e:
        print(f"  [exchange_rates] failed: {e}")
        return None
