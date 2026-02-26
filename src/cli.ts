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

            pm2.start({
                script: scriptPath,
                name: 'openspider-gateway',
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

const channelsMenu = program
    .command('channels')
    .description('Manage communication channels');

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
