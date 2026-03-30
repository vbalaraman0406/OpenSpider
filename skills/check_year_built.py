import requests
from html.parser import HTMLParser
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Referer': 'https://www.redfin.com/',
}

listings = [
    {'url': 'https://www.redfin.com/WA/Vancouver/15814-NE-70th-St-98682/home/14587389', 'addr': '15814 NE 70th St, Vancouver, WA 98682', 'price': 599900, 'beds': 5, 'baths': 3.0, 'sqft': 2355},
    {'url': 'https://www.redfin.com/WA/Vancouver/Vancouver/The-2167/home/197348201', 'addr': 'The 2167 Plan, Vancouver, WA 98682', 'price': 514960, 'beds': 5, 'baths': 2.5, 'sqft': 2167},
    {'url': 'https://www.redfin.com/WA/Vancouver/8907-NE-84th-St-98662/home/14580333', 'addr': '8907 NE 84th St, Vancouver, WA 98662', 'price': 560000, 'beds': 5, 'baths': 3.0, 'sqft': 2526},
    {'url': 'https://www.redfin.com/WA/Vancouver/4410-NE-163rd-Ave-98682/home/14642761', 'addr': '4410 NE 163rd Ave, Vancouver, WA 98682', 'price': 584000, 'beds': 5, 'baths': 2.5, 'sqft': 2748},
    {'url': 'https://www.redfin.com/WA/Vancouver/16604-NE-80th-St-98682/home/14575676', 'addr': '16604 NE 80th St, Vancouver, WA 98682', 'price': 575000, 'beds': 5, 'baths': 3.0, 'sqft': 2070},
    {'url': 'https://www.redfin.com/WA/Battle-Ground/Battle-Ground/Wellington/home/195202167', 'addr': 'Wellington Plan, Battle Ground, WA 98604', 'price': 590995, 'beds': 5, 'baths': 2.5, 'sqft': 2270},
]

for listing in listings:
    try:
        r = requests.get(listing['url'], headers=headers, timeout=15)
        text = r.text
        # Search for year built in the HTML
        yr_match = re.search(r'[Yy]ear\s*[Bb]uilt[^0-9]*(\d{4})', text)
        if yr_match:
            listing['year'] = int(yr_match.group(1))
        else:
            yr_match2 = re.search(r'Built\s+in\s+(\d{4})', text)
            if yr_match2:
                listing['year'] = int(yr_match2.group(1))
            else:
                yr_match3 = re.search(r'"yearBuilt":\s*(\d{4})', text)
                if yr_match3:
                    listing['year'] = int(yr_match3.group(1))
                else:
                    listing['year'] = 'Unknown'
        print(f"{listing['addr']} - Year: {listing['year']} - {listing['beds']}bd/{listing['baths']}ba - ${listing['price']:,}")
    except Exception as e:
        listing['year'] = 'Error'
        print(f"{listing['addr']} - Error: {e}")

print('\n=== MATCHES (2017+ year built, 2.5-3 baths) ===')
for l in listings:
    yr = l.get('year', 0)
    if isinstance(yr, int) and yr >= 2017 and 2.5 <= l['baths'] <= 3.0:
        print(f"${l['price']:,} | {l['addr']} | {l['beds']}bd/{l['baths']}ba | {l['sqft']}sqft | Built {yr} | {l['url']}")
