import fs from 'node:fs';
import path from 'node:path';

export class PersonaShell {
    private agentId: string;
    private workspacePath: string;

    constructor(agentId: string) {
        // First, try to match the role to an existing agent
        this.agentId = PersonaShell.resolveAgentId(agentId);
        this.workspacePath = path.join(process.cwd(), 'workspace', 'agents', this.agentId);

        // Only create the directory if it doesn't exist — do NOT create blindly
        // This was previously auto-creating empty folders for every unknown role name
        if (!fs.existsSync(this.workspacePath)) {
            fs.mkdirSync(this.workspacePath, { recursive: true });
        }
    }

    /**
     * Resolve a generic role name to an existing agent ID.
     * e.g. "Web Scraper" → "researcher", "File Writer" → "coder"
     * Falls back to lowercased + sanitized agentId if no match found.
     */
    static resolveAgentId(roleOrId: string): string {
        const normalized = roleOrId.toLowerCase().replace(/[^a-z0-9]/g, '');
        const agentsDir = path.join(process.cwd(), 'workspace', 'agents');

        if (!fs.existsSync(agentsDir)) return normalized;

        // 1. Check for exact folder name match (e.g. "researcher", "coder")
        const folders = fs.readdirSync(agentsDir).filter(f => {
            try { return fs.statSync(path.join(agentsDir, f)).isDirectory(); }
            catch { return false; }
        });

        // Exact match: folder name matches the input
        const exactMatch = folders.find(f => f === normalized || f === roleOrId.toLowerCase());
        if (exactMatch) return exactMatch;

        // 2. Check CAPABILITIES.json for matching role or name
        for (const folder of folders) {
            if (folder === 'manager') continue; // Don't match manager as a worker
            const capsPath = path.join(agentsDir, folder, 'CAPABILITIES.json');
            if (!fs.existsSync(capsPath)) continue;
            try {
                const caps = JSON.parse(fs.readFileSync(capsPath, 'utf-8'));
                const roleLower = (caps.role || '').toLowerCase();
                const nameLower = (caps.name || '').toLowerCase();

                // Role match: "Researcher" role matches for "web scraper", "researcher", etc.
                if (roleLower === normalized || nameLower === normalized) return folder;

                // Fuzzy match: if the input contains the role or vice versa
                if (normalized.includes(roleLower) || roleLower.includes(normalized)) return folder;
                if (normalized.includes(nameLower) || nameLower.includes(normalized)) return folder;
            } catch { }
        }

        // 3. Keyword-based matching for common role patterns
        const roleMapping: Record<string, string[]> = {
            'researcher': ['research', 'scraper', 'scraping', 'search', 'fetch', 'information', 'data gather', 'web', 'browse', 'lookup', 'find'],
            'coder': ['coder', 'developer', 'programmer', 'writer', 'file', 'script', 'code', 'build', 'implement', 'create', 'generate'],
            'tester': ['tester', 'test', 'qa', 'quality', 'verify', 'verification', 'validate'],
        };

        for (const [agentId, keywords] of Object.entries(roleMapping)) {
            if (!folders.includes(agentId)) continue; // Only match if the agent actually exists
            // Make sure it has a CAPABILITIES.json (not an empty folder)
            const capsPath = path.join(agentsDir, agentId, 'CAPABILITIES.json');
            if (!fs.existsSync(capsPath)) continue;

            if (keywords.some(kw => normalized.includes(kw))) return agentId;
        }

        // 4. No match — return longest-matching existing agent to prevent creating empty folders
        //    If nothing matches at all, return 'coder' as a catch-all general worker
        const coderExists = folders.includes('coder') && fs.existsSync(path.join(agentsDir, 'coder', 'CAPABILITIES.json'));
        if (coderExists) {
            console.log(`[PersonaShell] No agent matched role "${roleOrId}" — defaulting to "coder"`);
            return 'coder';
        }

        // Absolute fallback: use the sanitized name (this will still create a folder)
        console.log(`[PersonaShell] No agent matched role "${roleOrId}" — using sanitized folder name "${normalized}"`);
        return normalized;
    }

