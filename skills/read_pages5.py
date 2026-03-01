import urllib.request
import re
import html as htmlmod

def fetch_and_extract(url, max_chars=2500):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=15)
    text = resp.read().decode('utf-8', errors='replace')
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<header[^>]*>.*?</header>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<footer[^>]*>.*?</footer>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<br[^>]*>', '\n', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = htmlmod.unescape(text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    text = text.strip()
    return text[:max_chars]

urls = [
    ('L&I Contractor Registration Main', 'https://www.lni.wa.gov/licensing-permits/contractors/'),
    ('L&I Hire a Contractor', 'https://www.lni.wa.gov/licensing-permits/contractors/hire-a-contractor/'),
    ('L&I Verify', 'https://secure.lni.wa.gov/verify/'),
    ('Vancouver Permit - no permit list', 'https://www.cityofvancouver.us/permits/residential-building-permits/'),
]

for name, url in urls:
    print('='*60)
    print(f'PAGE: {name}')
    print(f'URL: {url}')
    print('='*60)
    try:
        content = fetch_and_extract(url, 2000)
        # look for keywords related to our research
        lines = content.split('\n')
        relevant = []
        keywords = ['permit', 'license', 'register', 'contractor', 'plumb', 'tile', 'bathroom', 'remodel', 'bond', 'insur', 'UBI', 'verify', 'lookup', 'search', 'not required', 'vanity', 'cosmetic', 'flooring']
        for line in lines:
            low = line.lower()
            if any(k in low for k in keywords):
                relevant.append(line.strip())
        if relevant:
            print('\n'.join(relevant[:30]))
        else:
            print(content[:1500])
    except Exception as e:
        print(f'Error: {e}')
    print()
