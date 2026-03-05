import json

with open('/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json', 'r') as f:
    data = json.load(f)

# Check the third stock job and enabled status of all stock jobs
for i, j in enumerate(data):
    jid = j.get('id', '')
    if jid in ['cron-lvoem5try', 'cron-uqf91a91j', 'cron-mzyrevand']:
        print(f"=== INDEX {i} | ID: {jid} ===")
        print(f"Name: '{j.get('name', '')}'")
        print(f"Description: '{j.get('description', '')}'") 
        print(f"Enabled: {j.get('enabled')}")
        print(f"Status: {j.get('status')}")
        print(f"PreferredTime: {j.get('preferredTime')}")
        print(f"intervalHours: {j.get('intervalHours')}")
        print(f"All keys: {list(j.keys())}")
        print(f"Prompt (first 300): {j.get('prompt','')[:300]}")
        print('---')
        print()

# Also check if schedule_task created NEW entries
print(f"\nTotal jobs in file: {len(data)}")
print("\nAll job names/descriptions:")
for i, j in enumerate(data):
    print(f"  [{i}] name='{j.get('name','')}' desc='{j.get('description','')[:60]}' id={j.get('id','')} enabled={j.get('enabled')}")
