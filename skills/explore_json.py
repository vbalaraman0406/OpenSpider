import requests, json, re
from bs4 import BeautifulSoup

url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
resp = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(resp.text, 'html.parser')

# Find __NEXT_DATA__
script = soup.find('script', id='__NEXT_DATA__')
if script:
    data = json.loads(script.string)
    props = data.get('props', {})
    pp = props.get('pageProps', {})
    print('pageProps keys:', list(pp.keys())[:20])
    # Look for any key containing 'pro' or 'service' or 'result'
    for k, v in pp.items():
        if isinstance(v, dict):
            print(f'  {k} (dict) keys: {list(v.keys())[:15]}')
            for k2, v2 in v.items():
                if isinstance(v2, list) and len(v2) > 0:
                    print(f'    {k2} (list len={len(v2)}), first item type: {type(v2[0]).__name__}')
                    if isinstance(v2[0], dict):
                        print(f'      first item keys: {list(v2[0].keys())[:15]}')
        elif isinstance(v, list) and len(v) > 0:
            print(f'  {k} (list len={len(v)}), first item type: {type(v[0]).__name__}')
            if isinstance(v[0], dict):
                print(f'    first item keys: {list(v[0].keys())[:15]}')
else:
    print('No __NEXT_DATA__ found')
    # Try finding JSON-LD
    scripts = soup.find_all('script', type='application/ld+json')
    print(f'Found {len(scripts)} JSON-LD scripts')
    for s in scripts:
        d = json.loads(s.string)
        if isinstance(d, list):
            print(f'  List of {len(d)} items')
            if d:
                print(f'  First item keys: {list(d[0].keys())[:10]}')
        else:
            print(f'  Type: {d.get("@type")}, keys: {list(d.keys())[:10]}')
