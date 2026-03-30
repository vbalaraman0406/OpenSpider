#!/bin/bash
echo '=== USA ===' 
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' 'https://downdetector.com/status/bmo/' 2>/dev/null | grep -ioE '(no problems at bmo|problems at bmo|user reports indicate[^<]*|possible problems|[0-9]+ reports)' | head -10
echo ''
echo '=== CANADA ==='
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' 'https://downdetector.ca/status/bmo/' 2>/dev/null | grep -ioE '(no problems at bmo|problems at bmo|user reports indicate[^<]*|possible problems|[0-9]+ reports)' | head -10
