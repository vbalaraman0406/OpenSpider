#!/usr/bin/env node

import { Command } from 'commander';
import { runSetup } from './setup';
import { bootstrap } from './index';
import { startTUI } from './cli-tui';
import pm2 from 'pm2';
import path from 'path';
import { spawn, execSync } from 'child_process';
import { onboardWhatsApp } from './whatsapp';
import fs from 'node:fs';

const program = new Command();

program
    .name('openspider')
    .description('Autonomous Multi-Agent System tailored for WhatsApp')
    .version('2.2.0');

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
                if (err) {
                    pm2.disconnect();
                    console.error('Failed to start background process:', err);
                    process.exit(2);
                }

                // Persist the process list so PM2 can resurrect it on reboot
                (pm2 as any).dump((dumpErr: any) => {
                    pm2.disconnect();
                    if (dumpErr) {
                        console.warn('⚠️  Could not save PM2 process list:', dumpErr.message);
                    }
                    console.log('\n==================================================');
                    console.log('✅ OpenSpider is now running in the background!');
                    console.log('==================================================');
                    console.log('\n🧭 Dashboard:   http://localhost:4001');
                    console.log('📜 View Logs:   openspider logs');
                    console.log('🛑 Stop Engine: openspider stop');
                    console.log('\n💡 To auto-start on reboot, run ONCE:');
                    console.log('   pm2 startup && pm2 save\n');
                    process.exit(0);
                });
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
    .command('restart')
    .description('Rebuild and restart the OpenSpider gateway daemon')
    .action(async () => {
        console.log('\n🕷️ Restarting OpenSpider Gateway...\n');

        // Step 1: Rebuild TypeScript
        console.log('🔨 Rebuilding TypeScript...');
        try {
            execSync('npm run build:backend', { cwd: process.cwd(), stdio: 'inherit' });
            console.log('✅ Build successful.\n');
        } catch {
            console.error('❌ Build failed. Fix errors before restarting.');
            process.exit(1);
        }

        // Step 2: Rebuild Dashboard (if it exists)
        const dashboardDir = path.join(process.cwd(), 'dashboard');
        if (fs.existsSync(path.join(dashboardDir, 'package.json'))) {
            console.log('🎨 Rebuilding Dashboard...');
            try {
                execSync('npm run build', { cwd: dashboardDir, stdio: 'inherit' });
                console.log('✅ Dashboard built.\n');
            } catch {
                console.warn('⚠️ Dashboard build failed. Continuing with restart...\n');
            }
        }

        // Step 2: Restart PM2 process
        pm2.connect((err) => {
            if (err) {
                console.error('Error connecting to PM2:', err);
                process.exit(2);
            }

            pm2.restart('openspider-gateway', (err) => {
                if (err) {
                    // If process doesn't exist, start it fresh
                    console.log('Process not running. Starting fresh...');

                    let scriptPath = path.join(__dirname, 'index.js');
                    if (__dirname.endsWith('src')) {
                        scriptPath = path.join(__dirname, '..', 'dist', 'index.js');
                    }
                    const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..') : path.join(__dirname, '..');

                    pm2.start({
                        script: scriptPath,
                        name: 'openspider-gateway',
                        cwd: rootDir
                    }, (err) => {
                        pm2.disconnect();
                        if (err) {
                            console.error('Failed to start:', err);
                            process.exit(2);
                        }
                        console.log('✅ OpenSpider started successfully!');
                        console.log('\n🧭 Dashboard:   http://localhost:4001');
                        console.log('📜 View Logs:   openspider logs\n');
                        process.exit(0);
                    });
                    return;
                }

                pm2.disconnect();
                console.log('==================================================');
                console.log('✅ OpenSpider has been restarted!');
                console.log('==================================================');
                console.log('\n🧭 Dashboard:   http://localhost:4001');
                console.log('📜 View Logs:   openspider logs\n');
                process.exit(0);
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

            // ── Protect user data from git reset ──
            // workspace/, .env, and baileys_auth_info/ contain user configs,
            // cron jobs, WhatsApp credentials, etc. that must survive updates.
            const backupDir = require('path').join(require('os').tmpdir(), 'openspider-update-backup');
            const fsBak = require('fs');
            const pathBak = require('path');

            console.log('💾 0. Backing up user data (workspace, .env, auth)...');
            try {
                if (fsBak.existsSync(backupDir)) fsBak.rmSync(backupDir, { recursive: true, force: true });
                fsBak.mkdirSync(backupDir, { recursive: true });

                // Back up workspace/
                const wsDir = pathBak.join(rootDir, 'workspace');
                if (fsBak.existsSync(wsDir)) {
                    execSync(`cp -a "${wsDir}" "${pathBak.join(backupDir, 'workspace')}"`, { stdio: 'pipe' });
                }
                // Back up .env
                const envFilePath = pathBak.join(rootDir, '.env');
                if (fsBak.existsSync(envFilePath)) {
                    fsBak.copyFileSync(envFilePath, pathBak.join(backupDir, '.env'));
                }
                // Back up baileys_auth_info/
                const baileysDir = pathBak.join(rootDir, 'baileys_auth_info');
                if (fsBak.existsSync(baileysDir)) {
                    execSync(`cp -a "${baileysDir}" "${pathBak.join(backupDir, 'baileys_auth_info')}"`, { stdio: 'pipe' });
                }
                console.log('   ✅ User data backed up.');
            } catch (bakErr: any) {
                console.warn('   ⚠️  Backup warning:', bakErr.message);
            }

            console.log('\n🔄 1. Resetting local file changes (e.g. package-lock conflicts)...');
            execSync('git reset --hard HEAD', { stdio: 'inherit', cwd: rootDir });

            console.log('\n⬇️  2. Pulling latest code from GitHub...');
            execSync('git fetch origin main', { stdio: 'inherit', cwd: rootDir });
            execSync('git reset --hard origin/main', { stdio: 'inherit', cwd: rootDir });

            // ── Restore user data ──
            console.log('\n♻️  Restoring user data...');
            try {
                const wsBackup = pathBak.join(backupDir, 'workspace');
                if (fsBak.existsSync(wsBackup)) {
                    // Merge: copy backup files over, preserving any new files from the repo
                    execSync(`cp -a "${wsBackup}/." "${pathBak.join(rootDir, 'workspace')}/"`, { stdio: 'pipe' });
                }
                const envBackup = pathBak.join(backupDir, '.env');
                if (fsBak.existsSync(envBackup)) {
                    fsBak.copyFileSync(envBackup, pathBak.join(rootDir, '.env'));
                }
                const baileysBackup = pathBak.join(backupDir, 'baileys_auth_info');
                if (fsBak.existsSync(baileysBackup)) {
                    execSync(`cp -a "${baileysBackup}" "${pathBak.join(rootDir, 'baileys_auth_info')}"`, { stdio: 'pipe' });
                }
                // Clean up backup
                fsBak.rmSync(backupDir, { recursive: true, force: true });
                console.log('   ✅ User data restored successfully.');
            } catch (restoreErr: any) {
                console.error('   ❌ Restore failed! Backup still at:', backupDir);
                console.error('      Error:', restoreErr.message);
            }

            console.log('\n📦 2. Installing dependencies...');
            execSync('npm install', { stdio: 'inherit', cwd: rootDir });

            console.log('\n🌐 3. Installing Playwright browser (Chromium)...');
            try {
                execSync('npx playwright install chromium', { stdio: 'inherit', cwd: rootDir });
                // Install system deps on Linux (required for headless Chrome)
                if (process.platform === 'linux') {
                    try {
                        execSync('npx playwright install-deps chromium', { stdio: 'inherit', cwd: rootDir });
                    } catch (_) {
                        console.log('   ⚠️  Could not install system deps (may need sudo). Run manually: sudo npx playwright install-deps chromium');
                    }
                }
                console.log('   ✅ Playwright Chromium ready.');
            } catch (_) {
                console.log('   ⚠️  Playwright install skipped (non-fatal). Browser tasks may not work.');
            }

            console.log('\n🔐 4. Preparing Dashboard Authentication...');
            const envPath = require('path').join(rootDir, '.env');
            const dashEnvPath = require('path').join(rootDir, 'dashboard', '.env');
            if (require('fs').existsSync(envPath)) {
                const envContent = require('fs').readFileSync(envPath, 'utf8');
                const keyMatch = envContent.match(/DASHBOARD_API_KEY=(.*)/);
                if (keyMatch && keyMatch[1]) {
                    require('fs').writeFileSync(dashEnvPath, `VITE_API_KEY=${keyMatch[1].trim()}`);
                    console.log('   ✅ Synchronized Dashboard API Key.');
                }
            }

            console.log('\n🔨 4. Building project...');
            execSync('npm run build', { stdio: 'inherit', cwd: rootDir });

            console.log('\n🔗 4. Updating global CLI...');
            execSync('npm install -g .', { stdio: 'inherit', cwd: rootDir });

            // Refresh system-wide symlink so all users on this Linux box can run openspider
            try {
                const openspiderBin = execSync('which openspider 2>/dev/null || echo ""', { cwd: rootDir }).toString().trim();
                if (openspiderBin && openspiderBin !== '') {
                    execSync(`ln -sf "${openspiderBin}" /usr/local/bin/openspider 2>/dev/null || true`, { stdio: 'pipe', cwd: rootDir });
                    console.log('   ✅ Updated system-wide symlink at /usr/local/bin/openspider');
                }
            } catch (_) { /* non-fatal */ }

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
    .description('Connect OpenSpider to WhatsApp by scanning a QR code')
    .action(async () => {
        console.log('\n🕷️  OpenSpider WhatsApp Login');
        console.log('─────────────────────────────────────────');
        console.log('Connecting to WhatsApp... stand by.\n');

        try {
            const makeWASocket = (await import('@whiskeysockets/baileys')).default;
            const { useMultiFileAuthState, fetchLatestBaileysVersion, DisconnectReason } = await import('@whiskeysockets/baileys');
            const qrcode = (await import('qrcode-terminal')).default;
            const fs = await import('node:fs');
            const path = await import('node:path');

            // Resolve project root from the compiled script location, NOT process.cwd()
            // This prevents files being created in the wrong directory when users
            // run 'openspider channels login' from ~ instead of the project root
            const projectRoot = __dirname.endsWith('src') || __dirname.endsWith('dist')
                ? path.join(__dirname, '..') : __dirname;

            // Always start fresh — stale credentials cause "Session rejected" errors
            const authDir = path.join(projectRoot, 'baileys_auth_info');
            if (fs.existsSync(authDir)) {
                fs.rmSync(authDir, { recursive: true, force: true });
                console.log('🧹 Cleared old WhatsApp sessions.');
            }
            fs.mkdirSync(authDir, { recursive: true });

            const { state, saveCreds } = await useMultiFileAuthState(authDir);
            const { version } = await fetchLatestBaileysVersion();
            const { makeCacheableSignalKeyStore } = await import('@whiskeysockets/baileys');
            const NodeCache = require('node-cache');

            const pino = require('pino');
            const silentLogger = pino({ level: 'silent' });
            const msgRetryCounterCache = new NodeCache();

            // Track sync state across reconnects
            let syncComplete = false;

            // Hard timeout — never hang more than 120s total
            const hardTimeout = setTimeout(() => {
                console.log('\n⏳ Sync taking longer than expected, but credentials are saved.');
                console.log('\n📱 Now run: pm2 start openspider-gateway\n');
                process.exit(0);
            }, 120000);

            function connectSocket() {
                const sock = makeWASocket({
                    version,
                    auth: {
                        creds: state.creds,
                        keys: makeCacheableSignalKeyStore(state.keys, silentLogger),
                    },
                    printQRInTerminal: false,
                    qrTimeout: 60000,
                    logger: silentLogger,
                    browser: ['OpenSpider', 'Chrome', '122.0.0'],
                    syncFullHistory: false,
                    markOnlineOnConnect: true,
                    msgRetryCounterCache,
                });

                sock.ev.on('creds.update', saveCreds);

                sock.ev.on('messaging-history.set', () => {
                    if (!syncComplete) {
                        syncComplete = true;
                        clearTimeout(hardTimeout);
                        console.log('✅ WhatsApp device sync complete!');
                        console.log('\n📱 Now run: pm2 start openspider-gateway\n');
                        setTimeout(() => process.exit(0), 2000);
                    }
                });

                sock.ev.on('connection.update', async (update: any) => {
                    const { connection, lastDisconnect, qr } = update;

                    if (qr) {
                        console.clear();
                        console.log('\n🕷️  Scan this QR code in WhatsApp → Linked Devices → Link a Device:\n');
                        qrcode.generate(qr, { small: true });
                        console.log('\n⏳ Waiting for scan... (QR expires in 60s, a new one will appear automatically)');
                    }

                    if (connection === 'open') {
                        console.log('\n✅ WhatsApp paired successfully!');
                        console.log('📁 Credentials saved to baileys_auth_info/');

                        // Auto-update whatsapp_config.json enabled flag
                        try {
                            const configPath = path.join(projectRoot, 'workspace', 'whatsapp_config.json');
                            let cfg: any = { enabled: true, dmPolicy: 'allowlist', allowedDMs: [], groupPolicy: 'disabled', allowedGroups: [], botMode: 'respond' };
                            if (fs.existsSync(configPath)) cfg = { ...JSON.parse(fs.readFileSync(configPath, 'utf-8')), enabled: true };
                            fs.writeFileSync(configPath, JSON.stringify(cfg, null, 2));
                        } catch (e) { }

                        // Flip ENABLE_WHATSAPP=true in .env
                        try {
                            const envPath = path.join(projectRoot, '.env');
                            if (fs.existsSync(envPath)) {
                                let envContent = fs.readFileSync(envPath, 'utf-8');
                                if (/ENABLE_WHATSAPP\s*=\s*false/i.test(envContent)) {
                                    envContent = envContent.replace(/ENABLE_WHATSAPP\s*=\s*false/gi, 'ENABLE_WHATSAPP = true');
                                    fs.writeFileSync(envPath, envContent);
                                } else if (!/ENABLE_WHATSAPP/i.test(envContent)) {
                                    fs.appendFileSync(envPath, '\nENABLE_WHATSAPP = true\n');
                                }
                            }
                        } catch (e) { }

                        console.log('⏳ Waiting for WhatsApp to finish device sync (your phone should say "Linked" shortly)...');
                    }

                    if (connection === 'close') {
                        const code = (lastDisconnect?.error as any)?.output?.statusCode;
                        if (code === DisconnectReason.loggedOut) {
                            clearTimeout(hardTimeout);
                            console.log('\n❌ Session rejected. Please try again.');
                            process.exit(1);
                        }
                        // 515 = "restart required", 428 = "connection replaced"
                        // WhatsApp sends these after pairing to trigger a reconnect for sync.
                        // Create a fresh socket to complete the registration handshake.
                        if (code === 515 || code === 428) {
                            console.log('🔄 WhatsApp requested reconnect (normal after pairing)...');
                            setTimeout(() => connectSocket(), 1000);
                        }
                    }
                });
            }

            connectSocket();

        } catch (err: any) {
            console.error('\nFailed to start WhatsApp login:', err.message);
            process.exit(1);
        }
    });

const toolsMenu = program
    .command('tools')
    .description('Manage Agent Tools and Skills');

toolsMenu
    .command('browser')
    .description('Configure the Browser Specialist (Local Headless vs Remote Client)')
    .action(async () => {
        try {
            const { runBrowserSetup } = await import('./browser/cli');
            await runBrowserSetup();
        } catch (error: any) {
            console.error('Failed to configure browser:', error.message);
            process.exit(1);
        }
    });

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
            provider === 'antigravity' ? (process.env.GEMINI_MODEL || 'gemini-2.0-flash') :
                provider === 'antigravity-internal' ? (process.env.GEMINI_MODEL || 'claude-opus-4-6-thinking') :
                    provider === 'ollama' ? (process.env.OLLAMA_MODEL || 'llama3') :
                        provider === 'openai' ? (process.env.OPENAI_MODEL || 'gpt-4o') :
                            provider === 'anthropic' ? (process.env.ANTHROPIC_MODEL || 'claude-3-5-sonnet') :
                                provider === 'custom' ? (process.env.CUSTOM_MODEL || 'N/A') : 'Unknown';

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

modelsMenu
    .command('select')
    .description('Interactively switch the active model for your current provider')
    .action(async () => {
        const p = await import('@clack/prompts');
        const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..') : path.join(__dirname, '..');
        const envPath = path.join(rootDir, '.env');
        require('dotenv').config({ path: envPath });

        const provider = process.env.DEFAULT_PROVIDER || '';
        if (!provider) {
            console.error('\n❌ No provider configured. Run: openspider onboard');
            process.exit(1);
        }

        console.log(`\n🕷️  Selecting model for provider: ${provider}\n`);

        let selectedModel = '';

        if (provider === 'openai') {
            // Fetch live models from OpenAI API
            const s = p.spinner();
            s.start('Fetching available models from OpenAI...');
            let options: { value: string; label: string }[] = [];
            try {
                const resp = await fetch('https://api.openai.com/v1/models', {
                    headers: { Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
                });
                if (resp.ok) {
                    const data: any = await resp.json();
                    options = (data.data as any[])
                        .map((m: any) => m.id as string)
                        .filter((id: string) => id.startsWith('gpt-') || id.startsWith('o1') || id.startsWith('o3'))
                        .sort((a: string, b: string) => b.localeCompare(a))
                        .map((id: string) => ({ value: id, label: id }));
                }
                s.stop('Models fetched!');
            } catch (_) {
                s.stop('Could not reach OpenAI — using curated list.');
            }
            if (options.length === 0) {
                options = [
                    { value: 'gpt-4o',      label: 'gpt-4o      — Recommended' },
                    { value: 'gpt-4o-mini', label: 'gpt-4o-mini — Cheapest' },
                    { value: 'gpt-4-turbo', label: 'gpt-4-turbo — 128k context' },
                    { value: 'gpt-4',       label: 'gpt-4       — Original GPT-4' },
                    { value: 'o1',          label: 'o1          — Deep reasoning' },
                    { value: 'o1-mini',     label: 'o1-mini     — Cheaper reasoning' },
                    { value: 'o3-mini',     label: 'o3-mini     — Latest reasoning' },
                ];
            }
            const choice = await p.select({ message: 'Choose OpenAI model:', options, initialValue: process.env.OPENAI_MODEL || 'gpt-4o' });
            if (p.isCancel(choice)) { p.cancel('Cancelled.'); process.exit(0); }
            selectedModel = choice as string;

        } else if (provider === 'anthropic') {
            const options = [
                { value: 'claude-opus-4-5',           label: 'claude-opus-4-5           — Most capable' },
                { value: 'claude-3-5-sonnet-20241022', label: 'claude-3-5-sonnet-20241022 — Recommended' },
                { value: 'claude-3-5-haiku-20241022',  label: 'claude-3-5-haiku-20241022  — Fastest & cheapest' },
                { value: 'claude-3-opus-20240229',     label: 'claude-3-opus-20240229     — Powerful reasoning' },
                { value: 'claude-3-haiku-20240307',    label: 'claude-3-haiku-20240307    — Budget' },
            ];
            const choice = await p.select({ message: 'Choose Anthropic model:', options, initialValue: process.env.ANTHROPIC_MODEL || 'claude-3-5-sonnet-20241022' });
            if (p.isCancel(choice)) { p.cancel('Cancelled.'); process.exit(0); }
            selectedModel = choice as string;

        } else if (provider === 'antigravity' || provider === 'antigravity-internal') {
            const options = [
                { value: 'gemini-2.5-flash',         label: 'gemini-2.5-flash       — Recommended' },
                { value: 'gemini-2.0-flash',          label: 'gemini-2.0-flash        — Fast & cheap' },
                { value: 'gemini-2.0-flash-thinking', label: 'gemini-2.0-flash-thinking — Reasoning' },
                { value: 'gemini-1.5-pro',            label: 'gemini-1.5-pro          — Large context' },
                { value: 'gemini-1.5-flash',          label: 'gemini-1.5-flash        — Budget' },
            ];
            const choice = await p.select({ message: 'Choose Gemini model:', options, initialValue: process.env.GEMINI_MODEL || 'gemini-2.5-flash' });
            if (p.isCancel(choice)) { p.cancel('Cancelled.'); process.exit(0); }
            selectedModel = choice as string;

        } else if (provider === 'ollama') {
            const input = await p.text({ message: 'Enter Ollama model name (e.g. llama3, qwen2.5-coder:32b):', placeholder: 'llama3', initialValue: process.env.OLLAMA_MODEL || '' });
            if (p.isCancel(input)) { p.cancel('Cancelled.'); process.exit(0); }
            selectedModel = input as string;

        } else {
            const input = await p.text({ message: 'Enter model name:', placeholder: 'model-name', initialValue: process.env.CUSTOM_MODEL || '' });
            if (p.isCancel(input)) { p.cancel('Cancelled.'); process.exit(0); }
            selectedModel = input as string;
        }

        // Write the new model to .env
        const envKey = provider === 'openai' ? 'OPENAI_MODEL' :
            provider === 'anthropic' ? 'ANTHROPIC_MODEL' :
                provider === 'ollama' ? 'OLLAMA_MODEL' :
                    provider === 'custom' ? 'CUSTOM_MODEL' : 'GEMINI_MODEL';

        const { execSync: exec } = require('child_process');
        const envContent = fs.existsSync(envPath) ? fs.readFileSync(envPath, 'utf-8') : '';
        const newLine = `${envKey}=${selectedModel}`;
        const updated = envContent.match(new RegExp(`^${envKey}=.*`, 'm'))
            ? envContent.replace(new RegExp(`^${envKey}=.*`, 'm'), newLine)
            : envContent + `\n${newLine}\n`;
        fs.writeFileSync(envPath, updated);

        console.log(`\n✅ Model updated to: ${selectedModel}`);
        console.log('♻️  Restart OpenSpider to apply: openspider stop && openspider start\n');
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

        const provider = process.env.DEFAULT_PROVIDER || 'Not Set';
        const primaryModel =
            provider === 'antigravity' ? (process.env.GEMINI_MODEL || 'gemini-2.0-flash') :
                provider === 'antigravity-internal' ? (process.env.GEMINI_MODEL || 'claude-opus-4-6-thinking') :
                    provider === 'ollama' ? (process.env.OLLAMA_MODEL || 'llama3') :
                        provider === 'openai' ? (process.env.OPENAI_MODEL || 'gpt-4o') :
                            provider === 'anthropic' ? (process.env.ANTHROPIC_MODEL || 'claude-3-5-sonnet') :
                                provider === 'custom' ? (process.env.CUSTOM_MODEL || 'N/A') : 'Unknown';

        const providerDisplay = provider === 'Not Set'
            ? '⚠️  Not configured (run: openspider onboard)'
            : `${provider} (${primaryModel})`;

        console.log('\n🕷️  OpenSpider Status');
        console.log('─'.repeat(50));
        console.log(`Version:          v${pkg.version}`);
        console.log(`Provider:         ${providerDisplay}`);
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
                    console.log('');
                    process.exit(0);
                    return;
                }

                const proc = desc[0];
                const status = proc?.pm2_env?.status || 'unknown';
                const uptime = proc?.pm2_env?.pm_uptime
                    ? Math.round((Date.now() - proc.pm2_env.pm_uptime) / 60000) + ' min'
                    : 'N/A';
                const restarts = proc?.pm2_env?.restart_time ?? 0;
                const icon = status === 'online' ? '✅' : '⛔';
                console.log(`Gateway:          ${icon} ${status}  (uptime: ${uptime}, restarts: ${restarts})`);

                // Query the health API for WhatsApp and other component statuses
                const port = process.env.PORT || '4001';
                const apiKey = process.env.DASHBOARD_API_KEY || '';
                const http = require('http');
                const req = http.get(
                    `http://localhost:${port}/api/health`,
                    { headers: { 'x-api-key': apiKey } },
                    (res: any) => {
                        let body = '';
                        res.on('data', (chunk: any) => body += chunk);
                        res.on('end', () => {
                            try {
                                const health = JSON.parse(body);
                                const wa = health?.components?.whatsapp || 'unknown';
                                const waIcon = wa === 'connected' ? '✅' : '⚠️ ';
                                console.log(`WhatsApp:         ${waIcon} ${wa}`);
                            } catch (e) {
                                console.log(`WhatsApp:         ⚠️  Could not reach health API`);
                            }
                            console.log('');
                            process.exit(0);
                        });
                    }
                );
                req.on('error', () => {
                    console.log(`WhatsApp:         ⚠️  Gateway API unreachable`);
                    console.log('');
                    process.exit(0);
                });
                req.end();
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

program
    .command('lid-map <lid> <phone>')
    .description('Map a WhatsApp LID to a phone number in the allowlist')
    .action((lid: string, phone: string) => {
        const rootDir = __dirname.endsWith('src') ? path.join(__dirname, '..') : path.join(__dirname, '..');
        const envPath = path.join(rootDir, '.env');
        require('dotenv').config({ path: envPath });

        const port = process.env.PORT || '4001';
        const apiKey = process.env.DASHBOARD_API_KEY || '';
        const http = require('http');

        const payload = JSON.stringify({ lid, phone });
        const options = {
            hostname: 'localhost',
            port: parseInt(port),
            path: '/api/whatsapp/lid-map',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': apiKey,
                'Content-Length': Buffer.byteLength(payload)
            }
        };

        const req = http.request(options, (res: any) => {
            let body = '';
            res.on('data', (chunk: any) => body += chunk);
            res.on('end', () => {
                try {
                    const result = JSON.parse(body);
                    if (result.success) {
                        console.log(`\n✅ ${result.message}`);
                    } else {
                        console.error(`\n❌ ${result.error || 'Unknown error'}`);
                    }
                } catch (e) {
                    console.error(`\n❌ Failed to parse response: ${body}`);
                }
                process.exit(0);
            });
        });

        req.on('error', (e: Error) => {
            console.error(`\n❌ Could not reach OpenSpider gateway at localhost:${port}.`);
            console.error('   Is the gateway running? Start it with: openspider start');
            process.exit(1);
        });

        req.write(payload);
        req.end();
    });

program.parse(process.argv);
