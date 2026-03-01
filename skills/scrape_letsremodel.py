import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = ['https://www.letsremodel.net', 'https://www.letsremodel.com', 'https://letsremodel.com']

for url in urls:
    print(f'\n=== {url} ===')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        html = resp.read().decode('utf-8', errors='replace')
        
        # Extract title
        title = re.findall(r'<title[^>]*>(.*?)</title>', html, re.I|re.S)
        print(f'Title: {title[0].strip() if title else "No title"}')
        
        # Extract phone numbers
        phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]?\s?\d{3}[\-\.\s]?\d{4}', html)
        phones = list(set(phones))
        print(f'Phones: {phones}')
        
        # Extract text content - remove scripts and styles
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S|re.I)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.S|re.I)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Print first 2000 chars of text
        print(f'Content (first 2000 chars): {text[:2000]}')
        
        # Look for address, Vancouver, WA
        if 'vancouver' in text.lower() or '98662' in text:
            print('\n*** MENTIONS VANCOUVER/98662 ***')
        
        # Look for services
        services_section = re.findall(r'(?:services|we offer|our services|what we do)[^.]*(?:\.|$)', text.lower())
        if services_section:
            print(f'Services mentions: {services_section[:3]}')
            
    except Exception as e:
        print(f'Error: {e}')
