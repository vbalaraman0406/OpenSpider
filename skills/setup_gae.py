import os

base = 'workspace/pitwall-ai'

# Ensure directories exist
for d in ['backend', 'frontend', 'backend/app']:
    os.makedirs(os.path.join(base, d), exist_ok=True)

# 1. backend/app.yaml
with open(os.path.join(base, 'backend/app.yaml'), 'w') as f:
    f.write("""runtime: python311
service: backend
instance_class: F2

entrypoint: gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind :$PORT

env_variables:
  PITWALL_ENV: "production"

automatic_scaling:
  min_instances: 0
  max_instances: 4
  target_cpu_utilization: 0.65
  min_pending_latency: 30ms
  max_pending_latency: automatic
""")

# 2. frontend/app.yaml
with open(os.path.join(base, 'frontend/app.yaml'), 'w') as f:
    f.write("""runtime: python311
service: default

handlers:
  - url: /static
    static_dir: build/static
    secure: always

  - url: /(.*\\.(json|ico|png|jpg|jpeg|svg|webp|woff2?|ttf|eot|css|js|map|txt|webmanifest))
    static_files: build/\\1
    upload: build/(.*\\.(json|ico|png|jpg|jpeg|svg|webp|woff2?|ttf|eot|css|js|map|txt|webmanifest))
    secure: always

  - url: /.*
    static_files: build/index.html
    upload: build/index.html
    secure: always
""")

# 3. dispatch.yaml
with open(os.path.join(base, 'dispatch.yaml'), 'w') as f:
    f.write("""dispatch:
  - url: "*/api/*"
    service: backend
""")

# 4. backend/requirements.txt
with open(os.path.join(base, 'backend/requirements.txt'), 'w') as f:
    f.write("""fastapi==0.115.6
uvicorn==0.34.0
gunicorn==23.0.0
fastf1==3.4.4
pandas==2.2.3
numpy==1.26.4
scikit-learn==1.6.1
xgboost==2.1.3
python-dateutil==2.9.0
requests==2.32.3
cachetools==5.5.1
""")

# 5. Makefile
with open(os.path.join(base, 'Makefile'), 'w') as f:
    f.write("""PROJECT_ID = pitwall-ai-prod

.PHONY: deploy-backend deploy-frontend deploy-all dev-backend dev-frontend

deploy-backend:
\tcd backend && gcloud app deploy app.yaml --project=$(PROJECT_ID) --quiet

deploy-frontend:
\tcd frontend && npm run build && gcloud app deploy app.yaml --project=$(PROJECT_ID) --quiet

deploy-all:
\tgcloud app deploy dispatch.yaml --project=$(PROJECT_ID) --quiet
\t$(MAKE) deploy-backend
\t$(MAKE) deploy-frontend

dev-backend:
\tcd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
\tcd frontend && npm start
""")

print('All 5 GAE config files created successfully:')
for root, dirs, files in os.walk(base):
    for fname in files:
        fpath = os.path.join(root, fname)
        sz = os.path.getsize(fpath)
        print(f'  {fpath} ({sz} bytes)')
