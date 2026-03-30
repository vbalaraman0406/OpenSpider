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

# Check what region 30772 actually is
gis_url = ('https://www.redfin.com/stingray/api/gis?al=1&market=seattle'
           '&num_homes=5&ord=redfin-recommended-asc&page_number=1'
           '&region_id=30772&region_type=6'
           '&sf=1,2,3,5,6,7&status=9&uipt=1&v=8')

resp = session.get(gis_url, timeout=20, verify=False)
data = resp.text
if data.startswith('{}&&'):
    data = data[4:]
parsed = json.loads(data)
homes = parsed.get('payload', {}).get('homes', [])
print(f'Region 30772: {len(homes)} homes')
for h in homes[:3]:
    print(f"  city={h.get('city')}, state={h.get('state')}, lat={h.get('latLong',{}).get('value',{}).get('latitude')}, lng={h.get('latLong',{}).get('value',{}).get('longitude')}")

# Try autocomplete for Vancouver WA
auto_url = 'https://www.redfin.com/stingray/do/location-autocomplete?location=Vancouver+WA&start=0&count=10&v=2'
resp2 = session.get(auto_url, timeout=15, verify=False)
print(f'\nAutocomplete status: {resp2.status_code}')
data2 = resp2.text
if data2.startswith('{}&&'):
    data2 = data2[4:]
print(f'Autocomplete response: {data2[:500]}')

# Try different region IDs that might be Vancouver WA
# Redfin city IDs for WA cities - let me try a range
for rid in [2846, 18791, 30772, 29470, 16163, 8447, 3218, 1564, 18640, 15519]:
    try:
        url = f'https://www.redfin.com/stingray/api/gis?al=1&num_homes=1&region_id={rid}&region_type=6&status=9&uipt=1&v=8'
        r = session.get(url, timeout=10, verify=False)
        d = r.text
        if d.startswith('{}&&'):
            d = d[4:]
        p = json.loads(d)
        hs = p.get('payload', {}).get('homes', [])
        if hs:
            h = hs[0]
            print(f"Region {rid}: city={h.get('city')}, state={h.get('state')}")
        else:
            # Check if there's region info in payload
            ri = p.get('payload', {}).get('regionInfo', {})
            print(f"Region {rid}: 0 homes, regionInfo={json.dumps(ri)[:200]}")
    except Exception as e:
        print(f"Region {rid}: error - {e}")
