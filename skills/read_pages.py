import urllib.request
import re
import html as htmlmod

def fetch_and_extract(url, max_chars=2500):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=15)
    text = resp.read().decode('utf-8', errors='replace')
    # Remove scripts, styles
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<header[^>]*>.*?</header>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<footer[^>]*>.*?</footer>', '', text, flags=re.DOTALL|re.IGNORECASE)
    # Convert to plain text
    text = re.sub(r'<br[^>]*>', '\n', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = htmlmod.unescape(text)
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    text = text.strip()
    return text[:max_chars]

# 1. L&I Register as Contractor
print('='*60)
print('PAGE 1: L&I - Register as a Contractor')
print('='*60)
try:
    content = fetch_and_extract('https://www.lni.wa.gov/licensing-permits/contractors/register-as-a-contractor/')
    print(content)
except Exception as e:
    print(f'Error: {e}')

# 2. L&I Verify a Contractor
print('\n' + '='*60)
print('PAGE 2: L&I - Verify a Contractor')
print('='*60)
try:
    content = fetch_and_extract('https://verify.lni.wa.gov/')
    print(content)
except Exception as e:
    print(f'Error: {e}')

# Also try the known lookup URL
try:
    content2 = fetch_and_extract('https://secure.lni.wa.gov/verify/')
    print(content2[:500])
except Exception as e:
    print(f'Alt URL error: {e}')

# 3. Vancouver WA building permits
print('\n' + '='*60)
print('PAGE 3: Vancouver WA - Building Permits')
print('='*60)
try:
    content = fetch_and_extract('https://www.cityofvancouver.us/community-development/permits-and-applications/', 2500)
    print(content)
except Exception as e:
    print(f'Error: {e}')
