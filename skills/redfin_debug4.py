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

# Check what zip 98660 actually returns
gis_url = ('https://www.redfin.com/stingray/api/gis?al=1&market=seattle'
           '&num_homes=5&ord=redfin-recommended-asc&page_number=1'
           '&region_id=98660&region_type=2'
           '&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
           '&min_num_beds=5&max_price=600000&min_year_built=2017')

resp = session.get(gis_url, timeout=15, verify=False)
data = resp.text
if data.startswith('{}&&'):
    data = data[4:]
parsed = json.loads(data)
homes = parsed.get('payload', {}).get('homes', [])
print(f'Zip 98660 (region_id=98660, type=2): {len(homes)} homes')
for h in homes[:3]:
    print(f"  city={h.get('city')}, state={h.get('state')}, zip={h.get('zip')}, beds={h.get('beds')}, baths={h.get('baths')}, price={h.get('price',{}).get('value') if isinstance(h.get('price'),dict) else h.get('price')}")

# The issue is Redfin uses internal IDs. Let me try the Redfin download/search CSV endpoint
# Or try a completely different approach - use the Redfin search URL and parse HTML
print('\n--- Trying Redfin search page HTML ---')
search_url = 'https://www.redfin.com/zipcode/98682/filter/property-type=house,min-beds=5,max-price=600000,min-year-built=2017'
resp2 = session.get(search_url, timeout=15, verify=False, allow_redirects=True)
print(f'Search page status: {resp2.status_code}')
print(f'Final URL: {resp2.url}')
if resp2.status_code == 200:
    # Look for listing data in the HTML
    text = resp2.text
    # Check for Vancouver WA
    if 'Vancouver' in text:
        print('Found Vancouver in page!')
    if 'WA 98' in text:
        print('Found WA zip codes in page!')
    # Look for JSON data embedded in page
    import re
    # Redfin embeds data in window.__reactServerState
    match = re.search(r'window\.__reactServerState\.InitialContext\s*=\s*(.+?);</script>', text)
    if match:
        print('Found InitialContext data!')
        ctx = match.group(1)[:500]
        print(f'First 500 chars: {ctx}')
    else:
        # Try other patterns
        match2 = re.search(r'"homes":\s*\[', text)
        if match2:
            print('Found homes array in page!')
            start = match2.start()
            print(f'Context: {text[start:start+300]}')
        else:
            print('No homes data found in HTML')
            print(f'Page title area: {text[:500]}')
else:
    print(f'Response: {resp2.text[:300]}')
