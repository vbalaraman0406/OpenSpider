#!/usr/bin/env node

import { Command } from 'commander';
import { runSetup } from './setup';
import { bootstrap } from './index';
import { startTUI } from './cli-tui';
import pm2 from 'pm2';
import path from 'path';
import { spawn } from 'child_process';
import { onboardWhatsApp } from './whatsapp';
import fs from 'node:fs';

const program = new Command();

program
    .name('openspider')
    .description('Autonomous Multi-Agent System tailored for WhatsApp')
    .version('2.0.2');

program
    .command('onboard')
    .description('Run the guided setup wizard to configure providers and personas')
    .action(async () => {
        try {
            await runSetup();
            console.log('\n🕷️ Setup complete! Run `openspider start` to run the engine in the background.');
        } catch (error) {
            console.error('Setup failed:', error);
            process.exit(1);
        }
    });

program
    .command('gateway')
    .description('Start the core agent engine and HTTP/WebSocket server in the foreground')
    .action(() => {
        console.log('\n🕷️ Starting OpenSpider Gateway in foreground...');
        bootstrap().catch((error) => {
            console.error('Failed to start gateway:', error);
            process.exit(1);
        });
    });

program
    .command('start')
    .description('Start the OpenSpider gateway as a background daemon process')
    .action(() => {
        console.log('\n🕷️ Starting OpenSpider Gateway in the background...');

        pm2.connect((err) => {
            if (err) {
                console.error('Error connecting to PM2:', err);
                process.exit(2);
            }

            // Determine the correct path to the compiled index.js
            let scriptPath = path.join(__dirname, 'index.js');
            if (__dirname.endsWith('src')) {
                // When running via ts-node in development
                scriptPath = path.join(__dirname, '..', 'dist', 'index.js');
            }

            const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..') : path.join(__dirname, '..');

            pm2.start({
                script: scriptPath,
                name: 'openspider-gateway',
                cwd: rootDir
            }, (err, apps) => {
                pm2.disconnect();
                if (err) {
                    console.error('Failed to start background process:', err);
                    process.exit(2);
                }
                console.log('\n==================================================');
                console.log('✅ OpenSpider is now running in the background!');
                console.log('==================================================');
                console.log('\n🧭 Dashboard:   http://localhost:4001');
                console.log('📜 View Logs:   openspider logs');
                console.log('🛑 Stop Engine: openspider stop\n');
                process.exit(0);
            });
        });
    });

program
    .command('stop')
    .description('Stop the backend OpenSpider gateway daemon')
    .action(() => {
        console.log('\n🕷️ Stopping OpenSpider Gateway...');

        pm2.connect((err) => {
            if (err) {
                console.error('Error connecting to PM2:', err);
                process.exit(2);
            }

            pm2.delete('openspider-gateway', (err, proc) => {
                pm2.disconnect();
                if (err) {
                    // PM2 throws an error if the process doesn't exist, which is fine
                    console.log('OpenSpider is not running.');
                    return;
                }
                console.log('⛔ OpenSpider has been stopped.');
            });
        });
    });

program
    .command('update')
    .description('Update OpenSpider to the latest version or publish a new release')
    .option('--bump <type>', 'Release a new version (patch, minor, major) and push to GitHub')
    .action((options) => {
        const { execSync } = require('child_process');
        const path = require('path');
        const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..') : path.join(__dirname, '..');

        try {
            if (options.bump) {
                console.log(`\n📦 Bumping version (${options.bump}) and publishing to GitHub...`);
                // Add all changes
                execSync('git add .', { stdio: 'inherit', cwd: rootDir });

                // Commit changes if any exist
                try {
                    execSync('git commit -m "chore: save work before release"', { stdio: 'ignore', cwd: rootDir });
                } catch (e) { /* Ignore if no changes to commit */ }

                // Bump version (this creates a commit and a tag)
                execSync(`npm version ${options.bump}`, { stdio: 'inherit', cwd: rootDir });

                console.log('\n🚀 Pushing to GitHub...');
                execSync('git push origin main --tags', { stdio: 'inherit', cwd: rootDir });
                console.log('\n✅ Release successfully pushed to GitHub!\n');
                return;
            }

            console.log('\n🕷️ Updating OpenSpider to the latest version...\n');

            console.log('🔄 1. Pulling latest code from GitHub...');
            execSync('git pull origin main', { stdio: 'inherit', cwd: rootDir });

            console.log('\n📦 2. Installing dependencies...');
            execSync('npm install', { stdio: 'inherit', cwd: rootDir });

            console.log('\n🔨 3. Building project...');
            execSync('npm run build', { stdio: 'inherit', cwd: rootDir });

            console.log('\n🔗 4. Updating global CLI...');
            execSync('npm install -g .', { stdio: 'inherit', cwd: rootDir });

            console.log('\n♻️  5. Restarting engine...');
            execSync('openspider stop && openspider start', { stdio: 'inherit', cwd: rootDir });

            console.log('\n🌟 OpenSpider is now fully up to date!\n');

        } catch (error: any) {
            console.error('\n❌ Update failed:', error.message);
            process.exit(1);
        }
    });

