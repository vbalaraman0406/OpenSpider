import requests
import json
import re
import time

# Use a more realistic browser session with cookies
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'max-age=0',
    'Sec-Ch-Ua': '"Chromium";v="131", "Not_A Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
})

results = []

# ===== HOMES.COM =====
print('=== Homes.com Search ===')
try:
    homes_url = 'https://www.homes.com/vancouver-wa/houses-for-sale/5-bedrooms/2-bathrooms/p1/?price-max=600000'
    resp = session.get(homes_url, timeout=15)
    print(f'Homes.com status: {resp.status_code}, length: {len(resp.text)}')
    if resp.status_code == 200:
        # Look for listing data in HTML
        # Homes.com uses Next.js with __NEXT_DATA__
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text)
        if match:
            next_data = json.loads(match.group(1))
            props = next_data.get('props', {}).get('pageProps', {})
            listings = props.get('listings', props.get('searchResults', props.get('properties', [])))
            if isinstance(listings, dict):
                listings = listings.get('results', listings.get('listings', []))
            print(f'Found {len(listings) if isinstance(listings, list) else "unknown"} listings')
            if isinstance(listings, list):
                for l in listings:
                    addr = l.get('address', l.get('fullAddress', 'N/A'))
                    if isinstance(addr, dict):
                        addr = f"{addr.get('street','')}, {addr.get('city','')}, {addr.get('state','')} {addr.get('zip','')}"
                    price = l.get('price', l.get('listPrice', 'N/A'))
                    beds = l.get('beds', l.get('bedrooms', 'N/A'))
                    baths = l.get('baths', l.get('bathrooms', 'N/A'))
                    sqft = l.get('sqft', l.get('squareFeet', 'N/A'))
                    year = l.get('yearBuilt', 'N/A')
                    url = l.get('url', l.get('detailUrl', ''))
                    if url and not url.startswith('http'):
                        url = 'https://www.homes.com' + url
                    
                    try:
                        if int(beds) >= 5 and float(baths) >= 2.5 and float(baths) <= 3 and int(year) >= 2017:
                            results.append({'address': addr, 'price': price, 'beds': beds, 'baths': baths, 'sqft': sqft, 'year_built': year, 'source': 'Homes.com', 'url': url})
                    except:
                        pass
        else:
            print('No __NEXT_DATA__ found')
            # Try to find listing cards in HTML
            cards = re.findall(r'class="[^"]*listing-card[^"]*".*?</article>', resp.text[:100000], re.DOTALL)
            print(f'Found {len(cards)} listing cards')
    else:
        print(f'Response: {resp.text[:300]}')
except Exception as e:
    print(f'Homes.com error: {e}')

# ===== MOVOTO =====
print('\n=== Movoto Search ===')
try:
    movoto_url = 'https://www.movoto.com/vancouver-wa/houses-for-sale/?minBeds=5&minBaths=2&maxPrice=600000'
    resp = session.get(movoto_url, timeout=15)
    print(f'Movoto status: {resp.status_code}, length: {len(resp.text)}')
except Exception as e:
    print(f'Movoto error: {e}')

# ===== GOOGLE SEARCH FOR LISTINGS =====
print('\n=== Google Search for Listings ===')
search_queries = [
    'Vancouver WA 5 bedroom house for sale under 600000 built 2017 2018 2019 2020 2021 2022 2023 2024 2025',
    'Ridgefield WA 5 bedroom house for sale under 600000 new construction',
    'Battle Ground WA 5 bedroom house for sale under 600000',
    'Camas WA 5 bedroom house for sale under 600000',
]

for query in search_queries[:2]:  # Limit to avoid rate limiting
    try:
        google_url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
        resp = session.get(google_url, timeout=15)
        print(f'Google "{query[:40]}...": status {resp.status_code}')
        if resp.status_code == 200:
            # Extract any listing URLs from Google results
            urls = re.findall(r'https?://(?:www\.)?(?:zillow|redfin|realtor)\.com/[^"\s<>]+', resp.text)
            print(f'  Found {len(urls)} real estate URLs')
            for u in urls[:5]:
                print(f'    {u[:100]}')
        time.sleep(1)
    except Exception as e:
        print(f'Google error: {e}')

# ===== REDFIN with different approach =====
print('\n=== Redfin Direct Page Fetch ===')
try:
    # Try fetching the actual Redfin search page
    redfin_url = 'https://www.redfin.com/city/19418/WA/Vancouver/filter/property-type=house,min-beds=5,min-baths=2,max-price=600000,min-year-built=2017'
    session.headers['Referer'] = 'https://www.google.com/'
    resp = session.get(redfin_url, timeout=15)
    print(f'Redfin page status: {resp.status_code}, length: {len(resp.text)}')
    if resp.status_code == 200:
        # Look for listing data
        match = re.search(r'window\.__reactServerState\s*=\s*({.*?});', resp.text[:100000])
        if match:
            print('Found __reactServerState')
        
        # Try to find property cards
        addresses = re.findall(r'"streetLine"\s*:\s*"([^"]+)"', resp.text)
        prices = re.findall(r'"price"\s*:\s*{\s*"value"\s*:\s*(\d+)', resp.text)
        print(f'Found {len(addresses)} addresses, {len(prices)} prices in Redfin HTML')
        
        # Also try to find the preloaded data
        match2 = re.search(r'"homes"\s*:\s*\[(.+?)\]', resp.text[:200000], re.DOTALL)
        if match2:
            print('Found homes array in Redfin HTML')
            try:
                homes_text = '[' + match2.group(1) + ']'
                # This might be too large/complex to parse directly
                # Extract individual home objects
                home_blocks = re.findall(r'\{"mlsId".*?"yearBuilt"\s*:\s*\d+.*?\}', homes_text[:50000])
                print(f'Found {len(home_blocks)} home blocks')
            except:
                pass
        
        # Try simpler extraction
        for i, addr in enumerate(addresses[:20]):
            price = prices[i] if i < len(prices) else 'N/A'
            print(f'  {addr} - ${price}')
    elif resp.status_code == 403:
        print('Redfin blocked (403)')
        print(f'Response: {resp.text[:200]}')
except Exception as e:
    print(f'Redfin page error: {e}')

print(f'\n=== TOTAL RESULTS: {len(results)} ===')
for i, r in enumerate(results):
    print(f"{i+1}. {r['address']} | {r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built {r['year_built']} | {r['source']} | {r['url']}")

with open('search_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f'Results saved to search_results.json')
