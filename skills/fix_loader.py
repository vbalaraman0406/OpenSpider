import os

loader_path = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/data/fastf1_loader.py'

with open(loader_path, 'r') as f:
    content = f.read()

# Fix the CACHE_DIR line - replace the broken os.path.join with simple /tmp/fastf1_cache
old_cache = 'CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "/tmp/fastf1_cache")'
new_cache = 'CACHE_DIR = "/tmp/fastf1_cache"'
content = content.replace(old_cache, new_cache)

# Also wrap makedirs and cache enable in try/except
old_makedirs = 'os.makedirs(CACHE_DIR, exist_ok=True)\nfastf1.Cache.enable_cache(CACHE_DIR)'
new_makedirs = 'try:\n    os.makedirs(CACHE_DIR, exist_ok=True)\n    fastf1.Cache.enable_cache(CACHE_DIR)\nexcept Exception as e:\n    logger.warning(f"Could not enable fastf1 cache: {e}")'
content = content.replace(old_makedirs, new_makedirs)

with open(loader_path, 'w') as f:
    f.write(content)

print('Fixed fastf1_loader.py cache dir')

# Verify
with open(loader_path, 'r') as f:
    for i, line in enumerate(f.readlines()[:25], 1):
        print(f'{i}: {line.rstrip()}')
