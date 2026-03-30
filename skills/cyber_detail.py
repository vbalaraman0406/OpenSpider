import requests
import re
from html import unescape

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

# Key articles to fetch details from
urls = [
    'https://thehackernews.com/',  # Main page for latest
    'https://www.bleepingcomputer.com/news/security/',
    'https://www.securityweek.com/category/vulnerabilities/',
]

# 1. Get The Hacker News full RSS with descriptions
try:
    r = requests.get('https://feeds.feedburner.com/TheHackersNews', headers=headers, timeout=15)
    items = re.findall(r'<item>(.*?)</item>', r.text, re.DOTALL)[:15]
    print("=== THE HACKER NEWS - FULL DETAILS ===")
    for item in items:
        title = re.search(r'<title>(.*?)</title>', item)
        desc = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
        link = re.search(r'<link />(.*?)\n', item) or re.search(r'<link>(.*?)</link>', item)
        pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item)
        if title:
            t = unescape(title.group(1))
            d = unescape(desc.group(1))[:300] if desc else ''
            d = re.sub(r'<[^>]+>', '', d).strip()
            l = link.group(1).strip() if link else ''
            pd = pubdate.group(1) if pubdate else ''
            print(f"\nTITLE: {t}")
            print(f"DATE: {pd}")
            print(f"LINK: {l}")
            print(f"DESC: {d}")
except Exception as e:
    print(f"THN error: {e}")

print("\n" + "="*80)

# 2. Get SecurityWeek RSS with descriptions
try:
    r = requests.get('https://www.securityweek.com/feed/', headers=headers, timeout=15)
    items = re.findall(r'<item>(.*?)</item>', r.text, re.DOTALL)[:15]
    print("\n=== SECURITYWEEK - FULL DETAILS ===")
    for item in items:
        title = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item) or re.search(r'<title>(.*?)</title>', item)
        desc = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', item, re.DOTALL) or re.search(r'<description>(.*?)</description>', item, re.DOTALL)
        pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item)
        if title:
            t = unescape(title.group(1))
            d = unescape(desc.group(1))[:300] if desc else ''
            d = re.sub(r'<[^>]+>', '', d).strip()
            pd = pubdate.group(1) if pubdate else ''
            print(f"\nTITLE: {t}")
            print(f"DATE: {pd}")
            print(f"DESC: {d}")
except Exception as e:
    print(f"SecurityWeek error: {e}")

print("\n" + "="*80)

# 3. Check CISA alerts/advisories RSS
try:
    r = requests.get('https://www.cisa.gov/cybersecurity-advisories/all.xml', headers=headers, timeout=15)
    if r.status_code == 200:
        items = re.findall(r'<item>(.*?)</item>', r.text, re.DOTALL)[:10]
        print(f"\n=== CISA ADVISORIES: {len(items)} items ===")
        for item in items:
            title = re.search(r'<title>(.*?)</title>', item)
            pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item)
            link = re.search(r'<link>(.*?)</link>', item)
            if title:
                print(f"  [{pubdate.group(1) if pubdate else 'N/A'}] {title.group(1)}")
                if link: print(f"    {link.group(1)}")
    else:
        print(f"CISA advisories: HTTP {r.status_code}")
except Exception as e:
    print(f"CISA advisories error: {e}")

print("\n" + "="*80)

# 4. Search for banking/financial sector breaches
try:
    r = requests.get('https://www.google.com/search?q=bank+breach+hack+financial+cybersecurity+2025+2026&tbs=qdr:d3&num=5', headers=headers, timeout=15)
    # Extract titles from Google results
    titles = re.findall(r'<h3[^>]*>(.*?)</h3>', r.text)
    print(f"\n=== BANKING/FINANCIAL SECTOR NEWS ===")
    for t in titles[:8]:
        clean = re.sub(r'<[^>]+>', '', t)
        print(f"  - {unescape(clean)}")
except Exception as e:
    print(f"Banking search error: {e}")

print("\nDone.")
