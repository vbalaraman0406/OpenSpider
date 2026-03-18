import WebSocket from 'ws';
import * as readline from 'readline';
import chalk from 'chalk';
import * as fs from 'fs';
import * as path from 'path';

// Read API key from the project's .env file
function getApiKey(): string {
    const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..') : path.join(__dirname, '..');
    const envPath = path.join(rootDir, '.env');
    try {
        if (fs.existsSync(envPath)) {
            const envContent = fs.readFileSync(envPath, 'utf-8');
            const match = envContent.match(/^DASHBOARD_API_KEY=(.+)$/m);
            if (match && match[1]) return match[1].trim();
        }
    } catch { }
    return process.env.DASHBOARD_API_KEY || '';
}

const BASE_URL = process.env.GATEWAY_URL || 'ws://localhost:4001';
const apiKey = getApiKey();
const GATEWAY_URL = apiKey ? `${BASE_URL}/?apiKey=${apiKey}` : BASE_URL;

const OPENSPIDER_ASCII = `
   ____                   ____        _     __
  / __ \\____  ___  ____  / __/____   (_)___/ /__  _____
 / / / / __ \\/ _ \\/ __ \\/\\ \\/ __ \\ / / __  / _ \\/ ___/
/ /_/ / /_/ /  __/ / / /___/ / /_/ // / /_/ /  __/ /
\\____/ .___/\\___/_/ /_//____/ .___//_/\\__,_/\\___/_/
    /_/                    /_/
`;

export async function startTUI() {
    console.clear();
    console.log(chalk.cyan(OPENSPIDER_ASCII));
    console.log(chalk.cyan('🕷️ Connecting to OpenSpider Gateway...'));
    if (!apiKey) {
        console.log(chalk.yellow('⚠️  No API key found in .env — connection may be rejected.'));
    }

    const ws = new WebSocket(GATEWAY_URL);

    // Setup interactive terminal
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        prompt: chalk.yellow('❯ ')
    });

    ws.on('open', () => {
        console.log(chalk.green('✔ Connected to OpenSpider TUI!'));
        console.log(chalk.gray('Type your message and press Enter to chat. Press Ctrl+C to exit.\n'));
        rl.prompt();
    });

    ws.on('message', (data) => {
        try {
            const messageStr = data.toString();
            const payload = JSON.parse(messageStr);

            // Temporarily clear the prompt line to print incoming logs nicely
            readline.clearLine(process.stdout, 0);
            readline.cursorTo(process.stdout, 0);

            if (payload.type === 'log') {
                // Dim system/thought logs so the chat stands out. We don't display them in the TUI per user request.
                // console.log(chalk.dim(`[Agent] ${payload.data}`));
            } else if (payload.type === 'usage') {
                const u = payload.data.usage;
                console.log(chalk.magenta(`    [API] Model: ${payload.data.model} | Tokens: ${u.promptTokens} in, ${u.completionTokens} out (${u.totalTokens} total)`));
            } else if (payload.type === 'chat_response') {
                // Bright color for final responses
                console.log(chalk.blue(`\n🤖 Antigravity: `) + chalk.white(payload.data) + '\n');
            }

            // Restore the prompt
            rl.prompt();
        } catch (error) {
            console.error(chalk.red('\nFailed to parse incoming message.'), error);
            rl.prompt();
        }
    });

    ws.on('close', (code, reason) => {
        const reasonStr = reason?.toString() || 'unknown';
        console.log(chalk.red(`\nDisconnected from OpenSpider Gateway. (code: ${code}, reason: ${reasonStr})`));
        process.exit(0);
    });

    ws.on('error', (error) => {
        console.error(chalk.red('\nWebSocket Error:'), error.message);
        console.log(chalk.yellow('Make sure the gateway is running: `openspider gateway`'));
        process.exit(1);
    });

    // Handle user input
    rl.on('line', (line) => {
        const text = line.trim();
        if (text) {
            if (text === '/exit' || text === '/quit') {
                ws.close();
                process.exit(0);
            }

            // Send the chat message payload
            ws.send(JSON.stringify({
                type: 'chat',
                text: text
            }));
        }
        rl.prompt();
    });

    // Handle Ctrl+C gracefully
    rl.on('close', () => {
        console.log(chalk.gray('\nExiting TUI...'));
        ws.close();
        process.exit(0);
    });
}
