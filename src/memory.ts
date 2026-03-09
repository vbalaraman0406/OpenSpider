import fs from 'node:fs';
import path from 'node:path';

const rootDir = __dirname.endsWith('src') || __dirname.endsWith('dist') ? path.join(__dirname, '..') : __dirname;
const WORKSPACE_DIR = path.join(rootDir, 'workspace');
const MEMORY_DIR = path.join(WORKSPACE_DIR, 'memory');

export function initWorkspace() {
    const isFirstRun = !fs.existsSync(WORKSPACE_DIR);

    if (isFirstRun) {
        fs.mkdirSync(WORKSPACE_DIR, { recursive: true });
    }

    // Always sync agents from workspace-defaults so newly shipped agents
    // (like canva-expert) appear on existing installs without a full re-onboard.
    // copyDirRecursive skips files that already exist, so user customizations are safe.
    const defaultsDir = path.join(rootDir, 'workspace-defaults');
    if (fs.existsSync(defaultsDir)) {
        if (isFirstRun) {
            console.log('[Workspace] First run detected — seeding from workspace-defaults/...');
        }
        copyDirRecursive(defaultsDir, WORKSPACE_DIR);
        if (isFirstRun) {
            console.log('[Workspace] Default agent configs, SOUL.md, and system settings copied successfully.');
        }
    }

    if (!fs.existsSync(MEMORY_DIR)) fs.mkdirSync(MEMORY_DIR, { recursive: true });

    // Initialize memory.md - Long term agent memory
    const memoryPath = path.join(WORKSPACE_DIR, 'memory.md');
    if (!fs.existsSync(memoryPath)) {
        fs.writeFileSync(memoryPath, `# Long Term Memory\n\nRecord enduring facts, system quirks, or important constraints discovered during operation here.\n`);
    }
}

/** Recursively copy a directory tree, skipping files that already exist at the destination */
function copyDirRecursive(src: string, dest: string) {
    if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });

    for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);

        if (entry.isDirectory()) {
            copyDirRecursive(srcPath, destPath);
        } else if (!fs.existsSync(destPath)) {
            // Only copy if the file doesn't already exist (don't overwrite user customizations)
            fs.copyFileSync(srcPath, destPath);
        }
    }
}

export function readMemoryContext(): string {
    initWorkspace();

    let context = "--- Context Memory ---\n\n";

    try {
        const ltm = fs.readFileSync(path.join(WORKSPACE_DIR, 'memory.md'), 'utf-8');
        context += `## memory.md (Long Term Key Information)\n${ltm}\n\n`;

        // Read recent short-term daily logs (up to 3 days to prevent amnesia across midnight)
        let recentLogs = '';
        for (let i = 2; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0];
            const logPath = path.join(MEMORY_DIR, `${dateStr}.md`);
            if (fs.existsSync(logPath)) {
                recentLogs += `## Conversation Log (${dateStr})\n${fs.readFileSync(logPath, 'utf-8')}\n\n`;
            }
        }

        if (recentLogs) {
            let todayLog = recentLogs;

            // --- OpenClaw Cognitive Compaction ---
            // Prevent runaway token bloat by applying a strict sliding window on raw transcripts.
            const MAX_MEMORY_CHARS = 100000;
            if (todayLog.length > MAX_MEMORY_CHARS) {
                console.log(`[Compaction] Daily transcript exceeds token limit. Pruning historical chatter...`);
                const truncatedIndex = todayLog.indexOf('\n\n', todayLog.length - MAX_MEMORY_CHARS);
                todayLog = `...[EARLIER CONTEXT PRUNED BY OPENCLAW COMPACTION TO SAVE TOKENS]...\n` +
                    (truncatedIndex !== -1 ? todayLog.substring(truncatedIndex) : todayLog.substring(todayLog.length - MAX_MEMORY_CHARS));
            }

            context += `${todayLog}\n\n`;
        } else {
            const todayStr = new Date().toISOString().split('T')[0];
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
