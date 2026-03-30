import os, json, glob

# Search for cron_jobs.json
for root, dirs, files in os.walk('/Users/vbalaraman/OpenSpider'):
    # Skip node_modules and .git
    dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '.next')]
    for f in files:
        if f == 'cron_jobs.json':
            path = os.path.join(root, f)
            print(f'Found: {path}')
            with open(path, 'r') as fh:
                data = json.load(fh)
            for j in data:
                name = j.get('name', '').lower()
                prompt = j.get('prompt', '').lower()
                if 'bmo' in name or 'bmo' in prompt or 'downdetector' in name or 'downdetector' in prompt:
                    print('=== JOB ===')
                    print(json.dumps(j, indent=2))
                    print()
