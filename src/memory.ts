import fs from 'node:fs';
import path from 'node:path';

const WORKSPACE_DIR = path.join(process.cwd(), 'workspace');
const MEMORY_DIR = path.join(WORKSPACE_DIR, 'memory');

export function initWorkspace() {
    if (!fs.existsSync(WORKSPACE_DIR)) fs.mkdirSync(WORKSPACE_DIR, { recursive: true });
    if (!fs.existsSync(MEMORY_DIR)) fs.mkdirSync(MEMORY_DIR, { recursive: true });

    // Initialize memory.md - Long term agent memory
    const memoryPath = path.join(WORKSPACE_DIR, 'memory.md');
    if (!fs.existsSync(memoryPath)) {
        fs.writeFileSync(memoryPath, `# Long Term Memory\n\nRecord enduring facts, system quirks, or important constraints discovered during operation here.\n`);
    }
}

export function readMemoryContext(): string {
    initWorkspace();

    let context = "--- Context Memory ---\n\n";

    try {
        const ltm = fs.readFileSync(path.join(WORKSPACE_DIR, 'memory.md'), 'utf-8');
        context += `## memory.md (Long Term Key Information)\n${ltm}\n\n`;

        // Read today's short-term daily log
        const todayStr = new Date().toISOString().split('T')[0];
        const todayPath = path.join(MEMORY_DIR, `${todayStr}.md`);

        if (fs.existsSync(todayPath)) {
            let todayLog = fs.readFileSync(todayPath, 'utf-8');

            // --- OpenClaw Cognitive Compaction ---
            // Prevent runaway token bloat by applying a strict sliding window on raw transcripts.
            const MAX_MEMORY_CHARS = 100000;
            if (todayLog.length > MAX_MEMORY_CHARS) {
                console.log(`[Compaction] Daily transcript exceeds token limit. Pruning historical chatter...`);
                const truncatedIndex = todayLog.indexOf('\n\n', todayLog.length - MAX_MEMORY_CHARS);
                todayLog = `...[EARLIER CONTEXT PRUNED BY OPENCLAW COMPACTION TO SAVE TOKENS]...\n` +
                    (truncatedIndex !== -1 ? todayLog.substring(truncatedIndex) : todayLog.substring(todayLog.length - MAX_MEMORY_CHARS));
            }

            context += `## Today's Conversation Log (${todayStr})\n${todayLog}\n\n`;
        } else {
            context += `## Today's Conversation Log (${todayStr})\n(No prior interactions today.)\n\n`;
        }

    } catch (e) {
        console.error("[Memory] Error reading context:", e);
    }

    context += "----------------------\n";
    return context;
}

export function logMemory(sender: 'User' | 'Agent', message: string) {
    initWorkspace();
    const now = new Date();
    const todayStr = now.toISOString().split('T')[0];
    const todayPath = path.join(MEMORY_DIR, `${todayStr}.md`);

    const logEntry = `[${now.toLocaleTimeString()}] **${sender}**: ${message}\n\n`;
    fs.appendFileSync(todayPath, logEntry, 'utf-8');
}
