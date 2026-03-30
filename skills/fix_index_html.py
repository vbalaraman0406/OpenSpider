import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Clean index.html - NO inline scripts, just #root div
index_html = '<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="UTF-8" />\n    <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n    <title>Pitwall.ai - F1 Analytics</title>\n  </head>\n  <body>\n    <div id="root"></div>\n    <script type="module" src="/src/main.tsx"></script>\n  </body>\n</html>\n'

# Write source index.html
path = os.path.join(base, 'frontend', 'index.html')
with open(path, 'w') as f:
    f.write(index_html)
print('Wrote source index.html:', len(index_html), 'bytes')

# Delete dist/index.html to force clean rebuild
dist_index = os.path.join(base, 'frontend', 'dist', 'index.html')
if os.path.exists(dist_index):
    os.remove(dist_index)
    print('Deleted old dist/index.html')

# Delete old JS bundle
dist_assets = os.path.join(base, 'frontend', 'dist', 'assets')
if os.path.exists(dist_assets):
    for f_name in os.listdir(dist_assets):
        fp = os.path.join(dist_assets, f_name)
        os.remove(fp)
        print('Deleted old asset:', f_name)

print('Ready for clean rebuild')
