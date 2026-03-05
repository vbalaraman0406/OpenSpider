const fs = require('fs');
const jobs = JSON.parse(fs.readFileSync('workspace/cron_jobs.json', 'utf8'));
const stock = jobs.filter(j => {
  const n = (j.name || '').toLowerCase();
  const p = (j.prompt || '').toLowerCase();
  return n.includes('stock') || n.includes('market') || n.includes('s&p') || n.includes('nasdaq') || p.includes('stock') || p.includes('market analysis');
});
// Print each job separately to avoid truncation
stock.forEach((job, i) => {
  console.log(`=== JOB ${i+1}: ${job.name} ===`);
  console.log('intervalHours:', job.intervalHours);
  console.log('preferredTime:', job.preferredTime);
  console.log('enabled:', job.enabled);
  console.log('lastRun:', job.lastRun);
  console.log('whatsappGroup:', job.whatsappGroup || 'NONE');
  console.log('PROMPT:', job.prompt);
  console.log('');
});
