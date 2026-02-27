import fs from 'node:fs';
import path from 'node:path';
import { ManagerAgent } from './agents/ManagerAgent';

const JOBS_FILE = path.join(process.cwd(), 'workspace', 'cron_jobs.json');

interface CronJob {
    id: string;
    description: string;
    prompt: string;
    intervalHours: number;
    lastRunTimestamp: number;
    agentId: string;
    status?: 'enabled' | 'disabled';
}

export function initScheduler() {
    const workspaceDir = path.join(process.cwd(), 'workspace');
    if (!fs.existsSync(workspaceDir)) fs.mkdirSync(workspaceDir, { recursive: true });

    if (!fs.existsSync(JOBS_FILE)) {
        fs.writeFileSync(JOBS_FILE, JSON.stringify([], null, 2));
    }

    console.log(`[Scheduler] Initializing Heartbeat loop (checking every 60s)...`);

    // The Heartbeat
    setInterval(() => {
        checkAndExecuteJobs();
    }, 60 * 1000);

    // Run once on startup just in case we missed a window
    setTimeout(checkAndExecuteJobs, 5000);
}

async function checkAndExecuteJobs() {
    try {
        if (!fs.existsSync(JOBS_FILE)) return;

        const fileData = fs.readFileSync(JOBS_FILE, 'utf-8');
        const jobs: CronJob[] = JSON.parse(fileData);
        let jobsModified = false;

        const now = Date.now();

        for (const job of jobs) {
            if (job.status === 'disabled') continue;

            const intervalMs = job.intervalHours * 60 * 60 * 1000;
            const timeSinceLastRun = now - job.lastRunTimestamp;

            if (timeSinceLastRun >= intervalMs) {
                console.log(`\n⏰ [Scheduler] Triggering Cron Job: "${job.description}"`);

                // Update timestamp immediately so if it crashes we don't rapid-fire
                job.lastRunTimestamp = now;
                jobsModified = true;

                // Execute the job in the background via the Manager Agent
                // We append a system note so the LLM knows why it woke up
                const manager = new ManagerAgent();
                const cronPrompt = `[SYSTEM CRON TRIGGER] Wake up and execute your scheduled background task. Do not ask me for permission. Just do it and summarize the results.\n\nTask: ${job.prompt}`;

                manager.processUserRequest(cronPrompt).then(result => {
                    console.log(`[Scheduler] Job "${job.description}" completed. Result:\n${result}`);
                }).catch(err => {
                    console.error(`[Scheduler] Job "${job.description}" failed:`, err);
                });
            }
        }

        if (jobsModified) {
            fs.writeFileSync(JOBS_FILE, JSON.stringify(jobs, null, 2));
        }

    } catch (e) {
        console.error(`[Scheduler] Loop Error:`, e);
    }
}

export async function runJobForcefully(jobId: string) {
    if (!fs.existsSync(JOBS_FILE)) return false;

    const fileData = fs.readFileSync(JOBS_FILE, 'utf-8');
    const jobs: CronJob[] = JSON.parse(fileData);

    const job = jobs.find(j => j.id === jobId);
    if (!job) return false;

    console.log(`\n⚡ [Scheduler] Manually Triggering Job: "${job.description}"`);

    // Update timestamp
    job.lastRunTimestamp = Date.now();
    fs.writeFileSync(JOBS_FILE, JSON.stringify(jobs, null, 2));

    const manager = new ManagerAgent();
    const cronPrompt = `[SYSTEM MANUAL TRIGGER] Wake up and execute your background task manually requested by the user. Do not ask me for permission. Just do it and summarize the results.\n\nTask: ${job.prompt}`;

    // Fire and forget
    manager.processUserRequest(cronPrompt).then(result => {
        console.log(`[Scheduler] Manual Job "${job.description}" completed. Result:\n${result}`);
    }).catch(err => {
        console.error(`[Scheduler] Manual Job "${job.description}" failed:`, err);
    });

    return true;
}
