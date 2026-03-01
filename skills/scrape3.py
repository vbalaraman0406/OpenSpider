import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try DuckDuckGo HTML
print('=== DuckDuckGo Search ===')
try:
    url = 'https://html.duckduckgo.com/html/?q=bathroom+renovation+contractors+Vancouver+WA+98662+reviews+2025+2026'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15, context=ctx)
    html = resp.read().decode('utf-8', errors='ignore')
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    print(text[:3000])
except Exception as e:
    print(f'DDG Error: {e}')

# Try Houzz
print('\n=== Houzz ===')
try:
    url = 'https://www.houzz.com/professionals/general-contractors/vancouver-wa-us-probr0-bo~t_11786~r_4956764'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15, context=ctx)
    html = resp.read().decode('utf-8', errors='ignore')
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    # Find contractor names and ratings
    chunks = text[:4000]
    print(chunks)
except Exception as e:
    print(f'Houzz Error: {e}')
