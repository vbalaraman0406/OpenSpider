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
    ('Vancouver WA Permits Main', 'https://www.cityofvancouver.us/community-development/'),
    ('Vancouver WA Building Permits', 'https://www.cityofvancouver.us/community-development/building-permits/'),
    ('Vancouver WA Remodel Permits', 'https://www.cityofvancouver.us/permits/'),
    ('Clark County Permits', 'https://clark.wa.gov/community-development/building-permits'),
    ('L&I Contractor Registration', 'https://www.lni.wa.gov/licensing-permits/contractor-registration/'),
    ('L&I Plumbing', 'https://www.lni.wa.gov/licensing-permits/plumbing/'),
]

for name, url in urls:
    print('='*60)
    print(f'PAGE: {name}')
    print(f'URL: {url}')
    print('='*60)
    try:
        content = fetch_and_extract(url)
        print(content[:1500])
    except Exception as e:
        print(f'Error: {e}')
    print()
