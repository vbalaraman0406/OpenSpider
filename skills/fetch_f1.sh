#!/bin/bash
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' 'https://en.wikipedia.org/wiki/2025_Formula_One_World_Championship' -o /tmp/f1_2025.html 2>/dev/null
echo "Downloaded $(wc -c < /tmp/f1_2025.html) bytes"
