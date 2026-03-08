import json

with open('workspace/cron_jobs.json', 'r') as f:
    jobs = json.load(f)

found = False
for job in jobs:
    if job.get('id') == 'cron-hc3fjkb7d':
        found = True
        prompt = job.get('prompt', '')
        print('FOUND JOB')
        print('Prompt length:', len(prompt))
        # Check for new driver names
        if 'Liam Lawson' in prompt:
            print('OK: Liam Lawson found')
        else:
            print('MISSING: Liam Lawson')
        if 'Valtteri Bottas' in prompt:
            print('OK: Valtteri Bottas found')
        else:
            print('MISSING: Valtteri Bottas')
        if 'Sergio Perez' in prompt:
            print('OK: Sergio Perez found')
        else:
            print('MISSING: Sergio Perez')
        if 'Oscar Piastri' in prompt:
            print('OK: Oscar Piastri found')
        else:
            print('MISSING: Oscar Piastri')
        if 'Carlos Sainz' in prompt:
            print('OK: Carlos Sainz found')
        else:
            print('MISSING: Carlos Sainz')
        if 'Ferrari' in prompt:
            print('OK: Ferrari found')
        else:
            print('MISSING: Ferrari')
        if 'Williams' in prompt:
            print('OK: Williams found')
        else:
            print('MISSING: Williams')
        if 'Bearman' in prompt:
            print('WARNING: Old driver Bearman still present')
        if 'Hadjar' in prompt:
            print('WARNING: Old driver Hadjar still present')
        if 'Aston Martin' in prompt:
            print('WARNING: Old constructor Aston Martin still present')
        if '$9.0M' in prompt:
            print('OK: Budget $9.0M found')
        else:
            print('MISSING: Budget $9.0M')
        # Print relevant sections
        lines = prompt.split('\n')
        for i, line in enumerate(lines):
            if 'Current' in line or 'Budget' in line or 'TURBO' in line:
                print(f'Line {i}: {line}')
        break

if not found:
    print('JOB NOT FOUND')
