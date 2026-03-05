const { getParticipatingGroups } = require('../dist/whatsapp.js');
getParticipatingGroups().then(g => {
  console.log(JSON.stringify(g, null, 2));
  process.exit(0);
}).catch(e => {
  console.error('ERROR:', e.message);
  process.exit(1);
});
