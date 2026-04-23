"""
UK price scraper
Primary  : Aldi UK via Playwright (headless Chrome)
Fallback : Numbeo London
"""

import asyncio
import json
import re

from .numbeo import get_city_prices

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

# (item_key, aldi_search_term, fallback_grams)
SEARCH_ITEMS: list[tuple[str, str, float]] = [
    ("tomato",     "tomatoes",         500),
    ("carrot",     "carrots",          1000),
    ("potato",     "potatoes",         1000),
    ("onion",      "onions",           1000),
    ("broccoli",   "broccoli",         400),
    ("cucumber",   "cucumber",         350),
    ("garlic",     "garlic",            52),
    ("bell_pepper","peppers",           160),
    ("apple",      "apples",           600),
    ("banana",     "bananas",          600),
    ("orange",     "oranges",          600),
    ("strawberry", "strawberries",     400),
    ("grape",      "grapes",           500),
]


def _parse_grams(text: str) -> float | None:
    t = text.lower()
    if m := re.search(r"(\d+\.?\d*)\s*kg", t):
        return float(m.group(1)) * 1000
    if m := re.search(r"(\d+\.?\d*)\s*g\b", t):
        return float(m.group(1))
    if m := re.search(r"(\d+\.?\d*)\s*oz", t):
        return float(m.group(1)) * 28.35
    return None


async def _scrape_aldi() -> dict | None:
    from playwright.async_api import async_playwright

    results: dict = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            locale="en-GB",
            user_agent=HEADERS["User-Agent"],
        )
        page = await ctx.new_page()

        for item_key, term, fallback_grams in SEARCH_ITEMS:
            try:
                await page.goto(
                    f"https://www.aldi.co.uk/search?q={term}",
                    wait_until="domcontentloaded",
                    timeout=25000,
                )
                await page.wait_for_timeout(2500)

                # 1) Try __NEXT_DATA__ structured product data
                parsed = False
                try:
                    nd = await page.evaluate(
                        "() => JSON.parse(document.getElementById('__NEXT_DATA__')?.textContent ?? '{}')"
                    )
                    products = (
                        nd.get("props", {})
                          .get("pageProps", {})
                          .get("searchResult", {})
                          .get("products", [])
                        or nd.get("props", {})
                           .get("pageProps", {})
                           .get("products", [])
                    )
                    if products:
                        p0 = products[0]
                        price = p0.get("price") or p0.get("regularPrice") or p0.get("priceNumeric")
                        size  = str(p0.get("size") or p0.get("unitSize") or p0.get("weight") or "")
                        grams = _parse_grams(size) or fallback_grams
                        if price:
                            gbp = float(price) / grams * 100
                            results[item_key] = {
                                "price_krw":   0,   # recalculated in crawl.py
                                "price_local": round(gbp, 3),
                                "currency":    "GBP",
                                "store":       "Aldi",
                            }
                            print(f"  [aldi] {item_key}: £{gbp:.3f}/100g (NEXT_DATA)")
                            parsed = True
                except Exception:
                    pass

                # 2) DOM fallback — look for price-per-unit string "£X.XX/100g" or "£X.XX/kg"
                if not parsed:
                    els = await page.query_selector_all("[class*='price']")
                    for el in els:
                        txt = await el.inner_text()
                        # match "£0.18/100g" or "£1.80/kg"
                        m_100g = re.search(r"£(\d+\.?\d*)/100\s*g", txt, re.I)
                        m_kg   = re.search(r"£(\d+\.?\d*)/kg", txt, re.I)
                        if m_100g:
                            gbp = float(m_100g.group(1))
                            results[item_key] = {
                                "price_krw":   0,
                                "price_local": gbp,
                                "currency":    "GBP",
                                "store":       "Aldi",
                            }
                            print(f"  [aldi] {item_key}: £{gbp}/100g (DOM /100g)")
                            parsed = True
                            break
                        if m_kg:
                            gbp = float(m_kg.group(1)) / 10  # per 100g
                            results[item_key] = {
                                "price_krw":   0,
                                "price_local": gbp,
                                "currency":    "GBP",
                                "store":       "Aldi",
                            }
                            print(f"  [aldi] {item_key}: £{gbp}/100g (DOM /kg)")
                            parsed = True
                            break

                if not parsed:
                    print(f"  [aldi] {item_key}: no price found")

            except Exception as e:
                print(f"  [aldi] {item_key} error: {e}")

        await browser.close()

    return results if results else None


def get_uk_prices(exchange_rate: int = 1750) -> dict | None:
    # Primary: Aldi UK Playwright
    print("  [uk] Trying Aldi UK (Playwright)...")
    try:
        results = asyncio.run(_scrape_aldi())
    except Exception as e:
        print(f"  [uk] Aldi failed: {e}")
        results = None

    if results:
        # Apply exchange rate
        for v in results.values():
            v["price_krw"] = round(v["price_local"] * exchange_rate)
        return results

    # Fallback: Numbeo London
    print("  [uk] Falling back to Numbeo London...")
    return get_city_prices("London", "GBP", exchange_rate, "Aldi")
