import requests
url = 'https://f1-dot-vish-cloud.wl.r.appspot.com/f1/'
resp = requests.get(url, timeout=15)
print('STATUS:', resp.status_code)
print('\n--- RESPONSE HEADERS ---')
for k, v in resp.headers.items():
    print(f'{k}: {v}')
print('\n--- CSP CHECK ---')
csp = resp.headers.get('Content-Security-Policy', 'NONE')
print('CSP:', csp)
xcsp = resp.headers.get('X-Content-Security-Policy', 'NONE')
print('X-CSP:', xcsp)
