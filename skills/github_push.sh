#!/bin/bash
cd /Users/vbalaraman/OpenSpider/workspace/pitwall-ai
git remote set-url origin https://vbalaraman0405:REDACTED_GITHUB_PAT@github.com/vbalaraman0405/pitwall-ai.git
echo "Remote URL set."
git push -u origin main 2>&1
PUSH_EXIT=$?
if [ $PUSH_EXIT -ne 0 ]; then
  echo "Push failed with exit code $PUSH_EXIT. Attempting to create repo via API..."
  curl -s -H "Authorization: token REDACTED_GITHUB_PAT" https://api.github.com/user/repos -d '{"name":"pitwall-ai","private":false,"description":"Pitwall.ai - F1 Analytics Platform powered by FastF1 + FastAPI + React"}'
  echo ""
  echo "Retrying push..."
  git push -u origin main 2>&1
  PUSH_EXIT2=$?
  if [ $PUSH_EXIT2 -ne 0 ]; then
    echo "Push failed again. Trying username vbalaraman0406..."
    git remote set-url origin https://vbalaraman0406:REDACTED_GITHUB_PAT@github.com/vbalaraman0406/pitwall-ai.git
    curl -s -H "Authorization: token REDACTED_GITHUB_PAT" https://api.github.com/user/repos -d '{"name":"pitwall-ai","private":false,"description":"Pitwall.ai - F1 Analytics Platform powered by FastF1 + FastAPI + React"}'
    echo ""
    git push -u origin main 2>&1
  fi
fi
echo "Done."