import os

# Check current app.yaml
with open('workspace/pitwall-ai/app.yaml') as f:
    content = f.read()
print('Current app.yaml:')
print(content)
print('---')

# The deploy showed target service: [default] which means service: f1 was not picked up
# Let me rewrite app.yaml to make sure it has service: f1
app_yaml = 'service: f1\nruntime: python311\n\nentrypoint: gunicorn -w 2 -k uvicorn.workers.UvicornWorker backend.main:app --bind :$PORT\n\ninstance_class: F2\n\nautomatic_scaling:\n  min_instances: 0\n  max_instances: 3\n\nenv_variables:\n  PYTHON_ENV: "production"\n'

with open('workspace/pitwall-ai/app.yaml', 'w') as f:
    f.write(app_yaml)
print('Rewrote app.yaml')

# Create .gcloudignore to skip node_modules, .git, etc.
gcloudignore = '''# Node
frontend/node_modules/
node_modules/

# Git
.git/
.gitignore

# Python
__pycache__/
*.pyc
.venv/
venv/

# Frontend source (only need dist)
frontend/src/
frontend/public/
frontend/*.ts
frontend/*.js
frontend/*.json
frontend/*.html

# Dev files
*.md
.env
*.sh
*.log
'''

with open('workspace/pitwall-ai/.gcloudignore', 'w') as f:
    f.write(gcloudignore)
print('Created .gcloudignore')

# Verify
with open('workspace/pitwall-ai/app.yaml') as f:
    print('Verified app.yaml:')
    print(f.read())
