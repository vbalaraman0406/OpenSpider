import fs from 'node:fs';
import path from 'node:path';
import { ManagerAgent } from './agents/ManagerAgent';
import { readJobsSync, writeJobsSync, withJobs, CronJob } from './CronStore';

const JOBS_FILE = path.join(process.cwd(), 'workspace', 'cron_jobs.json');

// Track active cron jobs so the WebSocket broadcast can suppress agent_flow events during cron runs
export let activeCronJobs = 0;

export function initScheduler() {
    const workspaceDir = path.join(process.cwd(), 'workspace');
    if (!fs.existsSync(workspaceDir)) fs.mkdirSync(workspaceDir, { recursive: true });

    if (!fs.existsSync(JOBS_FILE)) {
        writeJobsSync([]);
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

function getCronEmailFromAddress(): string {
    try {
        const emailConfigPath = path.join(process.cwd(), 'workspace', 'email_config.json');
        if (fs.existsSync(emailConfigPath)) {
            const emailConfig = JSON.parse(fs.readFileSync(emailConfigPath, 'utf-8'));
            if (emailConfig.cronFromEmail) return emailConfig.cronFromEmail;
        }
    } catch (e) { }
    return '';
}
// ─── Queue Structures ───
interface QueuedContext {
    job: CronJob;
    isManual: boolean;
    cronPrompt: string;
}

const jobQueue: QueuedContext[] = [];
let isProcessingQueue = false;

async function processJobQueue() {
    if (isProcessingQueue || jobQueue.length === 0) return;
    isProcessingQueue = true;

    while (jobQueue.length > 0) {
        const ctx = jobQueue.shift()!;
        try {
            await executeQueuedContext(ctx);
        } catch (e) {
            console.error(`[Scheduler] Queue execution failed for job "${ctx.job.description}":`, e);
        }
    }

    isProcessingQueue = false;
}

async function executeQueuedContext(ctx: QueuedContext) {
    const job = ctx.job;
    const prefix = ctx.isManual ? 'Manual Job' : 'Job';
    console.log(`\n▶️ [SchedulerQueue] Starting ${prefix}: "${job.description}"...`);

    // Digest-type jobs use DigestEngine instead of ManagerAgent
    if (job.type === 'digest') {
        activeCronJobs++;
        try {
            const { DigestEngine } = await import('./DigestEngine');
            const digest = await DigestEngine.compileDigest();
            const config = DigestEngine.getConfig();

            // Deliver via configured channels
            if (config.channels.includes('whatsapp') && config.whatsappTargets.length > 0) {
                try {
                    const { sendWhatsAppMessage } = require('./whatsapp');
                    for (const target of config.whatsappTargets) {
                        await sendWhatsAppMessage(target, digest);
                    }
                } catch (waErr: any) {
                    console.error(`[Scheduler] Digest WhatsApp delivery failed:`, waErr.message);
                }
            }

            activeCronJobs--;
            console.log(`[Scheduler] Digest "${job.description}" compiled successfully.`);
            console.log(JSON.stringify({
                type: 'cron_result',
                jobName: job.description,
                result: digest,
                timestamp: new Date().toISOString()
            }));
        } catch (err: any) {
            activeCronJobs--;
            console.error(`[Scheduler] Digest "${job.description}" failed:`, err);
        }
        return;
    }

    // Standard Agent Handling
    const manager = new ManagerAgent(job.modelOverride || undefined);
    activeCronJobs++;

    try {
        const result = await manager.processUserRequest(ctx.cronPrompt);
        activeCronJobs--;
        console.log(`[Scheduler] ${prefix} "${job.description}" completed. Result:\n${result}`);
        
        console.log(JSON.stringify({
            type: 'cron_result',
            jobName: job.description,
            result: result,
            timestamp: new Date().toISOString()
        }));

        if (!ctx.isManual) {
            // ─── EventBus + Workflow Chain Integration ───
            const { EventBus } = await import('./EventBus');
            EventBus.emit('cron_result', {
                source: 'cron_result',
                jobId: job.id,
                jobName: job.description,
                body: result,
            }).catch((err: any) => console.error('[Scheduler] EventBus emit failed:', err));

            const { WorkflowEngine } = await import('./WorkflowEngine');
            const chained = WorkflowEngine.getWorkflowsForCron(job.id);
            for (const wf of chained) {
                console.log(`🔗 [Scheduler] Triggering chained workflow: "${wf.name}"`);
                WorkflowEngine.executeWorkflow(wf.id, `Cron job "${job.description}" completed.\n\nResult:\n${result}`)
                    .catch((err: any) => console.error(`[Scheduler] Workflow "${wf.name}" failed:`, err));
            }
        }
    } catch (err) {
        activeCronJobs--;
        console.error(`[Scheduler] ${prefix} "${job.description}" failed:`, err);
    }
}

async function checkAndExecuteJobs() {
    try {
        // Use the mutex-protected withJobs() to atomically read and update timestamps.
        // This prevents race conditions with dashboard edits and agent schedule_task calls.
        const jobsToRun: CronJob[] = [];

        await withJobs((jobs: CronJob[]) => {
            if (jobs.length === 0) return jobs;

            const now = Date.now();
            const nowDate = new Date(now);

            for (const job of jobs) {
                if (job.status === 'disabled') continue;

                let shouldRun = false;

                if (job.preferredTime) {
                    shouldRun = shouldRunTimeOfDay(job, nowDate);
                    if (shouldRun) {
                        console.log(`\n⏰ [Scheduler] Time-of-day trigger for: "${job.description}" (preferred: ${job.preferredTime})`);
                    }
                } else {
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
                    jobsToRun.push({ ...job }); // Clone for execution outside the lock
                }
            }

            return jobs; // withJobs() writes this back atomically
        });

        if (jobsToRun.length === 0) return;

        // Prepare jobs for execution OUTSIDE the lock — the file is already updated
        const cronFrom = getCronEmailFromAddress();
        const cronFromNote = cronFrom ? `\n\n[CRON EMAIL SENDER RULE] IMPORTANT: When sending any emails as part of this automated task, you MUST always set the "from" field to "${cronFrom}" in your send_email tool call. This is a system-level requirement for all cron job emails.` : '';

        for (const job of jobsToRun) {
            // Inject agent routing directive so ManagerAgent delegates to the correct worker
            const agentDirective = (job.agentId && job.agentId !== 'manager')
                ? `\n\n[MANDATORY AGENT ROUTING] You MUST delegate this task to the "${job.agentId}" agent. Do NOT pick any other agent. This is a system-level directive from the scheduler.`
                : '';

            const explicitLogNote = `\n\n[LOGGING REQUIREMENT] In your final summary report (using the 'final_answer' tool), you MUST explicitly print the exact, raw email addresses and WhatsApp numbers/JIDs you sent messages to. Do NOT include this delivery status log inside the actual WhatsApp message or Email body you send to the user! Keep the user's message payload clean.`;
            const antiHallucinationNote = `\n\n[ANTI-HALLUCINATION DIRECTIVE] You MUST explicitly execute the required tool (e.g. 'send_email', 'send_whatsapp') to actually send a message. Do NOT simply draft the email/message content within your final "result" output. The task is only complete once you call the tool and receive a success confirmation.`;

            const cronPrompt = `[SYSTEM CRON TRIGGER] Wake up and execute your scheduled background task. Do not ask me for permission. Just do it and summarize the results.${cronFromNote}${agentDirective}${explicitLogNote}${antiHallucinationNote}\n\nTask: ${job.prompt}`;

            console.log(`[Scheduler] Queuing Background Job: "${job.description}"`);
            jobQueue.push({ job, isManual: false, cronPrompt });
        }

        // Kick off the queue processor
        processJobQueue();

    } catch (e) {
        console.error(`[Scheduler] Loop Error:`, e);
    }
}

export async function runJobForcefully(jobId: string) {
    let jobToRun: CronJob | null = null;

    await withJobs((jobs: CronJob[]) => {
        const job = jobs.find(j => j.id === jobId);
        if (job) {
            job.lastRunTimestamp = Date.now();
            jobToRun = { ...job };
        }
        return jobs;
    });

    if (!jobToRun) return false;
    const job = jobToRun as CronJob;

    console.log(`\n⚡ [Scheduler] Manually Triggering Job (pushing to queue): "${job.description}"`);

    const cronFrom = getCronEmailFromAddress();
    const cronFromNote = cronFrom ? `\n\n[CRON EMAIL SENDER RULE] IMPORTANT: When sending any emails as part of this automated task, you MUST always set the "from" field to "${cronFrom}" in your send_email tool call. This is a system-level requirement for all cron job emails.` : '';

    // Inject agent routing directive for manual runs too
    const agentDirective = (job.agentId && job.agentId !== 'manager')
        ? `\n\n[MANDATORY AGENT ROUTING] You MUST delegate this task to the "${job.agentId}" agent. Do NOT pick any other agent. This is a system-level directive from the scheduler.`
        : '';

    const explicitLogNote = `\n\n[LOGGING REQUIREMENT] In your final summary report, you MUST explicitly print the exact, raw email addresses and WhatsApp numbers/JIDs you sent messages to. Do NOT use abstract phrases like "default user", "the requested group", or "the recipient". Print the exact target strings returned by the tool output.`;
    const antiHallucinationNote = `\n\n[ANTI-HALLUCINATION DIRECTIVE] You MUST explicitly execute the required tool (e.g. 'send_email', 'send_whatsapp') to actually send a message. Do NOT simply draft the email/message content within your final "result" output. The task is only complete once you call the tool and receive a success confirmation.`;

    const cronPrompt = `[SYSTEM MANUAL TRIGGER] Wake up and execute your background task manually requested by the user. Do not ask me for permission. Just do it and summarize the results.${cronFromNote}${agentDirective}${explicitLogNote}${antiHallucinationNote}\n\nTask: ${job.prompt}`;

    jobQueue.push({ job, isManual: true, cronPrompt });
    processJobQueue();

    return true;
}
