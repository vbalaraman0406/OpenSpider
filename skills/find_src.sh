find . -maxdepth 1 -type d -not -name node_modules -not -name '.' 
echo '---'
find . -maxdepth 3 -type f -name '*.ts' -not -path './node_modules/*' 2>/dev/null
echo '---'
find . -maxdepth 3 -type d -name src -not -path './node_modules/*' 2>/dev/null
echo '---'
find . -maxdepth 3 -type d -name dist -not -path './node_modules/*' 2>/dev/null