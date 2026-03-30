import requests
import json
import warnings
warnings.filterwarnings('ignore')

# Use Redfin's location autocomplete to find Vancouver WA region ID
url = 'https://www.redfin.com/stingray/do/location-autocomplete?location=Vancouver%20WA&v=2'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.redfin.com/'
}

r = requests.get(url, headers=headers, timeout=15, verify=False)
data = r.text
if data.startswith('{}&&'):
    data = data[4:]

try:
    parsed = json.loads(data)
    print(json.dumps(parsed, indent=2)[:3000])
except:
    print('Raw response:')
    print(data[:3000])
