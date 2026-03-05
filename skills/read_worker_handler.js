const fs = require('fs');
const path = require('path');

const file = fs.readFileSync(path.join(__dirname, '..', 'src', 'agents', 'WorkerAgent.ts'), 'utf8');
const lines = file.split('\n');

// Print lines 360-400 (the send_whatsapp recipient resolution logic)
for (let i = 359; i < 410 && i < lines.length; i++) {
  console.log(`${i+1}: ${lines[i]}`);
}
