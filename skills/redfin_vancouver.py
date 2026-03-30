import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.redfin.com/',
}

# Try different region IDs around the range for Vancouver WA
# Vancouver WA is a major city, likely has a specific region ID
# Let me try the gis-csv endpoint which might be less protected

# Try searching with the download/csv endpoint
csv_url = 'https://www.redfin.com/stingray/api/gis-csv?al=1&market=portland&max_price=600000&min_beds=5&min_year_built=2017&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id=18791&region_type=6&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'

# Actually let me try the gis endpoint with different region types
# region_type 6 = city, 2 = county, 8 = zip
# Let me try zip codes for Vancouver WA: 98660, 98661, 98662, 98663, 98664, 98665, 98682, 98683, 98684, 98685, 98686

all_homes = []
zip_codes = ['98660','98661','98662','98663','98664','98665','98682','98683','98684','98685','98686','98604','98606','98607','98642']

for zc in zip_codes:
    try:
        url = f'https://www.redfin.com/stingray/api/gis?al=1&market=portland&max_price=600000&min_beds=5&min_year_built=2017&num_homes=50&ord=redfin-recommended-asc&page_number=1&region_id={zc}&region_type=8&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
        r = requests.get(url, headers=headers, timeout=10)
        t = r.text
        if t.startswith('{}&&'):
            t = t[4:]
        d = json.loads(t)
        homes = d.get('payload', {}).get('homes', [])
        if homes:
            print(f'ZIP {zc}: {len(homes)} homes')
            for h in homes:
                beds = h.get('beds', 0)
                baths = h.get('baths', 0)
                price_obj = h.get('price', {})
                price = price_obj.get('value', 0) if isinstance(price_obj, dict) else price_obj
                yr_obj = h.get('yearBuilt', {})
                yr = yr_obj.get('value', 0) if isinstance(yr_obj, dict) else yr_obj
                sqft_obj = h.get('sqFt', {})
                sqft = sqft_obj.get('value', 0) if isinstance(sqft_obj, dict) else sqft_obj
                addr = h.get('streetLine', {}).get('value', '') if isinstance(h.get('streetLine'), dict) else h.get('streetLine', '')
                city = h.get('city', '')
                state = h.get('state', '')
                zipcode = h.get('zip', '')
                url_path = h.get('url', '')
                link = f'https://www.redfin.com{url_path}' if url_path else ''
                if beds >= 5 and baths >= 2.5 and baths <= 3.0 and price <= 600000 and yr >= 2017:
                    print(f'  MATCH: ${price} | {addr}, {city}, {state} {zipcode} | {beds}bd/{baths}ba | {sqft}sqft | {yr} | {link}')
                    all_homes.append({'price':price,'addr':addr,'city':city,'state':state,'zip':zipcode,'beds':beds,'baths':baths,'sqft':sqft,'year':yr,'link':link})
        else:
            print(f'ZIP {zc}: 0 homes')
    except Exception as e:
        print(f'ZIP {zc} error: {e}')

print(f'\nTotal matching homes: {len(all_homes)}')
for h in all_homes:
    print(f"${h['price']} | {h['addr']}, {h['city']}, {h['state']} {h['zip']} | {h['beds']}bd/{h['baths']}ba | {h['sqft']}sqft | {h['year']} | {h['link']}")
