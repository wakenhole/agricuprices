"""
Test 1 — JD.com with Playwright (JS rendering needed for prices)
Test 2 — Walmart with Playwright + stealth headers
Test 3 — USDA AMS API (Walmart fallback, no auth needed)
"""

import asyncio
import json
import re
import requests
from playwright.async_api import async_playwright


# ─── helpers ────────────────────────────────────────────────

def section(title: str) -> None:
    print(f"\n{'='*60}\n  {title}\n{'='*60}")


# ─── JD.com via Playwright ───────────────────────────────────

async def test_jd_playwright():
    section("JD.COM — Playwright (headless Chrome)")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            locale="zh-CN",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = await ctx.new_page()

        try:
            print("  Navigating to JD search: 番茄 500g ...")
            await page.goto(
                "https://search.jd.com/Search?keyword=番茄+500g&enc=utf-8",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            await page.wait_for_timeout(3000)  # wait for JS

            # Try CSS selector for JD price
            items = await page.query_selector_all("li.gl-item")
            print(f"  Product items found: {len(items)}")

            for i, item in enumerate(items[:3]):
                title_el = await item.query_selector(".p-name em")
                price_el = await item.query_selector(".p-price strong i")

                title = await title_el.inner_text() if title_el else "?"
                price = await price_el.inner_text() if price_el else "?"

                print(f"  [{i+1}] {title[:30]!r}  →  ¥{price}")

            if not items:
                # dump first 500 chars of rendered HTML to debug
                html = await page.content()
                print(f"  No items — page snippet:\n{html[:500]}")

        except Exception as e:
            print(f"  ❌ Error: {e}")
        finally:
            await browser.close()


# ─── Walmart via Playwright ──────────────────────────────────

async def test_walmart_playwright():
    section("WALMART — Playwright (headless Chrome)")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            locale="en-US",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = await ctx.new_page()

        try:
            print("  Navigating to Walmart search: tomato ...")
            await page.goto(
                "https://www.walmart.com/search?q=tomato",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            await page.wait_for_timeout(3000)

            # Walmart product price selectors
            price_els = await page.query_selector_all('[itemprop="price"], [data-automation-id="product-price"]')
            item_els  = await page.query_selector_all('div[data-item-id]')

            print(f"  Price elements : {len(price_els)}")
            print(f"  Product cards  : {len(item_els)}")

            # Try extracting from __NEXT_DATA__
            nd_text = await page.evaluate(
                "() => document.getElementById('__NEXT_DATA__')?.textContent ?? ''"
            )
            if nd_text:
                nd = json.loads(nd_text)
                items = (nd.get("props", {})
                           .get("pageProps", {})
                           .get("initialData", {})
                           .get("searchResult", {})
                           .get("itemStacks", [{}])[0]
                           .get("items", []))
                print(f"  __NEXT_DATA__ items: {len(items)}")
                for item in items[:3]:
                    name  = item.get("name", "?")[:35]
                    price = item.get("price", {}).get("currentPrice", "?")
                    print(f"  💰 {name!r}  →  ${price}")
            else:
                # Check if we hit a bot/captcha page
                title = await page.title()
                print(f"  Page title: {title!r}")
                print("  ℹ️  No __NEXT_DATA__ — likely bot challenge page")

        except Exception as e:
            print(f"  ❌ Error: {e}")
        finally:
            await browser.close()


# ─── USDA AMS API (Walmart fallback) ────────────────────────

def test_usda_api():
    section("USDA AMS API — Walmart fallback (no auth)")

    # USDA Market News API: retail produce prices
    # Docs: https://mymarketnews.ams.usda.gov/public_data
    endpoints = [
        ("Retail produce report list", "https://mymarketnews.ams.usda.gov/api/v1/reports?slug=retail-produce-reports"),
        ("Fresh fruit/veg report",     "https://mymarketnews.ams.usda.gov/api/v1/reports/2636"),  # WA_FV001
    ]

    for label, url in endpoints:
        try:
            r = requests.get(url, headers={"Accept": "application/json"}, timeout=15)
            print(f"\n  [{label}]")
            print(f"  Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                # Show first few keys / items
                if isinstance(data, list):
                    print(f"  Items: {len(data)}")
                    if data:
                        print(f"  Sample: {json.dumps(data[0], ensure_ascii=False)[:300]}")
                elif isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())[:8]}")
            else:
                print(f"  Body: {r.text[:200]}")
        except Exception as e:
            print(f"  ❌ {e}")


# ─── main ────────────────────────────────────────────────────

async def main():
    await test_jd_playwright()
    await test_walmart_playwright()
    test_usda_api()

    print("\n" + "="*60)
    print("  TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
