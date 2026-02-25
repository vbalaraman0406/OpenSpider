import { exec } from 'node:child_process';
import { promisify } from 'node:util';
import fs from 'node:fs/promises';
import path from 'node:path';

const execAsync = promisify(exec);

export class DynamicExecutor {
    private skillsDir: string;

    constructor() {
        this.skillsDir = path.join(process.cwd(), 'skills');
    }

    /**
     * Ensure the local skills environment exists
     */
    async initialize() {
        try {
            await fs.access(this.skillsDir);
        } catch {
            await fs.mkdir(this.skillsDir, { recursive: true });
            // Initialize a basic package.json in the skills dir to keep it isolated
            await fs.writeFile(
                path.join(this.skillsDir, 'package.json'),
                JSON.stringify({ name: "openspider-dynamic-skills", version: "1.0.0", private: true }, null, 2)
            );
        }
    }

    /**
     * Allows the agent to run generic shell commands (within the skills directory)
     */
    async runCommand(command: string): Promise<{ stdout: string; stderr: string; error?: string }> {
        try {
            const { stdout, stderr } = await execAsync(command, { cwd: this.skillsDir, timeout: 60000 }); // 60s timeout
            return { stdout, stderr };
        } catch (e: any) {
            return { stdout: e.stdout || '', stderr: e.stderr || '', error: e.message };
        }
    }

    /**
     * Installs an NPM package dynamically if an agent decides it needs it
     */
    async installPackage(packageName: string): Promise<string> {
        const { stdout, error } = await this.runCommand(`npm install ${packageName}`);
        if (error) throw new Error(`Failed to install ${packageName}: ${error}`);
        return `Successfully installed ${packageName}.\n${stdout}`;
    }

    /**
     * Writes a script (Python, JS, etc.) to the skills folder
     */
    async writeScript(filename: string, content: string): Promise<string> {
        const filePath = path.join(this.skillsDir, filename);
        await fs.writeFile(filePath, content, 'utf-8');
        return `Script saved to ${filePath}`;
    }

    /**
     * Executes a saved script
     */
    async executeScript(filename: string, args: string = ''): Promise<{ stdout: string; stderr: string; error?: string }> {
        const ext = path.extname(filename);
        let command = '';

        if (ext === '.js' || ext === '.ts') command = `node ${filename} ${args}`;
        else if (ext === '.py') command = `python3 ${filename} ${args}`;
        else if (ext === '.sh') command = `bash ${filename} ${args}`;
        else throw new Error("Unsupported file extension for direct execution.");

        return this.runCommand(command);
    }
}
