const fs = require('fs');
const path = require('path');

// Read the raw JSON array from file
const jsonFilePath = path.join(__dirname, 'trump_temp_posts.json');
let rawData;
try {
  rawData = fs.readFileSync(jsonFilePath, 'utf8');
  console.log('Raw JSON data read successfully:');
  console.log(rawData);
} catch (error) {
  console.error('Error reading JSON file:', error.message);
  process.exit(1);
}

// Parse the JSON
let posts;
try {
  posts = JSON.parse(rawData);
  console.log('Parsed posts:', JSON.stringify(posts, null, 2));
} catch (error) {
  console.error('Error parsing JSON:', error.message);
  process.exit(1);
}

// Check if WhatsApp JIDs are passed as arguments
const args = process.argv.slice(2);
if (args.length > 0) {
  console.log('WhatsApp JIDs provided:', args.join(', '));
  // Simulate sending alerts via native API (as per instructions, the actual script will handle this)
  console.log('Simulating alert sending to JIDs...');
  // In the real script, this would call the native API to send WhatsApp messages
} else {
  console.log('No WhatsApp JIDs provided.');
}

console.log('Script execution completed.');