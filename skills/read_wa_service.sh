#!/bin/bash
echo '=== src directory structure ==='
find ./src -name '*.ts' -not -path '*/node_modules/*' | head -30
echo '=== Looking for whatsapp service ==='
find . -path '*/whatsapp*' -name '*.ts' -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*'
find . -path '*/services*' -name '*.ts' -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' | head -20
