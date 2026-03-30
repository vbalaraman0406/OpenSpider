import requests
import json
import os
import re
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

results = {}

# Check BMO Canada
try:
    r = requests.get('https://downdetector.ca/status/bmo/', headers=headers, timeout=15, allow_redirects=True)
    text = r.text
    # Extract status
    if 'no current problems' in text.lower() or 'no problems' in text.lower():
        ca_status = 'No current problems'
    elif 'possible problems' in text.lower():
        ca_status = 'Possible problems'
    elif 'problems at' in text.lower():
        ca_status = 'Problems detected'
    else:
        ca_status = 'Unknown'
    
    # Extract reported problems from the gauge/chart section
    ca_problems = []
    # Look for problem categories in the page
    problem_matches = re.findall(r'<td[^>]*>\s*([^<]+?)\s*</td>\s*<td[^>]*>\s*(\d+)\s*%', text)
    if problem_matches:
        for name, pct in problem_matches[:5]:
            ca_problems.append({'name': name.strip(), 'pct': int(pct)})
    
    if not ca_problems:
        # Try alternative pattern
        problem_matches2 = re.findall(r'"name"\s*:\s*"([^"]+)".*?"percentage"\s*:\s*(\d+)', text)
        for name, pct in problem_matches2[:5]:
            ca_problems.append({'name': name.strip(), 'pct': int(pct)})
    
    if not ca_problems:
        # Try looking for gauge labels
        gauge_matches = re.findall(r'class="[^"]*gauge-label[^"]*"[^>]*>([^<]+)<', text)
        for g in gauge_matches[:5]:
            ca_problems.append({'name': g.strip(), 'pct': 0})
    
    results['ca'] = {'status': ca_status, 'problems': ca_problems, 'url': r.url}
    print(f'CA Status: {ca_status}')
    print(f'CA Problems: {ca_problems}')
except Exception as e:
    results['ca'] = {'status': 'Error', 'problems': [], 'error': str(e)}
    print(f'CA Error: {e}')

# Check BMO USA
try:
    r = requests.get('https://downdetector.com/status/bmo/', headers=headers, timeout=15, allow_redirects=True)
    text = r.text
    final_url = r.url
    
    if 'bmo' in final_url.lower() and '/status/' in final_url.lower():
        if 'no current problems' in text.lower() or 'no problems' in text.lower():
            us_status = 'No current problems'
        elif 'possible problems' in text.lower():
            us_status = 'Possible problems'
        elif 'problems at' in text.lower():
            us_status = 'Problems detected'
        else:
            us_status = 'Unknown'
        
        us_problems = []
        problem_matches = re.findall(r'<td[^>]*>\s*([^<]+?)\s*</td>\s*<td[^>]*>\s*(\d+)\s*%', text)
        if problem_matches:
            for name, pct in problem_matches[:5]:
                us_problems.append({'name': name.strip(), 'pct': int(pct)})
        
        results['us'] = {'status': us_status, 'problems': us_problems, 'url': final_url}
    else:
        results['us'] = {'status': 'Page not available (redirected)', 'problems': [], 'url': final_url}
    
    print(f'US Status: {results["us"]["status"]}')
    print(f'US URL: {final_url}')
    print(f'US Problems: {results["us"].get("problems", [])}')
except Exception as e:
    results['us'] = {'status': 'Error', 'problems': [], 'error': str(e)}
    print(f'US Error: {e}')

# Load previous state
prev_path = 'workspace/bmo_downdetector_last.json'
prev_data = None
if os.path.exists(prev_path):
    with open(prev_path, 'r') as f:
        prev_data = json.load(f)

# Determine if there are changes
changed = False
if prev_data is None:
    changed = True
    print('No previous data - first run')
else:
    for region in ['ca', 'us']:
        old = prev_data.get(region, {})
        new = results.get(region, {})
        if old.get('status') != new.get('status'):
            changed = True
            print(f'{region.upper()} status changed: {old.get("status")} -> {new.get("status")}')
        old_probs = set(p['name'] for p in old.get('problems', []))
        new_probs = set(p['name'] for p in new.get('problems', []))
        if old_probs != new_probs:
            changed = True
            print(f'{region.upper()} problems changed: {old_probs} -> {new_probs}')

# Save current state
results['timestamp'] = datetime.now().isoformat()
with open(prev_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f'State saved to {prev_path}')

# Output decision
print(f'CHANGED={changed}')
print(f'RESULT_JSON={json.dumps(results)}')
