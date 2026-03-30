import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.redfin.com/',
}

url = 'https://www.redfin.com/stingray/api/gis?al=1&market=portland&max_price=600000&min_beds=5&min_year_built=2017&num_homes=50&ord=redfin-recommended-asc&page_number=1&region_id=98682&region_type=8&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
r = requests.get(url, headers=headers, timeout=10)
t = r.text
if t.startswith('{}&&'):
    t = t[4:]
d = json.loads(t)
homes = d.get('payload', {}).get('homes', [])
if homes:
    print('First home raw keys:', list(homes[0].keys()))
    print(json.dumps(homes[0], indent=2, default=str)[:2000])
