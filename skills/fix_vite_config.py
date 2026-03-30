import os

base = '/Users/vbalaraman/OpenSpider/workspace/pitwall-ai'

# Fix vite.config.js to disable code-splitting
vite_config = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/f1/',
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
});
"""

vite_path = os.path.join(base, 'frontend', 'vite.config.js')
with open(vite_path, 'w') as f:
    f.write(vite_config)
print(f'Wrote vite.config.js: {len(vite_config)} bytes')

# Also delete vite.config.ts if it exists to avoid conflicts
vite_ts = os.path.join(base, 'frontend', 'vite.config.ts')
if os.path.exists(vite_ts):
    os.remove(vite_ts)
    print(f'Deleted conflicting vite.config.ts')
else:
    print('No vite.config.ts to delete')

# Verify
with open(vite_path, 'r') as f:
    print(f.read())
