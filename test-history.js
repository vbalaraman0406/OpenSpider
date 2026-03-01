"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const process_1 = __importDefault(require("process"));
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
const memoryDir = path_1.default.join(process_1.default.cwd(), 'workspace', 'memory');
const todayStr = new Date().toISOString().split('T')[0];
const todayPath = path_1.default.join(memoryDir, `${todayStr}.md`);
const logContent = fs_1.default.readFileSync(todayPath, 'utf-8');
// Split strictly by the exact prefix, capturing timestamp and sender
const parts = logContent.split(/^\[(.*?)\] \*\*(.*?)\*\*: /m);
const history = [];
// parts[0] is preamble (often empty line)
// segments repeat in groups of 3: [timestamp, sender, textBody]
for (let i = 1; i < parts.length; i += 3) {
    const timestamp = parts[i];
    const rawSender = parts[i + 1];
    const text = parts[i + 2];
    let displaySender = rawSender;
    if (rawSender === 'User')
        displaySender = 'You';
    if (rawSender === 'Agent')
        displaySender = 'Agent';
    history.push({
        type: 'chat',
        data: `[${displaySender}] ${text ? text.trim() : ""}`,
    });
}
console.log(`Parsed ${history.length} entries.`);
console.log(`Last entry raw data length: ${history[history.length - 1]?.data.length}`);
console.log(history[history.length - 1]?.data);
//# sourceMappingURL=test-history.js.map