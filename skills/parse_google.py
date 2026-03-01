import re
import json

with open('google_raw.html', 'r') as f:
    html = f.read()

print(f'HTML length: {len(html)}')

# Check for CAPTCHA
if 'captcha' in html.lower() or 'unusual traffic' in html.lower():
    print('CAPTCHA detected!')

# Extract all links with their text
all_links = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
relevant_links = []
for href, text in all_links:
    text_clean = re.sub(r'<[^>]+>', '', text).strip()
    if text_clean and len(text_clean) > 5:
        skip_domains = ['google.com', 'gstatic.com', 'googleapis.com', 'schema.org', 'w3.org']
        if not any(d in href for d in skip_domains):
            relevant_links.append((href, text_clean))

print(f'\nRelevant links found: {len(relevant_links)}')
for href, text in relevant_links[:30]:
    print(f'  {text[:100]}')
    print(f'    -> {href[:150]}')

# Extract all text and look for contractor-related content
text_only = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
text_only = re.sub(r'<script[^>]*>.*?</script>', '', text_only, flags=re.DOTALL)
text_only = re.sub(r'<[^>]+>', '\n', text_only)
text_only = re.sub(r'&[a-z]+;', ' ', text_only)
text_only = re.sub(r'\n+', '\n', text_only)

lines = [l.strip() for l in text_only.split('\n') if l.strip() and len(l.strip()) > 10]

print(f'\n=== Relevant text lines ===')
keywords = ['bath', 'remodel', 'contractor', 'tile', 'renovation', 'plumb', 'vancouver', 'rating', 'review', 'star']
for line in lines:
    if any(kw in line.lower() for kw in keywords):
        print(f'  {line[:250]}')

# Extract phone numbers with surrounding context
print(f'\n=== Phone numbers ===')
phones = re.finditer(r'(.{0,60})(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})(.{0,60})', text_only)
for m in phones:
    before = m.group(1).strip()
    phone = m.group(2).strip()
    after = m.group(3).strip()
    print(f'  {before} | {phone} | {after}')

# Look for star ratings (e.g. "4.8" near "star" or review counts)
print(f'\n=== Ratings ===')
rating_patterns = re.findall(r'(\d\.\d)\s*(?:star|/5|out of|\(\d)', text_only, re.IGNORECASE)
print(f'  Ratings: {rating_patterns}')

# Look for JSON-LD structured data
print(f'\n=== JSON-LD ===')
jsonld = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.DOTALL)
for j in jsonld:
    try:
        data = json.loads(j)
        print(json.dumps(data, indent=2)[:800])
    except:
        print(j[:300])

# Look for data-attrid or data-header-feature patterns (Google local pack)
print(f'\n=== Data attributes ===')
attribs = re.findall(r'data-attrid="([^"]+)"', html)
for a in set(attribs):
    print(f'  attrid: {a}')

# Look for aria-label with business info
print(f'\n=== Aria labels ===')
aria = re.findall(r'aria-label="([^"]+)"', html)
for a in aria:
    if any(kw in a.lower() for kw in ['bath', 'remodel', 'contractor', 'tile', 'renovation', 'plumb', 'rating', 'star', 'review']):
        print(f'  {a[:200]}')
