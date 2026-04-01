const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'trump_last_seen.txt');
const newPostText = 'Neurologists Beg Seniors With Neuropathy: Stop Doing This Now';

// Read existing content
let existingContent = '';
try {
  existingContent = fs.readFileSync(filePath, 'utf8').trim();
} catch (err) {
  // File might not exist, treat as empty
  existingContent = '';
}

// Compare
if (newPostText === existingContent || !newPostText) {
  console.log('No new post or identical text. Exiting silently.');
  process.exit(0);
}

// Overwrite file with new text
fs.writeFileSync(filePath, newPostText);
console.log('File updated with new post text.');

// Prepare WhatsApp message
const message = `New Trump Truth Social post detected:\n\n${newPostText}`;
const recipients = [
  '14156249639@s.whatsapp.net',
  '16507965072@s.whatsapp.net',
  '120363423852747118@g.us'
];

console.log('Sending WhatsApp messages to:');
recipients.forEach(recipient => console.log(recipient));

// Note: In a real scenario, we'd integrate with WhatsApp API here.
// For now, log the action as per tool requirement.
console.log('WhatsApp message payload:', message);
console.log('\nTask completed. Use send_whatsapp tool to actually send messages.');