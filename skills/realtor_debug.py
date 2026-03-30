import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9'
}

url = 'https://www.realtor.com/realestateandhomes-search/Vancouver_WA/beds-5/baths-2/price-na-600000/age-5'
try:
    resp = requests.get(url, headers=headers, timeout=20, verify=False)
    print(f'Status: {resp.status_code}')
    print(f'HTML length: {len(resp.text)}')
    print(resp.text[:1500])
except Exception as e:
    print(f'Error: {e}')
