import json

with open('thumbtack_bathroom.html', 'r') as f:
    html = f.read()

import re
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if not m:
    print('No __NEXT_DATA__ found')
    exit()

data = json.loads(m.group(1))
fdp = data['props']['pageProps']['frontDoorPage']

# Explore proListSection
pls = fdp.get('proListSection', {})
print('proListSection type:', type(pls))
if isinstance(pls, dict):
    print('proListSection keys:', list(pls.keys()))
    for k, v in pls.items():
        if isinstance(v, list):
            print(f'  {k} is list, len={len(v)}')
            if len(v) > 0:
                item = v[0]
                if isinstance(item, dict):
                    print(f'    first item keys: {list(item.keys())}')
                    # Print first item
                    print(json.dumps(item, indent=2)[:2000])
                else:
                    print(f'    first item type: {type(item)}, val: {str(item)[:200]}')
        elif isinstance(v, dict):
            print(f'  {k} is dict, keys: {list(v.keys())}')
        else:
            print(f'  {k} = {str(v)[:200]}')

# Also check reviewsSection
rs = fdp.get('reviewsSection', {})
if isinstance(rs, dict):
    print('\nreviewsSection keys:', list(rs.keys()))
