const { jsonrepair } = require('jsonrepair');
const fs = require('fs');

const payload = fs.readFileSync('payload.json', 'utf8');
try {
    JSON.parse(payload);
} catch (e) {
    console.log("JSON.PARSE ERROR:", e.message);
}
