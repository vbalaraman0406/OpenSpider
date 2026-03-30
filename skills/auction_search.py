import requests
import json

results = []

# Site 1: Auction.com - search via their API
print("=== AUCTION.COM ===")
try:
    url = "https://www.auction.com/api/search"
    # Try their search page directly
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    r = requests.get("https://www.auction.com/residential/vancouver-wa/", headers=headers, timeout=15)
    print(f"Auction.com status: {r.status_code}")
    if r.status_code == 200:
        # Check if there are any 5-bed listings mentioned
        text = r.text
        if '5 bed' in text.lower() or '5 br' in text.lower() or '5 Bed' in text:
            print("Found references to 5-bed properties")
        else:
            print("No 5-bed references found on page")
        # Count total listings
        import re
        listing_count = text.count('property-card') or text.count('auction-item')
        print(f"Listing card references: {listing_count}")
except Exception as e:
    print(f"Auction.com error: {e}")

# Site 2: HUD Home Store
print("\n=== HUD HOME STORE ===")
try:
    # HUD has a search API
    url = "https://www.hudhomestore.gov/Listing/PropertySearchResult"
    params = {
        "sState": "WA",
        "sCounty": "Clark",
        "iMinBR": "5",
        "iMaxBR": "5",
        "iMaxListPrice": "600000"
    }
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    r = requests.get("https://www.hudhomestore.gov/Listing/PropertySearchResult", params=params, headers=headers, timeout=15)
    print(f"HUD status: {r.status_code}")
    if r.status_code == 200:
        if 'No properties found' in r.text or 'no results' in r.text.lower():
            print("No matching HUD properties found")
        else:
            print(f"Page length: {len(r.text)} chars")
            # Look for addresses
            addresses = re.findall(r'\d+\s+[A-Z][a-zA-Z\s]+(?:St|Ave|Dr|Rd|Blvd|Ct|Ln|Way|Pl)', r.text[:5000])
            if addresses:
                print(f"Possible addresses found: {addresses[:5]}")
            else:
                print("No clear address patterns found")
except Exception as e:
    print(f"HUD error: {e}")

# Site 3: Foreclosure.com
print("\n=== FORECLOSURE.COM ===")
try:
    url = "https://www.foreclosure.com/search/WA/Clark-County/"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    r = requests.get(url, headers=headers, timeout=15)
    print(f"Foreclosure.com status: {r.status_code}")
    if r.status_code == 200:
        print(f"Page length: {len(r.text)} chars")
except Exception as e:
    print(f"Foreclosure.com error: {e}")

# Site 4: Hubzu
print("\n=== HUBZU.COM ===")
try:
    url = "https://www.hubzu.com/property-search/WA/Vancouver"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    r = requests.get(url, headers=headers, timeout=15)
    print(f"Hubzu status: {r.status_code}")
    if r.status_code == 200:
        print(f"Page length: {len(r.text)} chars")
except Exception as e:
    print(f"Hubzu error: {e}")

# Site 5: Xome
print("\n=== XOME.COM ===")
try:
    url = "https://www.xome.com/realestate/Vancouver-WA"
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    r = requests.get(url, headers=headers, timeout=15)
    print(f"Xome status: {r.status_code}")
    if r.status_code == 200:
        print(f"Page length: {len(r.text)} chars")
except Exception as e:
    print(f"Xome error: {e}")

print("\n=== INITIAL SCAN COMPLETE ===")
