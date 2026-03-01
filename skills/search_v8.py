import urllib.request
import json
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# Try SerpAPI-style or use startpage.com which is more scrape-friendly
# Also try Brave Search API which has a simpler structure

queries = [
    'bathroom remodeling contractor Vancouver WA 98662',
    'bathroom tile contractor Vancouver WA reviews',
    'best bathroom renovation Vancouver WA rated'
]

all_results = []

# Try Brave Search (HTML)
for q in queries:
    try:
        url = f'https://search.brave.com/search?q={q.replace(" ", "+")}'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        print(f'Brave query: {q}')
        print(f'Status: {resp.status}, HTML length: {len(html)}')
        
        # Extract snippets - Brave uses <div class="snippet-description">
        snippets = re.findall(r'<div class="snippet-description[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
        titles = re.findall(r'<span class="snippet-title">(.*?)</span>', html, re.DOTALL)
        
        if not snippets:
            snippets = re.findall(r'<p class="snippet-description">(.*?)</p>', html, re.DOTALL)
        if not titles:
            titles = re.findall(r'<div class="title">(.*?)</div>', html, re.DOTALL)
            
        print(f'Titles: {len(titles)}, Snippets: {len(snippets)}')
        
        # Also try generic extraction
        # Look for rating patterns like "4.8 stars" or "4.8/5"
        ratings = re.findall(r'(\d\.\d)\s*(?:stars?|/5|rating|out of)', html, re.IGNORECASE)
        print(f'Ratings found: {ratings}')
        
        # Look for phone numbers
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', html)
        phones = list(set(phones))
        print(f'Phones found: {phones}')
        
        # Look for business names near ratings
        biz_patterns = re.findall(r'([A-Z][A-Za-z\s&]+(?:Remodel|Construction|Tile|Bath|Renovation|Contractor|Home|Kitchen|Plumb)[A-Za-z\s]*)', html)
        biz_patterns = list(set(biz_patterns))
        print(f'Business names: {biz_patterns[:10]}')
        
        # Print first 2000 chars to understand structure
        clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)
        clean = re.sub(r'<[^>]+>', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        print(f'Text preview: {clean[:1500]}')
        print('---')
    except Exception as e:
        print(f'Brave error for {q}: {e}')
        print('---')
