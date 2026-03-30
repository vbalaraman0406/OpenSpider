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

gis_url = ('https://www.redfin.com/stingray/api/gis?al=1&market=seattle'
           '&num_homes=350&ord=redfin-recommended-asc&page_number=1'
           '&region_id=30772&region_type=6'
           '&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
           '&min_num_beds=5&max_price=600000&min_year_built=2017')

resp = session.get(gis_url, timeout=20, verify=False)
data = resp.text
if data.startswith('{}&&'):
    data = data[4:]
parsed = json.loads(data)
homes = parsed.get('payload', {}).get('homes', [])
print(f'Total homes: {len(homes)}')

# Print first 3 homes raw structure
for i, home in enumerate(homes[:3]):
    print(f'\n--- Home {i+1} ---')
    print(json.dumps(home, indent=2)[:800])

# Print all unique keys
if homes:
    print(f'\n--- All keys in first home ---')
    print(sorted(homes[0].keys()))

# Check what cities/states are in the results
cities_found = set()
states_found = set()
baths_values = set()
for h in homes:
    cities_found.add(h.get('city', 'NONE'))
    states_found.add(h.get('state', 'NONE'))
    baths_values.add(h.get('baths', 'NONE'))

print(f'\nCities found: {cities_found}')
print(f'States found: {states_found}')
print(f'Baths values: {sorted(baths_values)}')
