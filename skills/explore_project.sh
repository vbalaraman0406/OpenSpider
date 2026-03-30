#!/bin/bash
echo '=== Top-level directories ==='
ls -la
echo '=== Find all .ts files ==='
find . -name '*.ts' -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' | head -40
echo '=== Find all .js files in non-node_modules ==='
find . -name '*.js' -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' | head -40
