import urllib.request
import re
import ssl
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Scrape main page
print('=== MAIN PAGE ===')
try:
    req = urllib.request.Request('https://www.fazzolari.com', headers=headers)
    resp = urllib.request.urlopen(req, timeout=10, context=ctx)
    html = resp.read().decode('utf-8', errors='ignore')
    
    # Phone numbers
    phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]+\d{3}[\-\.\s]+\d{4}', html)
    phones = list(set(phones))
    print(f'Phones: {phones}')
    
    # Email
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', html)
    emails = list(set(emails))
    print(f'Emails: {emails}')
    
    # Extract text content (strip tags)
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S|re.I)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.S|re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Print relevant sections
    print(f'\nPage text (first 1500 chars):\n{text[:1500]}')
    
    # Find internal links for services page
    links = re.findall(r'href="(/[^"]*|https?://(?:www\.)?fazzolari\.com[^"]*)', html)
    links = list(set(links))
    print(f'\nInternal links: {links[:20]}')
except Exception as e:
    print(f'Error: {e}')

# Try services/about pages
for page in ['/services', '/about', '/contact', '/our-services', '/what-we-do', '/remodeling']:
    print(f'\n=== {page} ===')
    try:
        req = urllib.request.Request(f'https://www.fazzolari.com{page}', headers=headers)
        resp = urllib.request.urlopen(req, timeout=8, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S|re.I)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.S|re.I)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]+\d{3}[\-\.\s]+\d{4}', html)
        if phones:
            print(f'Phones: {list(set(phones))}')
        print(f'Text (first 800 chars): {text[:800]}')
    except Exception as e:
        print(f'  -> {str(e)[:60]}')