program
    .command('logs')
    .description('View real-time logs from the background OpenSpider gateway')
    .action(() => {
        console.log('\n🕷️ Streaming logs (Press Ctrl+C to exit)...');

        // Use npx pm2 logs to stream the output naturally
        const pm2Logs = spawn('npx', ['pm2', 'logs', 'openspider-gateway', '--lines', '100'], { stdio: 'inherit' });

        pm2Logs.on('close', (code) => {
            process.exit(code ?? 0);
        });
    });

program
    .command('dashboard')
    .description('Open the OpenSpider dashboard in your default browser')
    .action(async () => {
        try {
            // dynamic import because 'open' is often an ESM module
            const open = (await import('open')).default;
            console.log('\n🕷️ Opening OpenSpider Dashboard at http://localhost:4001...');
            await open('http://localhost:4001');
            process.exit(0);
        } catch (error: any) {
            console.error('Failed to open dashboard:', error.message);
            process.exit(1);
        }
    });

const channelsMenu = program
    .command('channels')
    .description('Manage communication channels');

channelsMenu
    .command('login')
    .description('View the live WhatsApp QR Code for authentication')
    .action(async () => {
        const fs = await import('node:fs');
        const path = await import('node:path');
        const qrcode = await import('qrcode-terminal');
        const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..') : path.join(__dirname, '..');
        const qrPath = path.join(rootDir, '.latest_qr.txt');

        console.log('\n🕷️ Watching for WhatsApp QR Code from background engine (Press Ctrl+C to exit)...');
        let lastQr = '';

        const checkQr = () => {
            if (fs.existsSync(qrPath)) {
                const qr = fs.readFileSync(qrPath, 'utf-8');
                if (qr !== lastQr && qr.trim() !== '') {
                    console.clear();
                    console.log('\n🕷️ [WhatsApp] Scan this live QR code to connect OpenSpider:');
                    qrcode.default.generate(qr, { small: true });
                    lastQr = qr;
                }
            } else if (lastQr) {
                console.log('\n✅ OpenSpider successfully connected to WhatsApp!');
                process.exit(0);
            }
        };

        checkQr();
        setInterval(checkQr, 1000);
    });

const toolsMenu = program
    .command('tools')
    .description('Manage Agent Tools and Skills');

const emailToolsMenu = toolsMenu
    .command('email')
    .description('Manage Email Capabilities');

emailToolsMenu
    .command('setup')
    .description('Configure OAuth 2.0 credentials for the Send Email skill')
    .action(async () => {
        try {
            console.log('\\n🕷️ OpenSpider Email Tool OAuth Setup');
            const p = await import('@clack/prompts');
            const fs = await import('node:fs');
            const path = await import('node:path');
            const { execSync } = await import('node:child_process');

            console.log('\\nTo enable the agent to send emails autonomously, we use Google OAuth 2.0.\\n');
            console.log('1. Go to Google Cloud Console (https://console.cloud.google.com/apis/credentials)');
            console.log('2. Create an OAuth Client ID (Application Type: Desktop app)');
            console.log('3. Download the JSON file\\n');

            const credsPathInput = await p.text({
                message: 'Enter the absolute path to your downloaded credentials JSON file (e.g. /Downloads/client_secret_xyz.json):',
                placeholder: '/Users/name/Downloads/client_secret_xyz.json'
            });

            if (p.isCancel(credsPathInput)) {
                p.cancel('Setup cancelled.');
                process.exit(0);
            }

            const sourceBaseCreds = credsPathInput as string;

            if (!fs.existsSync(sourceBaseCreds)) {
                console.error(`\\n❌ Could not find credentials file at: ${sourceBaseCreds}`);
                process.exit(1);
            }

            const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..') : path.join(__dirname, '..');
            const workspaceDir = path.join(rootDir, 'workspace');
            if (!fs.existsSync(workspaceDir)) fs.mkdirSync(workspaceDir);

            const destCredsPath = path.join(workspaceDir, 'gmail_credentials.json');
            fs.copyFileSync(sourceBaseCreds, destCredsPath);
            console.log(`\\n✅ Copied credentials to: ${destCredsPath}`);

            console.log('\\n🚀 Opening browser to authenticate with Google...\\n');

            // Execute the python script with --setup
            const pythonScript = path.join(rootDir, 'skills', 'send_email.py');

            try {
                // Notice stdio: inherit allows the Python app flow to print the localhost callback URL and listen interactively
                execSync(`python3 "${pythonScript}" --setup`, { stdio: 'inherit' });
                p.outro('\\n✅ OAuth Authentication Successful! Your agents can now send emails autonomously.');
                process.exit(0);
            } catch (authErr: any) {
                console.error('\\n❌ OAuth Authentication failed:', authErr.message);
                process.exit(1);
            }

        } catch (error: any) {
            console.error('Failed to setup email tools:', error.message);
            process.exit(1);
        }
    });

