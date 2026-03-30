import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

results = []

cities = {
    'Vancouver, WA': '19118',
    'Battle Ground, WA': '2590',
    'Camas, WA': '4830',
    'Washougal, WA': '23370',
    'Ridgefield, WA': '17460',
}

for city, region_id in cities.items():
    try:
        url = f'https://www.redfin.com/stingray/api/gis?al=1&market=seattle&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id={region_id}&region_type=6&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            text = resp.text
            if text.startswith('{}&&'):
                text = text[4:]
            data = json.loads(text)
            homes = data.get('payload', {}).get('homes', [])
            
            # Debug: find homes with 5+ beds and print their raw data
            for h in homes:
                beds = h.get('beds', 0)
                if beds and int(beds) >= 5:
                    price = h.get('price', 'N/A')
                    baths = h.get('baths', 0)
                    sqft = h.get('sqFt', 'N/A')
                    yr = h.get('yearBuilt', 'N/A')
                    addr = f"{h.get('streetLine', '')} {h.get('city', '')} {h.get('state', '')} {h.get('zip', '')}"
                    link = h.get('url', '')
                    if link and not link.startswith('http'):
                        link = 'https://www.redfin.com' + link
                    
                    print(f"\n{city} - 5+ bed home:")
                    print(f"  addr: {addr}")
                    print(f"  price: {price} (type: {type(price).__name__})")
                    print(f"  beds: {beds}, baths: {baths}")
                    print(f"  sqft: {sqft} (type: {type(sqft).__name__})")
                    print(f"  yearBuilt: {yr} (type: {type(yr).__name__})")
                    print(f"  url: {link}")
                    
                    # Parse values
                    try:
                        if isinstance(price, dict):
                            price_val = price.get('value', 0)
                        elif isinstance(price, str):
                            price_val = int(price.replace('$','').replace(',',''))
                        else:
                            price_val = int(price)
                        
                        baths_val = float(baths) if baths else 0
                        
                        if isinstance(yr, dict):
                            yr_val = yr.get('value', 0)
                        elif isinstance(yr, str):
                            yr_val = int(yr) if len(str(yr)) == 4 else 0
                        else:
                            yr_val = int(yr) if yr and int(yr) > 1900 and int(yr) < 2030 else 0
                        
                        if isinstance(sqft, dict):
                            sqft_val = sqft.get('value', 0)
                        elif isinstance(sqft, str):
                            sqft_val = int(sqft.replace(',',''))
                        else:
                            sqft_val = int(sqft) if sqft else 0
                        
                        print(f"  PARSED: price={price_val}, baths={baths_val}, yr={yr_val}, sqft={sqft_val}")
                        
                        # Apply filters
                        if 2.5 <= baths_val <= 3.0 and price_val <= 600000 and yr_val >= 2017:
                            results.append({
                                'address': addr.strip(),
                                'price': f"${price_val:,}",
                                'beds': int(beds),
                                'baths': baths_val,
                                'sqft': sqft_val,
                                'year': yr_val,
                                'url': link,
                                'source': 'Redfin'
                            })
                            print(f"  >>> MATCH! <<<")
                        else:
                            reasons = []
                            if baths_val < 2.5 or baths_val > 3.0:
                                reasons.append(f'baths={baths_val}')
                            if price_val > 600000:
                                reasons.append(f'price=${price_val:,}')
                            if yr_val < 2017:
                                reasons.append(f'year={yr_val}')
                            print(f"  FILTERED OUT: {', '.join(reasons)}")
                    except Exception as e:
                        print(f"  Parse error: {e}")
    except Exception as e:
        print(f"Error for {city}: {e}")

print(f"\n\n=== TOTAL MATCHING: {len(results)} ===")
for r in results:
    print(f"{r['address']} | {r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built:{r['year']} | {r['url']}")

with open('redfin_results.json', 'w') as f:
    json.dump(results, f, indent=2)
