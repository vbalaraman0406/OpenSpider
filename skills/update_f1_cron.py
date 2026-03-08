import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

for job in jobs:
    if job.get('id') == 'cron-hc3fjkb7d':
        old_prompt = job['prompt']
        print('=== OLD PROMPT ===')
        print(old_prompt[:500])
        print('...')
        
        # Replace old driver references with new ones
        # Need to find the Current Drivers/Constructors section and update it
        # Let's look for patterns
        import re
        
        # Replace Current Drivers line
        new_drivers = 'Current Drivers: Oscar Piastri ($25.5M, TURBO), Carlos Sainz ($11.8M), Liam Lawson ($6.5M), Valtteri Bottas ($5.9M), Sergio Perez ($6.0M)'
        new_constructors = 'Current Constructors: Ferrari ($23.3M), Williams ($12.0M)'
        new_budget = 'Budget remaining: $9.0M'
        
        # Replace Current Drivers line
        prompt = re.sub(r'Current Drivers:.*?(?=\n|Current Constructors)', new_drivers + '\n', old_prompt, flags=re.DOTALL)
        # Replace Current Constructors line  
        prompt = re.sub(r'Current Constructors:.*?(?=\n|Budget)', new_constructors + '\n', prompt, flags=re.DOTALL)
        # Replace Budget remaining line
        prompt = re.sub(r'Budget remaining:.*?(?=\n|$)', new_budget, prompt)
        
        job['prompt'] = prompt
        print('\n=== NEW PROMPT ===')
        print(prompt[:800])
        print('...')
        break

with open('workspace/cron_jobs.json', 'w') as f:
    json.dump(jobs, f, indent=2)

print('\nFile written successfully.')
