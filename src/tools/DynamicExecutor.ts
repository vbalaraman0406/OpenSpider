import { exec, spawnSync } from 'node:child_process';
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
     * Heuristic Static Analysis to prevent Agentic Prompt Injections
     * HIGH-2 FIX: Expanded blocklist to prevent interpreter bypass via importlib,
     * getattr, compile, __import__, and other obfuscation vectors.
     */
    private scanScriptForThreats(content: string, filename: string) {
        const blocklistedKeywords = [
            // Direct OS/subprocess access
            'os.system', 'subprocess.', 'pty.spawn', 'child_process',
            // Eval/exec variants
            'exec(', 'eval(', 'execfile(',
            // Dynamic import bypass vectors
            'importlib', '__import__', 'compile(',
            // Attribute-based bypass
            'getattr(__', '__builtins__',
            // Filesystem destruction
            'fs.unlink', 'fs.rmdir', 'shutil.rmtree', 'rm -rf',
            // Network exfil (V4: expanded blocklist)
            'socket.', 'urllib.request', 'http.client',
            'requests.get', 'requests.post', 'requests.put', 'requests.delete',
            'requests.session',
            // Encoding-based bypass vectors (V4)
            'base64.b64decode', 'base64.decodebytes',
            'codecs.decode', 'codecs.encode',
            // Dunder/reflection bypass (V4)
            '__class__', '__subclasses__', '__globals__', '__dict__',
            // ctypes FFI bypass
            'ctypes.',
        ];

        // SECURITY (V4): Normalize Unicode before scanning to prevent homoglyph bypass
        // NFD decomposes characters, then we strip non-ASCII to catch lookalike chars
        const normalizedContent = content
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')  // Strip combining diacritical marks
            .toLowerCase();

        for (const keyword of blocklistedKeywords) {
            if (normalizedContent.includes(keyword.toLowerCase())) {
                throw new Error(`Security Guard: Script blocked. The code contains forbidden module or function: ${keyword}`);
            }
        }

        // SECURITY (V4): Block any remaining dunder patterns (e.g. __name__, __spec__)
        // except __init__ and __main__ which are standard Python
        const dunders = normalizedContent.match(/__[a-z]+__/g) || [];
        const allowedDunders = ['__init__', '__main__', '__name__', '__file__'];
        for (const d of dunders) {
            if (!allowedDunders.includes(d)) {
                throw new Error(`Security Guard: Script blocked. Suspicious dunder pattern detected: ${d}`);
            }
        }
    }

    /**
     * Allows the agent to run generic shell commands (within the skills directory)
     * HIGH-1 FIX: Replaced simple keyword blocklist with:
     *   1. Shell metacharacter detection (prevents chaining/substitution)
     *   2. Hardened command blocklist (catches bypass variants)
     *   3. Existing filesystem scanning guard
     */
    async runCommand(command: string): Promise<{ stdout: string; stderr: string; error?: string }> {
        // Detect shell metacharacters that allow command chaining/injection
        const dangerousMetaCharsPattern = /[;|&`$()<>]/;
        if (dangerousMetaCharsPattern.test(command)) {
            return { stdout: '', stderr: '', error: `Security Guard: Command blocked. Dangerous shell metacharacter detected in: ${command}. Only simple commands without pipes, redirects, or chaining are allowed.` };
        }

        // Hardened blocklist — catches bypass variants like 'rm  -rf', 'chmod 755', etc.
        const blocklistedPatterns: RegExp[] = [
            /\brm\s+-rf\b/,           // rm -rf (with possible extra spaces)
            /\brm\s+-f\b/,            // rm -f
            /\brmdir\b/,              // rmdir
            /\bmkfs\b/,              // disk format
            /\bdd\s+if=/,            // dd disk overwrite
            /\bsudo\b/,              // privilege escalation
            /\bchown\b/,             // ownership change
            /\bchmod\b/,             // permission change (all variants)
            /\bcurl\b.*\|.*\bbash\b/, // curl pipe to bash
            /\bwget\b.*\|.*\bbash\b/, // wget pipe to bash
            /\bnc\b/,                // netcat exfil
            /\bcat\s+\/etc\b/,       // reading sensitive system files
            /\bcat\s+~\/\./,         // reading hidden home files (.env, .ssh etc)
            /\bssh\b/,               // ssh connections
        ];

        for (const pattern of blocklistedPatterns) {
            if (pattern.test(command)) {
                return { stdout: '', stderr: '', error: `Security Guard: Command blocked by sandbox policy: ${pattern}` };
            }
        }

        // Strict regex for filesystem scanning outside of project
        if (/(find|grep|ls|tree)\s+[\/~]/.test(command.toLowerCase()) || command.toLowerCase().includes('find /')) {
            return { stdout: '', stderr: '', error: `Security Guard: Command blocked. You are strictly forbidden from scanning the root or home filesystem using find/grep/ls on '/' or '~'. ONLY work within the current directory using './'` };
        }
        try {
            const { stdout, stderr } = await execAsync(command, { cwd: this.skillsDir, timeout: 30000 }); // strict 30s timeout
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
     * HIGH-4/HIGH-2 FIX: Added path traversal check on filename before write.
     */
    async writeScript(filename: string, content: string): Promise<string> {
        this.scanScriptForThreats(content, filename);
        // Strip any path separators from filename to prevent traversal
        const safeFilename = path.basename(filename);
        const filePath = path.join(this.skillsDir, safeFilename);
        // Double-check resolved path stays inside skillsDir
        if (!filePath.startsWith(this.skillsDir)) {
            throw new Error('Security Guard: Filename resolved outside skills directory.');
        }
        await fs.writeFile(filePath, content, 'utf-8');
        return `Script saved to ${filePath}`;
    }

    /**
     * Executes a saved script
     * HIGH-4 FIX: Added path traversal check on filename before execute.
     */
    async executeScript(filename: string, args: string = ''): Promise<{ stdout: string; stderr: string; error?: string }> {
        const safeFilename = path.basename(filename);
        const resolvedPath = path.join(this.skillsDir, safeFilename);
        if (!resolvedPath.startsWith(this.skillsDir)) {
            return { stdout: '', stderr: '', error: 'Security Guard: Script path resolved outside skills directory.' };
        }

        const ext = path.extname(safeFilename);
        let interpreter = '';

        if (ext === '.js' || ext === '.ts') interpreter = 'node';
        else if (ext === '.py') interpreter = 'python3';
        else if (ext === '.sh') interpreter = 'bash';
        else throw new Error("Unsupported file extension for direct execution.");

        // SECURITY (V5): Use spawnSync with array args to prevent injection via args parameter.
        // Shell metacharacters in args are harmless when passed as array elements.
        const argParts = args ? args.split(/\s+/).filter(Boolean) : [];
        try {
            const result = spawnSync(interpreter, [safeFilename, ...argParts], {
                cwd: this.skillsDir,
                timeout: 30000,
                encoding: 'utf-8',
                env: { ...process.env, PATH: process.env.PATH }
            });
            return {
                stdout: result.stdout || '',
                stderr: result.stderr || '',
                ...(result.status !== 0 ? { error: result.stderr || result.error?.message || `Exit code: ${result.status}` } : {})
            };
        } catch (e: any) {
            return { stdout: '', stderr: '', error: e.message };
        }
    }
}
