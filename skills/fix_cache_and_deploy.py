import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Fix main.py - use /tmp for cache on GCP App Engine (read-only filesystem)
main_path = os.path.join(base, 'backend/main.py')
with open(main_path, 'r') as f:
    content = f.read()

# Replace any cache directory creation that uses relative paths or /workspace/cache
# with /tmp/fastf1_cache which is writable on App Engine
content = content.replace("os.makedirs('cache'", "os.makedirs('/tmp/fastf1_cache'")
content = content.replace('os.makedirs("cache"', 'os.makedirs("/tmp/fastf1_cache"')
content = content.replace("os.makedirs('cache/')", "os.makedirs('/tmp/fastf1_cache')")
content = content.replace("os.path.join(os.path.dirname(__file__), 'cache')", "'/tmp/fastf1_cache'")
content = content.replace("'cache'", "'/tmp/fastf1_cache'")
content = content.replace('"cache"', '"/tmp/fastf1_cache"')

with open(main_path, 'w') as f:
    f.write(content)

print('Fixed main.py cache directory to /tmp/fastf1_cache')
print('\n--- main.py content ---')
with open(main_path, 'r') as f:
    print(f.read())

# Also fix fastf1_loader.py if it references cache directory
loader_path = os.path.join(base, 'backend/data/fastf1_loader.py')
if os.path.exists(loader_path):
    with open(loader_path, 'r') as f:
        loader_content = f.read()
    
    loader_content = loader_content.replace("os.makedirs('cache'", "os.makedirs('/tmp/fastf1_cache'")
    loader_content = loader_content.replace('os.makedirs("cache"', 'os.makedirs("/tmp/fastf1_cache"')
    loader_content = loader_content.replace("'cache'", "'/tmp/fastf1_cache'")
    loader_content = loader_content.replace('"cache"', '"/tmp/fastf1_cache"')
    
    with open(loader_path, 'w') as f:
        f.write(loader_content)
    print('\nFixed fastf1_loader.py cache directory to /tmp/fastf1_cache')

print('\nDone. Ready for deployment.')
