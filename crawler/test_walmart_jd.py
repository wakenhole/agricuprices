"""
Walmart & JD.com connectivity test
Tries multiple approaches and reports exactly what each site returns.
"""

import json
import re
import sys
import time
import requests
from bs4 import BeautifulSoup

TIMEOUT = 20

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}

CN_HEADERS = {
    **BROWSER_HEADERS,
    "Accept-Language": "zh-CN,zh;q=0.9",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print("="*60)


def report(label: str, r: requests.Response) -> None:
    print(f"\n[{label}]")
    print(f"  Status      : {r.status_code}")
    print(f"  Content-Type: {r.headers.get('Content-Type', '-')}")
    print(f"  Body length : {len(r.content)} bytes")

    text = r.text[:2000]

    # detect bot challenge pages
    challenges = ["captcha", "robot", "cloudflare", "incapsula", "datadome",
                  "challenge", "px_captcha", "perimeterx"]
    found = [c for c in challenges if c.lower() in text.lower()]
    if found:
        print(f"  ⚠️  Bot challenge detected: {found}")
    elif r.status_code == 200:
        print(f"  ✅ 200 OK — scanning for price data...")
        # look for price-like patterns
        prices = re.findall(r'(?:price|Price|PRICE)["\s:]+(\d+\.?\d*)', text)
        if prices:
            print(f"  💰 Price candidates: {prices[:5]}")
        else:
            print(f"  ℹ️  No obvious price fields found in first 2000 chars")


# ─────────────────────────────────────────────────────────────
# WALMART
# ─────────────────────────────────────────────────────────────
section("WALMART — Test 1: Homepage")
try:
    r = requests.get("https://www.walmart.com", headers=BROWSER_HEADERS, timeout=TIMEOUT)
    report("walmart.com /", r)
except Exception as e:
    print(f"  ❌ Exception: {e}")

time.sleep(2)

section("WALMART — Test 2: Search (tomato)")
try:
    r = requests.get(
        "https://www.walmart.com/search",
        params={"q": "tomato"},
        headers=BROWSER_HEADERS,
        timeout=TIMEOUT,
    )
    report("walmart.com /search?q=tomato", r)
    if r.status_code == 200:
        # Try to extract __NEXT_DATA__
        match = re.search(r'__NEXT_DATA__\s*=\s*(\{.*?\})\s*;', r.text, re.DOTALL)
        if match:
            try:
                nd = json.loads(match.group(1))
                items = (nd.get("props", {})
                           .get("pageProps", {})
                           .get("initialData", {})
                           .get("searchResult", {})
                           .get("itemStacks", [{}])[0]
                           .get("items", []))
                print(f"  📦 __NEXT_DATA__ found, items: {len(items)}")
                if items:
                    p = items[0].get("price", {})
                    print(f"  💰 First item price: {p}")
            except Exception as e:
                print(f"  ⚠️  __NEXT_DATA__ parse error: {e}")
        else:
            print("  ℹ️  No __NEXT_DATA__ found")
except Exception as e:
    print(f"  ❌ Exception: {e}")

time.sleep(2)

section("WALMART — Test 3: Open API (no auth)")
try:
    r = requests.get(
        "https://www.walmart.com/api/2/page/store-header",
        headers={**BROWSER_HEADERS, "Accept": "application/json"},
        timeout=TIMEOUT,
    )
    report("walmart.com api/store-header", r)
except Exception as e:
    print(f"  ❌ Exception: {e}")

time.sleep(3)

# ─────────────────────────────────────────────────────────────
# JD.COM
# ─────────────────────────────────────────────────────────────
section("JD.COM — Test 1: Homepage")
try:
    r = requests.get("https://www.jd.com", headers=CN_HEADERS, timeout=TIMEOUT)
    report("jd.com /", r)
except Exception as e:
    print(f"  ❌ Exception: {e}")

time.sleep(2)

section("JD.COM — Test 2: Search (番茄)")
try:
    r = requests.get(
        "https://search.jd.com/Search",
        params={"keyword": "番茄 500g", "enc": "utf-8"},
        headers=CN_HEADERS,
        timeout=TIMEOUT,
    )
    report("search.jd.com 番茄", r)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        price_tag = soup.select_one("li.gl-item .p-price strong i")
        if price_tag:
            print(f"  💰 Price found: ¥{price_tag.get_text(strip=True)}")
        else:
            print("  ℹ️  No price tag found — JS rendering may be required")
except Exception as e:
    print(f"  ❌ Exception: {e}")

time.sleep(2)

section("JD.COM — Test 3: JD Fresh category page")
try:
    r = requests.get(
        "https://channel.jd.com/fresh.html",
        headers=CN_HEADERS,
        timeout=TIMEOUT,
    )
    report("jd.com fresh channel", r)
except Exception as e:
    print(f"  ❌ Exception: {e}")

print("\n" + "="*60)
print("  TEST COMPLETE")
print("="*60)
