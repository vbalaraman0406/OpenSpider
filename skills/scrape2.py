import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Get full Thumbtack page
url = 'https://www.thumbtack.com/wa/vancouver/bathroom-remodeling/'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    resp = urllib.request.urlopen(req, timeout=15, context=ctx)
    html = resp.read().decode('utf-8', errors='ignore')
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    # Print chars 1500-5000 to get more contractors
    print(text[1500:5000])
except Exception as e:
    print(f'Error: {e}')

# Also try a direct Google-like search
print('\n=== Google Search ===')
try:
    gurl = 'https://www.google.com/search?q=best+bathroom+renovation+contractors+Vancouver+WA+98662+reviews+2025'
    req = urllib.request.Request(gurl, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    resp = urllib.request.urlopen(req, timeout=15, context=ctx)
    html = resp.read().decode('utf-8', errors='ignore')
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    print(text[:3000])
except Exception as e:
    print(f'Error: {e}')
