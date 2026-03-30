import os
os.makedirs('workspace', exist_ok=True)
with open('workspace/trump_truth_last_check.txt', 'w') as f:
    f.write('2020-01-01T00:00:00+00:00')
print('Timestamp file written successfully')