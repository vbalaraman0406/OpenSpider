import requests
import json
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
})

# Check the detail page for yearBuilt
detail_url = 'https://www.zillow.com/homedetails/2320-N-R-St-Washougal-WA-98671/328533122_zpid/'
print('Fetching detail page...')
try:
    resp = session.get(detail_url, timeout=30)
    print('Status: ' + str(resp.status_code))
    if resp.status_code == 200:
        # Look for yearBuilt in the page
        yr_match = re.search(r'yearBuilt[":]+(\d{4})', resp.text)
        if yr_match:
            print('Year Built: ' + yr_match.group(1))
        else:
            yr_match2 = re.search(r'Year [Bb]uilt[^0-9]*(\d{4})', resp.text)
            if yr_match2:
                print('Year Built: ' + yr_match2.group(1))
            else:
                print('Year Built not found in page')
        
        # Also try __NEXT_DATA__
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text)
        if match:
            data = json.loads(match.group(1))
            # Navigate to property details
            props = data.get('props', {}).get('pageProps', {})
            # Try different paths
            gdp = props.get('gdpClientCache', {})
            if gdp:
                for key in gdp:
                    val = json.loads(gdp[key]) if isinstance(gdp[key], str) else gdp[key]
                    prop = val.get('property', {})
                    if prop:
                        print('yearBuilt: ' + str(prop.get('yearBuilt', 'N/A')))
                        print('bedrooms: ' + str(prop.get('bedrooms', 'N/A')))
                        print('bathrooms: ' + str(prop.get('bathrooms', 'N/A')))
                        print('livingArea: ' + str(prop.get('livingArea', 'N/A')))
                        print('price: ' + str(prop.get('price', 'N/A')))
                        break
except Exception as e:
    print('Error: ' + str(e))

# Also try Vancouver WA with a different URL pattern
print('')
print('Trying Vancouver WA alternate URL...')
try:
    resp2 = session.get('https://www.zillow.com/homes/Vancouver,-WA_rb/', timeout=30)
    print('Status: ' + str(resp2.status_code))
    if resp2.status_code == 200:
        match2 = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp2.text)
        if match2:
            data2 = json.loads(match2.group(1))
            sp = data2.get('props', {}).get('pageProps', {}).get('searchPageState', {})
            sr = sp.get('cat1', {}).get('searchResults', {})
            results = sr.get('listResults', [])
            print('Results: ' + str(len(results)))
            for item in results:
                hdp = item.get('hdpData', {}).get('homeInfo', {})
                beds = item.get('beds', 0)
                price = hdp.get('price', 999999)
                if beds and int(beds) >= 5 and int(price) <= 600000:
                    addr = item.get('address', 'N/A')
                    baths = item.get('baths', 0)
                    sqft = item.get('area', 'N/A')
                    detail = item.get('detailUrl', '')
                    if detail and not detail.startswith('http'):
                        detail = 'https://www.zillow.com' + detail
                    print('FOUND: ' + addr + ' | $' + str(price) + ' | ' + str(beds) + 'bd/' + str(baths) + 'ba | ' + detail)
        else:
            print('No data found')
except Exception as e:
    print('Error: ' + str(e))
