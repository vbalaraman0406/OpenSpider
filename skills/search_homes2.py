import requests
import json
import re
from urllib.parse import quote_plus

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

all_listings = []

# 1. Try Redfin download endpoint
print('=== REDFIN CSV DOWNLOAD ===')
redfin_urls = [
    'https://www.redfin.com/city/19087/WA/Vancouver/filter/property-type=house,min-beds=5,min-baths=2.5,max-baths=3,max-price=600k,min-year-built=2017',
    'https://www.redfin.com/city/16816/WA/Ridgefield/filter/property-type=house,min-beds=5,min-baths=2.5,max-price=600k,min-year-built=2017',
    'https://www.redfin.com/city/1638/WA/Battle-Ground/filter/property-type=house,min-beds=5,min-baths=2.5,max-price=600k,min-year-built=2017',
    'https://www.redfin.com/city/3089/WA/Camas/filter/property-type=house,min-beds=5,min-baths=2.5,max-price=600k,min-year-built=2017',
    'https://www.redfin.com/city/21117/WA/Washougal/filter/property-type=house,min-beds=5,min-baths=2.5,max-price=600k,min-year-built=2017',
]

for url in redfin_urls:
    try:
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        print(f'Redfin {url.split("/")[5]}: status={r.status_code}, len={len(r.text)}')
        # Look for listing cards in HTML
        addresses = re.findall(r'"streetLine":"([^"]+)"', r.text)
        prices = re.findall(r'"price":(\d+)', r.text)
        beds = re.findall(r'"beds":(\d+)', r.text)
        baths = re.findall(r'"baths":(\d+\.?\d*)', r.text)
        sqfts = re.findall(r'"sqFt":(\d+)', r.text)
        urls_found = re.findall(r'"url":"(/WA/[^"]+)"', r.text)
        city_name = url.split('/')[5]
        for i in range(min(len(addresses), len(prices))):
            listing = {
                'address': addresses[i] if i < len(addresses) else 'N/A',
                'price': f'${int(prices[i]):,}' if i < len(prices) else 'N/A',
                'beds': beds[i] if i < len(beds) else 'N/A',
                'baths': baths[i] if i < len(baths) else 'N/A',
                'sqft': sqfts[i] if i < len(sqfts) else 'N/A',
                'year_built': '2017+',
                'source': 'Redfin',
                'link': f'https://www.redfin.com{urls_found[i]}' if i < len(urls_found) else url,
                'city': city_name
            }
            all_listings.append(listing)
            print(f'  Found: {listing["address"]} - {listing["price"]}')
        if not addresses:
            # Try to find any listing data in different format
            cards = re.findall(r'class="[^"]*homecard[^"]*"[^>]*>(.{200,500}?)</div>', r.text, re.DOTALL)
            print(f'  No JSON data found. Found {len(cards)} card divs.')
            # Check for "No results" message
            if 'No results found' in r.text or 'no matching' in r.text.lower():
                print(f'  No results for {city_name}')
    except Exception as e:
        print(f'  Error: {e}')

# 2. Try Zillow search results page
print('\n=== ZILLOW ===')
zillow_urls = [
    'https://www.zillow.com/vancouver-wa/houses/5-_beds/2.5-3_baths/0-600000_price/2017-_built/',
    'https://www.zillow.com/ridgefield-wa/houses/5-_beds/2.5-3_baths/0-600000_price/2017-_built/',
    'https://www.zillow.com/battle-ground-wa/houses/5-_beds/2.5-3_baths/0-600000_price/2017-_built/',
    'https://www.zillow.com/camas-wa/houses/5-_beds/2.5-3_baths/0-600000_price/2017-_built/',
]

for url in zillow_urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f'Zillow {url.split("/")[3]}: status={r.status_code}, len={len(r.text)}')
        # Zillow embeds data in script tags
        matches = re.findall(r'"address":"([^"]+)".*?"price":(\d+).*?"beds":(\d+).*?"baths":(\d+)', r.text[:50000])
        for m in matches:
            print(f'  Found: {m[0]} - ${int(m[1]):,}')
    except Exception as e:
        print(f'  Error: {e}')

# 3. Try Homes.com
print('\n=== HOMES.COM ===')
homes_url = 'https://www.homes.com/vancouver-wa/houses-for-sale/5-bedrooms/2-bathrooms/price-to-600000/year-built-2017/'
try:
    r = requests.get(homes_url, headers=headers, timeout=15)
    print(f'Homes.com: status={r.status_code}, len={len(r.text)}')
except Exception as e:
    print(f'  Error: {e}')

# 4. Google search as fallback
print('\n=== GOOGLE SEARCH ===')
queries = [
    'Vancouver WA 5 bedroom house for sale under $600000 built 2017 2018 2019 2020 2021 2022 2023 2024',
    'Clark County WA 5 bed 3 bath house for sale under 600000 new construction',
]

for q in queries:
    try:
        url = f'https://html.duckduckgo.com/html/?q={quote_plus(q)}'
        r = requests.get(url, headers=headers, timeout=15)
        print(f'DDG search: status={r.status_code}')
        # Extract result snippets
        results = re.findall(r'class="result__snippet">(.*?)</a>', r.text, re.DOTALL)
        for res in results[:5]:
            clean = re.sub(r'<[^>]+>', '', res).strip()
            print(f'  {clean[:200]}')
        # Extract links
        links = re.findall(r'class="result__url"[^>]*href="([^"]+)"', r.text)
        for l in links[:5]:
            print(f'  Link: {l}')
    except Exception as e:
        print(f'  Error: {e}')

print(f'\n=== TOTAL LISTINGS FOUND: {len(all_listings)} ===')
for l in all_listings:
    print(f"{l['address']} | {l['price']} | {l['beds']}bd/{l['baths']}ba | {l['sqft']}sqft | {l['source']} | {l['link']}")
