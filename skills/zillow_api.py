import requests
import json
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
})

# First get Vancouver WA page to extract correct regionId
r = session.get('https://www.zillow.com/vancouver-wa/houses/', timeout=30)
print(f'Status: {r.status_code}')

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text)
if match:
    data = json.loads(match.group(1))
    props = data.get('props', {}).get('pageProps', {})
    sp = props.get('searchPageState', {})
    # Extract queryState to get regionId
    qs = sp.get('queryState', {})
    print(f'QueryState regionSelection: {qs.get("regionSelection", [])}')
    print(f'QueryState filterState: {json.dumps(qs.get("filterState", {}), indent=2)}')
    
    # Get all results and print beds distribution
    sr = sp.get('cat1', {}).get('searchResults', {})
    results = sr.get('listResults', [])
    print(f'Total results: {len(results)}')
    
    bed_counts = {}
    for item in results:
        beds = item.get('beds', 0)
        bed_counts[beds] = bed_counts.get(beds, 0) + 1
    print(f'Bed distribution: {bed_counts}')
    
    # Now try with proper searchQueryState using the regionId from the page
    region_sel = qs.get('regionSelection', [])
    if region_sel:
        region_id = region_sel[0].get('regionId')
        region_type = region_sel[0].get('regionType')
        print(f'Correct regionId: {region_id}, regionType: {region_type}')
        
        # Build proper search URL with filters
        search_state = {
            'pagination': {},
            'isMapVisible': False,
            'filterState': {
                'sort': {'value': 'days'},
                'beds': {'min': 5},
                'baths': {'min': 2},
                'price': {'max': 600000},
                'con': {'value': False},
                'mf': {'value': False},
                'land': {'value': False},
                'tow': {'value': False},
                'apa': {'value': False},
                'manu': {'value': False},
            },
            'isListVisible': True,
            'regionSelection': [{'regionId': region_id, 'regionType': region_type}],
        }
        
        encoded = json.dumps(search_state)
        url2 = f'https://www.zillow.com/vancouver-wa/houses/?searchQueryState={requests.utils.quote(encoded)}'
        print(f'\nFetching filtered URL...')
        r2 = session.get(url2, timeout=30)
        print(f'Status: {r2.status_code}')
        
        if r2.status_code == 200:
            match2 = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r2.text)
            if match2:
                data2 = json.loads(match2.group(1))
                sp2 = data2.get('props', {}).get('pageProps', {}).get('searchPageState', {})
                qs2 = sp2.get('queryState', {})
                print(f'Applied filterState: {json.dumps(qs2.get("filterState", {}), indent=2)}')
                sr2 = sp2.get('cat1', {}).get('searchResults', {})
                results2 = sr2.get('listResults', [])
                print(f'Filtered results: {len(results2)}')
                
                bed_counts2 = {}
                for item in results2:
                    beds = item.get('beds', 0)
                    bed_counts2[beds] = bed_counts2.get(beds, 0) + 1
                print(f'Bed distribution: {bed_counts2}')
                
                # Print all 5+ bed listings
                for item in results2:
                    hdp = item.get('hdpData', {}).get('homeInfo', {})
                    beds = item.get('beds', 0)
                    if beds and beds >= 5:
                        addr = item.get('address', 'N/A')
                        price = hdp.get('price', item.get('unformattedPrice', 'N/A'))
                        baths = item.get('baths', hdp.get('bathrooms', 'N/A'))
                        sqft = item.get('area', hdp.get('livingArea', 'N/A'))
                        year = hdp.get('yearBuilt', 'N/A')
                        url = item.get('detailUrl', '')
                        print(f'  {addr} | ${price} | {beds}bd/{baths}ba | {sqft}sqft | yr:{year} | {url}')
else:
    print('No __NEXT_DATA__ found')
