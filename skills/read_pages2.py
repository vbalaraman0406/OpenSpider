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

# 1. Vancouver WA permits page
print('='*60)
print('PAGE: Vancouver WA Permits')
print('='*60)
try:
    content = fetch_and_extract('https://www.cityofvancouver.us/community-development/permits-and-applications/')
    print(content)
except Exception as e:
    print(f'Error: {e}')

# 2. L&I plumbing requirements
print('\n' + '='*60)
print('PAGE: L&I Plumbing Requirements')
print('='*60)
try:
    content = fetch_and_extract('https://www.lni.wa.gov/licensing-permits/electrical-plumbing-certification/plumbing-certification/')
    print(content)
except Exception as e:
    print(f'Error: {e}')

# 3. Try L&I verify page - the known correct URL
print('\n' + '='*60)
print('PAGE: L&I Verify')
print('='*60)
try:
    content = fetch_and_extract('https://secure.lni.wa.gov/verify/')
    print(content[:1000])
except Exception as e:
    print(f'Error: {e}')
