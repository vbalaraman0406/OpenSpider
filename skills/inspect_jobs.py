import json

with open('workspace/cron_jobs.json', 'r') as f:
    data = json.load(f)

if isinstance(data, list):
    print(f'Array of {len(data)} items')
    for i, job in enumerate(data):
        if isinstance(job, dict):
            print(f'  [{i}] keys={list(job.keys())}')
            # Print id-like fields
            for k in job:
                if 'id' in k.lower() or 'name' in k.lower() or 'iran' in str(job[k]).lower():
                    print(f'       {k}: {str(job[k])[:200]}')
        else:
            print(f'  [{i}] type={type(job).__name__}: {str(job)[:100]}')
elif isinstance(data, dict):
    print(f'Dict with keys: {list(data.keys())}')
    for k in data:
        v = data[k]
        if isinstance(v, list):
            print(f'  {k}: array of {len(v)}')
            for i, item in enumerate(v[:5]):
                if isinstance(item, dict):
                    print(f'    [{i}] keys={list(item.keys())}')
                    for ik in item:
                        if 'id' in ik.lower() or 'name' in ik.lower() or 'iran' in str(item[ik]).lower():
                            print(f'         {ik}: {str(item[ik])[:200]}')
        else:
            print(f'  {k}: {str(v)[:200]}')
