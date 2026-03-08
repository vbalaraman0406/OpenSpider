import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

def write(path, content):
    full = os.path.join(base, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(content)
    print(f'Created: {path}')

# 1. README.md
write('README.md', """# Pitwall.ai - F1 Analytics Dashboard

> Real-time Formula 1 race analytics, telemetry visualization, and predictive insights.

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11, FastAPI, FastF1, Pandas, scikit-learn |
| **Frontend** | React 18, Tailwind CSS, Recharts |
| **Hosting** | Google App Engine |
| **Data** | FastF1 (Official F1 Timing Data) |

## Features

- Race results and classification tables
- Lap time analysis with interactive charts
- Driver telemetry comparison (speed, throttle, brake, gear)
- Tire strategy visualization
- Head-to-head driver statistics
- Predictive race modeling (coming soon)

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure
```
pitwall-ai/
  backend/
    app/
      main.py          # FastAPI application
      f1_data.py        # FastF1 data service
    requirements.txt
    app.yaml           # GAE config
  frontend/
    src/
      pages/           # Page components
      components/       # Shared components
      App.jsx
      index.css
    tailwind.config.js
    package.json
```

## Roadmap

- [x] Project scaffolding
- [x] FastF1 data integration
- [x] Race dashboard with results table
- [x] Lap time charts
- [ ] Live timing integration
- [ ] ML-based race predictions
- [ ] Weather impact analysis
- [ ] Custom domain setup

## License

MIT
""")

# 2. .gitignore
write('.gitignore', """# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.env
venv/
*.egg
.f1cache/
cache/

# Node
node_modules/
.next/
out/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
*.log
""")

# 3. backend/requirements.txt
write('backend/requirements.txt', """fastf1==3.7.0
fastapi==0.115.0
uvicorn[standard]==0.30.0
pandas==2.2.0
numpy==1.26.0
scikit-learn==1.4.0
python-dotenv==1.0.0
gunicorn==22.0.0
""")

# 4. backend/app/__init__.py
write('backend/app/__init__.py', '')

# 5. backend/app.yaml
write('backend/app.yaml', """runtime: python311

instance_class: F2

automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 0
  max_instances: 3

entrypoint: gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind :$PORT

env_variables:
  CACHE_DIR: "/tmp/f1cache"
""")

print('Batch 1 complete: README, gitignore, requirements, app.yaml')
