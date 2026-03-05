const fs = require('fs');
const jobs = JSON.parse(fs.readFileSync('workspace/cron_jobs.json', 'utf8'));
const stock = jobs.filter(j => {
  const n = (j.name || '').toLowerCase();
  const p = (j.prompt || j.task || j.content || '').toLowerCase();
  return n.includes('stock') || n.includes('market') || n.includes('s&p') || n.includes('nasdaq') || p.includes('stock') || p.includes('market analysis');
});
console.log(JSON.stringify(stock, null, 2));
