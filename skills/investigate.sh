#!/bin/bash
echo '=== SCHEDULER PROCESSES ==='
ps aux 2>/dev/null | grep -iE '(sched|cron|heartbeat|openspider|node)' | grep -v grep | grep -v 'Chrome' | grep -v 'investigate' | head -20

echo ''
echo '=== ALL PROJECT FILES (non node_modules) ==='
find ./ -maxdepth 5 -type f \( -name '*.js' -o -name '*.ts' -o -name '*.mjs' -o -name '*.json' -o -name '*.db' -o -name '*.sqlite' -o -name '*.log' \) -not -path '*/node_modules/*' -not -path '*/.next/*' -not -path '*/dist/*' -not -path '*/.git/*' 2>/dev/null | sort | head -80

echo ''
echo '=== GREP FOR SCHEDULER/CRON IN SOURCE ==='
grep -rl 'schedule\|cron\|heartbeat\|setInterval' ./ --include='*.ts' --include='*.js' --include='*.mjs' -not -path '*/node_modules/*' -not -path '*/.next/*' -not -path '*/.git/*' 2>/dev/null | head -20

echo ''
echo '=== GREP FOR TASK STORAGE ==='
grep -rl 'cron-\|scheduledTasks\|taskRegistry\|cronJobs' ./ --include='*.ts' --include='*.js' --include='*.json' -not -path '*/node_modules/*' -not -path '*/.next/*' -not -path '*/.git/*' 2>/dev/null | head -20
