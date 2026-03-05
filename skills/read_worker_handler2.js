const fs = require('fs');
const path = require('path');

const file = fs.readFileSync(path.join(__dirname, '..', 'src', 'agents', 'WorkerAgent.ts'), 'utf8');
const lines = file.split('\n');

// Print lines 370-402
for (let i = 372; i < 402 && i < lines.length; i++) {
  console.log(`${i+1}: ${lines[i]}`);
}
