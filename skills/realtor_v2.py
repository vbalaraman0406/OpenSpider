import requests
from bs4 import BeautifulSoup
import json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
})

cities = ['Vancouver_WA', 'Ridgefield_WA', 'Battle-Ground_WA', 'Camas_WA', 'Washougal_WA', 'Brush-Prairie_WA']
all_listings = []

for city in cities:
    url = f'https://www.realtor.com/realestateandhomes-search/{city}/beds-5/baths-2/price-na-600000/age-8'
    print(f'Fetching: {city}')
    try:
        resp = session.get(url, timeout=20)
        print(f'  Status: {resp.status_code}, Len: {len(resp.text)}')
        soup = BeautifulSoup(resp.text, 'html.parser')
        nd = soup.find('script', {'id': '__NEXT_DATA__'})
        if nd and nd.string:
            data = json.loads(nd.string)
            pp = data.get('props', {}).get('pageProps', {})
            print(f'  pageProps keys: {list(pp.keys())[:10]}')
            sr = pp.get('searchResults', pp.get('properties', {}))
            if isinstance(sr, dict):
                hs = sr.get('home_search', sr)
                results = hs.get('results', hs.get('properties', []))
                print(f'  Results count: {len(results) if results else 0}')
                if results:
                    for r in results:
                        desc = r.get('description', {})
                        loc = r.get('location', {})
                        addr = loc.get('address', {}) if isinstance(loc, dict) else {}
                        beds = desc.get('beds', 0) or 0
                        baths = desc.get('baths', 0) or 0
                        price = r.get('list_price', 0) or 0
                        yr = desc.get('year_built', 0) or 0
                        sqft = desc.get('sqft', 'N/A')
                        href = r.get('href', '')
                        address = f"{addr.get('line', '')} {addr.get('city', '')} {addr.get('state_code', '')} {addr.get('postal_code', '')}".strip()
                        if beds >= 5 and baths >= 2.5 and baths <= 3.5 and price <= 600000 and yr >= 2017:
                            listing = {
                                'address': address,
                                'price': price,
                                'beds': beds,
                                'baths': baths,
                                'sqft': sqft,
                                'year': yr,
                                'link': 'https://www.realtor.com' + href if href else 'N/A',
                                'source': 'Realtor.com'
                            }
                            all_listings.append(listing)
                            print(f'    MATCH: {address} | ${price} | {beds}bd/{baths}ba | {sqft}sqft | {yr}')
            else:
                print(f'  searchResults type: {type(sr)}')
        else:
            print('  No __NEXT_DATA__ found')
            # Try finding JSON-LD or other data
            scripts = soup.find_all('script', type='application/json')
            print(f'  Found {len(scripts)} JSON scripts')
    except Exception as e:
        print(f'  Error: {e}')

print(f'\n=== TOTAL MATCHING LISTINGS: {len(all_listings)} ===')
for i, l in enumerate(all_listings, 1):
    print(f"{i}. {l['address']} | ${l['price']:,} | {l['beds']}bd/{l['baths']}ba | {l['sqft']}sqft | {l['year']} | {l['link']}")

# Save to file for later use
with open('realtor_results.json', 'w') as f:
    json.dump(all_listings, f, indent=2)
