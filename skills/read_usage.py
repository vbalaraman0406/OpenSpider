import os

parent = os.path.dirname(os.getcwd())

# Read usage.ts
usage_file = os.path.join(parent, 'src', 'usage.ts')
print('===== usage.ts =====')
with open(usage_file, 'r') as f:
    print(f.read())
