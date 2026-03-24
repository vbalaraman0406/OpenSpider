/**
 * EventBus — In-memory pub/sub for event-driven triggers
 *
 * Receives events from sources (Gmail, WhatsApp, webhooks, cron results)
 * and matches them against registered trigger rules. When a trigger matches,
 * it spawns the configured action (workflow execution or agent task).
 */
import fs from 'node:fs';
import path from 'node:path';
import { WorkflowEngine } from './WorkflowEngine';
import { ManagerAgent } from './agents/ManagerAgent';

const TRIGGERS_FILE = path.join(process.cwd(), 'workspace', 'event_triggers.json');

// ─── Types ──────────────────────────────────────────────────────────────────

export interface EventFilter {
    /** Glob/contains match on sender (email from, WhatsApp sender) */
    from?: string;
    /** Contains match on subject/message */
    subject_contains?: string;
    /** Contains match on body/content */
    body_contains?: string;
    /** Exact match on any custom field */
    [key: string]: string | undefined;
}

export interface TriggerAction {
    type: 'workflow' | 'agent_task';
    /** For workflow type: ID of the workflow to execute */
    workflowId?: string;
    /** For agent_task type: prompt to send to ManagerAgent */
    prompt?: string;
}

export interface EventTrigger {
    id: string;
    name: string;
    description?: string;
    status: 'enabled' | 'disabled';
    /** Event source to listen to */
    source: 'gmail' | 'whatsapp' | 'webhook' | 'cron_result';
    /** Filter rules — all must match */
    filter: EventFilter;
    /** Action to take when trigger fires */
    action: TriggerAction;
    createdAt: string;
    lastFiredAt?: string;
    fireCount: number;
}

export interface EventPayload {
    source: string;
    from?: string;
    subject?: string;
    body?: string;
    [key: string]: any;
}

// ─── Persistence ────────────────────────────────────────────────────────────

function readTriggers(): EventTrigger[] {
    try {
        if (!fs.existsSync(TRIGGERS_FILE)) return [];
        return JSON.parse(fs.readFileSync(TRIGGERS_FILE, 'utf-8'));
    } catch (e) {
        console.error('[EventBus] Failed to read event_triggers.json:', e);
        return [];
    }
}

function writeTriggers(triggers: EventTrigger[]) {
    try {
        const dir = path.dirname(TRIGGERS_FILE);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        fs.writeFileSync(TRIGGERS_FILE, JSON.stringify(triggers, null, 2));
    } catch (e) {
        console.error('[EventBus] Failed to write event_triggers.json:', e);
    }
}

// ─── Filter Matching ────────────────────────────────────────────────────────

/**
 * Glob-style match: supports * wildcard.
 * e.g., "*@company.com" matches "boss@company.com"
 */
function globMatch(pattern: string, value: string): boolean {
    if (!pattern || !value) return false;
    const regexStr = pattern
        .replace(/[.+^${}()|[\]\\]/g, '\\$&')  // Escape regex special chars (except *)
        .replace(/\*/g, '.*');                    // Convert * to .*
    return new RegExp(`^${regexStr}$`, 'i').test(value);
}

/**
 * Check if an event payload matches all filter rules.
 * Empty filter matches everything.
 */
function matchFilter(filter: EventFilter, payload: EventPayload): boolean {
    for (const [key, pattern] of Object.entries(filter)) {
        if (!pattern) continue;

        if (key === 'from') {
            // Extract bare email from "Display Name <email@domain.com>" format
            let fromAddr = payload.from || '';
            const angleBracketMatch = fromAddr.match(/<([^>]+)>/);
            if (angleBracketMatch && angleBracketMatch[1]) fromAddr = angleBracketMatch[1];
            if (!globMatch(pattern, fromAddr)) return false;
        } else if (key === 'subject_contains') {
            if (!(payload.subject || '').toLowerCase().includes(pattern.toLowerCase())) return false;
        } else if (key === 'body_contains') {
            if (!(payload.body || '').toLowerCase().includes(pattern.toLowerCase())) return false;
        } else {
            // Generic field match
            const payloadVal = payload[key];
            if (typeof payloadVal === 'string') {
                if (!globMatch(pattern, payloadVal)) return false;
            } else {
                return false;
            }
        }
    }
    return true;
}

