import { readFileSync, writeFileSync } from 'fs';

const configPath = '/Users/vbalaraman/OpenSpider/workspace/whatsapp_config.json';
const config = JSON.parse(readFileSync(configPath, 'utf8'));

console.log('Before update:');
const target = config.allowedDMs.find(d => d.number === '61423475992');
console.log(JSON.stringify(target, null, 2));

if (target) {
  target.mode = 'always';
  writeFileSync(configPath, JSON.stringify(config, null, 2));
  console.log('\nAfter update:');
  console.log(JSON.stringify(target, null, 2));
  console.log('\nConfig saved successfully.');
} else {
  console.log('Number 61423475992 not found in allowedDMs!');
}