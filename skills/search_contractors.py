import subprocess
import json
import re
import urllib.request
import urllib.parse

def search_google(query):
    """Search using a simple HTTP request to Google and extract snippets."""
    encoded = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded}&num=20"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        return html
    except Exception as e:
        return f"ERROR: {e}"

def extract_text_from_html(html):
    """Strip HTML tags to get readable text."""
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_urls_and_titles(html):
    """Extract URLs and their associated text from search results."""
    results = []
    # Find all anchor tags with href
    links = re.findall(r'<a[^>]+href="(/url\?q=([^&"]+)[^"]*|([^"]*))"[^>]*>(.*?)</a>', html, re.DOTALL)
    for match in links:
        url = match[1] if match[1] else match[2]
        title = re.sub(r'<[^>]+>', '', match[3])
        if url and ('http' in url) and not ('google.com' in url) and not ('youtube.com' in url):
            url = urllib.parse.unquote(url)
            results.append({'url': url, 'title': title.strip()})
    return results

queries = [
    'site:bbb.org bathroom remodel contractor Vancouver WA',
    'site:houzz.com bathroom remodel Vancouver WA',
    'Google Maps bathroom remodel contractors Vancouver WA 98662 top rated',
    'best bathroom remodel contractors Vancouver WA 98662 reviews',
    'bathroom tile contractor Vancouver WA 98662 rated',
    'bathroom renovation contractor Vancouver WA reviews phone number',
    'top rated bathroom remodeling companies Vancouver Washington 98662'
]

all_data = []
for q in queries:
    print(f"\n=== Searching: {q} ===")
    html = search_google(q)
    if html.startswith('ERROR'):
        print(html)
        continue
    
    # Extract URLs and titles
    urls_titles = extract_urls_and_titles(html)
    for item in urls_titles[:15]:
        print(f"  URL: {item['url'][:100]}")
        print(f"  Title: {item['title'][:100]}")
    
    # Extract readable text (first 5000 chars for analysis)
    text = extract_text_from_html(html)
    # Look for phone numbers
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    if phones:
        print(f"  Phones found: {phones[:10]}")
    
    # Look for ratings
    ratings = re.findall(r'(\d\.\d)\s*(?:star|rating|out of|/5|★)', text, re.IGNORECASE)
    if ratings:
        print(f"  Ratings found: {ratings[:10]}")
    
    # Print relevant snippet portions
    # Look for contractor-related content
    relevant_sections = []
    words = text.split()
    for i, w in enumerate(words):
        if any(kw in w.lower() for kw in ['contractor', 'remodel', 'bathroom', 'tile', 'vanity', 'plumb', 'renovation']):
            start = max(0, i-10)
            end = min(len(words), i+20)
            snippet = ' '.join(words[start:end])
            if len(snippet) > 30:
                relevant_sections.append(snippet)
    
    # Deduplicate and print
    seen = set()
    for s in relevant_sections[:20]:
        short = s[:50]
        if short not in seen:
            seen.add(short)
            print(f"  Snippet: {s[:200]}")
    
    all_data.append({'query': q, 'text': text[:3000], 'urls': urls_titles[:10]})

print("\n\n=== FULL TEXT DUMPS FOR PARSING ===")
for d in all_data:
    print(f"\n--- Query: {d['query']} ---")
    print(d['text'][:2000])
