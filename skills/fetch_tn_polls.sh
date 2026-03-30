#!/bin/bash
# Try to fetch key articles using curl
echo '=== Source 1: Matrize IANS Survey ==='
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' 'https://www.google.com/search?q=Matrize+IANS+Tamil+Nadu+2026+opinion+poll+seat+prediction' 2>/dev/null | python3 -c "
import sys, re
html = sys.stdin.read()
snippets = re.findall(r'<div[^>]*class=\"[^\"]*BNeawe[^\"]*\"[^>]*>(.*?)</div>', html, re.DOTALL)
for s in snippets[:15]:
    clean = re.sub(r'<[^>]+>', ' ', s).strip()
    if len(clean) > 40:
        print(clean[:300])
        print('---')
"

echo ''
echo '=== Source 2: TN 2026 Alliance Details ==='
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' 'https://www.google.com/search?q=Tamil+Nadu+2026+election+alliance+DMK+AIADMK+BJP+TVK+seat+sharing' 2>/dev/null | python3 -c "
import sys, re
html = sys.stdin.read()
snippets = re.findall(r'<div[^>]*class=\"[^\"]*BNeawe[^\"]*\"[^>]*>(.*?)</div>', html, re.DOTALL)
for s in snippets[:15]:
    clean = re.sub(r'<[^>]+>', ' ', s).strip()
    if len(clean) > 40:
        print(clean[:300])
        print('---')
"

echo ''
echo '=== Source 3: TN 2026 Controversies ==='
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' 'https://www.google.com/search?q=Tamil+Nadu+2026+election+controversies+breaking+news+latest' 2>/dev/null | python3 -c "
import sys, re
html = sys.stdin.read()
snippets = re.findall(r'<div[^>]*class=\"[^\"]*BNeawe[^\"]*\"[^>]*>(.*?)</div>', html, re.DOTALL)
for s in snippets[:15]:
    clean = re.sub(r'<[^>]+>', ' ', s).strip()
    if len(clean) > 40:
        print(clean[:300])
        print('---')
"