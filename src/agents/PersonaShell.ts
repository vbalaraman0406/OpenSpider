import fs from 'node:fs';
import path from 'node:path';

export class PersonaShell {
    private agentId: string;
    private workspacePath: string;

    constructor(agentId: string) {
        this.agentId = agentId.toLowerCase();
        this.workspacePath = path.join(process.cwd(), 'workspace', 'agents', this.agentId);

        // Ensure directory exists if we load an unknown agent
        if (!fs.existsSync(this.workspacePath)) {
            fs.mkdirSync(this.workspacePath, { recursive: true });
        }
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
            prompt += `[CAPABILITIES & LOADOUT]\n${JSON.stringify(caps, null, 2)}\n\n`;
        }

        return prompt;
    }
}
