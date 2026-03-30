import os
os.makedirs('workspace/memory', exist_ok=True)
with open('workspace/memory/trump_truth_last_check.md', 'w') as f:
    f.write('Last check timestamp: 2026-03-20 15:50:00 PDT\nLast post content hash: NONE (first run)')
print('Memory file created.')