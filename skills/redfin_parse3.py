import json
import re

with open('redfin_page.html', 'r') as f:
    html = f.read()

match = re.search(r'root\.__reactServerState\.InitialContext\s*=\s*({.*?});\s*(?:</script>|root\.)', html, re.DOTALL)
if not match:
    match = re.search(r'InitialContext\s*=\s*({.+?})\s*;\s*</script>', html, re.DOTALL)

if match:
    ctx = json.loads(match.group(1))
    cache = ctx.get('ReactServerAgent.cache', {}).get('dataCache', {})
    
    all_homes = []
    for key in cache:
        val = cache[key]
        rb = val.get('responseBody', {})
        if isinstance(rb, str):
            try:
                rb = json.loads(rb)
            except:
                continue
        if isinstance(rb, dict):
            payload = rb.get('payload', {})
            if isinstance(payload, dict):
                homes = payload.get('homes', [])
                if homes:
                    print(f'Cache key has {len(homes)} homes: {key[:60]}')
                    all_homes.extend(homes)
    
    print(f'\nTotal homes found in cache: {len(all_homes)}')
    
    # Filter and extract
    results = []
    for h in all_homes:
        beds = h.get('beds', 0)
        baths = h.get('baths', 0)
        price = h.get('price', {}).get('value', 0) if isinstance(h.get('price'), dict) else h.get('price', 0)
        yb = h.get('yearBuilt', {}).get('value', 0) if isinstance(h.get('yearBuilt'), dict) else h.get('yearBuilt', 0)
        sqft = h.get('sqFt', {}).get('value', 'N/A') if isinstance(h.get('sqFt'), dict) else h.get('sqFt', 'N/A')
        addr = h.get('streetLine', {}).get('value', '') if isinstance(h.get('streetLine'), dict) else h.get('streetLine', '')
        city = h.get('city', '')
        state = h.get('state', '')
        zc = h.get('zip', '')
        url_path = h.get('url', '')
        
        print(f'  {addr}, {city} {state} - beds={beds}, baths={baths}, price={price}, yb={yb}')
        
        # Apply filters
        if beds < 5:
            continue
        try:
            b = float(baths)
            if b < 2.5 or b > 3.0:
                continue
        except:
            continue
        if price > 600000 or price == 0:
            continue
        if yb < 2017:
            continue
        
        listing_url = f'https://www.redfin.com{url_path}' if url_path else 'N/A'
        results.append({
            'address': f'{addr}, {city}, {state} {zc}',
            'price': price, 'beds': beds, 'baths': baths,
            'sqft': sqft, 'year_built': yb, 'url': listing_url
        })
    
    print(f'\nFiltered results: {len(results)}')
    with open('redfin_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    for r in results:
        ps = f"${r['price']:,}" if isinstance(r['price'], (int,float)) else str(r['price'])
        print(f"MATCH: {r['address']} | {ps} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | {r['year_built']} | {r['url']}")
else:
    print('Could not find InitialContext in HTML')
