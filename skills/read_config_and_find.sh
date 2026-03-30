#!/bin/bash
echo '=== whatsapp_config.json ==='
cat /Users/vbalaraman/OpenSpider/whatsapp_config.json
echo ''
echo '=== Find list_groups or group-related JS files ==='
find /Users/vbalaraman/OpenSpider -name 'list_groups*' -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null
find /Users/vbalaraman/OpenSpider -name 'extract_groups*' -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null
find /Users/vbalaraman/OpenSpider -name 'find_groups*' -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null
find /Users/vbalaraman/OpenSpider -name 'test_group*' -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null
echo '=== workspace directory ==='
ls /Users/vbalaraman/OpenSpider/workspace/ 2>/dev/null
echo '=== Check for group cache/store files ==='
find /Users/vbalaraman/OpenSpider -name '*group*' -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null
