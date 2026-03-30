#!/bin/bash
gcloud app services set-traffic f1 --splits f1v50=1 --project vish-cloud --quiet
