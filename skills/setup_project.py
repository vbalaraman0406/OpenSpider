import os

base = os.path.dirname(os.path.abspath(__file__))

dirs = [
    'backend/app',
    'backend/cache',
    'frontend/src/pages',
    'frontend/src/components',
    'frontend/public'
]

for d in dirs:
    os.makedirs(os.path.join(base, d), exist_ok=True)
    print(f'Created: {d}')

print('All directories created.')