    /**
     * Bootstrap a new agent with proper pillar files.
     * Called from the "Create Agent" UI or when the system intentionally needs a new agent.
     */
    static bootstrapAgent(id: string, name: string, role: string, description: string = ''): void {
        const agentDir = path.join(process.cwd(), 'workspace', 'agents', id.toLowerCase());
        fs.mkdirSync(agentDir, { recursive: true });

        // IDENTITY.md
        fs.writeFileSync(
            path.join(agentDir, 'IDENTITY.md'),
            `# ${name}\n\nYou are **${name}**, an OpenSpider Agent specialized as a **${role}**.\n\n${description || `Your primary function is to execute tasks related to the ${role} role with precision and thoroughness.`}\n`,
            'utf-8'
        );

        // SOUL.md
        fs.writeFileSync(
            path.join(agentDir, 'SOUL.md'),
            `# Soul Directives for ${name}\n\n- Execute all assigned tasks with thoroughness and accuracy\n- Always provide detailed, well-formatted results\n- Report failures honestly — never fabricate data\n- Collaborate effectively when receiving context from other agents\n`,
            'utf-8'
        );

        // USER.md
        fs.writeFileSync(
            path.join(agentDir, 'USER.md'),
            `# User Context\n\nNo user preferences or context learned yet. This file will be updated as the agent learns about the user's needs and preferences.\n`,
            'utf-8'
        );

        // CAPABILITIES.json
        const defaultTools: Record<string, string[]> = {
            'researcher': ['search_web', 'read_url', 'run_command', 'write_script', 'execute_script'],
            'coder': ['read_file', 'write_file', 'run_command', 'write_script', 'execute_script'],
            'tester': ['run_command', 'write_script', 'execute_script'],
        };
        const tools = defaultTools[role.toLowerCase()] || ['run_command', 'write_script', 'execute_script'];

        fs.writeFileSync(
            path.join(agentDir, 'CAPABILITIES.json'),
            JSON.stringify({
                name,
                role,
                allowedTools: tools,
                maxLoops: 15,
                status: 'running'
            }, null, 4),
            'utf-8'
        );

        console.log(`[PersonaShell] Bootstrapped new agent: ${name} (${id}) with all pillar files`);
    }

    private readFileSafe(fileName: string, defaultContent: string = ""): string {
        const filePath = path.join(this.workspacePath, fileName);
        if (fs.existsSync(filePath)) {
            return fs.readFileSync(filePath, 'utf-8');
        }
        return defaultContent;
    }

    public getIdentity(): string {
        return this.readFileSafe('IDENTITY.md', `You are an OpenSpider Agent known as ${this.agentId}.`);
    }

    public getSoul(): string {
        return this.readFileSafe('SOUL.md', "No specific ethos defined.");
    }

    public getUserContext(): string {
        return this.readFileSafe('USER.md', "No human context provided.");
    }

    public getCapabilities(): any {
        const caps = this.readFileSafe('CAPABILITIES.json', null as any);
        if (caps) {
            try {
                return JSON.parse(caps);
            } catch (e) {
                return {};
            }
        }
        return {};
    }

    public compileSystemPrompt(): string {
        const identity = this.getIdentity();
        const soul = this.getSoul();
        const user = this.getUserContext();
        const caps = this.getCapabilities();

        let prompt = `[AUTHORITATIVE IDENTITY CAPABILITIES]\nYour absolute name is: ${caps?.name || this.agentId}\nYour role is: ${caps?.role || 'Agent'}\n\n`;
        prompt += `[IDENTITY]\n${identity}\n\n`;
        prompt += `[SOUL - STRICT DIRECTIVES]\n${soul}\n\n`;
        prompt += `[USER CONTEXT]\n${user}\n\n`;

        if (caps && Object.keys(caps).length > 0) {
            // Only inject LLM-relevant fields — strip operational metadata to save tokens
            const llmCaps: any = {};
            if (caps.name) llmCaps.name = caps.name;
            if (caps.role) llmCaps.role = caps.role;
            if (caps.description) llmCaps.description = caps.description;
            if (caps.emoji) llmCaps.emoji = caps.emoji;
            if (caps.allowedTools || caps.tools) llmCaps.tools = caps.allowedTools || caps.tools;
            prompt += `[CAPABILITIES]\n${JSON.stringify(llmCaps)}\n\n`;
        }

        return prompt;
    }
}
