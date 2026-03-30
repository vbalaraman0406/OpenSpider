import os

backend_reqs_path = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/backend/requirements.txt'
root_reqs_path = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/requirements.txt'

# Read backend requirements
if os.path.exists(backend_reqs_path):
    with open(backend_reqs_path, 'r') as f:
        backend_reqs = f.read()
    print('Backend requirements.txt contents:')
    print(backend_reqs)
else:
    backend_reqs = ''
    print('No backend requirements.txt found')

# Create root requirements.txt with all needed deps
root_reqs = """fastapi>=0.100.0
uvicorn>=0.23.0
gunicorn>=21.2.0
fastf1>=3.3.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
requests>=2.31.0
python-dotenv>=1.0.0
httpx>=0.24.0
pytest-timeout>=2.2.0
"""

with open(root_reqs_path, 'w') as f:
    f.write(root_reqs)

print('\nRoot requirements.txt created at:', root_reqs_path)
print(root_reqs)
