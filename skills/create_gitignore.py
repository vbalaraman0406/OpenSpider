import os

repo_dir = 'workspace/pitwall-ai'
with open(os.path.join(repo_dir, '.gitignore'), 'w') as f:
    f.write('node_modules/\n__pycache__/\n*.pyc\n.env\n*.egg-info/\ndist/\nbuild/\n.vite/\nfastf1_cache/\n*.log\n')
print('Created .gitignore')
