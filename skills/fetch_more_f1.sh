#!/bin/bash
# Fetch pre-season testing results
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' 'https://www.google.com/search?q=2025+F1+pre-season+testing+Bahrain+results+lap+times+fastest' -o /tmp/f1_testing.html 2>/dev/null
echo "Testing: $(wc -c < /tmp/f1_testing.html) bytes"

# Fetch F1 Fantasy prices 2025
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' 'https://www.google.com/search?q=2025+F1+Fantasy+driver+prices+constructor+prices+budget' -o /tmp/f1_fantasy_prices.html 2>/dev/null
echo "Fantasy prices: $(wc -c < /tmp/f1_fantasy_prices.html) bytes"

# Fetch F1 Fantasy scoring system
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' 'https://www.google.com/search?q=F1+Fantasy+2025+scoring+system+points+turbo+driver' -o /tmp/f1_fantasy_scoring.html 2>/dev/null
echo "Fantasy scoring: $(wc -c < /tmp/f1_fantasy_scoring.html) bytes"

# Fetch 2025 F1 power rankings
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' 'https://www.google.com/search?q=2025+F1+team+power+rankings+predictions+car+performance' -o /tmp/f1_rankings.html 2>/dev/null
echo "Rankings: $(wc -c < /tmp/f1_rankings.html) bytes"

# Fetch expert F1 Fantasy picks
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' 'https://www.google.com/search?q=2025+F1+Fantasy+best+team+picks+round+1+Australia+expert+recommendations' -o /tmp/f1_expert_picks.html 2>/dev/null
echo "Expert picks: $(wc -c < /tmp/f1_expert_picks.html) bytes"

# Fetch race calendar
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' 'https://www.google.com/search?q=2025+F1+race+calendar+schedule+dates' -o /tmp/f1_calendar.html 2>/dev/null
echo "Calendar: $(wc -c < /tmp/f1_calendar.html) bytes"
