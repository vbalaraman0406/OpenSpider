const fs = require('fs');
const payload = fs.readFileSync('payload.json', 'utf8');

const regex = /\{/g;
let match;
while ((match = regex.exec(payload)) !== null) {
    console.log(`Found "{" at position ${match.index}`);
    console.log(`Context: ${payload.substring(match.index - 20, match.index + 20).replace(/\n/g, '\\n')}`);
}
