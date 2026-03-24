/**
 * GmailPoller — Polls Gmail every 5 minutes for new emails and emits
 * matching events to the EventBus so event triggers can fire.
 *
 * This is needed because Google Pub/Sub webhooks cannot push to localhost.
 * The poller uses the existing GmailService OAuth credentials.
 */
import { EventBus } from './EventBus';

const POLL_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes
// Start looking back 2 hours to catch emails that arrived before startup
let lastPollTimestamp = Date.now() - (2 * 60 * 60 * 1000);
let pollerInterval: ReturnType<typeof setInterval> | null = null;
// Track processed email IDs to avoid firing the same email twice
const processedEmailIds = new Set<string>();

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

        // Build query for emails newer than last poll
        // Gmail API uses 'newer_than' relative time or 'after' epoch (seconds)
        const afterEpochSecs = Math.floor(lastPollTimestamp / 1000);
        const query = `after:${afterEpochSecs}`;

        const result = await gmail.readEmails({ query, maxResults: 20 });
        if (!result.success || !result.emails || result.emails.length === 0) {
            return;
        }

        console.log(`\n📬 [GmailPoller] Found ${result.emails.length} new email(s) since last poll`);

        for (const email of result.emails) {
            // Skip emails we've already processed
            if (processedEmailIds.has(email.id)) continue;
            processedEmailIds.add(email.id);

            // Emit each email as an event to the EventBus
            const matched = await EventBus.emit('gmail', {
                source: 'gmail',
                from: email.from || '',
                subject: email.subject || '',
                body: email.snippet || '',
                id: email.id
            });

            if (matched) {
                console.log(`  ⚡ [GmailPoller] Trigger matched for: "${email.subject}"`);
            }
        }

        lastPollTimestamp = Date.now();
    } catch (err: any) {
        // Silently handle - Gmail may not be configured
        if (err.message?.includes('Missing Gmail OAuth')) {
            // Gmail not set up - that's fine, skip polling
            return;
        }
        console.error('[GmailPoller] Poll error:', err.message);
    }
}

/**
 * Start the Gmail poller. Called once at server startup.
 */
export function startGmailPoller(): void {
    console.log('[GmailPoller] Starting Gmail event poller (every 5 minutes)');

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
        console.log('[GmailPoller] Stopped');
    }
}
