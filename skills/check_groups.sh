#!/bin/bash
echo '=== whatsapp_config.json ==='
cat ./whatsapp_config.json
echo ''
echo '=== WhatsApp service files ==='
find . -name 'whatsapp*' -not -path '*/node_modules/*' -not -path '*/.git/*'
