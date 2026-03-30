#!/bin/bash
echo '=== TS files with group resolution ==='
find . -name '*.ts' -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' | while read f; do
  if grep -q 'resolveGroup\|groupName\|fetchGroup\|getGroup\|Family' "$f" 2>/dev/null; then
    echo "$f"
  fi
done
echo '=== JSON files with group names ==='
find . -name '*.json' -not -path '*/node_modules/*' -not -path '*/.git/*' | while read f; do
  if grep -q 'Family' "$f" 2>/dev/null; then
    echo "$f"
  fi
done
echo '=== Auth/store files ==='
find . -name 'auth_info*' -o -name 'store*' -o -name 'session*' -o -name 'baileys*' | grep -v node_modules | grep -v .git | head -10
