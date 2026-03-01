import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

req = urllib.request.Request('https://www.letsremodel.net', headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Find all rating widgets with their surrounding context to map to platforms
# Look for the pattern: platform image/link near a rating
pattern = r'<div[^>]*class="[^"]*rating[^"]*"[^>]*>[\s\S]*?</div>'
blocks = re.findall(pattern, html, re.I)
print(f'Found {len(blocks)} rating divs')

# Alternative: find all img alt texts in order, then all ratings in order
imgs = re.findall(r'alt="([^"]*(?:houzz|google|yelp|angi|facebook)[^"]*?)"', html, re.I)
print('Platform images in order:', imgs)

# Find all href links to review platforms in order
review_links = re.findall(r'href="([^"]*(?:houzz\.com|google\.com/maps|yelp\.com|angi\.com|facebook\.com)[^"]*?)"', html, re.I)
print('Review platform links in order:', review_links)

# Find all rating values in order
ratings_ordered = re.findall(r'Rated (\d+\.\d+) out of 5.*?avg\.\s*rating\s*\((\d+)\s*reviews\)', html, re.I|re.DOTALL)
print('Ratings in order:', ratings_ordered)

# Now let me find each rating section by looking at the HTML structure
# Find sections that contain both a platform link and a rating
sections = re.split(r'Rated \d+\.\d+ out of 5', html)
print(f'\nFound {len(sections)-1} rating sections')
for i, section in enumerate(sections[:-1]):
    # Look backwards from each rating for the nearest platform identifier
    # Take last 500 chars before the split point
    context = section[-500:] if len(section) > 500 else section
    platforms_found = re.findall(r'(houzz|google|yelp|angi|facebook)', context, re.I)
    print(f'Section {i}: platforms before rating = {platforms_found}')

# Get the about page remaining text
req2 = urllib.request.Request('https://www.letsremodel.net/about/', headers=headers)
with urllib.request.urlopen(req2, timeout=15) as resp2:
    html2 = resp2.read().decode('utf-8', errors='ignore')

text2 = re.sub(r'<script[^>]*>.*?</script>', '', html2, flags=re.DOTALL|re.I)
text2 = re.sub(r'<style[^>]*>.*?</style>', '', text2, flags=re.DOTALL|re.I)
text2 = re.sub(r'<[^>]+>', ' ', text2)
text2 = re.sub(r'\s+', ' ', text2).strip()

# Find the about section
idx = text2.lower().find('family business')
if idx > -1:
    print('\n=== ABOUT KEY SECTION ===')
    print(text2[idx:idx+1000])

# License info
licenses = re.findall(r'(?:OR|WA|CCB|license|contractor)[^,;.]*(?:\d{5,}|[A-Z]{5,}\*\w+)', text2, re.I)
print('\nLicenses:', licenses)
