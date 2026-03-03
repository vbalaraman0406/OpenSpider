import urllib.request
import json
import ssl
import re

ssl._create_default_https_context = ssl._create_unverified_context
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

# Try Google Finance pages
symbols = [
    ('SPY', 'NYSEARCA'),
    ('LMT', 'NYSE'),
    ('RTX', 'NYSE'),
    ('NOC', 'NYSE'),
]

for sym, exchange in symbols:
    url = f'https://www.google.com/finance/quote/{sym}:{exchange}'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode('utf-8', errors='replace')
            # Google Finance has price in specific patterns
            match = re.search(r'data-last-price="([^"]+)"', data)
            change = re.search(r'data-last-normal-market-change-percent="([^"]+)"', data)
            if match:
                p = match.group(1)
                c = change.group(1) if change else 'N/A'
                print(f'{sym}: ${float(p):.2f} ({c}%)')
            else:
                # Try another pattern
                match2 = re.search(r'class="YMlKec fxKbKc">\$([\d,\.]+)', data)
                if match2:
                    print(f'{sym}: ${match2.group(1)}')
                else:
                    print(f'{sym}: Could not parse')
    except Exception as e:
        print(f'{sym}: ERROR - {e}')

# Try oil and gold from Google Finance
for commodity, ticker in [('Crude Oil', 'CL=F'), ('Gold', 'GC=F')]:
    url = f'https://www.google.com/finance/quote/{ticker}'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode('utf-8', errors='replace')
            match = re.search(r'class="YMlKec fxKbKc">\$?([\d,\.]+)', data)
            if match:
                print(f'{commodity}: ${match.group(1)}')
            else:
                print(f'{commodity}: Could not parse')
    except Exception as e:
        print(f'{commodity}: ERROR - {e}')
