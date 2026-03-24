import json

with open('/Users/vbalaraman/OpenSpider/workspace/cron_jobs.json', 'r') as f:
    data = json.load(f)

# Print all keys from first job
print('Keys in first job:', list(data[0].keys()))
print('---')

# Print all jobs with all their fields (truncated)
for i, j in enumerate(data):
    # Print all string fields
    summary = {k: (str(v)[:80] if isinstance(v, str) else v) for k, v in j.items() if k != 'prompt'}
    prompt_preview = str(j.get('prompt', ''))[:60]
    summary['prompt_preview'] = prompt_preview
    # Check if any field contains BMO or Downdetector
    all_text = json.dumps(j).upper()
    if 'BMO' in all_text or 'DOWNDETECTOR' in all_text:
        print(f'*** MATCH [{i}]: {json.dumps(summary, indent=2)}')
