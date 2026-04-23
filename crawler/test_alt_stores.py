"""
Alternative store test:
  Germany  → Kaufland  (kaufland.de)
  UK       → Aldi UK   (aldi.co.uk)
  Australia→ Coles     (coles.com.au)
"""

import asyncio
import json
import re
import time

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

TIMEOUT = 15
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


def report(label: str, r: requests.Response) -> None:
    bots = [w for w in ["captcha", "robot", "challenge", "blocked", "access denied", "cloudflare"]
            if w in r.text.lower()]
    status = "✅" if r.status_code == 200 and not bots else "⚠️" if r.status_code == 200 else "❌"
    print(f"  {status} [{label}] {r.status_code}  {len(r.content):,}B")
    if bots:
        print(f"     Bot signals: {bots}")


# ─── KAUFLAND (Germany) ──────────────────────────────────────

section("KAUFLAND — requests: product search page")
try:
    r = requests.get(
        "https://www.kaufland.de/product-search/",
        params={"search_value": "Tomaten"},
        headers={**HEADERS, "Accept-Language": "de-DE,de;q=0.9"},
        timeout=TIMEOUT,
    )
    report("kaufland.de search", r)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        # Kaufland uses data-price attribute or class="price"
        prices = (soup.select("[class*='price']") +
                  soup.select("[data-price]") +
                  soup.select("[class*='Price']"))
        prices = prices[:5]
        print(f"  Price elements: {len(prices)}")
        for p in prices:
            txt = p.get_text(strip=True)
            if txt:
                print(f"  → {txt[:60]}")
        # look for JSON-LD
        ld = soup.find("script", type="application/ld+json")
        if ld:
            print(f"  JSON-LD found: {ld.string[:200] if ld.string else 'empty'}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

section("KAUFLAND — requests: internal API")
try:
    r = requests.get(
        "https://www.kaufland.de/api/search",
        params={"query": "Tomaten", "limit": 5, "locale": "de-DE"},
        headers={**HEADERS, "Accept": "application/json", "Accept-Language": "de-DE"},
        timeout=TIMEOUT,
    )
    report("kaufland.de /api/search", r)
    if r.status_code == 200:
        try:
            data = r.json()
            print(f"  JSON keys: {list(data.keys())[:6]}")
        except Exception:
            print(f"  Body preview: {r.text[:200]}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

# ─── ALDI UK ─────────────────────────────────────────────────

section("ALDI UK — requests: search page")
try:
    r = requests.get(
        "https://www.aldi.co.uk/search",
        params={"q": "tomatoes"},
        headers={**HEADERS, "Accept-Language": "en-GB,en;q=0.9"},
        timeout=TIMEOUT,
    )
    report("aldi.co.uk /search", r)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        prices = soup.select(".price, [class*='price'], [class*='Price']")
        print(f"  Price elements: {len(prices)}")
        for p in prices[:5]:
            txt = p.get_text(strip=True)
            if txt and "£" in txt:
                print(f"  → {txt[:60]}")
        # check for product grid
        products = soup.select("[class*='product'], article")
        print(f"  Product cards: {len(products)}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

section("ALDI UK — requests: product listing page")
try:
    r = requests.get(
        "https://www.aldi.co.uk/fresh-vegetables",
        headers={**HEADERS, "Accept-Language": "en-GB,en;q=0.9"},
        timeout=TIMEOUT,
    )
    report("aldi.co.uk /fresh-vegetables", r)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        prices = [p.get_text(strip=True) for p in soup.select("[class*='price']") if "£" in p.get_text()]
        print(f"  Prices found: {prices[:5]}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

# ─── COLES (Australia) ───────────────────────────────────────

section("COLES — requests: search page")
try:
    r = requests.get(
        "https://www.coles.com.au/search/results",
        params={"q": "tomatoes"},
        headers={**HEADERS, "Accept-Language": "en-AU,en;q=0.9"},
        timeout=TIMEOUT,
    )
    report("coles.com.au search", r)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        prices = soup.select("[class*='price'], [class*='Price']")
        print(f"  Price elements: {len(prices)}")
        for p in prices[:5]:
            txt = p.get_text(strip=True)
            if txt:
                print(f"  → {txt[:60]}")
        # check __NEXT_DATA__
        nd = soup.find("script", id="__NEXT_DATA__")
        if nd and nd.string:
            data = json.loads(nd.string)
            # drill into search results
            results = (data.get("props", {})
                          .get("pageProps", {})
                          .get("searchResults", {})
                          .get("results", []))
            print(f"  __NEXT_DATA__ results: {len(results)}")
            for item in results[:3]:
                name  = item.get("name", "?")[:30]
                price = item.get("pricing", {}).get("now")
                size  = item.get("size", "?")
                print(f"  💰 {name}: A${price} / {size}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

section("COLES — requests: internal API")
try:
    r = requests.get(
        "https://www.coles.com.au/api/2.0/page/catalogue/search-results",
        params={"q": "tomatoes", "page": 1, "pageSize": 5},
        headers={**HEADERS, "Accept": "application/json"},
        timeout=TIMEOUT,
    )
    report("coles.com.au internal API", r)
    if r.status_code == 200:
        try:
            data = r.json()
            print(f"  JSON keys: {list(data.keys())[:6]}")
        except Exception:
            print(f"  Body: {r.text[:200]}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

# ─── Playwright for any site that showed promise ─────────────

async def pw_test(label: str, url: str, selectors: list[str], lang: str) -> None:
    section(f"{label} — Playwright")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(locale=lang, user_agent=HEADERS["User-Agent"])
        page = await ctx.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(4000)
            title = await page.title()
            print(f"  Title: {title!r}")
            for sel in selectors:
                els = await page.query_selector_all(sel)
                if els:
                    print(f"  [{sel}]: {len(els)} elements")
                    for el in els[:3]:
                        txt = (await el.inner_text()).strip()
                        if txt:
                            print(f"    → {txt[:60]}")
                    break
            else:
                print("  No price elements found")
        except Exception as e:
            print(f"  ❌ {e}")
        finally:
            await browser.close()


async def main() -> None:
    await pw_test(
        "Kaufland",
        "https://www.kaufland.de/product-search/?search_value=Tomaten",
        ["[class*='price']", "[data-price]", "span[class*='Price']"],
        "de-DE",
    )
    await pw_test(
        "Aldi UK",
        "https://www.aldi.co.uk/search?q=tomatoes",
        [".price", "[class*='price']", "[class*='Price']"],
        "en-GB",
    )
    await pw_test(
        "Coles",
        "https://www.coles.com.au/search/results?q=tomatoes",
        ["[class*='price']", "[data-testid*='price']", "[class*='Price']"],
        "en-AU",
    )
    print("\n" + "="*60 + "\n  TEST COMPLETE\n" + "="*60)


asyncio.run(main())
