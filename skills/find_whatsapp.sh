#!/bin/bash
find . -name '*.ts' -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' > /tmp/ts_files.txt
grep -rl 'Family' $(cat /tmp/ts_files.txt) 2>/dev/null
echo '---SEPARATOR---'
grep -rl 'whitelist' $(cat /tmp/ts_files.txt) 2>/dev/null
echo '---SEPARATOR---'
grep -rl 'groupJid\|group_jid\|groupId' $(cat /tmp/ts_files.txt) 2>/dev/null
echo '---SEPARATOR---'
find . -name '*.json' -not -path '*/node_modules/*' -not -path '*/.git/*' -path '*whitelist*' 2>/dev/null
echo '---SEPARATOR---'
find . -name 'whatsapp*' -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null