// ─── Event Bus ──────────────────────────────────────────────────────────────

export class EventBus {

    /**
     * Emit an event. Checks all enabled triggers for the given source,
     * matches filters, and fires matching trigger actions.
     *
     * Returns true if any trigger matched and was fired.
     */
    static async emit(source: string, payload: EventPayload): Promise<boolean> {
        const triggers = readTriggers();
        const matching = triggers.filter(
            t => t.status === 'enabled' && t.source === source && matchFilter(t.filter, payload)
        );

        if (matching.length === 0) return false;

        console.log(`\n⚡ [EventBus] ${matching.length} trigger(s) matched for event source "${source}"`);

        for (const trigger of matching) {
            console.log(`  → Firing trigger: "${trigger.name}" (action: ${trigger.action.type})`);

            // Update fire count and timestamp
            trigger.lastFiredAt = new Date().toISOString();
            trigger.fireCount = (trigger.fireCount || 0) + 1;

            // Build context string from event payload
            const context = Object.entries(payload)
                .filter(([k]) => k !== 'source')
                .map(([k, v]) => `${k}: ${typeof v === 'string' ? v.substring(0, 500) : JSON.stringify(v)}`)
                .join('\n');

            try {
                if (trigger.action.type === 'workflow' && trigger.action.workflowId) {
                    // Fire workflow with event data as context
                    WorkflowEngine.executeWorkflow(trigger.action.workflowId, context)
                        .then(result => {
                            console.log(`  ✓ [EventBus] Workflow "${result.workflowName}" ${result.status} (${result.totalDurationMs}ms)`);
                        })
                        .catch(err => {
                            console.error(`  ✗ [EventBus] Workflow failed:`, err.message);
                        });
                } else if (trigger.action.type === 'agent_task' && trigger.action.prompt) {
                    // Fire agent task with event context
                    const prompt = `[EVENT TRIGGER: ${trigger.name}]\nSource: ${source}\n\n${context}\n\n[TASK]\n${trigger.action.prompt}`;
                    const manager = new ManagerAgent();
                    manager.processUserRequest(prompt)
                        .then(result => {
                            console.log(`  ✓ [EventBus] Agent task completed for trigger "${trigger.name}"`);
                        })
                        .catch(err => {
                            console.error(`  ✗ [EventBus] Agent task failed:`, err.message);
                        });
                }
            } catch (err: any) {
                console.error(`  ✗ [EventBus] Failed to fire trigger "${trigger.name}":`, err.message);
            }
        }

        // Persist updated fire counts
        writeTriggers(triggers);

        return true;
    }

    // ─── CRUD ───────────────────────────────────────────────────────────

    static getTriggers(): EventTrigger[] {
        return readTriggers();
    }

    static getTrigger(id: string): EventTrigger | undefined {
        return readTriggers().find(t => t.id === id);
    }

    static saveTrigger(trigger: EventTrigger): EventTrigger {
        const triggers = readTriggers();
        const existing = triggers.findIndex(t => t.id === trigger.id);
        if (existing >= 0) {
            triggers[existing] = trigger;
        } else {
            trigger.createdAt = trigger.createdAt || new Date().toISOString();
            trigger.fireCount = trigger.fireCount || 0;
            triggers.push(trigger);
        }
        writeTriggers(triggers);
        return trigger;
    }

    static deleteTrigger(id: string): boolean {
        const triggers = readTriggers();
        const filtered = triggers.filter(t => t.id !== id);
        if (filtered.length === triggers.length) return false;
        writeTriggers(filtered);
        return true;
    }

    /**
     * Get triggers for a specific event source.
     */
    static getTriggersForSource(source: string): EventTrigger[] {
        return readTriggers().filter(t => t.status === 'enabled' && t.source === source);
    }
}
