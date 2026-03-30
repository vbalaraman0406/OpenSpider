import os, time

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Rename .gcloudignore to force full upload
gi = os.path.join(base, '.gcloudignore')
gi_bak = gi + '.bak'
if os.path.exists(gi):
    os.rename(gi, gi_bak)
    print('Renamed .gcloudignore to .bak')

# Write a proper .gcloudignore that excludes node_modules but nothing else
with open(gi, 'w') as f:
    f.write('node_modules/\n.git/\n__pycache__/\n*.pyc\nfrontend/src/\nfrontend/node_modules/\n')
print('Wrote minimal .gcloudignore')

# Add unique marker to requirements.txt to bust hash
req = os.path.join(base, 'requirements.txt')
with open(req, 'r') as f:
    content = f.read()
ts = str(time.time())
if '# DEPLOY' in content:
    lines = [l for l in content.split('\n') if '# DEPLOY' not in l]
    content = '\n'.join(lines)
content = content.rstrip() + '\n# DEPLOY=' + ts + '\n'
with open(req, 'w') as f:
    f.write(content)
print('requirements.txt cache-busted with', ts)
