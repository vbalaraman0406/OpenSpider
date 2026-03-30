import requests
import re
import json
from html.parser import HTMLParser
import warnings
warnings.filterwarnings('ignore')

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

# Check Foreclosure.com more deeply - it had the most data
print("=== FORECLOSURE.COM DEEP CHECK ===")
try:
    r = requests.get('https://www.foreclosure.com/listings/WA/Vancouver/', headers=headers, timeout=15, verify=False)
    html = r.text
    # Save first 5000 chars for analysis
    print(html[:3000])
except Exception as e:
    print(f"Error: {e}")
