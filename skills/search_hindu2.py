import requests
import re
import html as h

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try The Hindu's own search
urls_to_try = [
    ('The Hindu Search', 'https://www.thehindu.com/search/?q=Tamil+Nadu+election+2026&order=DESC&sort=publishdate'),
    ('Google broad', 'https://www.google.com/search?q=Tamil+Nadu+election+2026+thehindu&num=10'),
    ('Google broad2', 'https://www.google.com/search?q=Tamil+Nadu+2026+election+news&num=10'),
    ('Google polls', 'https://www.google.com/search?q=Tamil+Nadu+2026+election+opinion+poll+seat+prediction&num=10'),
]

for label, url in urls_to_try:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print('=== ' + label + ' (status: ' + str(r.status_code) + ') ===')
        if 'thehindu.com/search' in url:
            # Extract article titles and links from The Hindu search
            titles = re.findall(r'<h3[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', r.text)
            if not titles:
                titles = re.findall(r'class="story-card[^"]*"[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', r.text, re.DOTALL)
            if not titles:
                # Try broader pattern
                titles = re.findall(r'href="(https://www\.thehindu\.com/[^"]+)"[^>]*>([^<]{15,})</a>', r.text)
            for u, t in titles[:8]:
                print('  ' + t.strip())
                print('  ' + u)
                print()
            if not titles:
                print('  No article links found')
                # Print a snippet of the HTML to debug
                print('  HTML snippet: ' + r.text[500:1500])
        else:
            # Google results
            links = re.findall(r'/url\?q=(https?://[^&]+)&', r.text)
            unique = list(dict.fromkeys(links))[:8]
            for link in unique:
                clean = h.unescape(link)
                if 'google.com' not in clean:
                    print('  ' + clean)
            if not unique:
                print('  No results')
        print()
    except Exception as e:
        print('Error for ' + label + ': ' + str(e))
