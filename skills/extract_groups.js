const fs = require('fs');
const jobs = JSON.parse(fs.readFileSync('workspace/cron_jobs.json', 'utf8'));
const groups = new Set();
jobs.forEach(j => {
  if (j.whatsappGroup) groups.add(j.whatsappGroup);
});

try {
  const config = JSON.parse(fs.readFileSync('workspace/whatsapp_config.json', 'utf8'));
  if (config.groups) {
    Object.keys(config.groups).forEach(g => groups.add(g));
  }
  console.log('whatsapp_config.json found and parsed.');
} catch(e) {
  console.log('whatsapp_config.json not found or not parseable.');
}

console.log('\n=== ALL UNIQUE WHATSAPP GROUPS ===');
const sorted = [...groups].sort();
sorted.forEach((g, i) => console.log((i+1) + '. ' + g));
console.log('\nTotal: ' + sorted.length + ' groups');
