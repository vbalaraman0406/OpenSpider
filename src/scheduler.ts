import fs from 'node:fs';
import path from 'node:path';
import { ManagerAgent } from './agents/ManagerAgent';

const JOBS_FILE = path.join(process.cwd(), 'workspace', 'cron_jobs.json');

// Track active cron jobs so the WebSocket broadcast can suppress agent_flow events during cron runs
export let activeCronJobs = 0;

interface CronJob {
    id: string;
    description: string;
    prompt: string;
    intervalHours: number;
    lastRunTimestamp: number;
    agentId: string;
    status?: 'enabled' | 'disabled';
    // NEW: preferred time-of-day scheduling (e.g. "07:00", "14:30")
    // When set, the job runs once per day at this time instead of using intervalHours.
    // The intervalHours field is ignored when preferredTime is set.
    preferredTime?: string;
    // Timezone offset from UTC in hours (e.g. -8 for PST, -7 for PDT)
    // Defaults to the server's local timezone if not set.
    timezoneOffset?: number;
}

export function initScheduler() {
    const workspaceDir = path.join(process.cwd(), 'workspace');
    if (!fs.existsSync(workspaceDir)) fs.mkdirSync(workspaceDir, { recursive: true });

    if (!fs.existsSync(JOBS_FILE)) {
        fs.writeFileSync(JOBS_FILE, JSON.stringify([], null, 2));
    }

    console.log(`[Scheduler] Initializing Heartbeat loop (checking every 60s)...`);

    // The Heartbeat — checks every 60 seconds
    setInterval(() => {
        checkAndExecuteJobs();
    }, 60 * 1000);

    // Run once on startup just in case we missed a window
    setTimeout(checkAndExecuteJobs, 5000);
}

/**
 * Check if a time-of-day job should run.
 * A job should run if:
 * 1. The current time is within a 5-minute window of the preferred time
 * 2. The job hasn't run today (based on the last run date)
 */
function shouldRunTimeOfDay(job: CronJob, now: Date): boolean {
    if (!job.preferredTime) return false;

    const parts = job.preferredTime.split(':').map(Number);
    const prefHours = parts[0];
    const prefMinutes = parts[1];
    if (prefHours === undefined || prefMinutes === undefined || isNaN(prefHours) || isNaN(prefMinutes)) return false;

    // Get the current time in the job's timezone (or server local)
    const currentHours = now.getHours();
    const currentMinutes = now.getMinutes();

    // Check if current time is within a 5-minute window of preferred time
    const currentTotalMinutes = currentHours * 60 + currentMinutes;
    const preferredTotalMinutes = prefHours * 60 + prefMinutes;
    const diff = Math.abs(currentTotalMinutes - preferredTotalMinutes);

    if (diff > 5 && diff < (24 * 60 - 5)) return false; // Not in the window

    // Check if the job already ran today (same calendar date in local time)
    const lastRun = new Date(job.lastRunTimestamp);
    const lastRunDate = lastRun.toLocaleDateString();
    const todayDate = now.toLocaleDateString();

    if (lastRunDate === todayDate) return false; // Already ran today

    return true;
}

async function checkAndExecuteJobs() {
    try {
        if (!fs.existsSync(JOBS_FILE)) return;

        const fileData = fs.readFileSync(JOBS_FILE, 'utf-8');
        const jobs: CronJob[] = JSON.parse(fileData);
        let jobsModified = false;

        const now = Date.now();
        const nowDate = new Date(now);

        for (const job of jobs) {
            if (job.status === 'disabled') continue;

            let shouldRun = false;

            if (job.preferredTime) {
                // Time-of-day scheduling: run once per day at the preferred time
                shouldRun = shouldRunTimeOfDay(job, nowDate);
                if (shouldRun) {
                    console.log(`\n⏰ [Scheduler] Time-of-day trigger for: "${job.description}" (preferred: ${job.preferredTime})`);
                }
            } else {
                // Interval-based scheduling: run every N hours
                const intervalMs = job.intervalHours * 60 * 60 * 1000;
                const timeSinceLastRun = now - job.lastRunTimestamp;

                if (timeSinceLastRun >= intervalMs) {
                    shouldRun = true;
                    console.log(`\n⏰ [Scheduler] Interval trigger for: "${job.description}" (every ${job.intervalHours}h)`);
                }
            }

            if (shouldRun) {
                // Update timestamp immediately so if it crashes we don't rapid-fire
                job.lastRunTimestamp = now;
                jobsModified = true;

                // Execute the job in the background via the Manager Agent
                const manager = new ManagerAgent();
                const cronPrompt = `[SYSTEM CRON TRIGGER] Wake up and execute your scheduled background task. Do not ask me for permission. Just do it and summarize the results.\n\nTask: ${job.prompt}`;

                activeCronJobs++;
                manager.processUserRequest(cronPrompt).then(result => {
                    activeCronJobs--;
                    console.log(`[Scheduler] Job "${job.description}" completed. Result:\n${result}`);
                }).catch(err => {
                    activeCronJobs--;
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
    activeCronJobs++;
    manager.processUserRequest(cronPrompt).then(result => {
        activeCronJobs--;
        console.log(`[Scheduler] Manual Job "${job.description}" completed. Result:\n${result}`);
    }).catch(err => {
        activeCronJobs--;
        console.error(`[Scheduler] Manual Job "${job.description}" failed:`, err);
    });

    return true;
}
