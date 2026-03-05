const fs = require('fs');
const path = require('path');

// Read whatsapp.ts to find auth path
try {
  const src = fs.readFileSync(path.join(__dirname, '..', 'src', 'whatsapp.ts'), 'utf8');
  const lines = src.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.includes('auth') || line.includes('store') || line.includes('Auth') || line.includes('Store')) {
      console.log(`L${i+1}: ${line.trim()}`);
    }
  }
} catch(e) {
  console.error('Could not read whatsapp.ts:', e.message);
}

console.log('\n--- Searching for store files ---');

// Search for store/cache files
function searchDir(dir, depth) {
  if (depth > 3) return;
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const e of entries) {
      if (e.name === 'node_modules' || e.name === '.git') continue;
      const full = path.join(dir, e.name);
      if (e.isDirectory()) {
        if (e.name.includes('auth') || e.name.includes('store') || e.name.includes('baileys') || e.name.includes('session')) {
          console.log('DIR:', full);
          // List contents
          try {
            const contents = fs.readdirSync(full);
            contents.forEach(c => console.log('  -', c));
          } catch(err) {}
        }
        searchDir(full, depth + 1);
      } else if (e.name.includes('store') || e.name.includes('group') || e.name.includes('session')) {
        console.log('FILE:', full);
      }
    }
  } catch(e) {}
}

searchDir(path.join(__dirname, '..'), 0);
