import requests
import json
import re

# Try Realtor.com API endpoint that their frontend uses
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.realtor.com/',
}

# Search areas
areas = [
    'Vancouver_WA',
    'Ridgefield_WA', 
    'Battle-Ground_WA',
    'Camas_WA',
    'Washougal_WA',
    'Brush-Prairie_WA'
]

all_listings = []

for area in areas:
    url = f'https://www.realtor.com/api/v1/hulk_main_srp?client_id=rdc-x&schema=vesta&query=%7B%22status%22%3A%5B%22for_sale%22%5D%2C%22primary%22%3Atrue%2C%22search_location%22%3A%7B%22location%22%3A%22{area}%22%7D%2C%22beds%22%3A%7B%22min%22%3A5%7D%2C%22list_price%22%3A%7B%22max%22%3A600000%7D%2C%22prop_type%22%3A%5B%22single_family%22%5D%2C%22year_built%22%3A%7B%22min%22%3A2017%7D%7D'
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('data', {}).get('home_search', {}).get('results', [])
            for r in results:
                addr = r.get('location', {}).get('address', {})
                address = f"{addr.get('line', '')}, {addr.get('city', '')}, {addr.get('state_code', '')} {addr.get('postal_code', '')}"
                price = r.get('list_price', 'N/A')
                beds = r.get('description', {}).get('beds', 'N/A')
                baths = r.get('description', {}).get('baths', 'N/A')
                sqft = r.get('description', {}).get('sqft', 'N/A')
                year = r.get('description', {}).get('year_built', 'N/A')
                permalink = r.get('permalink', '')
                link = f'https://www.realtor.com/realestateandhomes-detail/{permalink}' if permalink else 'N/A'
                
                all_listings.append({
                    'address': address,
                    'price': f'${price:,}' if isinstance(price, (int, float)) else str(price),
                    'beds': beds,
                    'baths': baths,
                    'sqft': sqft,
                    'year_built': year,
                    'link': link
                })
            print(f'{area}: Found {len(results)} results')
        else:
            print(f'{area}: HTTP {resp.status_code}')
    except Exception as e:
        print(f'{area}: Error - {e}')

# Also try the GraphQL API that Realtor.com uses
if not all_listings:
    print('\nTrying GraphQL API...')
    graphql_url = 'https://www.realtor.com/api/v1/rdc_search_srp?client_id=rdc-search-for-sale-search&schema=vesta'
    
    for area in areas:
        payload = {
            'query': '''query ConsumerSearchMainQuery($query: HomeSearchCriteria!, $limit: Int, $offset: Int, $sort: [SearchAPISort]) {
                home_search: home_search(query: $query, sort: $sort, limit: $limit, offset: $offset) {
                    count
                    results {
                        property_id
                        list_price
                        permalink
                        description {
                            beds
                            baths
                            sqft
                            year_built
                        }
                        location {
                            address {
                                line
                                city
                                state_code
                                postal_code
                            }
                        }
                    }
                }
            }''',
            'variables': {
                'query': {
                    'status': ['for_sale'],
                    'primary': True,
                    'search_location': {'location': area.replace('_', ', ').replace('-', ' ')},
                    'beds': {'min': 5},
                    'list_price': {'max': 600000},
                    'prop_type': ['single_family'],
                    'year_built': {'min': 2017}
                },
                'limit': 42,
                'offset': 0,
                'sort': [{'field': 'list_date', 'direction': 'desc'}]
            }
        }
        
        try:
            resp = requests.post(graphql_url, json=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get('data', {}).get('home_search', {}).get('results', [])
                for r in results:
                    addr = r.get('location', {}).get('address', {})
                    address = f"{addr.get('line', '')}, {addr.get('city', '')}, {addr.get('state_code', '')} {addr.get('postal_code', '')}"
                    price = r.get('list_price', 'N/A')
                    beds = r.get('description', {}).get('beds', 'N/A')
                    baths = r.get('description', {}).get('baths', 'N/A')
                    sqft = r.get('description', {}).get('sqft', 'N/A')
                    year = r.get('description', {}).get('year_built', 'N/A')
                    permalink = r.get('permalink', '')
                    link = f'https://www.realtor.com/realestateandhomes-detail/{permalink}' if permalink else 'N/A'
                    
                    all_listings.append({
                        'address': address,
                        'price': f'${price:,}' if isinstance(price, (int, float)) else str(price),
                        'beds': beds,
                        'baths': baths,
                        'sqft': sqft,
                        'year_built': year,
                        'link': link
                    })
                print(f'{area}: Found {len(results)} results (GraphQL)')
            else:
                print(f'{area}: HTTP {resp.status_code} (GraphQL)')
        except Exception as e:
            print(f'{area}: Error (GraphQL) - {e}')

print(f'\nTotal listings found: {len(all_listings)}')
for i, l in enumerate(all_listings, 1):
    print(f"\n--- Listing {i} ---")
    print(f"Address: {l['address']}")
    print(f"Price: {l['price']}")
    print(f"Beds: {l['beds']} | Baths: {l['baths']} | SqFt: {l['sqft']}")
    print(f"Year Built: {l['year_built']}")
    print(f"Link: {l['link']}")
