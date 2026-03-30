#!/bin/bash
echo '=== 1. HTML source from server ==='
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/ | head -20
echo ''
echo '=== 2. Check JS bundle accessibility ==='
# Extract JS filename from HTML
JS_FILE=$(curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/ | grep -o 'src="[^"]*\.js"' | head -1 | sed 's/src="//;s/"//')
echo "JS file referenced: $JS_FILE"
if [ -n "$JS_FILE" ]; then
  echo '=== 3. Fetching JS bundle ==='
  curl -s -o /dev/null -w 'HTTP_CODE=%{http_code} SIZE=%{size_download}' "https://f1-dot-vish-cloud.wl.r.appspot.com${JS_FILE}"
  echo ''
  echo '=== 4. First 200 chars of JS ==='
  curl -s "https://f1-dot-vish-cloud.wl.r.appspot.com${JS_FILE}" | head -c 200
  echo ''
fi
echo '=== 5. Check CSS bundle ==='
CSS_FILE=$(curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/ | grep -o 'href="[^"]*\.css"' | head -1 | sed 's/href="//;s/"//')
echo "CSS file referenced: $CSS_FILE"
if [ -n "$CSS_FILE" ]; then
  curl -s -o /dev/null -w 'HTTP_CODE=%{http_code} SIZE=%{size_download}' "https://f1-dot-vish-cloud.wl.r.appspot.com${CSS_FILE}"
  echo ''
fi
echo '=== 6. Check /f1/api/health ==='
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/health
echo ''
echo '=== 7. Check /f1/api/debug ==='
curl -s https://f1-dot-vish-cloud.wl.r.appspot.com/f1/api/debug
echo ''
echo '=== 8. Local dist files ==='
ls -la /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/
echo ''
ls -la /Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/dist/assets/
