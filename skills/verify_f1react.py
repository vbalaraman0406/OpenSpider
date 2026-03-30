import requests

url = 'https://f1-dot-vish-cloud.wl.r.appspot.com/f1/'
resp = requests.get(url, timeout=15)
print('STATUS:', resp.status_code)
print('LENGTH:', len(resp.text))
print('HTML:')
print(resp.text)
print()
if 'index-Cv5HRAMH.js' in resp.text:
    print('>>> CLEAN REACT BUILD DETECTED')
elif 'innerHTML' in resp.text:
    print('>>> OLD INLINE HTML DETECTED - stale cache')
else:
    print('>>> UNKNOWN HTML VERSION')

# Check JS bundle
import re
matches = re.findall(r'index-[A-Za-z0-9_-]+\.js', resp.text)
print('JS bundles referenced:', matches)

# Check health endpoint
health = requests.get('https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/health', timeout=15)
print('\nHealth status:', health.status_code)
print('Health body:', health.text[:200])
