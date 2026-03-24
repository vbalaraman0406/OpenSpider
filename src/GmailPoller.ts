/**
 * GmailPoller — Polls Gmail every 5 minutes for new emails and emits
 * matching events to the EventBus so event triggers can fire.
 *
 * This is needed because Google Pub/Sub webhooks cannot push to localhost.
 * The poller uses the existing GmailService OAuth credentials.
 *
 * DEDUP: Processed email IDs are persisted to disk so the same email
 * is never fired twice, even across server restarts.
 */
import { EventBus } from './EventBus';
import * as fs from 'node:fs';
import * as path from 'node:path';

const POLL_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes
let pollerInterval: ReturnType<typeof setInterval> | null = null;

// ─── Persistent Dedup ──────────────────────────────────────────────────────
const DEDUP_FILE = path.join(process.cwd(), 'workspace', 'gmail_poller_dedup.json');
const MAX_DEDUP_IDS = 500;

/** Load processed email IDs from disk. */
function loadProcessedIds(): Set<string> {
    try {
        if (fs.existsSync(DEDUP_FILE)) {
            const data = JSON.parse(fs.readFileSync(DEDUP_FILE, 'utf-8'));
            if (Array.isArray(data)) {
                console.log(`[GmailPoller] Loaded ${data.length} dedup IDs from disk`);
                return new Set(data);
            }
        }
    } catch (e) { /* fresh install */ }
    return new Set();
}

/** Save processed email IDs to disk. */
function saveProcessedIds(ids: Set<string>): void {
    try {
        // Keep only the most recent IDs to prevent unbounded growth
        const arr = Array.from(ids);
        const toSave = arr.length > MAX_DEDUP_IDS ? arr.slice(arr.length - MAX_DEDUP_IDS) : arr;
        fs.writeFileSync(DEDUP_FILE, JSON.stringify(toSave));
    } catch (e) { /* non-critical */ }
}

// Initialize from disk
const processedEmailIds = loadProcessedIds();

/**
 * Check Gmail for new emails since last poll and emit events to EventBus.
 */
async function pollGmail(): Promise<void> {
    try {
        // Only poll if there are gmail triggers registered
        const gmailTriggers = EventBus.getTriggersForSource('gmail');
        if (gmailTriggers.length === 0) return;

        // Dynamic import to avoid circular deps and allow graceful failure
        const { GmailService } = require('./services/GmailService');
        const gmail = GmailService.getInstance();

        // Query for recent emails (last 2 hours).
        // We rely on the dedup set to avoid re-processing, not the timestamp.
        const twoHoursAgo = Math.floor((Date.now() - 2 * 60 * 60 * 1000) / 1000);
        const query = `after:${twoHoursAgo}`;

        const result = await gmail.readEmails({ query, maxResults: 20 });
        if (!result.success || !result.emails || result.emails.length === 0) {
            return;
        }

        let newCount = 0;
        let matchedCount = 0;

        for (const email of result.emails) {
            // Skip emails we've already processed (survives restarts)
            if (processedEmailIds.has(email.id)) continue;
            processedEmailIds.add(email.id);
            newCount++;

            // Emit each email as an event to the EventBus
            const matched = await EventBus.emit('gmail', {
                source: 'gmail',
                from: email.from || '',
                subject: email.subject || '',
                body: email.snippet || '',
                id: email.id
            });

            if (matched) {
                matchedCount++;
                console.log(`  ⚡ [GmailPoller] Trigger matched for: "${email.subject}"`);
            }
        }

        if (newCount > 0) {
            console.log(`\n📬 [GmailPoller] Processed ${newCount} new email(s), ${matchedCount} matched triggers`);
            // Persist dedup set after each poll
            saveProcessedIds(processedEmailIds);
        }
    } catch (err: any) {
        // Silently handle - Gmail may not be configured
        if (err.message?.includes('Missing Gmail OAuth')) {
            return;
        }
        console.error('[GmailPoller] Poll error:', err.message);
    }
}

/**
 * Start the Gmail poller. Called once at server startup.
 */
export function startGmailPoller(): void {
    console.log(`[GmailPoller] Starting Gmail event poller (every 5 minutes, ${processedEmailIds.size} dedup IDs loaded)`);

    // Do first poll after 10 seconds (let server initialize)
    setTimeout(() => {
        pollGmail();
        // Then poll every 5 minutes
        pollerInterval = setInterval(pollGmail, POLL_INTERVAL_MS);
    }, 10_000);
}

/**
 * Stop the Gmail poller.
 */
export function stopGmailPoller(): void {
    if (pollerInterval) {
        clearInterval(pollerInterval);
        pollerInterval = null;
        // Save dedup state on shutdown
        saveProcessedIds(processedEmailIds);
        console.log('[GmailPoller] Stopped (dedup saved)');
    }
}