emailToolsMenu
    .command('test')
    .description('Send a test email using the configured OAuth credentials')
    .option('-t, --to <email>', 'Recipient email address')
    .option('-s, --subject <text>', 'Email subject line', 'Test from OpenSpider')
    .option('-b, --body <text>', 'Email body content', 'This is a test email sent from the OpenSpider CLI!')
    .action(async (options) => {
        try {
            const p = await import('@clack/prompts');
            const { spawn } = await import('node:child_process');
            const path = await import('node:path');

            let toEmail = options.to;
            if (!toEmail) {
                toEmail = await p.text({
                    message: 'Enter recipient email address (e.g. you@gmail.com):',
                    placeholder: 'you@gmail.com',
                });
                if (p.isCancel(toEmail)) process.exit(0);
            }

            console.log(`\\n🕷️ Firing test email to ${toEmail}...`);

            const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..') : path.join(__dirname, '..');
            const pythonScript = path.join(rootDir, 'skills', 'send_email.py');

            const pyParams = [pythonScript, '--to', toEmail.trim(), '--subject', options.subject, '--body', options.body];
            const child = spawn('python3', pyParams, { stdio: 'inherit' });

            child.on('close', (code) => {
                if (code === 0) {
                    console.log('\\n✅ Test email dispatched successfully!');
                } else {
                    console.error(`\\n❌ Test email failed with exit code ${code}. Did you run 'openspider tools email setup' first?`);
                }
                process.exit(code ?? 0);
            });

        } catch (error: any) {
            console.error('Failed to send test email:', error.message);
            process.exit(1);
        }
    });

const webhooksMenu = program
    .command('webhooks')
    .description('Manage incoming webhooks for event-driven automation');

const gmailWebhooksMenu = webhooksMenu
    .command('gmail')
    .description('Manage Gmail Pub/Sub push webhooks');

