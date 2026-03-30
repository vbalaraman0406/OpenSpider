import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

urls = [
    ('The Hindu TN Politics', 'https://www.thehindu.com/news/national/tamil-nadu/'),
    ('The Hindu Elections', 'https://www.thehindu.com/elections/'),
    ('DuckDuckGo TN Election', 'https://html.duckduckgo.com/html/?q=Tamil+Nadu+election+2026+thehindu.com'),
    ('DuckDuckGo TN Polls', 'https://html.duckduckgo.com/html/?q=Tamil+Nadu+2026+election+opinion+poll+seat+prediction'),
]

for label, url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print('=== ' + label + ' (status: ' + str(r.status_code) + ') ===')
        if 'thehindu.com' in url:
            # Extract article headlines
            titles = re.findall(r'href="(https://www\.thehindu\.com/news/[^"]+)"[^>]*>\s*([^<]{20,}?)\s*</a>', r.text)
            if not titles:
                titles = re.findall(r'<h[23][^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', r.text)
            if not titles:
                titles = re.findall(r'"title"\s*:\s*"([^"]+)".*?"url"\s*:\s*"([^"]+)"', r.text)
                titles = [(u, t) for t, u in titles]
            for u, t in titles[:10]:
                t = t.strip()
                if len(t) > 15 and ('election' in t.lower() or 'dmk' in t.lower() or 'aiadmk' in t.lower() or 'bjp' in t.lower() or 'tvk' in t.lower() or 'poll' in t.lower() or 'tamil' in t.lower() or 'seat' in t.lower() or 'vote' in t.lower() or 'campaign' in t.lower() or 'alliance' in t.lower() or 'assembly' in t.lower() or len(titles) <= 10):
                    print('  ' + t)
                    print('  ' + u)
                    print()
            if not titles:
                # Show first few links
                all_links = re.findall(r'href="([^"]+)"[^>]*>([^<]{15,})</a>', r.text)
                for u2, t2 in all_links[:10]:
                    print('  ' + t2.strip() + ' | ' + u2)
                print()
        else:
            # DuckDuckGo results
            results = re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.+?)</a>', r.text, re.DOTALL)
            if not results:
                results = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*class="result__a"[^>]*>(.+?)</a>', r.text, re.DOTALL)
            if not results:
                results = re.findall(r'href="(https?://[^"]+)"[^>]*>([^<]{20,})</a>', r.text)
            for u, t in results[:10]:
                clean_t = re.sub(r'<[^>]+>', '', t).strip()
                if len(clean_t) > 10:
                    print('  ' + clean_t)
                    print('  ' + u)
                    print()
            if not results:
                print('  No results found')
                print('  Snippet: ' + r.text[:800])
        print()
    except Exception as e:
        print('Error: ' + str(e))
