import fs from 'node:fs';
import path from 'node:path';
import { getProvider } from './llm';

// ═══════════════════════════════════════════════════════════════
// DigestEngine — Compiles a smart daily briefing from cron job
// results. Aggregates, deduplicates, and uses LLM to produce
// a structured digest delivered via WhatsApp/email.
// ═══════════════════════════════════════════════════════════════

export interface DigestSection {
    emoji: string;
    title: string;
    content: string;
}

export interface DigestConfig {
    enabled: boolean;
    preferredTime: string;       // HH:MM format
    channels: ('whatsapp' | 'email')[];
    sections: {
        markets: boolean;
        alerts: boolean;
        monitoring: boolean;
        general: boolean;
    };
    hoursBack: number;           // How far back to look for cron results
    whatsappTargets: string[];   // JIDs for delivery
    emailTargets: string[];      // Email addresses for delivery
}

interface CronLogEntry {
    jobName: string;
    result: string;
    timestamp: string;
}

const DEFAULT_CONFIG: DigestConfig = {
    enabled: false,
    preferredTime: '07:00',
    channels: ['whatsapp'],
    sections: {
        markets: true,
        alerts: true,
        monitoring: true,
        general: true,
    },
    hoursBack: 24,
    whatsappTargets: [],
    emailTargets: [],
};

const CONFIG_PATH = path.join(process.cwd(), 'workspace', 'digest_config.json');
const CRON_LOGS_PATH = path.join(process.cwd(), 'workspace', 'cron_logs.json');

export class DigestEngine {

    /**
     * Load digest configuration from disk.
     */
    static getConfig(): DigestConfig {
        try {
            if (fs.existsSync(CONFIG_PATH)) {
                const raw = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
                return { ...DEFAULT_CONFIG, ...raw };
            }
        } catch (e) {
            console.error('[DigestEngine] Failed to read config:', e);
        }
        return { ...DEFAULT_CONFIG };
    }

    /**
     * Save digest configuration to disk.
     */
    static saveConfig(config: Partial<DigestConfig>): DigestConfig {
        const current = DigestEngine.getConfig();
        const merged = { ...current, ...config };
        fs.writeFileSync(CONFIG_PATH, JSON.stringify(merged, null, 2));
        console.log('[DigestEngine] Config saved.');
        return merged;
    }

    /**
     * Read cron logs from the last N hours.
     */
    private static readRecentLogs(hoursBack: number): CronLogEntry[] {
        try {
            if (!fs.existsSync(CRON_LOGS_PATH)) return [];

            const raw = JSON.parse(fs.readFileSync(CRON_LOGS_PATH, 'utf-8'));
            if (!Array.isArray(raw)) return [];

            const cutoff = Date.now() - hoursBack * 60 * 60 * 1000;
            return raw.filter((entry: CronLogEntry) => {
                if (!entry.timestamp) return false;
                return new Date(entry.timestamp).getTime() > cutoff;
            });
        } catch (e) {
            console.error('[DigestEngine] Failed to read cron logs:', e);
            return [];
        }
    }

    /**
     * Categorize a cron job result by its job name.
     */
    private static categorizeJob(jobName: string): 'markets' | 'alerts' | 'monitoring' | 'general' {
        const lower = jobName.toLowerCase();
        if (lower.includes('market') || lower.includes('s&p') || lower.includes('nasdaq') ||
            lower.includes('stock') || lower.includes('pre-market') || lower.includes('home price') ||
            lower.includes('portfolio')) {
            return 'markets';
        }
        if (lower.includes('monitor') || lower.includes('downdetector') || lower.includes('bmo') ||
            lower.includes('status') || lower.includes('uptime')) {
            return 'monitoring';
        }
        if (lower.includes('alert') || lower.includes('urgent') || lower.includes('outage')) {
            return 'alerts';
        }
        return 'general';
    }

