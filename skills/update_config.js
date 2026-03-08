const fs = require('fs');
const path = '/Users/vbalaraman/OpenSpider/workspace/whatsapp_config.json';
const cfg = JSON.parse(fs.readFileSync(path, 'utf8'));
if (!cfg.allowedDMs.includes('14164222657')) cfg.allowedDMs.push('14164222657');
fs.writeFileSync(path, JSON.stringify(cfg, null, 2));
console.log(fs.readFileSync(path, 'utf8'));