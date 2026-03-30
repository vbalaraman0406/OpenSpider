import requests
import json
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
results = {}

# 1. Fetch BleepingComputer RSS for recent zero-day news
try:
    r = requests.get('https://www.bleepingcomputer.com/feed/', headers=headers, timeout=15)
    if r.status_code == 200:
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall('.//item')[:20]:
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            pubdate = item.find('pubDate').text if item.find('pubDate') is not None else ''
            desc = item.find('description').text if item.find('description') is not None else ''
            # Filter for security-relevant articles
            keywords = ['zero-day', 'cve-', 'vulnerability', 'exploit', 'ransomware', 'breach', 'hack', 'cisa', 'patch', 'malware']
            if any(k in title.lower() or k in desc.lower()[:200] for k in keywords):
                items.append({'title': title, 'link': link, 'date': pubdate[:25]})
        results['bleeping'] = items[:10]
    else:
        results['bleeping_error'] = f'Status {r.status_code}'
except Exception as e:
    results['bleeping_error'] = str(e)

# 2. Fetch The Hacker News RSS
try:
    r = requests.get('https://feeds.feedburner.com/TheHackersNews', headers=headers, timeout=15)
    if r.status_code == 200:
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall('.//item')[:20]:
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            pubdate = item.find('pubDate').text if item.find('pubDate') is not None else ''
            keywords = ['zero-day', 'cve-', 'vulnerability', 'exploit', 'ransomware', 'breach', 'hack', 'cisa', 'patch', 'malware', 'ai ', 'deepfake']
            if any(k in title.lower() for k in keywords):
                items.append({'title': title, 'link': link, 'date': pubdate[:25]})
        results['hackernews'] = items[:10]
    else:
        results['hackernews_error'] = f'Status {r.status_code}'
except Exception as e:
    results['hackernews_error'] = str(e)

# 3. Check NVD for recent critical CVEs (CVSS >= 9.0)
try:
    end = datetime.utcnow()
    start = end - timedelta(days=3)
    url = f'https://services.nvd.nist.gov/rest/json/cves/2.0?pubStartDate={start.strftime("%Y-%m-%dT00:00:00.000")}&pubEndDate={end.strftime("%Y-%m-%dT23:59:59.999")}&cvssV3Severity=CRITICAL'
    r = requests.get(url, headers=headers, timeout=20)
    if r.status_code == 200:
        data = r.json()
        nvd_cves = []
        for vuln in data.get('vulnerabilities', [])[:15]:
            cve = vuln.get('cve', {})
            cve_id = cve.get('id', '')
            desc_list = cve.get('descriptions', [])
            desc = next((d['value'] for d in desc_list if d.get('lang') == 'en'), 'N/A')[:150]
            metrics = cve.get('metrics', {})
            score = 'N/A'
            for key in ['cvssMetricV31', 'cvssMetricV30']:
                if key in metrics:
                    score = metrics[key][0].get('cvssData', {}).get('baseScore', 'N/A')
                    break
            nvd_cves.append({'id': cve_id, 'score': score, 'desc': desc})
        results['nvd_critical'] = nvd_cves
        results['nvd_total'] = data.get('totalResults', 0)
    else:
        results['nvd_error'] = f'Status {r.status_code}'
except Exception as e:
    results['nvd_error'] = str(e)

print(json.dumps(results, indent=2, default=str))
