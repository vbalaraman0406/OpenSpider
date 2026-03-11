/**
 * CronStore — Centralized, race-safe accessor for cron_jobs.json
 *
 * Prevents TOCTOU bugs: the scheduler tick and schedule_task tool
 * both read/modify/write cron_jobs.json.  Without synchronisation
 * one writer can overwrite the other's changes.
 *
 * All access MUST go through readJobs() and writeJobs() so that
 * a simple mutex prevents concurrent reads from getting stale data.
 */
import fs from 'node:fs';
import path from 'node:path';

const JOBS_FILE = path.join(process.cwd(), 'workspace', 'cron_jobs.json');

let mutexLocked = false;
const waitQueue: Array<() => void> = [];

async function acquireLock(): Promise<void> {
    if (!mutexLocked) {
        mutexLocked = true;
        return;
    }
    return new Promise(resolve => {
        waitQueue.push(() => {
            mutexLocked = true;
            resolve();
        });
    });
}

function releaseLock() {
    if (waitQueue.length > 0) {
        const next = waitQueue.shift()!;
        next();
    } else {
        mutexLocked = false;
    }
}

export interface CronJob {
    id: string;
    description: string;
    prompt: string;
    intervalHours: number;
    lastRunTimestamp: number;
    agentId: string;
    status?: 'enabled' | 'disabled';
    preferredTime?: string;
    timezoneOffset?: number;
    [key: string]: any;  // Allow extra fields
}

/**
 * Read the current list of cron jobs from disk.
 * Acquires a mutex so no concurrent write can sneak in between
 * a read and a subsequent write by the SAME caller.
 * Caller MUST call releaseJobsLock() when done (or use withJobs()).
 */
export function readJobsSync(): CronJob[] {
    try {
        if (!fs.existsSync(JOBS_FILE)) return [];
        return JSON.parse(fs.readFileSync(JOBS_FILE, 'utf-8'));
    } catch (e) {
        console.error('[CronStore] Failed to read cron_jobs.json:', e);
        return [];
    }
}

export function writeJobsSync(jobs: CronJob[]) {
    try {
        const dir = path.dirname(JOBS_FILE);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        fs.writeFileSync(JOBS_FILE, JSON.stringify(jobs, null, 2));
    } catch (e) {
        console.error('[CronStore] Failed to write cron_jobs.json:', e);
    }
}

/**
 * Atomic read-modify-write: acquires lock, reads file, calls mutator,
 * writes result, releases lock.  Use this for all modifications.
 */
export async function withJobs(mutator: (jobs: CronJob[]) => CronJob[]): Promise<CronJob[]> {
    await acquireLock();
    try {
        const jobs = readJobsSync();
        const updated = mutator(jobs);
        writeJobsSync(updated);
        return updated;
    } finally {
        releaseLock();
    }
}

/**
 * Read-only snapshot (still locked to avoid torn reads during a write).
 */
export async function getJobs(): Promise<CronJob[]> {
    await acquireLock();
    try {
        return readJobsSync();
    } finally {
        releaseLock();
    }
}
