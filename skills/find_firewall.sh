grep -rl 'allowedDM\|dmPolicy\|mention' . --include='*.js' --include='*.ts' --exclude-dir=node_modules 2>/dev/null
echo '==='
grep -rl 'mentionedJid\|mentioned' . --include='*.js' --include='*.ts' --exclude-dir=node_modules 2>/dev/null
echo '==='
cat package.json 2>/dev/null | head -30