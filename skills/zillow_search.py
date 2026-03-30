import requests
import json

# Zillow search API endpoint
url = 'https://www.zillow.com/search/GetSearchPageState.htm'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.zillow.com/vancouver-wa/houses/',
}

# Search parameters for Vancouver WA area
search_query = {
    'pagination': {},
    'isMapVisible': True,
    'filterState': {
        'beds': {'min': 5},
        'baths': {'min': 2},
        'price': {'max': 600000},
        'built': {'min': 2017},
        'isForSaleByAgent': {'value': True},
        'isForSaleByOwner': {'value': True},
        'isNewConstruction': {'value': True},
        'isForSaleForeclosure': {'value': True},
        'isAuction': {'value': True},
        'isComingSoon': {'value': True},
        'isPreMarketForeclosure': {'value': False},
        'isPreMarketPreForeclosure': {'value': False},
        'isMakeMeMove': {'value': False},
        'con': {'value': False},
        'mf': {'value': False},
        'land': {'value': False},
        'tow': {'value': False},
        'apa': {'value': False},
        'manu': {'value': False},
    },
    'isListVisible': True,
    'mapZoom': 10,
    'regionSelection': [{'regionId': 27445, 'regionType': 6}],  # Vancouver WA
    'usersSearchTerm': 'Vancouver, WA',
}

params = {
    'searchQueryState': json.dumps(search_query),
    'wants': json.dumps({'cat1': ['listResults', 'mapResults'], 'cat2': ['total']}),
    'requestId': 1,
}

try:
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        # Extract listings
        results = []
        cat1 = data.get('cat1', {})
        search_results = cat1.get('searchResults', {})
        list_results = search_results.get('listResults', [])
        map_results = search_results.get('mapResults', [])
        
        print(f'List results: {len(list_results)}')
        print(f'Map results: {len(map_results)}')
        
        all_results = list_results if list_results else map_results
        
        for item in all_results[:20]:
            addr = item.get('address', item.get('addressStreet', 'N/A'))
            price = item.get('price', item.get('unformattedPrice', 'N/A'))
            beds = item.get('beds', 'N/A')
            baths = item.get('baths', 'N/A')
            area = item.get('area', item.get('livingArea', 'N/A'))
            detail_url = item.get('detailUrl', 'N/A')
            zpid = item.get('zpid', '')
            status = item.get('statusText', '')
            
            # Try to get hdpData for more details
            hdp = item.get('hdpData', {}).get('homeInfo', {})
            year_built = hdp.get('yearBuilt', 'N/A')
            if beds == 'N/A' and hdp:
                beds = hdp.get('bedrooms', 'N/A')
            if baths == 'N/A' and hdp:
                baths = hdp.get('bathrooms', 'N/A')
            
            print(f'---')
            print(f'Address: {addr}')
            print(f'Price: {price}')
            print(f'Beds: {beds}, Baths: {baths}')
            print(f'SqFt: {area}')
            print(f'Year Built: {year_built}')
            print(f'URL: {detail_url}')
            print(f'Status: {status}')
    else:
        print(f'Response: {resp.text[:500]}')
except Exception as e:
    print(f'Error: {e}')
