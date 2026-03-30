import requests
import json
import warnings
warnings.filterwarnings('ignore')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Upgrade-Insecure-Requests': '1',
})
session.get('https://www.redfin.com/', timeout=15, verify=False)
session.headers.update({
    'Accept': '*/*',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Referer': 'https://www.redfin.com/',
})

# Vancouver WA area zip codes
zip_codes = [
    '98660', '98661', '98662', '98663', '98664', '98665', '98682', '98683', '98684', '98685', '98686',  # Vancouver
    '98642',  # Ridgefield
    '98604',  # Battle Ground
    '98607',  # Camas/Washougal
    '98606',  # Brush Prairie
]

all_listings = []
seen_urls = set()

for zc in zip_codes:
    # Search by zip code using region_type=2 (zip code type)
    # First try to find the region ID for this zip
    # Redfin zip code region IDs are different - let's try direct search
    gis_url = (f'https://www.redfin.com/stingray/api/gis?al=1&market=seattle'
               f'&num_homes=100&ord=redfin-recommended-asc&page_number=1'
               f'&region_id={zc}&region_type=2'
               f'&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
               f'&min_num_beds=5&max_price=600000&min_year_built=2017')
    
    try:
        resp = session.get(gis_url, timeout=15, verify=False)
        data = resp.text
        if data.startswith('{}&&'):
            data = data[4:]
        parsed = json.loads(data)
        homes = parsed.get('payload', {}).get('homes', [])
        
        if homes:
            print(f'Zip {zc}: {len(homes)} homes found')
            for home in homes:
                price_obj = home.get('price', {})
                price = price_obj.get('value', 0) if isinstance(price_obj, dict) else (price_obj or 0)
                beds = home.get('beds', 0)
                baths = home.get('baths', 0)
                sqft_obj = home.get('sqFt', {})
                sqft = sqft_obj.get('value', 'N/A') if isinstance(sqft_obj, dict) else (sqft_obj or 'N/A')
                yb_obj = home.get('yearBuilt', {})
                yb = yb_obj.get('value', 0) if isinstance(yb_obj, dict) else (yb_obj or 0)
                sl_obj = home.get('streetLine', {})
                addr = sl_obj.get('value', '') if isinstance(sl_obj, dict) else (sl_obj or '')
                city = home.get('city', '')
                state = home.get('state', '')
                zipcode = home.get('zip', '')
                url_path = home.get('url', '')
                listing_url = f"https://www.redfin.com{url_path}" if url_path else 'N/A'
                
                if listing_url in seen_urls:
                    continue
                if state != 'WA':
                    continue
                if beds < 5:
                    continue
                try:
                    b = float(baths)
                    if b < 2.5 or b > 3.0:
                        continue
                except:
                    continue
                if price > 600000:
                    continue
                if yb < 2017:
                    continue
                
                seen_urls.add(listing_url)
                full_addr = f"{addr}, {city}, {state} {zipcode}"
                all_listings.append({
                    'address': full_addr,
                    'price': price,
                    'beds': beds,
                    'baths': baths,
                    'sqft': sqft,
                    'year_built': yb,
                    'url': listing_url
                })
        else:
            print(f'Zip {zc}: 0 homes')
    except Exception as e:
        print(f'Zip {zc}: error - {e}')

print(f'\nTotal matching listings: {len(all_listings)}')

with open('redfin_results.json', 'w') as f:
    json.dump(all_listings, f, indent=2)

if all_listings:
    print('\n| Address | Price | Beds | Baths | SqFt | Year Built | URL |')
    print('|---------|-------|------|-------|------|------------|-----|')
    for l in all_listings:
        price_str = f"${l['price']:,.0f}" if isinstance(l['price'], (int, float)) else str(l['price'])
        print(f"| {l['address']} | {price_str} | {l['beds']} | {l['baths']} | {l['sqft']} | {l['year_built']} | [Link]({l['url']}) |")
else:
    print('No matching listings found.')
