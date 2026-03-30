import requests
import re
import json
import warnings
warnings.filterwarnings('ignore')

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Try Xome API - they often have a JSON API
print("=== XOME API CHECK ===")
try:
    # Try their search API
    r = requests.get('https://www.xome.com/api/search?location=vancouver-wa&beds=5&maxPrice=600000', headers=headers, timeout=15, verify=False)
    print(f"API Status: {r.status_code}, Length: {len(r.text)}")
    if r.status_code == 200:
        try:
            data = json.loads(r.text)
            print(json.dumps(data, indent=2)[:2000])
        except:
            print(r.text[:1000])
except Exception as e:
    print(f"Xome API Error: {e}")

# Try Xome main page and look for embedded JSON/state
print("\n=== XOME PAGE DATA ===")
try:
    r = requests.get('https://www.xome.com/realestate/vancouver-wa?beds=5&maxPrice=600000', headers=headers, timeout=15, verify=False)
    html = r.text
    print(f"Status: {r.status_code}, Length: {len(html)}")
    # Look for __NEXT_DATA__ or similar embedded state
    next_data = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if next_data:
        data = json.loads(next_data.group(1))
        print("Found __NEXT_DATA__:")
        print(json.dumps(data, indent=2)[:2500])
    # Look for window.__INITIAL_STATE__ or similar
    init_state = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
    if init_state:
        print("Found __INITIAL_STATE__")
        print(init_state.group(1)[:2000])
    # Look for any JSON data blocks
    json_blocks = re.findall(r'"properties"\s*:\s*\[([^\]]{100,}?)\]', html)
    if json_blocks:
        print(f"Found {len(json_blocks)} property JSON blocks")
        for b in json_blocks[:2]:
            print(b[:500])
except Exception as e:
    print(f"Xome Error: {e}")

# Try Auction.com API
print("\n=== AUCTION.COM API CHECK ===")
try:
    api_url = 'https://www.auction.com/api/search?location=vancouver-wa&bedrooms=5&maxPrice=600000&propertyType=residential'
    r = requests.get(api_url, headers=headers, timeout=15, verify=False)
    print(f"Status: {r.status_code}, Length: {len(r.text)}")
    if r.status_code == 200:
        print(r.text[:1500])
except Exception as e:
    print(f"Auction.com API Error: {e}")

# Try Hubzu API
print("\n=== HUBZU API CHECK ===")
try:
    api_url = 'https://www.hubzu.com/api/properties?state=WA&city=Vancouver&bedrooms=5'
    r = requests.get(api_url, headers=headers, timeout=15, verify=False)
    print(f"Status: {r.status_code}, Length: {len(r.text)}")
    if r.status_code == 200:
        print(r.text[:1500])
except Exception as e:
    print(f"Hubzu API Error: {e}")

print("\n=== DONE ===")
