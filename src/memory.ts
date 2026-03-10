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
        let ltm = fs.readFileSync(path.join(WORKSPACE_DIR, 'memory.md'), 'utf-8');
        // Cap long-term memory to prevent unbounded growth
        const LTM_LIMIT = 5000;
        if (ltm.length > LTM_LIMIT) {
            ltm = ltm.slice(-LTM_LIMIT);
            const firstNewline = ltm.indexOf('\n');
            ltm = '...[LTM TRUNCATED]...\n' + (firstNewline !== -1 ? ltm.slice(firstNewline + 1) : ltm);
        }
        context += `## memory.md (Long Term Key Information)\n${ltm}\n\n`;

        // Tiered memory window — balances cross-day awareness with token budget:
        //   Today      → 15 000 chars (most recent, bottom of log)
        //   Yesterday  → 2 000 chars tail (reminder of what was in-progress)
        //   2 days ago → 1 500 chars tail (older context, very compressed)
        const TODAY_LIMIT    = 15000;
        const PREV_DAY_LIMIT = 2000;
        const TWO_DAY_LIMIT  = 1500;

        for (let i = 2; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const dateStr = date.toISOString().split('T')[0]!;
            const logPath = path.join(MEMORY_DIR, `${dateStr}.md`);
            if (!fs.existsSync(logPath)) continue;

            let log = fs.readFileSync(logPath, 'utf-8');
            const limit = i === 0 ? TODAY_LIMIT : i === 1 ? PREV_DAY_LIMIT : TWO_DAY_LIMIT;

            if (log.length > limit) {
                const tail = log.slice(-limit);
                const firstNewline = tail.indexOf('\n');
                const prefix = i === 0
                    ? '...[EARLIER TODAY PRUNED TO SAVE TOKENS]...\n'
                    : `...[SUMMARY: only last ${limit / 1000}KB shown for ${dateStr}]...\n`;
                log = prefix + (firstNewline !== -1 ? tail.slice(firstNewline + 1) : tail);
                if (i === 0) console.log(`[Compaction] Today's log pruned to ${limit / 1000}KB.`);
            }

            const label = i === 0 ? 'Today' : i === 1 ? 'Yesterday' : '2 Days Ago';
            context += `## Conversation Log — ${label} (${dateStr})\n${log}\n\n`;
        }

    } catch (e) {
        console.error("[Memory] Error reading context:", e);
    }

    context += "----------------------\n";
    return context;
}


export function logMemory(sender: 'User' | 'Agent', message: string, channel?: 'whatsapp' | 'dashboard' | 'cron') {
    initWorkspace();
    const now = new Date();
    const todayStr = now.toISOString().split('T')[0];
    const todayPath = path.join(MEMORY_DIR, `${todayStr}.md`);

    // Truncate very long messages (huge error traces, massive API dumps) to prevent context bloat
    // Raised from 500 to 4000 to preserve links, tables, and structured agent responses
    const truncated = message.length > 4000 ? message.slice(0, 4000) + '...[TRUNCATED]' : message;

    // Channel tag for cross-channel awareness
    const channelTag = channel === 'whatsapp' ? ' 📱' : channel === 'dashboard' ? ' 🖥️' : channel === 'cron' ? ' ⏰' : '';

    const logEntry = `[${now.toLocaleTimeString()}] **${sender}**${channelTag}: ${truncated}\n\n`;
    fs.appendFileSync(todayPath, logEntry, 'utf-8');
}


/**
 * Memory Retention Policy: auto-delete old daily logs to prevent unbounded disk growth.
 * Keeps the last 30 days, called during workspace initialization.
 */
export function cleanupOldMemoryLogs(retentionDays: number = 30) {
    try {
        if (!fs.existsSync(MEMORY_DIR)) return;

        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - retentionDays);
        const cutoffStr = cutoff.toISOString().split('T')[0]!;

        let cleaned = 0;
        for (const file of fs.readdirSync(MEMORY_DIR)) {
            // Only touch YYYY-MM-DD.md files
            if (!/^\d{4}-\d{2}-\d{2}\.md$/.test(file)) continue;
            const fileDate = file.replace('.md', '');
            if (fileDate < cutoffStr) {
                fs.unlinkSync(path.join(MEMORY_DIR, file));
                cleaned++;
            }
        }

        if (cleaned > 0) {
            console.log(`[Memory] Retention cleanup: removed ${cleaned} log file(s) older than ${retentionDays} days.`);
        }
    } catch (e) {
        console.error("[Memory] Retention cleanup error:", e);
    }
}


/**
 * End-of-day compaction: compress yesterday's raw conversation log into
 * a compact digest. Removes redundant timestamps and intermediate system
 * messages, keeping only User/Agent exchanges.
 * Called once per day during workspace initialization.
 */
export function compactYesterdayLog() {
    try {
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        const dateStr = yesterday.toISOString().split('T')[0]!;
        const logPath = path.join(MEMORY_DIR, `${dateStr}.md`);
        const compactedMarker = '[COMPACTED]';

        if (!fs.existsSync(logPath)) return;

        const raw = fs.readFileSync(logPath, 'utf-8');

        // Skip if already compacted or too small to bother
        if (raw.startsWith(compactedMarker) || raw.length < 2000) return;

        // Extract User/Agent lines, strip timestamps, deduplicate
        const lines = raw.split('\n');
        const exchanges: string[] = [];
        const seen = new Set<string>();

        for (const line of lines) {
            const match = line.match(/\[.*?\] \*\*(User|Agent)\*\*(.*?):\s*(.*)/);
            if (match) {
                const [, sender, channelTag, content] = match;
                const key = `${sender}:${content!.substring(0, 100)}`;
                if (!seen.has(key)) {
                    seen.add(key);
                    // Compact: remove timestamp, keep sender + channel + short content
                    const shortContent = content!.length > 300 ? content!.substring(0, 300) + '...' : content!;
                    exchanges.push(`**${sender}**${channelTag}: ${shortContent}`);
                }
            }
        }

        if (exchanges.length === 0) return;

        const compacted = `${compactedMarker} ${dateStr} — ${exchanges.length} exchanges\n\n${exchanges.join('\n')}\n`;
        fs.writeFileSync(logPath, compacted, 'utf-8');

        const savings = Math.round((1 - compacted.length / raw.length) * 100);
        console.log(`[Memory] Compacted ${dateStr} log: ${raw.length} → ${compacted.length} chars (${savings}% reduction, ${exchanges.length} exchanges kept).`);

    } catch (e) {
        console.error("[Memory] Compaction error:", e);
    }
}
