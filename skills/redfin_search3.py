import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.redfin.com/',
}

# First, look up Vancouver WA region ID
lookup_url = 'https://www.redfin.com/stingray/do/location-autocomplete?location=Vancouver%20WA&v=2'
try:
    resp = requests.get(lookup_url, headers=headers, timeout=15)
    text = resp.text
    if text.startswith('{}&&'):
        text = text[4:]
    print('Location lookup result:')
    print(text[:1500])
except Exception as e:
    print(f'Lookup error: {e}')

print('\n---\n')

# Try with URL-based search using download endpoint
search_url = 'https://www.redfin.com/stingray/api/gis?al=1&market=portland&max_price=600000&min_baths=2&min_beds=5&min_year_built=2017&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id=18791&region_type=6&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
try:
    resp2 = requests.get(search_url, headers=headers, timeout=15)
    text2 = resp2.text
    if text2.startswith('{}&&'):
        text2 = text2[4:]
    data = json.loads(text2)
    homes = data.get('payload', {}).get('homes', [])
    print(f'Search with region_id 18791: Found {len(homes)} homes')
    if homes:
        for h in homes[:5]:
            print(json.dumps(h, indent=2)[:500])
except Exception as e:
    print(f'Search error: {e}')

print('\n---\n')

# Try with different region IDs for Vancouver WA
for rid in [18791, 30772, 29470]:
    try:
        url = f'https://www.redfin.com/stingray/api/gis?al=1&market=portland&max_price=600000&min_beds=5&min_year_built=2017&num_homes=50&ord=redfin-recommended-asc&page_number=1&region_id={rid}&region_type=6&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
        r = requests.get(url, headers=headers, timeout=10)
        t = r.text
        if t.startswith('{}&&'):
            t = t[4:]
        d = json.loads(t)
        h = d.get('payload', {}).get('homes', [])
        print(f'Region {rid}: {len(h)} homes')
        if h:
            for home in h[:2]:
                city = home.get('city', '')
                state = home.get('state', '')
                print(f'  -> {city}, {state}')
    except Exception as e:
        print(f'Region {rid} error: {e}')
