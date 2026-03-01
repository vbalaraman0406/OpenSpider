import subprocess
import json
import sys

# We'll use urllib to search Google and parse results
import urllib.request
import urllib.parse
import re

def search_google(query):
    encoded = urllib.parse.quote(query)
    url = f'https://www.google.com/search?q={encoded}&num=10'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        return html
    except Exception as e:
        return f'Error: {e}'

# Search 1
print('=== SEARCH 1: Lets Remodel contractor Vancouver WA bathroom ===')
html1 = search_google("Let's Remodel contractor Vancouver WA bathroom")
# Extract URLs and snippets
urls1 = re.findall(r'href="(https?://[^"]+)"', html1)
# Filter relevant URLs
relevant1 = [u for u in urls1 if 'google' not in u and 'youtube' not in u and 'cache' not in u][:15]
for u in relevant1:
    print(u)

print()
print('=== SEARCH 2: Lets Remodel Vancouver Washington ===')
html2 = search_google("Let's Remodel Vancouver Washington")
urls2 = re.findall(r'href="(https?://[^"]+)"', html2)
relevant2 = [u for u in urls2 if 'google' not in u and 'youtube' not in u and 'cache' not in u][:15]
for u in relevant2:
    print(u)

# Also try to extract any phone numbers from the search results
print()
print('=== PHONE NUMBERS FOUND ===')
phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html1 + html2)
for p in set(phones):
    print(p)

# Extract text snippets mentioning 'remodel'
print()
print('=== SNIPPETS ===')
snippets = re.findall(r'([^<>]{20,200}[Rr]emodel[^<>]{0,200})', html1)
for s in snippets[:10]:
    clean = re.sub(r'\s+', ' ', s).strip()
    print(clean[:200])
