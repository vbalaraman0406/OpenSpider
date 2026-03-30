import { getParticipatingGroups } from '../dist/whatsapp.js';

try {
  const groups = await getParticipatingGroups();
  if (groups && groups.length > 0) {
    groups.forEach(g => {
      console.log(`JID: ${g.id} | Name: ${g.subject || g.name || 'unknown'}`);
    });
  } else {
    console.log('No groups found or function returned empty.');
  }
} catch (e) {
  console.log('Error:', e.message);
}
process.exit(0);
