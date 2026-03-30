import requests
import json
from datetime import datetime, timedelta

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

results = {}

# 1. Check CISA KEV catalog (JSON feed)
try:
    r = requests.get('https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json', headers=headers, timeout=15)
    if r.status_code == 200:
        data = r.json()
        vulns = data.get('vulnerabilities', [])
        # Get entries from last 7 days to be safe
        recent = []
        cutoff = datetime.now() - timedelta(days=7)
        for v in vulns:
            try:
                added = datetime.strptime(v.get('dateAdded',''), '%Y-%m-%d')
                if added >= cutoff:
                    recent.append(v)
            except:
                pass
        results['cisa_kev'] = recent[:20]  # limit
        results['cisa_kev_total'] = len(recent)
        results['cisa_catalog_count'] = data.get('catalogVersion', 'unknown')
        results['cisa_count'] = data.get('count', len(vulns))
    else:
        results['cisa_kev_error'] = f'Status {r.status_code}'
except Exception as e:
    results['cisa_kev_error'] = str(e)

print(json.dumps(results, indent=2, default=str))
