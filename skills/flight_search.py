import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

print('Testing connectivity...')
try:
    r = requests.get('https://www.google.com', headers=headers, timeout=10)
    print(f'Google status: {r.status_code}')
except Exception as e:
    print(f'Error: {e}')

print('Done')
