const fs = require('fs');
const path = require('path');
const memoryDir = path.join(process.cwd(), 'workspace', 'memory');
if (!fs.existsSync(memoryDir)) {
    console.log("Memory dir not found");
    process.exit(0);
}
const files = fs.readdirSync(memoryDir)
    .filter(f => /^\d{4}-\d{2}-\d{2}\.md$/.test(f))
    .sort();
let logContent = "";
for (const file of files) {
    logContent += fs.readFileSync(path.join(memoryDir, file), 'utf-8') + "\n\n";
}
const logLines = logContent.split('\n');
const history = [];
let currentTimestamp = "";
let currentSender = "";
let currentText = [];
for (const line of logLines) {
    const match = line.match(/^\[(.*?)\] \*\*(.*?)\*\*: (.*)/);
    if (match) {
        if (currentTimestamp) {
            history.push({ type: 'chat', data: `[${currentSender}] ${currentText.join('\n').trim()}` });
        }
        currentTimestamp = match[1];
        currentSender = match[2];
        currentText = [match[3]];
    } else if (currentTimestamp) {
        currentText.push(line);
    }
}
if (currentTimestamp) {
    history.push({ type: 'chat', data: `[${currentSender}] ${currentText.join('\n').trim()}` });
}
console.log(history.length);
