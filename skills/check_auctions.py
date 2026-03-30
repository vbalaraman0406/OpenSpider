import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# 1. Auction.com
print("=== 1. AUCTION.COM ===")
try:
    r = requests.get('https://www.auction.com/residential/vancouver-wa/', headers=headers, timeout=15, verify=False)
    html = r.text
    print(f"Status: {r.status_code}, Length: {len(html)}")
    beds = re.findall(r'(\d+)\s*(?:bed|br|bedroom)', html.lower())[:20]
    prices = re.findall(r'\$[\d,]+', html)[:20]
    print(f"Beds: {beds}")
    print(f"Prices: {prices}")
    if '5' not in beds:
        print("No 5-bedroom listings found on Auction.com")
except Exception as e:
    print(f"Error: {e}")

# 2. Hubzu
print("\n=== 2. HUBZU ===")
try:
    r = requests.get('https://www.hubzu.com/property-search/WA/Vancouver', headers=headers, timeout=15, verify=False)
    html = r.text
    print(f"Status: {r.status_code}, Length: {len(html)}")
    beds = re.findall(r'(\d+)\s*(?:bed|br|bedroom)', html.lower())[:20]
    prices = re.findall(r'\$[\d,]+', html)[:20]
    print(f"Beds: {beds}")
    print(f"Prices: {prices}")
except Exception as e:
    print(f"Error: {e}")

# 3. Xome
print("\n=== 3. XOME ===")
try:
    r = requests.get('https://www.xome.com/realestate/vancouver-wa', headers=headers, timeout=15, verify=False)
    html = r.text
    print(f"Status: {r.status_code}, Length: {len(html)}")
    beds = re.findall(r'(\d+)\s*(?:bed|br|bedroom)', html.lower())[:20]
    prices = re.findall(r'\$[\d,]+', html)[:20]
    print(f"Beds: {beds}")
    print(f"Prices: {prices}")
except Exception as e:
    print(f"Error: {e}")

# 4. HUD Home Store
print("\n=== 4. HUD HOME STORE ===")
try:
    r = requests.get('https://www.hudhomestore.gov/Listing/PropertySearchResult?sState=WA&sCounty=Clark&iBed=5', headers=headers, timeout=15, verify=False)
    html = r.text
    print(f"Status: {r.status_code}, Length: {len(html)}")
    beds = re.findall(r'(\d+)\s*(?:bed|br|bedroom)', html.lower())[:20]
    prices = re.findall(r'\$[\d,]+', html)[:20]
    print(f"Beds: {beds}")
    print(f"Prices: {prices}")
    # Check for specific listing data
    addresses = re.findall(r'\d+\s+[A-Z][a-zA-Z\s]+(?:St|Ave|Dr|Rd|Ln|Ct|Way|Blvd|Pl)', html)[:10]
    print(f"Addresses: {addresses}")
except Exception as e:
    print(f"Error: {e}")

# 5. Foreclosure.com
print("\n=== 5. FORECLOSURE.COM ===")
try:
    r = requests.get('https://www.foreclosure.com/listings/WA/Vancouver/', headers=headers, timeout=15, verify=False)
    html = r.text
    print(f"Status: {r.status_code}, Length: {len(html)}")
    beds = re.findall(r'(\d+)\s*(?:bed|br|bedroom)', html.lower())[:20]
    prices = re.findall(r'\$[\d,]+', html)[:20]
    print(f"Beds: {beds}")
    print(f"Prices: {prices}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== DONE ===")
