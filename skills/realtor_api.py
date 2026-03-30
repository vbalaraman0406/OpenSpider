import requests
import json

# Try Realtor.com's internal API endpoint used by their frontend
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Origin': 'https://www.realtor.com',
    'Referer': 'https://www.realtor.com/'
})

# Try the Realtor.com RDC API
api_url = 'https://api.realtor.com/rdc-search-api/v2/search'

# Also try their newer GraphQL endpoint
gql_url = 'https://www.realtor.com/api/v1/rdc_search_srp'

locations = [
    'Vancouver, WA',
    'Ridgefield, WA', 
    'Battle Ground, WA',
    'Camas, WA',
    'Washougal, WA',
    'Brush Prairie, WA'
]

all_listings = []

for location in locations:
    # Try the search API
    params = {
        'client_id': 'rdc-x',
        'schema': 'vesta',
        'limit': 50,
        'offset': 0,
        'beds_min': 5,
        'baths_min': 2,
        'price_max': 600000,
        'year_built_min': 2017,
        'status': 'for_sale',
        'location': location,
        'sort': 'relevance'
    }
    
    try:
        resp = session.get(api_url, params=params, timeout=15)
        print(f'{location}: API status {resp.status_code}')
        if resp.status_code == 200:
            data = resp.json()
            print(f'  Keys: {list(data.keys())[:10]}')
            results = data.get('results', data.get('properties', []))
            print(f'  Results: {len(results)}')
    except Exception as e:
        print(f'{location}: API error - {e}')

# Try alternate API endpoints
alt_urls = [
    'https://parser-external.geo.moveaws.com/suggest',
    'https://www.realtor.com/frontdoor/graphql'
]

for alt_url in alt_urls:
    try:
        if 'suggest' in alt_url:
            resp = session.get(alt_url, params={'input': 'Vancouver, WA', 'limit': 5}, timeout=10)
        else:
            gql_query = {
                'query': '{home_search(query:{status:["for_sale"],primary:true,search_location:{location:"Vancouver, WA"},beds:{min:5},baths:{min:2},list_price:{max:600000},year_built:{min:2017}},limit:20){total,results{property_id,list_price,description{beds,baths,sqft,year_built},location{address{line,city,state_code,postal_code}},href}}}'
            }
            resp = session.post(alt_url, json=gql_query, timeout=10)
        print(f'\nAlt URL {alt_url}: {resp.status_code}')
        print(f'  Response: {resp.text[:500]}')
    except Exception as e:
        print(f'\nAlt URL {alt_url}: Error - {e}')

print(f'\nTotal listings found: {len(all_listings)}')
