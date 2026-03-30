#!/bin/bash
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  'https://downdetector.com/status/bmo-harris/' 2>/dev/null | \
  python3 -c "
import sys, re
html = sys.stdin.read()

# Check for CAPTCHA/block
if 'cf-browser-verification' in html or 'challenge-platform' in html:
    print('BLOCKED: Cloudflare challenge detected')

# Title
t = re.search(r'<title>(.*?)</title>', html, re.I)
if t: print(f'TITLE: {t.group(1)}')

# Status check
if 'No problems at BMO' in html:
    print('STATUS: NO_PROBLEMS')
elif 'Problems at BMO' in html:
    print('STATUS: PROBLEMS_DETECTED')
elif 'Possible problems' in html:
    print('STATUS: POSSIBLE_PROBLEMS')
else:
    print('STATUS: UNKNOWN')

# CSS class indicators
if 'is-danger' in html: print('CSS: is-danger found')
if 'is-warning' in html: print('CSS: is-warning found') 
if 'is-success' in html: print('CSS: is-success found')

# Report counts
reports = re.findall(r'(\d+)\s*reports?', html, re.I)
if reports: print(f'REPORTS: {reports[:10]}')

# Extract visible text around status
clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.I)
clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL|re.I)
clean = re.sub(r'<[^>]+>', ' ', clean)
clean = re.sub(r'\s+', ' ', clean).strip()
print(f'TEXT_PREVIEW: {clean[:1500]}')
"
