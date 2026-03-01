const { jsonrepair } = require('jsonrepair');

function dualLayerRepair(text) {
    try {
        const cleanJSON = text.trim();
        const firstBrace = cleanJSON.indexOf('{');
        const lastBrace = cleanJSON.lastIndexOf('}');
        let jsonStr = cleanJSON.substring(firstBrace, lastBrace + 1);

        const keys = ["thought", "action", "command", "target", "args", "filename", "content", "message", "summary_of_findings"];

        const extracted = {};

        for (const key of keys) {
            const keyMatch = new RegExp(`"${key}"\\s*:\\s*"([\\s\\S]*?)"(?:\\s*,\\s*"[A-Za-z_]+"|\\s*})`, 'i').exec(jsonStr);
            if (keyMatch && keyMatch[1]) {
                let rawValue = keyMatch[1];
                rawValue = rawValue.replace(/(?<!\\)"/g, '\\"');
                rawValue = rawValue.replace(/\n/g, '\\n').replace(/\r/g, '\\r').replace(/\t/g, '\\t');
                extracted[key] = rawValue;
            }
        }

        if (Object.keys(extracted).length === 0) throw new Error("No keys matched regex");

        const rebuiltParts = Object.entries(extracted).map(([k, v]) => `"${k}": "${v}"`);
        const rebuiltJSON = `{ ${rebuiltParts.join(", ")} }`;

        return JSON.parse(rebuiltJSON);
    } catch (e) {
        const cleanJSON = text.trim();
        const firstBrace = cleanJSON.indexOf('{');
        const lastBrace = cleanJSON.lastIndexOf('}');
        let jsonStr = cleanJSON.substring(firstBrace, lastBrace + 1);
        return JSON.parse(jsonrepair(jsonStr));
    }
}

const fs = require('fs');
const payload = fs.readFileSync('payload.json', 'utf8');

console.log("Testing dualLayerRepair...");
try {
    const res = dualLayerRepair(payload);
    console.log("SUCCESS!");
    console.log("Keys:", Object.keys(res));
    console.log("Content length:", res.content ? res.content.length : 0);
    console.log("Content end:", res.content ? res.content.substring(res.content.length - 100) : 'N/A');
} catch (e) {
    console.log("FAILED:", e.message);
}
