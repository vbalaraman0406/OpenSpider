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
    .version('1.0.0');

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
                // You can add environment variables if needed
                // env: { NODE_ENV: "production" }
            }, (err, apps) => {
                pm2.disconnect();
                if (err) {
                    console.error('Failed to start background process:', err);
                    process.exit(2);
                }
                console.log('✅ OpenSpider is now running in the background!');
                console.log('To view the WhatsApp QR code or logs, run: openspider logs');
                console.log('To start chatting, run: openspider tui');
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
        require('dotenv').config();
        console.log('\n🕷️ OpenSpider Configure Models:');
        console.log('---------------------------------');
        console.log(`Default Provider:   ${process.env.DEFAULT_PROVIDER || 'Not Set'}`);
        console.log(`Primary Model:      ${process.env.DEFAULT_PROVIDER === 'antigravity' ? process.env.GEMINI_MODEL :
            process.env.DEFAULT_PROVIDER === 'ollama' ? process.env.OLLAMA_MODEL :
                process.env.DEFAULT_PROVIDER === 'openai' ? process.env.OPENAI_MODEL :
                    process.env.DEFAULT_PROVIDER === 'anthropic' ? process.env.ANTHROPIC_MODEL :
                        process.env.DEFAULT_PROVIDER === 'custom' ? process.env.CUSTOM_MODEL : 'Unknown'
            }`);
        console.log(`Fallback Model:     ${process.env.FALLBACK_MODEL || 'None'}`);
        console.log('---------------------------------');
        process.exit(0);
    });

program
    .command('tui')
    .description('Launch the Terminal User Interface to chat with the agent')
    .action(async () => {
        await startTUI();
    });

program.parse(process.argv);