gmailWebhooksMenu
    .command('setup')
    .description('Automate GCP setup and configure `gog` for Gmail Webhooks')
    .option('-p, --project <id>', 'Your Google Cloud Project ID')
    .option('-a, --account <email>', 'The Gmail account you want to monitor')
    .action((options) => {
        console.log('\n🕷️ OpenSpider Gmail Webhook Setup');

        const runSetup = (projectId: string, account: string) => {
            try {
                const { execSync } = require('child_process');

                console.log(`\n⚙️  Setting active GCP Project to: ${projectId}`);
                execSync(`gcloud config set project ${projectId} --quiet`, { stdio: 'inherit' });

                console.log(`\n⚙️  Enabling Gmail and Pub/Sub APIs...`);
                execSync(`gcloud services enable gmail.googleapis.com pubsub.googleapis.com --quiet`, { stdio: 'inherit' });

                console.log(`\n⚙️  Creating Pub/Sub Topic 'gog-gmail-watch'...`);
                try {
                    execSync(`gcloud pubsub topics create gog-gmail-watch --quiet`, { stdio: 'pipe' });
                    console.log('✅ Created new topic.');
                } catch (e: any) {
                    if (e.message.includes('ALREADY_EXISTS')) {
                        console.log('✅ Topic already exists.');
                    } else {
                        console.log('⚠️  Failed to create topic (might already exist):', e.message);
                    }
                }

                console.log(`\n⚙️  Granting Gmail API the Publisher role...`);
                execSync(`gcloud pubsub topics add-iam-policy-binding gog-gmail-watch \\
                    --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \\
                    --role=roles/pubsub.publisher --quiet`, { stdio: 'inherit' });

                console.log(`\n✅ GCP Setup Complete.`);
                console.log(`\n🕷️ Next steps to start monitoring:`);
                console.log(`\n1. Start the watch on the address:`);
                console.log(`   gog gmail watch start --account ${account} --label INBOX --topic projects/${projectId}/topics/gog-gmail-watch`);

                console.log(`\n2. Serve the webhook endpoint (requires Tailscale installed):`);
                console.log(`   tailscale serve --bg 4001`);
                console.log(`   tailscale funnel --bg 4001`);

                console.log(`\n3. Run the push handler pointing to your Tailscale URL:`);
                console.log(`   gog gmail watch serve --account ${account} --bind 127.0.0.1 --port 8788 --path /gmail-pubsub --token <SHARED_SECRET> --hook-url http://127.0.0.1:4001/hooks/gmail --hook-token OPENSPIDER_HOOK_TOKEN --include-body --max-bytes 20000\n`);
                process.exit(0);
            } catch (e: any) {
                if (e.message && e.message.includes('INVALID_ARGUMENT') || (e.message && e.message.includes('valid project ID'))) {
                    console.error('\n❌ Setup failed: You provided a Project Name instead of a Project ID.');
                    console.error('   Google Cloud requires the exact alphanumeric Project ID (e.g., "vish-cloud-123456").');
                    console.error('   You can find your exact Project ID by running:  gcloud projects list');
                } else {
                    console.error('\n❌ Setup failed. Ensure you are logged in using `gcloud auth login` and have the necessary IAM permissions.', e.message);
                }
                process.exit(1);
            }
        };

        if (options.project && options.account) {
            runSetup(options.project, options.account);
        } else {
            const readline = require('readline').createInterface({
                input: process.stdin,
                output: process.stdout
            });

            readline.question('Enter your Google Cloud Project ID: ', (projectId: string) => {
                if (!projectId) { console.error("Project ID is required."); process.exit(1); }
                readline.question('Enter the Gmail account to watch (e.g., openspider@gmail.com): ', (account: string) => {
                    if (!account) { console.error("Account email is required."); process.exit(1); }
                    readline.close();
                    runSetup(projectId, account);
                });
            });
        }
    });

gmailWebhooksMenu
    .command('run')
    .description('Start the standalone Gateway webhook listener')
    .action(() => {
        console.log('\n🕷️ Starting OpenSpider Webhook Listener...');
        bootstrap().catch((error) => {
            console.error('Failed to start webhook listener:', error);
            process.exit(1);
        });
    });

channelsMenu
    .command('whatsapp')
    .description('Manage WhatsApp channel')
    .command('login')
    .description('Initialize the WhatsApp connection and print the QR code')
    .action(async () => {
        console.log('🕷️ Initializing WhatsApp Login...');
        try {
            await onboardWhatsApp();
            console.log('✅ Connected successfully!');
            process.exit(0);
        } catch (error: any) {
            console.error('Failed to connect:', error.message);
            process.exit(1);
        }
    });

const modelsMenu = program
    .command('models')
    .description('Manage and view LLM Models');

modelsMenu
    .command('list')
    .description('List currently configured models from .env')
    .action(() => {
        // BUGFIX: resolve .env relative to the project root (parent of dist/), not CWD.
        // When openspider is run from any directory, __dirname = .../dist/
        // and require('dotenv').config() without a path defaults to process.cwd()/.env
        // which fails unless the user happens to be in the project root.
        const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..') : path.join(__dirname, '..');
        const envPath = path.join(rootDir, '.env');
        require('dotenv').config({ path: envPath });

        const provider = process.env.DEFAULT_PROVIDER || 'Not Set';

        // Pick the primary model based on the active provider
        const primaryModel =
            provider === 'antigravity' ? (process.env.GEMINI_MODEL || 'Not Set') :
                provider === 'antigravity-internal' ? (process.env.GEMINI_MODEL || 'Not Set') :
                    provider === 'ollama' ? (process.env.OLLAMA_MODEL || 'Not Set') :
                        provider === 'openai' ? (process.env.OPENAI_MODEL || 'Not Set') :
                            provider === 'anthropic' ? (process.env.ANTHROPIC_MODEL || 'Not Set') :
                                provider === 'custom' ? (process.env.CUSTOM_MODEL || 'Not Set') : 'Unknown';

        // Build list of all configured providers
        const configured: string[] = [];
        if (process.env.GEMINI_API_KEY) configured.push(`antigravity  (model: ${process.env.GEMINI_MODEL || 'gemini-2.0-flash'})`);
        if (process.env.OLLAMA_HOST) configured.push(`ollama       (model: ${process.env.OLLAMA_MODEL || 'llama3'}, host: ${process.env.OLLAMA_HOST})`);
        if (process.env.OPENAI_API_KEY) configured.push(`openai       (model: ${process.env.OPENAI_MODEL || 'gpt-4o'})`);
        if (process.env.ANTHROPIC_API_KEY) configured.push(`anthropic    (model: ${process.env.ANTHROPIC_MODEL || 'claude-3-5-sonnet'})`);
        if (process.env.CUSTOM_BASE_URL) configured.push(`custom       (model: ${process.env.CUSTOM_MODEL || 'N/A'}, url: ${process.env.CUSTOM_BASE_URL})`);
        // antigravity-internal is the managed cloud mode (no separate key env var)
        if (provider === 'antigravity-internal' && configured.length === 0) {
            configured.push(`antigravity-internal  (model: ${process.env.GEMINI_MODEL || 'claude-opus-4-6-thinking'})`);
        }
        console.log('\n🕷️  OpenSpider Model Configuration:');
        console.log('─'.repeat(50));
        console.log(`Default Provider:   ${provider}`);
        console.log(`Primary Model:      ${primaryModel}`);
        console.log(`Fallback Model:     ${process.env.FALLBACK_MODEL || 'None'}`);
        console.log('─'.repeat(50));
        if (configured.length > 0) {
            console.log('\nAll configured providers:');
            configured.forEach(p => console.log(`  ✅ ${p}`));
        } else {
            console.log('\n⚠️  No providers configured. Run: openspider onboard');
        }
        console.log(`\nConfig file: ${envPath}`);
        console.log('');
        process.exit(0);
    });

