import urllib.request
import re
import html
import json

url = 'https://www.instagram.com/reel/DVWEXdQEp-B/?igsh=MWloYWEzOG8zY2pvcQ=='

req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
})

try:
    resp = urllib.request.urlopen(req, timeout=15)
    page = resp.read().decode('utf-8', errors='replace')
except Exception as e:
    print(f'Error fetching: {e}')
    page = ''

if not page:
    print('No page content.')
    exit()

# Try to find any require/define calls with media data
# Instagram embeds data in script tags with require calls
patterns_to_try = [
    r'"caption"\s*:\s*\{[^}]*"text"\s*:\s*"([^"]{1,500})"',
    r'"edge_media_to_caption".*?"text"\s*:\s*"([^"]{1,1000})"',
    r'"shortcode"\s*:\s*"([^"]+)"',
    r'"owner"\s*:\s*\{[^}]*"username"\s*:\s*"([^"]+)"',
    r'"full_name"\s*:\s*"([^"]+)"',
    r'"edge_liked_by"\s*:\s*\{[^}]*"count"\s*:\s*(\d+)',
    r'"edge_media_preview_like"\s*:\s*\{[^}]*"count"\s*:\s*(\d+)',
    r'"edge_media_to_comment"\s*:\s*\{[^}]*"count"\s*:\s*(\d+)',
    r'"video_view_count"\s*:\s*(\d+)',
    r'"taken_at_timestamp"\s*:\s*(\d+)',
    r'"is_video"\s*:\s*(true|false)',
    r'"video_url"\s*:\s*"([^"]+)"',
    r'"display_url"\s*:\s*"([^"]+)"',
    r'"accessibility_caption"\s*:\s*"([^"]{1,500})"',
]

print('=== PATTERN MATCHES ===')
for p in patterns_to_try:
    matches = re.findall(p, page)
    if matches:
        print(f'Pattern: {p[:60]}...')
        for m in matches[:3]:
            print(f'  -> {m[:300]}')
        print()

# Also try to find xdt_api__v1__media__shortcode__web_info or similar
api_match = re.search(r'xdt_api__v1__media__shortcode__web_info', page)
if api_match:
    print('Found xdt_api reference')
    # Get surrounding context
    start = max(0, api_match.start() - 100)
    end = min(len(page), api_match.end() + 2000)
    snippet = page[start:end]
    print(snippet[:2000])

# Look for any large JSON objects in script tags
scripts = re.findall(r'<script[^>]*>([^<]{500,})</script>', page)
print(f'\nFound {len(scripts)} large script blocks')
for i, s in enumerate(scripts[:5]):
    # Check if it contains media-related keywords
    keywords = ['caption', 'username', 'shortcode', 'video_url', 'like_count', 'comment_count']
    found_kw = [k for k in keywords if k in s]
    if found_kw:
        print(f'\nScript {i} ({len(s)} chars) contains: {found_kw}')
        # Find the relevant section
        for kw in found_kw:
            idx = s.find(kw)
            if idx >= 0:
                print(f'  Context around "{kw}": ...{s[max(0,idx-50):idx+200]}...')
                print()
