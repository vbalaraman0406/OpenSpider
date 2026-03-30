import json, os, pathlib

# Ensure directories exist
os.makedirs('workspace/memory', exist_ok=True)

# Write baseline JSON
baseline = {
    "address": "9405 NE 102nd St, Vancouver, WA 98662",
    "baselinePrice": 799000,
    "lastStatus": "active",
    "lastChecked": "2026-03-24T16:49:00-07:00",
    "sources": {
        "zillow": 799000,
        "redfin": 799000,
        "realtor": None
    }
}

with open('workspace/memory/home_watch_baseline.json', 'w') as f:
    json.dump(baseline, f, indent=2)
print('Baseline written.')

# Append log line to daily log
log_file = 'workspace/memory/2026-03-24.md'
log_line = '- **16:49 PDT** — Home Watch: 9405 NE 102nd St, Vancouver WA — No change, still **$799,000** active. Confirmed on Zillow & Redfin. Realtor.com inaccessible.\n'

with open(log_file, 'a') as f:
    f.write(log_line)
print('Log written.')
