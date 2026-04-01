const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'trump_last_seen.txt');
const newPostText = 'Neurologists Beg Seniors With Neuropathy: Stop Doing This Now';

// Overwrite file with new text
fs.writeFileSync(filePath, newPostText);
console.log('File updated with new post text.');