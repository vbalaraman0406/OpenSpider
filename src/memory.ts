import fs from 'node:fs';
import path from 'node:path';

const WORKSPACE_DIR = path.join(process.cwd(), 'workspace');
const MEMORY_DIR = path.join(WORKSPACE_DIR, 'memory');

export function initWorkspace() {
    if (!fs.existsSync(WORKSPACE_DIR)) fs.mkdirSync(WORKSPACE_DIR, { recursive: true });
    if (!fs.existsSync(MEMORY_DIR)) fs.mkdirSync(MEMORY_DIR, { recursive: true });

    // Initialize SOUL.md - Defines the Agent's identity and boundaries
    const soulPath = path.join(WORKSPACE_DIR, 'SOUL.md');
    if (!fs.existsSync(soulPath)) {
        fs.writeFileSync(soulPath, `# OpenSpider Soul\n\nYou are OpenSpider, an autonomous agentic system.\nYour primary goal is to safely and intelligently orchestrate tasks on behalf of the user.\n\nBoundary Rules:\n- Do NOT execute destructive terminal commands without explicit user permission.\n- Do NOT delete files outside of the workspace directory.\n- Always be concise and professional.`);
    }

    // Initialize USER.md - Defines facts about the user
    const userPath = path.join(WORKSPACE_DIR, 'USER.md');
    if (!fs.existsSync(userPath)) {
        fs.writeFileSync(userPath, `# User Context\n\nThis document contains persistent facts about the user for you to remember across sessions.\n`);
    }

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
        const soul = fs.readFileSync(path.join(WORKSPACE_DIR, 'SOUL.md'), 'utf-8');
        context += `## SOUL.md (Your Identity & Rules)\n${soul}\n\n`;

        const user = fs.readFileSync(path.join(WORKSPACE_DIR, 'USER.md'), 'utf-8');
        context += `## USER.md (Facts about the User)\n${user}\n\n`;

        const ltm = fs.readFileSync(path.join(WORKSPACE_DIR, 'memory.md'), 'utf-8');
        context += `## memory.md (Long Term Key Information)\n${ltm}\n\n`;

        // Read today's short-term daily log
        const todayStr = new Date().toISOString().split('T')[0];
        const todayPath = path.join(MEMORY_DIR, `${todayStr}.md`);

        if (fs.existsSync(todayPath)) {
            const todayLog = fs.readFileSync(todayPath, 'utf-8');
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

export function logMemory(role: 'User' | 'OpenSpider', message: string) {
    initWorkspace();
    const now = new Date();
    const todayStr = now.toISOString().split('T')[0];
    const timestampStr = now.toISOString().split('T')[1];
    const timestamp = timestampStr ? timestampStr.replace('Z', '') : now.toLocaleTimeString();
    const todayPath = path.join(MEMORY_DIR, `${todayStr}.md`);

    const logEntry = `[${timestamp}] **${role}**: ${message}\n\n`;
    fs.appendFileSync(todayPath, logEntry, 'utf-8');
}
