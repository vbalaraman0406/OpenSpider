import requests
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

url = 'https://www.zillow.com/vancouver-wa/houses/5-_beds/2-_baths/0-600000_price/'
resp = requests.get(url, headers=headers, timeout=30)
print(f'Status: {resp.status_code}')

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text)
if match:
    data = json.loads(match.group(1))
    props = data.get('props', {}).get('pageProps', {})
    search_results = props.get('searchPageState', {}).get('cat1', {}).get('searchResults', {})
    list_results = search_results.get('listResults', [])
    print(f'Total list results: {len(list_results)}')
    
    # Print first 5 raw listings to understand structure
    for i, item in enumerate(list_results[:5]):
        hdp = item.get('hdpData', {}).get('homeInfo', {})
        print(f'\n--- Listing {i+1} ---')
        print(f'address: {item.get("address", "N/A")}')
        print(f'addressStreet: {item.get("addressStreet", "N/A")}')
        print(f'price: {item.get("price", "N/A")}')
        print(f'beds: {item.get("beds", "N/A")}')
        print(f'baths: {item.get("baths", "N/A")}')
        print(f'area: {item.get("area", "N/A")}')
        print(f'detailUrl: {item.get("detailUrl", "N/A")}')
        print(f'statusText: {item.get("statusText", "N/A")}')
        print(f'hdp.yearBuilt: {hdp.get("yearBuilt", "N/A")}')
        print(f'hdp.bedrooms: {hdp.get("bedrooms", "N/A")}')
        print(f'hdp.bathrooms: {hdp.get("bathrooms", "N/A")}')
        print(f'hdp.price: {hdp.get("price", "N/A")}')
        print(f'hdp.livingArea: {hdp.get("livingArea", "N/A")}')
        print(f'hdp.city: {hdp.get("city", "N/A")}')
        print(f'hdp.state: {hdp.get("state", "N/A")}')
        print(f'hdp.zipcode: {hdp.get("zipcode", "N/A")}')
    
    # Count how many have 5+ beds
    five_bed = 0
    for item in list_results:
        hdp = item.get('hdpData', {}).get('homeInfo', {})
        beds = item.get('beds', hdp.get('bedrooms', 0))
        baths = item.get('baths', hdp.get('bathrooms', 0))
        year = hdp.get('yearBuilt', 0)
        price = item.get('unformattedPrice', hdp.get('price', 999999))
        try:
            beds = int(beds) if beds else 0
            baths = float(baths) if baths else 0
            year = int(year) if year else 0
            price = int(price) if price else 999999
        except:
            pass
        if beds >= 5:
            five_bed += 1
            if baths >= 2.5 and baths <= 3.0 and year >= 2017 and price <= 600000:
                print(f'\nMATCH: {item.get("address")} | ${price} | {beds}bd/{baths}ba | yr:{year}')
    print(f'\nListings with 5+ beds: {five_bed}')
else:
    print('No __NEXT_DATA__ found')
