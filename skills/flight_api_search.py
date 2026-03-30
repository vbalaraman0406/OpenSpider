import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Try Skiplagged API for PDX-LAX
print('=== Trying Skiplagged API ===')
try:
    url = 'https://skiplagged.com/api/search.php'
    params = {
        'from': 'PDX',
        'to': 'LAX',
        'depart': '2026-06-22',
        'return': '2026-06-26',
        'format': 'v3',
        'counts[adults]': 1,
        'counts[children]': 0,
    }
    r = requests.get(url, params=params, headers=headers, timeout=20)
    print(f'Skiplagged status: {r.status_code}')
    if r.status_code == 200:
        try:
            data = json.loads(r.text)
            print(json.dumps(data, indent=2)[:3000])
        except:
            print(r.text[:2000])
except Exception as e:
    print(f'Skiplagged error: {e}')

# Try Google Flights ITA Matrix style
print('\n=== Trying alternative flight search ===')
try:
    url2 = 'https://www.google.com/async/flights/search'
    r2 = requests.get(url2, headers=headers, timeout=15)
    print(f'Google async status: {r2.status_code}')
except Exception as e:
    print(f'Google async error: {e}')

print('\nDone')
