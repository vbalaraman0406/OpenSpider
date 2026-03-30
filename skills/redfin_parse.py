import requests
import json
import re
import warnings
warnings.filterwarnings('ignore')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Upgrade-Insecure-Requests': '1',
})
session.get('https://www.redfin.com/', timeout=15, verify=False)

# Search multiple zip codes covering Vancouver WA area
zips = {
    '98660': 'Vancouver', '98661': 'Vancouver', '98662': 'Vancouver',
    '98663': 'Vancouver', '98664': 'Vancouver', '98665': 'Vancouver',
    '98682': 'Vancouver', '98683': 'Vancouver', '98684': 'Vancouver',
    '98685': 'Vancouver', '98686': 'Vancouver',
    '98642': 'Ridgefield', '98604': 'Battle Ground',
    '98607': 'Camas/Washougal', '98606': 'Brush Prairie',
}

all_listings = []
seen_addrs = set()

for zc, area in zips.items():
    url = f'https://www.redfin.com/zipcode/{zc}/filter/property-type=house,max-price=600k,min-beds=5,min-year-built=2017'
    try:
        resp = session.get(url, timeout=15, verify=False)
        if resp.status_code != 200:
            continue
        text = resp.text
        
        # Extract React server state JSON
        # Look for the homes data in the page
        # Try to find listing cards in HTML
        # Redfin uses homeCards or similar patterns
        
        # Method 1: Look for JSON data in script tags
        matches = re.findall(r'"homes"\s*:\s*\[(.*?)\]', text, re.DOTALL)
        if matches:
            for m in matches:
                try:
                    homes_json = json.loads('[' + m + ']')
                    for h in homes_json:
                        addr = h.get('streetLine', h.get('address', ''))
                        if isinstance(addr, dict):
                            addr = addr.get('value', '')
                        if addr in seen_addrs:
                            continue
                        price = h.get('price', {}).get('value', 0) if isinstance(h.get('price'), dict) else h.get('price', 0)
                        beds = h.get('beds', 0)
                        baths = h.get('baths', 0)
                        sqft = h.get('sqFt', {}).get('value', 'N/A') if isinstance(h.get('sqFt'), dict) else h.get('sqFt', 'N/A')
                        yb = h.get('yearBuilt', {}).get('value', 0) if isinstance(h.get('yearBuilt'), dict) else h.get('yearBuilt', 0)
                        url_path = h.get('url', '')
                        city = h.get('city', area)
                        state = h.get('state', 'WA')
                        zipcode = h.get('zip', zc)
                        
                        # Filter
                        try:
                            b = float(baths)
                            if b < 2.5 or b > 3.0:
                                continue
                        except:
                            continue
                        if beds < 5 or price > 600000 or yb < 2017:
                            continue
                        
                        seen_addrs.add(addr)
                        listing_url = f'https://www.redfin.com{url_path}' if url_path else 'N/A'
                        all_listings.append({
                            'address': f'{addr}, {city}, {state} {zipcode}',
                            'price': price, 'beds': beds, 'baths': baths,
                            'sqft': sqft, 'year_built': yb, 'url': listing_url
                        })
                except:
                    pass
        
        # Method 2: Parse listing cards from HTML
        # Look for homecard patterns
        cards = re.findall(r'class="[^"]*(?:HomeCard|homecard|MapHomeCard)[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>', text, re.DOTALL)
        
        # Method 3: Look for address patterns in the page
        addr_matches = re.findall(r'"streetLine"\s*:\s*\{"value"\s*:\s*"([^"]+)"', text)
        price_matches = re.findall(r'"price"\s*:\s*\{"value"\s*:\s*(\d+)', text)
        beds_matches = re.findall(r'"beds"\s*:\s*(\d+)', text)
        baths_matches = re.findall(r'"baths"\s*:\s*([\d.]+)', text)
        sqft_matches = re.findall(r'"sqFt"\s*:\s*\{"value"\s*:\s*(\d+)', text)
        yb_matches = re.findall(r'"yearBuilt"\s*:\s*\{"value"\s*:\s*(\d+)', text)
        url_matches = re.findall(r'"url"\s*:\s*"(/[^"]+/home/\d+)"', text)
        
        if addr_matches:
            print(f'Zip {zc} ({area}): Found {len(addr_matches)} addresses via regex')
            for i in range(len(addr_matches)):
                addr = addr_matches[i]
                if addr in seen_addrs:
                    continue
                price = int(price_matches[i]) if i < len(price_matches) else 0
                beds = int(beds_matches[i]) if i < len(beds_matches) else 0
                baths = float(baths_matches[i]) if i < len(baths_matches) else 0
                sqft = int(sqft_matches[i]) if i < len(sqft_matches) else 'N/A'
                yb = int(yb_matches[i]) if i < len(yb_matches) else 0
                url_path = url_matches[i] if i < len(url_matches) else ''
                
                if beds < 5 or baths < 2.5 or baths > 3.0 or price > 600000 or yb < 2017:
                    continue
                
                seen_addrs.add(addr)
                listing_url = f'https://www.redfin.com{url_path}' if url_path else 'N/A'
                all_listings.append({
                    'address': f'{addr}, {area}, WA {zc}',
                    'price': price, 'beds': beds, 'baths': baths,
                    'sqft': sqft, 'year_built': yb, 'url': listing_url
                })
        else:
            # Check if page says no results
            if 'No results found' in text or 'no matching' in text.lower():
                print(f'Zip {zc} ({area}): No results on page')
            else:
                print(f'Zip {zc} ({area}): Could not parse listings')
    except Exception as e:
        print(f'Zip {zc} ({area}): Error - {e}')

print(f'\nTotal matching listings: {len(all_listings)}')
with open('redfin_results.json', 'w') as f:
    json.dump(all_listings, f, indent=2)

if all_listings:
    print('\n| Address | Price | Beds | Baths | SqFt | Year Built | URL |')
    print('|---------|-------|------|-------|------|------------|-----|')
    for l in all_listings:
        ps = f"${l['price']:,}" if isinstance(l['price'], (int,float)) else str(l['price'])
        print(f"| {l['address']} | {ps} | {l['beds']} | {l['baths']} | {l['sqft']} | {l['year_built']} | [Link]({l['url']}) |")
else:
    print('No matching listings found across all zip codes.')
