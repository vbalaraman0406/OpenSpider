import fs from 'node:fs';
import path from 'node:path';

const WORKSPACE_DIR = path.join(process.cwd(), 'workspace');
const USAGE_FILE = path.join(WORKSPACE_DIR, 'usage.jsonl');

export interface TokenUsage {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
}

export interface UsageEntry {
    timestamp: string;
    model: string;
    usage: TokenUsage;
    sessionKey?: string;
    agentId?: string;
}

export interface UsageSummary {
    totalTokens: number;
    totalCostEst: number;
    models: Record<string, number>;
    dailyTokens: { date: string, tokens: number }[];
    recentSessions: UsageEntry[];
}

// Ensures workspace directory exists
function initWorkspace() {
    if (!fs.existsSync(WORKSPACE_DIR)) fs.mkdirSync(WORKSPACE_DIR, { recursive: true });
}

// Ensure the usage file exists
export function initUsageLog() {
    initWorkspace();
    if (!fs.existsSync(USAGE_FILE)) {
        fs.writeFileSync(USAGE_FILE, '', 'utf-8');
    }
}

/**
 * Logs usage and returns true if an alert threshold is breached
 */
export function logUsage(entry: UsageEntry): { isAlert: boolean, message?: string } {
    initUsageLog();

    // Add timestamp if missing
    if (!entry.timestamp) {
        entry.timestamp = new Date().toISOString();
    }

    try {
        fs.appendFileSync(USAGE_FILE, JSON.stringify(entry) + '\n', 'utf-8');

        // Threshold check: alert if a single hit exceeds 5,000 tokens
        if (entry.usage && entry.usage.totalTokens > 5000) {
            return {
                isAlert: true,
                message: `⚠️ High Token Usage Alert: ${entry.agentId || 'Agent'} consumed ${entry.usage.totalTokens.toLocaleString()} tokens using ${entry.model}.`
            };
        }
    } catch (e: any) {
        console.error('[Usage System] Failed to write usage log:', e.message);
    }

    return { isAlert: false };
}

export function getUsageSummary(): UsageSummary {
    initUsageLog();

    const summary: UsageSummary = {
        totalTokens: 0,
        totalCostEst: 0,
        models: {},
        dailyTokens: [],
        recentSessions: []
    };

    try {
        const content = fs.readFileSync(USAGE_FILE, 'utf-8');
        const lines = content.split('\n').filter(line => line.trim() !== '');

        const dailyMap: Record<string, number> = {};

        // Parse and process last 100 entries for sessions, but all for aggregations
        const entries: UsageEntry[] = [];
        for (const line of lines) {
            try {
                const entry: UsageEntry = JSON.parse(line);
                entries.push(entry);

                if (entry.usage && entry.usage.totalTokens) {
                    summary.totalTokens += entry.usage.totalTokens;

                    // Aggregate models
                    const md = entry.model || 'unknown';
                    summary.models[md] = (summary.models[md] || 0) + entry.usage.totalTokens;

                    // Aggregate daily
                    const parts = entry.timestamp ? new Date(entry.timestamp).toISOString().split('T') : new Date().toISOString().split('T');
                    const dateStr = parts[0] || 'unknown-date';
                    dailyMap[dateStr] = (dailyMap[dateStr] || 0) + entry.usage.totalTokens;
                }
            } catch (e) {
                // Ignore malformed JSONL lines
            }
        }

        // Convert daily map to sorted array
        summary.dailyTokens = Object.entries(dailyMap)
            .map(([date, tokens]) => ({ date, tokens }))
            .sort((a, b) => a.date.localeCompare(b.date));

        // Let's grab the last 50 for recent sessions
        summary.recentSessions = entries.slice(-50).reverse();

        // Rough estimation: 1 million tokens = ~$1.00 (avg mix of cheap/expensive)
        // Just an illustrative number to populate the UI realistically
        summary.totalCostEst = Number((summary.totalTokens / 1000000).toFixed(4));

    } catch (e: any) {
        console.error('[Usage System] Failed to read usage log:', e.message);
    }

    return summary;
}
