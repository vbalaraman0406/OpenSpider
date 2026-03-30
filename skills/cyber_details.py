import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

# Get more details from specific story pages
urls = {
    'CyberScoop': 'https://cyberscoop.com/',
    'CISA Alerts': 'https://www.cisa.gov/news-events/cybersecurity-advisories',
}

for name, url in urls.items():
    print(f'\n=== {name} ===')
    try:
        r = requests.get(url, headers=headers, timeout=15)
        headlines = re.findall(r'<h[23][^>]*>\s*(?:<a[^>]*>)?\s*([^<]{20,}?)\s*(?:</a>)?\s*</h[23]>', r.text)
        if not headlines:
            headlines = re.findall(r'<a[^>]*>([^<]{25,}?)</a>', r.text)
            headlines = [h for h in headlines if not any(x in h.lower() for x in ['cookie', 'privacy', 'subscribe', 'newsletter', 'menu', 'search', 'javascript'])]
        seen = set()
        count = 0
        for h in headlines:
            h = h.strip()
            if h not in seen and len(h) > 20 and count < 15:
                seen.add(h)
                print(f'  - {h}')
                count += 1
        if count == 0:
            print('  (No headlines extracted)')
    except Exception as e:
        print(f'  Error: {e}')

# Now search for specific topics
print('\n=== Google: Ransomware news today ===')
try:
    r = requests.get('https://www.google.com/search?q=ransomware+attack+news+today+2025&tbs=qdr:d', headers=headers, timeout=15)
    titles = re.findall(r'<h3[^>]*>([^<]+)</h3>', r.text)
    for t in titles[:10]:
        print(f'  - {t.strip()}')
except Exception as e:
    print(f'  Error: {e}')

print('\n=== Google: Nation-state cyber attack today ===')
try:
    r = requests.get('https://www.google.com/search?q=nation+state+APT+cyber+attack+2025+today&tbs=qdr:d', headers=headers, timeout=15)
    titles = re.findall(r'<h3[^>]*>([^<]+)</h3>', r.text)
    for t in titles[:10]:
        print(f'  - {t.strip()}')
except Exception as e:
    print(f'  Error: {e}')

print('\n=== Google: Critical infrastructure cyber threat 2025 ===')
try:
    r = requests.get('https://www.google.com/search?q=critical+infrastructure+cyber+threat+attack+2025&tbs=qdr:d', headers=headers, timeout=15)
    titles = re.findall(r'<h3[^>]*>([^<]+)</h3>', r.text)
    for t in titles[:10]:
        print(f'  - {t.strip()}')
except Exception as e:
    print(f'  Error: {e}')

print('\n=== Google: Supply chain cyber attack 2025 ===')
try:
    r = requests.get('https://www.google.com/search?q=software+supply+chain+cyber+attack+compromise+2025&tbs=qdr:d', headers=headers, timeout=15)
    titles = re.findall(r'<h3[^>]*>([^<]+)</h3>', r.text)
    for t in titles[:10]:
        print(f'  - {t.strip()}')
except Exception as e:
    print(f'  Error: {e}')

print('\n=== Google: Cybersecurity regulation 2025 ===')
try:
    r = requests.get('https://www.google.com/search?q=cybersecurity+regulation+policy+change+2025&tbs=qdr:d', headers=headers, timeout=15)
    titles = re.findall(r'<h3[^>]*>([^<]+)</h3>', r.text)
    for t in titles[:10]:
        print(f'  - {t.strip()}')
except Exception as e:
    print(f'  Error: {e}')
