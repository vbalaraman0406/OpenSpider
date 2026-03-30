import requests
import json
from datetime import datetime, timedelta

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

# 1. CISA KEV recent entries
try:
    r = requests.get('https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json', headers=headers, timeout=15)
    data = r.json()
    vulns = data.get('vulnerabilities', [])
    cutoff = datetime.now() - timedelta(days=7)
    for v in vulns:
        try:
            added = datetime.strptime(v.get('dateAdded',''), '%Y-%m-%d')
            if added >= cutoff:
                print(f"KEV: {v.get('cveID')} | {v.get('vendorProject')} | {v.get('product')} | {v.get('vulnerabilityName')} | Added: {v.get('dateAdded')} | Due: {v.get('dueDate')} | Action: {v.get('requiredAction','')[:80]}")
        except:
            pass
except Exception as e:
    print(f"KEV Error: {e}")

print("\n---\n")

# 2. Fetch THN for AI/banking/ransomware news
try:
    import xml.etree.ElementTree as ET
    r = requests.get('https://feeds.feedburner.com/TheHackersNews', headers=headers, timeout=15)
    root = ET.fromstring(r.content)
    for item in root.findall('.//item')[:20]:
        title = item.find('title').text if item.find('title') is not None else ''
        pubdate = item.find('pubDate').text if item.find('pubDate') is not None else ''
        print(f"THN: [{pubdate[:16]}] {title}")
except Exception as e:
    print(f"THN Error: {e}")

print("\n---\n")

# 3. SecurityWeek RSS
try:
    r = requests.get('https://www.securityweek.com/feed/', headers=headers, timeout=15)
    if r.status_code == 200:
        root = ET.fromstring(r.content)
        for item in root.findall('.//item')[:15]:
            title = item.find('title').text if item.find('title') is not None else ''
            pubdate = item.find('pubDate').text if item.find('pubDate') is not None else ''
            print(f"SW: [{pubdate[:16]}] {title}")
except Exception as e:
    print(f"SW Error: {e}")
