import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai/frontend/src'

# Read current api.ts
api_path = os.path.join(base, 'api.ts')
with open(api_path) as f:
    content = f.read()
print('=== Current api.ts ===')
print(content)

# Read Dashboard.tsx to see what it imports
dash_path = os.path.join(base, 'pages', 'Dashboard.tsx')
with open(dash_path) as f:
    dash = f.read()

# Find all imports from api
import re
api_imports = re.findall(r"from\s+['\"]\.\.?\/api['\"]|import\s+.*from\s+['\"]\.\.?\/api['\"]", dash)
print(f'\nDashboard api imports: {api_imports}')

# Check all pages for api imports
pages_dir = os.path.join(base, 'pages')
all_imports = set()
for fname in os.listdir(pages_dir):
    if fname.endswith('.tsx'):
        fpath = os.path.join(pages_dir, fname)
        with open(fpath) as f:
            page_content = f.read()
        # Find named imports from api
        matches = re.findall(r'import\s+\{([^}]+)\}\s+from\s+[\'\"]\.\.?\/api[\'\"]', page_content)
        for m in matches:
            for name in m.split(','):
                all_imports.add(name.strip())
        # Find default imports
        matches2 = re.findall(r'import\s+(\w+)\s+from\s+[\'\"]\.\.?\/api[\'\"]', page_content)
        for m in matches2:
            all_imports.add(f'default:{m}')

print(f'\nAll API imports needed across pages: {all_imports}')

# Write comprehensive api.ts with all needed exports
new_api_ts = '''import axios from 'axios';

const api = axios.create({
  baseURL: '/f1/api',
  timeout: 30000,
});

export const getRaces = async (year: number) => {
  try {
    const response = await api.get(`/races/${year}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching races:', error);
    return [];
  }
};

export const getRaceResults = async (year: number, round: number) => {
  try {
    const response = await api.get(`/race/${year}/${round}/results`);
    return response.data;
  } catch (error) {
    console.error('Error fetching race results:', error);
    return [];
  }
};

export const getRaceLaps = async (year: number, round: number) => {
  try {
    const response = await api.get(`/race/${year}/${round}/laps`);
    return response.data;
  } catch (error) {
    console.error('Error fetching race laps:', error);
    return [];
  }
};

export const getDrivers = async (year: number) => {
  try {
    const response = await api.get(`/drivers/${year}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching drivers:', error);
    return [];
  }
};

export const getDriverStats = async (year: number, driverId: string) => {
  try {
    const response = await api.get(`/driver/${year}/${driverId}/stats`);
    return response.data;
  } catch (error) {
    console.error('Error fetching driver stats:', error);
    return {};
  }
};

export default api;
''';

with open(api_path, 'w') as f:
    f.write(new_api_ts)
print('\n[OK] Written comprehensive api.ts with all named exports')

# Verify
with open(api_path) as f:
    print('\n=== New api.ts ===')
    print(f.read())
