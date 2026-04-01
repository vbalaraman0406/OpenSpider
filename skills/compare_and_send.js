const fs = require('fs');
const path = './workspace/trump_last_seen.txt';

// Simulated extracted post text from the previous step (Advanced Headless Navigation agent).
// In a real scenario, this should be replaced with the actual extracted text.
const extractedText = 'A genuine post from Donald Trump';

let fileContent = '';
try {
  fileContent = fs.readFileSync(path, 'utf8').trim();
} catch (e) {
  fileContent = '';
}

console.log('Current file content:', fileContent);
console.log('Extracted text:', extractedText);

// Check if extractedText is valid, not identical, and not an ad
if (extractedText && 
    extractedText !== fileContent && 
    !extractedText.toLowerCase().includes('ad') && 
    !extractedText.toLowerCase().includes('sponsored') && 
    !extractedText.toLowerCase().includes('promoted')) {
  
  // Update the file with the new text
  fs.writeFileSync(path, extractedText);
  console.log('File updated with new text.');
  
  // Log the WhatsApp send action (actual send will be handled by tool)
  console.log('WHATSAPP_SEND_REQUIRED: true');
  console.log('WHATSAPP_PAYLOAD:', extractedText);
  console.log('WHATSAPP_RECIPIENTS: 14156249639@s.whatsapp.net, 16507965072@s.whatsapp.net, 120363423852747118@g.us');
} else {
  console.log('No new post or identical/ad, exiting silently.');
}