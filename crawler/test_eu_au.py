"""
Test EU/AU scrapers: REWE (Germany), Tesco (UK), Woolworths (Australia)
Tries both requests and Playwright per site, reports what works.
"""

import asyncio
import re
import time

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


def section(title: str) -> None:
    print(f"\n{'='*60}\n  {title}\n{'='*60}")


def report_response(label: str, r: requests.Response) -> None:
    print(f"\n  [{label}] {r.status_code}  {len(r.content)}B  {r.headers.get('Content-Type','')[:40]}")
    txt = r.text
    bots = [w for w in ["captcha","robot","challenge","blocked","forbidden","403"]
            if w in txt.lower()]
    if bots:
        print(f"  ⚠️  Bot signals: {bots}")
    elif r.status_code == 200:
        print(f"  ✅ 200 OK")


# ─── REWE (Germany) ─────────────────────────────────────────

section("REWE — requests: JSON API")
try:
    r = requests.get(
        "https://shop.rewe.de/api/products",
        params={"search": "Tomaten", "page": 0, "pageSize": 5, "market": "3600530"},
        headers={**HEADERS, "Accept": "application/json"},
        timeout=15,
    )
    report_response("shop.rewe.de/api/products", r)
    if r.status_code == 200:
        items = r.json().get("_embedded", {}).get("products", [])
        print(f"  Products found: {len(items)}")
        if items:
            p = items[0]["listing"]["price"]["value"] / 100
            print(f"  💰 First product: €{p}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

section("REWE — requests: HTML search page")
try:
    r = requests.get(
        "https://www.rewe.de/suche/",
        params={"search": "Tomaten"},
        headers=HEADERS,
        timeout=15,
    )
    report_response("rewe.de/suche Tomaten", r)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        prices = soup.select("[class*='price']")
        print(f"  Price elements: {len(prices)}")
        for p in prices[:3]:
            print(f"  → {p.get_text(strip=True)[:50]}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

# ─── Tesco (UK) ─────────────────────────────────────────────

section("Tesco — requests: JSON search API")
try:
    r = requests.get(
        "https://www.tesco.com/groceries/en-GB/search",
        params={"query": "tomatoes", "count": 5},
        headers={**HEADERS, "Accept": "application/json"},
        timeout=15,
    )
    report_response("tesco.com search JSON", r)
    if r.status_code == 200:
        data = r.json()
        results = (data.get("productsByCategory") or [{}])[0].get("products", [])
        print(f"  Products found: {len(results)}")
        if results:
            print(f"  💰 First: £{results[0].get('price')} / {results[0].get('unitOfMeasure','?')}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

section("Tesco — requests: HTML search page")
try:
    r = requests.get(
        "https://www.tesco.com/groceries/en-GB/search",
        params={"query": "tomatoes"},
        headers=HEADERS,
        timeout=15,
    )
    report_response("tesco.com HTML search", r)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        prices = soup.select("[data-auto='price-value'], .price-per-sellable-unit")
        print(f"  Price elements: {len(prices)}")
        for p in prices[:3]:
            print(f"  → {p.get_text(strip=True)[:50]}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

# ─── Woolworths (Australia) ──────────────────────────────────

section("Woolworths — requests: POST search API")
try:
    r = requests.post(
        "https://www.woolworths.com.au/apis/ui/Search/products",
        json={"SearchTerm": "tomatoes", "PageNumber": 1, "PageSize": 5, "SortType": "TraderRelevance"},
        headers={**HEADERS, "Content-Type": "application/json"},
        timeout=15,
    )
    report_response("woolworths POST search", r)
    if r.status_code == 200:
        products = r.json().get("Products", [])
        print(f"  Products found: {len(products)}")
        if products:
            p = products[0]
            print(f"  💰 {p.get('Name','?')[:30]}: A${p.get('Price')}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

section("Woolworths — requests: HTML search page")
try:
    r = requests.get(
        "https://www.woolworths.com.au/shop/search/products",
        params={"searchTerm": "tomatoes"},
        headers=HEADERS,
        timeout=15,
    )
    report_response("woolworths.com.au HTML", r)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        prices = soup.select(".price, [class*='Price']")
        print(f"  Price elements: {len(prices)}")
        for p in prices[:3]:
            print(f"  → {p.get_text(strip=True)[:50]}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

# ─── Playwright fallback for any that failed ─────────────────

async def playwright_test(site: str, url: str, price_selector: str, lang: str = "en-US") -> None:
    section(f"{site} — Playwright headless Chrome")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(locale=lang, user_agent=HEADERS["User-Agent"])
        page = await ctx.new_page()
        try:
            print(f"  Loading {url[:60]}...")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            title = await page.title()
            print(f"  Page title: {title!r}")
            els = await page.query_selector_all(price_selector)
            print(f"  Price elements ({price_selector}): {len(els)}")
            for el in els[:3]:
                txt = await el.inner_text()
                print(f"  → {txt.strip()[:50]}")
        except Exception as e:
            print(f"  ❌ {e}")
        finally:
            await browser.close()


async def main() -> None:
    await playwright_test(
        "REWE",
        "https://www.rewe.de/suche/?search=Tomaten",
        "[class*='price'], [class*='Price']",
        "de-DE",
    )
    await playwright_test(
        "Tesco",
        "https://www.tesco.com/groceries/en-GB/search?query=tomatoes",
        "[data-auto='price-value'], .price-per-sellable-unit",
        "en-GB",
    )
    await playwright_test(
        "Woolworths",
        "https://www.woolworths.com.au/shop/search/products?searchTerm=tomatoes",
        ".price, [class*='Price']",
        "en-AU",
    )
    print("\n" + "="*60 + "\n  TEST COMPLETE\n" + "="*60)


asyncio.run(main())