program
    .command('status')
    .description('Show current OpenSpider gateway status and configuration')
    .action(() => {
        // Handle both dev mode (src) and compiled mode (dist). 
        // When running via `npm link` (global bin), __dirname is effectively where the executing script lives.
        const rootDir = __dirname.endsWith('src') || __dirname.endsWith('dist') ? path.join(__dirname, '..') : __dirname;
        const envPath = path.join(rootDir, '.env');
        require('dotenv').config({ path: envPath });

        const pkg = JSON.parse(fs.readFileSync(path.join(rootDir, 'package.json'), 'utf-8'));

        console.log('\n🕷️  OpenSpider Status');
        console.log('─'.repeat(50));
        console.log(`Version:          v${pkg.version}`);
        console.log(`Provider:         ${process.env.DEFAULT_PROVIDER || '⚠️  Not configured (run: openspider onboard)'}`);
        console.log(`API Port:         ${process.env.PORT || '4001'}`);
        console.log(`Dashboard:        http://localhost:${process.env.PORT || '4001'}`);
        console.log(`Gateway Token:    ${process.env.DASHBOARD_API_KEY || '⚠️  Not generated'}`);
        console.log('─'.repeat(50));

        // Check if PM2 process is running
        pm2.connect((err) => {
            if (err) {
                console.log('Gateway:          ⚠️  PM2 not available');
                pm2.disconnect();
                process.exit(0);
                return;
            }
            pm2.describe('openspider-gateway', (err, desc: any[]) => {
                pm2.disconnect();
                if (err || !desc || desc.length === 0) {
                    console.log('Gateway:          ⛔ Not running  (start with: openspider start)');
                } else {
                    const proc = desc[0];
                    const status = proc?.pm2_env?.status || 'unknown';
                    const uptime = proc?.pm2_env?.pm_uptime
                        ? Math.round((Date.now() - proc.pm2_env.pm_uptime) / 60000) + ' min'
                        : 'N/A';
                    const restarts = proc?.pm2_env?.restart_time ?? 0;
                    const icon = status === 'online' ? '✅' : '⛔';
                    console.log(`Gateway:          ${icon} ${status}  (uptime: ${uptime}, restarts: ${restarts})`);
                }
                console.log('');
                process.exit(0);
            });
        });
    });

program
    .command('tui')
    .description('Launch the Terminal User Interface to chat with the agent')
    .action(async () => {
        await startTUI();
    });
program
    .command('token')
    .description('Print the secure Gateway Token for use in the Chrome Extension')
    .action(() => {
        const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..') : path.join(__dirname, '..');
        const envPath = path.join(rootDir, '.env');
        require('dotenv').config({ path: envPath });

        const token = process.env.DASHBOARD_API_KEY;
        if (!token) {
            console.log('\n⚠️  No Gateway Token configured in .env yet.');
        } else {
            console.log(`\n🔑 OpenSpider Gateway Token:\n${token}\n`);
            console.log('Copy and paste this into the OpenSpider Browser Relay Chrome Extension.');
        }
        process.exit(0);
    });

program.parse(process.argv);
