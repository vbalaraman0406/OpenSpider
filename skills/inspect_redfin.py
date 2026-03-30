import requests
import json

url = 'https://www.redfin.com/stingray/api/gis?al=1&market=seattle&min_stories=1&num_homes=20&ord=price-asc&page_number=1&region_id=18791&region_type=6&sf=1,2,3,5,6,7&status=9&uipt=1&v=8&min_num_beds=5&min_num_baths=2.5&min_year_built=2020'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.redfin.com/city/18791/WA/Vancouver'
}

r = requests.get(url, headers=headers, timeout=15, verify=False)
data = r.text
if data.startswith('{}&&'):
    data = data[4:]
parsed = json.loads(data)
homes = parsed.get('payload', {}).get('homes', [])

# Print the keys of the first home to understand structure
if homes:
    first = homes[0]
    print('TOP LEVEL KEYS:', list(first.keys()))
    for k, v in first.items():
        if isinstance(v, dict):
            print(f'  {k} keys: {list(v.keys())[:20]}')
            # Print a sample of nested values
            for k2, v2 in list(v.items())[:5]:
                print(f'    {k2}: {v2}')
        else:
            print(f'  {k}: {v}')
    print('\n--- FULL FIRST HOME JSON (truncated) ---')
    print(json.dumps(first, indent=2)[:2000])
