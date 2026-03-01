import urllib.request
import re

# Scrape main website
url = 'https://fazzhomes.com/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    
    # Extract phone numbers
    phones = re.findall(r'[\(]?\d{3}[\)]?[\s\-\.]?\d{3}[\s\-\.]?\d{4}', html)
    print('Phone numbers found:', list(set(phones)))
    
    # Extract email
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', html)
    print('Emails found:', list(set(emails)))
    
    # Look for services - search for keywords
    # Extract meta description
    meta = re.findall(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    print('Meta description:', meta)
    
    # Extract title
    title = re.findall(r'<title>(.*?)</title>', html, re.IGNORECASE)
    print('Title:', title)
    
    # Look for navigation links to find services pages
    nav_links = re.findall(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', html, re.DOTALL)
    print('\nNavigation/Links (unique text):')
    seen = set()
    for href, text in nav_links:
        clean = re.sub(r'<[^>]+>', '', text).strip()
        if clean and clean not in seen and len(clean) < 80:
            seen.add(clean)
            if any(kw in clean.lower() or kw in href.lower() for kw in ['service', 'remodel', 'build', 'kitchen', 'bath', 'custom', 'renovation', 'addition', 'about', 'contact', 'portfolio']):
                print(f'  {clean} -> {href}')
    
    # Look for service-related content
    # Find sections with service keywords
    service_sections = re.findall(r'(?:services?|what we do|our work|specializ|remodel|build)[^<]{0,500}', html, re.IGNORECASE)
    for s in service_sections[:5]:
        clean = re.sub(r'\s+', ' ', s).strip()[:200]
        print(f'\nService mention: {clean}')
        
except Exception as e:
    print(f'Error: {e}')