    /**
     * Compile a digest from recent cron log results.
     * Groups by category, deduplicates, and prepares for LLM summarization.
     */
    static async compileDigest(hoursBack?: number): Promise<string> {
        const config = DigestEngine.getConfig();
        const lookback = hoursBack || config.hoursBack || 24;
        const logs = DigestEngine.readRecentLogs(lookback);

        if (logs.length === 0) {
            return '📭 No cron job results found in the last ' + lookback + ' hours. Nothing to digest.';
        }

        // Group logs by category
        const grouped: Record<string, CronLogEntry[]> = {
            markets: [],
            alerts: [],
            monitoring: [],
            general: [],
        };

        for (const log of logs) {
            const category = DigestEngine.categorizeJob(log.jobName);
            grouped[category]!.push(log);
        }

        // Deduplicate within each category (keep latest per job name)
        for (const category of Object.keys(grouped)) {
            const entries = grouped[category]!;
            const latestByJob = new Map<string, CronLogEntry>();
            for (const entry of entries) {
                const existing = latestByJob.get(entry.jobName);
                if (!existing || new Date(entry.timestamp) > new Date(existing.timestamp)) {
                    latestByJob.set(entry.jobName, entry);
                }
            }
            grouped[category] = Array.from(latestByJob.values());
        }

        // Build raw summary for LLM
        const rawSections: string[] = [];
        const sectionConfig = config.sections;

        if (sectionConfig.markets && grouped.markets!.length > 0) {
            rawSections.push('=== MARKETS ===\n' + grouped.markets!.map(l =>
                `Job: ${l.jobName}\nTime: ${l.timestamp}\nResult: ${l.result.substring(0, 1500)}`
            ).join('\n---\n'));
        }

        if (sectionConfig.alerts && grouped.alerts!.length > 0) {
            rawSections.push('=== ALERTS ===\n' + grouped.alerts!.map(l =>
                `Job: ${l.jobName}\nTime: ${l.timestamp}\nResult: ${l.result.substring(0, 1500)}`
            ).join('\n---\n'));
        }

        if (sectionConfig.monitoring && grouped.monitoring!.length > 0) {
            rawSections.push('=== MONITORING ===\n' + grouped.monitoring!.map(l =>
                `Job: ${l.jobName}\nTime: ${l.timestamp}\nResult: ${l.result.substring(0, 1500)}`
            ).join('\n---\n'));
        }

        if (sectionConfig.general && grouped.general!.length > 0) {
            rawSections.push('=== GENERAL ===\n' + grouped.general!.map(l =>
                `Job: ${l.jobName}\nTime: ${l.timestamp}\nResult: ${l.result.substring(0, 1500)}`
            ).join('\n---\n'));
        }

        if (rawSections.length === 0) {
            return '📭 All enabled digest sections were empty. No notable results in the last ' + lookback + ' hours.';
        }

        // Use LLM to summarize into a structured digest
        try {
            const digest = await DigestEngine.summarizeWithLLM(rawSections.join('\n\n'));
            return digest;
        } catch (e: any) {
            console.error('[DigestEngine] LLM summarization failed, returning raw digest:', e.message);
            return DigestEngine.formatRawDigest(grouped, sectionConfig);
        }
    }

    /**
     * Use LLM to produce a polished, structured digest.
     */
    private static async summarizeWithLLM(rawData: string): Promise<string> {
        const provider = getProvider();
        const today = new Date().toLocaleDateString('en-US', {
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
        });

        const systemPrompt = `You are a concise executive briefing writer. Your job is to take raw automated monitoring results and produce a clean, scannable daily digest.

RULES:
- Use emoji section headers (📊 MARKETS, ⚠️ ALERTS, 🔍 MONITORING, 📋 GENERAL)
- Keep each section to 2-4 bullet points maximum
- Highlight anomalies and actionable items in bold
- If monitoring shows "no issues", summarize as "✅ All clear" in one line
- Strip redundant data — the user wants signal, not noise
- Total output must be under 2000 characters for WhatsApp readability
- Start with a greeting line: "☀️ *Daily Digest — ${today}*"
- End with a one-line sentiment: e.g. "Overall: 🟢 Quiet day" or "Overall: 🟡 Heads up on markets"`;

        const messages = [
            { role: 'system' as const, content: systemPrompt },
            { role: 'user' as const, content: `Here are the raw monitoring results from the last 24 hours. Compile them into a clean daily digest:\n\n${rawData}` },
        ];

        const response = await provider.generateResponse(messages, 'digest-engine');

        // Extract just the text content
        if (typeof response === 'string') return response;
        return String(response);
    }

    /**
     * Fallback: format a raw digest without LLM if summarization fails.
     */
    private static formatRawDigest(
        grouped: Record<string, CronLogEntry[]>,
        sections: DigestConfig['sections']
    ): string {
        const today = new Date().toLocaleDateString('en-US', {
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
        });
        const parts: string[] = [`☀️ *Daily Digest — ${today}*\n`];

        if (sections.markets && grouped.markets!.length > 0) {
            parts.push('📊 *MARKETS*');
            for (const log of grouped.markets!) {
                parts.push(`• ${log.jobName}: ${log.result.substring(0, 200).replace(/\n/g, ' ')}`);
            }
            parts.push('');
        }

        if (sections.alerts && grouped.alerts!.length > 0) {
            parts.push('⚠️ *ALERTS*');
            for (const log of grouped.alerts!) {
                parts.push(`• ${log.jobName}: ${log.result.substring(0, 200).replace(/\n/g, ' ')}`);
            }
            parts.push('');
        }

        if (sections.monitoring && grouped.monitoring!.length > 0) {
            parts.push('🔍 *MONITORING*');
            for (const log of grouped.monitoring!) {
                const short = log.result.substring(0, 150).replace(/\n/g, ' ');
                const isClean = /no\s+(issues?|outages?|problems?)/i.test(short);
                parts.push(`• ${log.jobName}: ${isClean ? '✅ All clear' : short}`);
            }
            parts.push('');
        }

        if (sections.general && grouped.general!.length > 0) {
            parts.push('📋 *GENERAL*');
            for (const log of grouped.general!) {
                parts.push(`• ${log.jobName}: ${log.result.substring(0, 200).replace(/\n/g, ' ')}`);
            }
            parts.push('');
        }

        parts.push('_Generated automatically by OpenSpider DigestEngine_');
        return parts.join('\n');
    }
}
