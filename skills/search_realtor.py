import requests
import json
import warnings
warnings.filterwarnings('ignore')

# Try Realtor.com API
url = 'https://www.realtor.com/api/v1/hulk_main_srp?client_id=rdc-x&schema=vesta'

payload = {
    "query": {
        "status": ["for_sale"],
        "primary": True,
        "search_location": {"location": "Vancouver, WA"},
        "beds_min": 5,
        "baths_min": 2.5,
        "year_built_min": 2020,
        "type": ["single_family"]
    },
    "sort": {"direction": "asc", "field": "list_price"},
    "limit": 20,
    "offset": 0
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

try:
    r = requests.post(url, json=payload, headers=headers, timeout=15, verify=False)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(json.dumps(data, indent=2)[:2500])
    else:
        print(f'Response: {r.text[:500]}')
except Exception as e:
    print(f'Error: {e}')

# Also try the Homes.com / alternative approach
print('\n--- Trying alternative Google approach ---')
try:
    google_url = 'https://www.google.com/search?q=Vancouver+WA+5+bedroom+2.5+bath+house+for+sale+new+construction+under+700000'
    r2 = requests.get(google_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}, timeout=15, verify=False)
    # Extract snippets with prices
    import re
    prices = re.findall(r'\$[\d,]+', r2.text)
    addresses = re.findall(r'\d+\s+[A-Z][a-z]+\s+(?:St|Ave|Dr|Ct|Ln|Way|Blvd|Rd|Pl|Cir)', r2.text)
    print(f'Found {len(prices)} price mentions, {len(addresses)} address mentions')
    for p in prices[:10]:
        print(f'  Price: {p}')
    for a in addresses[:10]:
        print(f'  Address: {a}')
except Exception as e:
    print(f'Google error: {e}')
