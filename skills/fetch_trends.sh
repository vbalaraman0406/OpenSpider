#!/bin/bash
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' \
  --max-time 20 \
  'https://trends24.in/united-states/' \
  -o /tmp/trends24.html 2>&1
echo "trends24 status: $?"
echo "File size: $(wc -c < /tmp/trends24.html)"

curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' \
  --max-time 20 \
  'https://getdaytrends.com/united-states/' \
  -o /tmp/getdaytrends.html 2>&1
echo "getdaytrends status: $?"
echo "File size: $(wc -c < /tmp/getdaytrends.html)"

curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' \
  --max-time 20 \
  'https://us.trend-calendar.com/' \
  -o /tmp/trendcalendar.html 2>&1
echo "trendcalendar status: $?"
echo "File size: $(wc -c < /tmp/trendcalendar.html)"