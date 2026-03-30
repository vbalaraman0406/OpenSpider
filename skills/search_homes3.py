import requests
import json
import subprocess

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# First, find correct Redfin region IDs for our cities
cities = ['Vancouver, WA', 'Battle Ground, WA', 'Ridgefield, WA', 'Camas, WA', 'Washougal, WA', 'Brush Prairie, WA']

for city in cities:
    try:
        url = f'https://www.redfin.com/stingray/do/location-autocomplete?location={city.replace(" ", "%20").replace(",", "%2C")}&start=0&count=5&v=2'
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        data = resp.text
        if '&&' in data:
            data = data.split('&&')[1]
        result = json.loads(data)
        sections = result.get('payload', {}).get('sections', [])
        for section in sections:
            for row in section.get('rows', []):
                name = row.get('name', '')
                rid = row.get('id', '')
                rtype = row.get('type', '')
                subname = row.get('subName', '')
                if 'WA' in str(subname) or 'WA' in str(name):
                    print(f'{city}: id={rid}, type={rtype}, name={name}, subName={subname}')
    except Exception as e:
        print(f'Error looking up {city}: {e}')

print('\n--- Now searching with correct IDs ---')
