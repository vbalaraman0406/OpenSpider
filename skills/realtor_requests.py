import requests
import re
import json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive'
})

cities = [
    ('Vancouver_WA', 'Vancouver WA'),
    ('Ridgefield_WA', 'Ridgefield WA'),
    ('Battle-Ground_WA', 'Battle Ground WA'),
    ('Camas_WA', 'Camas WA'),
    ('Washougal_WA', 'Washougal WA'),
    ('Brush-Prairie_WA', 'Brush Prairie WA')
]

all_listings = []

for city_slug, city_name in cities:
    url = f'https://www.realtor.com/realestateandhomes-search/{city_slug}/beds-5/baths-2/price-na-600000/age-8'
    try:
        resp = session.get(url, timeout=20, allow_redirects=True)
        html = resp.text
        final_url = resp.url
        print(f'{city_name}: {resp.status_code} | {len(html)} bytes | URL: {final_url[:80]}')
        
        if 'realtor.com' not in final_url:
            print(f'  REDIRECTED away from realtor.com')
            continue
        
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if match:
            data = json.loads(match.group(1))
            page_props = data.get('props', {}).get('pageProps', {})
            
            search_results = page_props.get('searchResults', {})
            if isinstance(search_results, dict):
                home_search = search_results.get('home_search', {})
                if isinstance(home_search, dict):
                    results = home_search.get('results', [])
                    total = home_search.get('total', 0)
                    print(f'  Total: {total}, Page results: {len(results)}')
                    
                    for p in results:
                        desc = p.get('description', {})
                        loc = p.get('location', {}).get('address', {})
                        addr = f"{loc.get('line', '')}, {loc.get('city', '')}, {loc.get('state_code', '')} {loc.get('postal_code', '')}"
                        
                        price = p.get('list_price', 0)
                        beds = desc.get('beds', 0)
                        baths = desc.get('baths', 0)
                        sqft = desc.get('sqft', 'N/A')
                        yr = desc.get('year_built', 0)
                        href = p.get('href', '')
                        link = f'https://www.realtor.com{href}' if href and not href.startswith('http') else href
                        
                        try:
                            baths_num = float(baths) if baths else 0
                            yr_num = int(yr) if yr else 0
                            price_num = int(price) if price else 0
                        except:
                            baths_num = 0
                            yr_num = 0
                            price_num = 0
                        
                        if baths_num >= 2.5 and yr_num >= 2017 and 0 < price_num <= 600000:
                            listing = {
                                'address': addr,
                                'price': f'${price_num:,}',
                                'beds': beds,
                                'baths': baths,
                                'sqft': sqft if sqft else 'N/A',
                                'year_built': yr,
                                'link': link if link else 'N/A'
                            }
                            all_listings.append(listing)
                            print(f'  MATCH: {addr} | ${price_num:,} | {beds}bd/{baths}ba | {sqft}sqft | Built {yr}')
                else:
                    print(f'  home_search type: {type(home_search)}')
            else:
                # Try alternate structure
                keys = list(page_props.keys())[:15]
                print(f'  pageProps keys: {keys}')
        else:
            print(f'  No __NEXT_DATA__ found')
            # Show snippet
            title_match = re.search(r'<title>(.*?)</title>', html)
            if title_match:
                print(f'  Title: {title_match.group(1)}')
            print(f'  Snippet: {html[:400]}')
    except Exception as e:
        print(f'{city_name}: Error - {e}')

print(f'\n=== TOTAL MATCHING LISTINGS: {len(all_listings)} ===')
for i, l in enumerate(all_listings, 1):
    print(f'{i}. {l["address"]} | {l["price"]} | {l["beds"]}bd/{l["baths"]}ba | {l["sqft"]}sqft | Built {l["year_built"]} | {l["link"]}')

# Save results to JSON
with open('/tmp/realtor_results.json', 'w') as f:
    json.dump(all_listings, f, indent=2)
print(f'\nResults saved to /tmp/realtor_results.json')
