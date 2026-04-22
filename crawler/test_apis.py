"""
Quick smoke test for official APIs.
Usage:
  python crawler/test_apis.py kamis
  python crawler/test_apis.py kroger
  python crawler/test_apis.py all
"""

import sys


def test_kamis():
    print("\n=== KAMIS API Test ===")
    from sources.korea import KAMIS_KEY, KAMIS_ID, _fetch_price
    if not KAMIS_KEY:
        print("❌ KAMIS_API_KEY not set"); return

    print(f"  Key: {KAMIS_KEY[:6]}...  ID: {KAMIS_ID}")
    # Test tomato (code 211, category 100)
    price = _fetch_price("100", "211")
    if price:
        print(f"  ✅ 토마토: ₩{round(price/10)}/100g  (raw: ₩{price}/kg)")
    else:
        print("  ❌ Price fetch failed — check key/ID or try again tomorrow")


def test_kroger():
    print("\n=== Kroger API Test ===")
    from sources.usa import CLIENT_ID, CLIENT_SECRET, _get_token, _get_location_id, _search_product
    if not CLIENT_ID:
        print("❌ KROGER_CLIENT_ID not set"); return

    print(f"  Client ID: {CLIENT_ID[:8]}...")
    try:
        token = _get_token()
        print("  ✅ Token obtained")
        location_id = _get_location_id(token)
        print(f"  ✅ Location ID: {location_id}")
        result = _search_product(token, location_id, "roma tomatoes")
        if result:
            usd, grams = result
            print(f"  ✅ Tomato: ${usd:.2f} / {grams:.0f}g  →  ${usd/grams*100:.2f}/100g")
        else:
            print("  ⚠️  Product found but no parseable price/size")
    except Exception as e:
        print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target in ("kamis", "all"):
        test_kamis()
    if target in ("kroger", "all"):
        test_kroger()
