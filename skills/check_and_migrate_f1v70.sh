#!/bin/bash
gcloud app versions list --service f1 --project vish-cloud 2>&1
echo '=== MIGRATING TO f1v70 ==='
gcloud app services set-traffic f1 --splits f1v70=1 --project vish-cloud --quiet 2>&1
echo '=== DONE ==='
