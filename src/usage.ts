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
    totalRequests: number;
    avgTokensPerRequest: number;
    previousPeriodCost: number;
    models: Record<string, number>;
    agents: Record<string, number>;
    dailyTokens: { date: string, totalTokens: number, promptTokens: number, completionTokens: number }[];
    recentSessions: UsageEntry[];
}

// Pricing per 1,000,000 tokens (USD)
const PRICING_MATRIX: Record<string, { prompt: number, completion: number }> = {
    'claude-3-opus-20240229': { prompt: 15.00, completion: 75.00 },
    'claude-3-sonnet-20240229': { prompt: 3.00, completion: 15.00 },
    'claude-3-haiku-20240307': { prompt: 0.25, completion: 1.25 },
    'claude-opus-4-6-thinking': { prompt: 15.00, completion: 75.00 }, // Proxied through Antigravity to Claude Opus 4
    'gpt-4o': { prompt: 5.00, completion: 15.00 },
    'gpt-4-turbo': { prompt: 10.00, completion: 30.00 },
    'gpt-3.5-turbo': { prompt: 0.50, completion: 1.50 },
    // NVIDIA NIM models (free-tier / credit-based — set to $0, update if pricing changes)
    'nvidia/llama-3.1-nemotron-ultra-253b-v1': { prompt: 0, completion: 0 },
    // DeepSeek (very low cost)
    'deepseek-chat': { prompt: 0.27, completion: 1.10 },
};

function calculateExactCost(model: string, usage: TokenUsage): number {
    const pricing = PRICING_MATRIX[model] || PRICING_MATRIX[Object.keys(PRICING_MATRIX).find(k => model.includes(k)) || ''] || null;
    if (!pricing) return 0; // Unknown or local models (Ollama) count as $0
    return ((usage.promptTokens || 0) * pricing.prompt / 1_000_000) + ((usage.completionTokens || 0) * pricing.completion / 1_000_000);
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

        // Threshold check: alert if a single hit exceeds 25,000 tokens
        if (entry.usage && entry.usage.totalTokens > 25000) {
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

export function getUsageSummary(daysScope: number = 30): UsageSummary {
    initUsageLog();

    const summary: UsageSummary = {
        totalTokens: 0,
        totalCostEst: 0,
        totalRequests: 0,
        avgTokensPerRequest: 0,
        previousPeriodCost: 0,
        models: {},
        agents: {},
        dailyTokens: [],
        recentSessions: []
    };

    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() - daysScope);
    // Previous period: e.g. if daysScope=7, previous period is 14..7 days ago
    const prevPeriodStart = new Date();
    prevPeriodStart.setDate(prevPeriodStart.getDate() - daysScope * 2);
    let previousPeriodCost = 0;
    const cutoffTimestamp = targetDate.getTime();

    try {
        const content = fs.readFileSync(USAGE_FILE, 'utf-8');
        const lines = content.split('\n').filter(line => line.trim() !== '');

        const dailyMap: Record<string, { total: number, prompt: number, comp: number }> = {};

        // Parse and process last 100 entries for sessions, but all for aggregations
        const entries: UsageEntry[] = [];
        for (const line of lines) {
            try {
                const entry: UsageEntry = JSON.parse(line);

                // Filter by date scope
                const entryTime = entry.timestamp ? new Date(entry.timestamp).getTime() : 0;

                // Check if entry falls in previous period (for cost delta comparison)
                if (daysScope !== 0 && entryTime >= prevPeriodStart.getTime() && entryTime < cutoffTimestamp) {
                    if (entry.usage && entry.usage.totalTokens) {
                        previousPeriodCost += calculateExactCost(entry.model, entry.usage);
                    }
                    continue;
                }

                if (entryTime < cutoffTimestamp && daysScope !== 0) continue; // daysScope 0 = All Time

                entries.push(entry);

                if (entry.usage && entry.usage.totalTokens) {
                    summary.totalTokens += entry.usage.totalTokens;
                    summary.totalRequests += 1;

                    // Exact cost calculate logic
                    summary.totalCostEst += calculateExactCost(entry.model, entry.usage);

                    // Aggregate models
                    const md = entry.model || 'unknown';
                    summary.models[md] = (summary.models[md] || 0) + entry.usage.totalTokens;

                    // Aggregate agents
                    const ag = entry.agentId || 'gateway';
                    summary.agents[ag] = (summary.agents[ag] || 0) + entry.usage.totalTokens;

                    // Aggregate daily
                    const parts = entry.timestamp ? new Date(entry.timestamp).toISOString().split('T') : new Date().toISOString().split('T');
                    const dateStr = parts[0] || 'unknown-date';

                    if (!dailyMap[dateStr]) dailyMap[dateStr] = { total: 0, prompt: 0, comp: 0 };
                    dailyMap[dateStr].total += entry.usage.totalTokens;
                    dailyMap[dateStr].prompt += (entry.usage.promptTokens || 0);
                    dailyMap[dateStr].comp += (entry.usage.completionTokens || 0);
                }
            } catch (e) {
                // Ignore malformed JSONL lines
            }
        }

        // Convert daily map to sorted array
        summary.dailyTokens = Object.entries(dailyMap)
            .map(([date, data]) => ({ date, totalTokens: data.total, promptTokens: data.prompt, completionTokens: data.comp }))
            .sort((a, b) => a.date.localeCompare(b.date));

        // Let's grab the last 150 for recent sessions filtering in UI
        summary.recentSessions = entries.slice(-150).reverse();

        // Fix precision for cost
        summary.totalCostEst = Number(summary.totalCostEst.toFixed(5));
        summary.previousPeriodCost = Number(previousPeriodCost.toFixed(5));
        summary.avgTokensPerRequest = summary.totalRequests > 0 ? Math.round(summary.totalTokens / summary.totalRequests) : 0;

    } catch (e: any) {
        console.error('[Usage System] Failed to read usage log:', e.message);
    }

    return summary;
}
