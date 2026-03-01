import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

sites = {
    'Reliable Men': 'https://www.reliablemen.com',
    'Lets Remodel': 'https://www.letsremodel.com', 
    'Fazzolari': 'https://www.fazzolari.com',
    'Mountainwood': 'https://www.mountainwoodhomes.com',
    'Beto and Son': 'https://www.betoandson.com'
}

for name, url in sites.items():
    print(f'\n{"="*60}')
    print(f'=== {name} === ({url})')
    print('='*60)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract phones
        phones = list(set(re.findall(r'[\(]?\d{3}[\)\-\.\s]?\s?\d{3}[\-\.\s]\d{4}', html)))
        print(f'Phones: {phones[:5]}')
        
        # Extract text content (strip tags)
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Print first 800 chars of text
        print(f'Content preview: {text[:800]}')
        
        # Look for address/location
        addr = re.findall(r'\d+\s+[A-Z][a-zA-Z\s]+(?:St|Ave|Blvd|Dr|Rd|Way|Ln|Ct|Hwy|Suite|Ste)[\.,]?\s*(?:#\d+)?[\s,]*(?:Vancouver|Portland|Camas|Washougal|Battle Ground)', text, re.IGNORECASE)
        if addr:
            print(f'Addresses found: {addr[:3]}')
            
        # Look for license numbers
        lic = re.findall(r'(?:CCB|License|Lic)[#:\s]*([A-Z0-9]+)', text, re.IGNORECASE)
        if lic:
            print(f'License: {lic[:3]}')
    except Exception as e:
        print(f'Error: {e}')
