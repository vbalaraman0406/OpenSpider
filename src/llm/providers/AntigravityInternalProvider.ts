import { LLMProvider, ChatMessage, TokenUsage } from '../BaseProvider';
import { loginToAntigravity, AuthState, clearAuthState } from '../../auth/antigravity';
import { randomUUID } from 'crypto';

export class AntigravityInternalProvider implements LLMProvider {
    public providerName = 'antigravity-internal';
    private model: string;
    private authState: AuthState | null = null;

    // Fallback models in priority order — verified against daily-cloudcode-pa endpoint
    private static readonly MODEL_FALLBACKS: string[] = [
        'claude-sonnet-4-5',
        'gemini-2.5-flash',
        'claude-opus-4-6-thinking',
        'gemini-2.5-pro',
    ];

    constructor() {
        this.model = process.env.GEMINI_MODEL || 'claude-sonnet-4-5';
    }

    private async ensureAuth(): Promise<AuthState> {
        if (!this.authState || this.authState.expires < Date.now()) {
            this.authState = await loginToAntigravity();
        }
        if (!this.authState) {
            throw new Error("Failed to initialize Google IDE Authentication state.");
        }
        return this.authState;
    }

    private formatMessages(messages: ChatMessage[]): { contents: any[], systemInstruction?: { parts: { text: string }[] } } {
        let systemText = '';
        const contents = [];

        for (const msg of messages) {
            if (msg.role === 'system') {
                systemText += (typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)) + '\n';
            } else {
                if (Array.isArray(msg.content)) {
                    const parts = msg.content.map(p => {
                        if (p.type === 'text') return { text: p.text };
                        if (p.type === 'image_url') {
                            const [mimePart, b64] = p.image_url.url.split(',');
                            const mimeType = mimePart?.split(':')[1]?.split(';')[0] || 'image/jpeg';
                            return { inlineData: { mimeType, data: b64 } };
                        }
                        return null;
                    }).filter(Boolean);
                    contents.push({ role: msg.role === 'user' ? 'user' : 'model', parts });
                } else {
                    contents.push({ role: msg.role === 'user' ? 'user' : 'model', parts: [{ text: msg.content }] });
                }
            }
        }

        // Use the dedicated systemInstruction field — matches real Antigravity IDE API format
        const result: { contents: any[], systemInstruction?: { parts: { text: string }[] } } = { contents };
        if (systemText.trim()) {
            result.systemInstruction = { parts: [{ text: systemText.trim() }] };
        }
        return result;
    }

    async generateResponse(messages: ChatMessage[], agentId?: string): Promise<{ text: string, usage?: TokenUsage }> {
        console.log(`[Agent] [AntigravityInternal] Generating response using ${this.model}...`);
        let auth = await this.ensureAuth();
        const formatted = this.formatMessages(messages);

        const url = `${auth.endpoint}/v1internal:streamGenerateContent?alt=sse`;

        const requestPayload: any = {
            contents: formatted.contents,
            generationConfig: {
                thinkingConfig: {
                    include_thoughts: true,
                    thinking_budget: 8192
                },
                maxOutputTokens: 64000
            }
        };
        if (formatted.systemInstruction) {
            requestPayload.systemInstruction = formatted.systemInstruction;
        }

        const wrappedBody = {
            project: auth!.projectId,
            model: this.model,
            userAgent: "vscode_cloudshelleditor",
            requestType: "chat",
            requestId: randomUUID(),
            request: requestPayload,
        };

        let response!: Response;
        let streamText = '';
        let attempt = 0;
        const maxAttempts = 5;
        let hasRetriedAuth = false;

        // Log payload size for context bloat monitoring
        const payloadSizeKB = (JSON.stringify(requestPayload).length / 1024).toFixed(1);
        console.log(`[Context] Payload size: ${payloadSizeKB}KB (${formatted.contents.length} parts)`);

        // Highly Optimized Stealth Mode: Add a proactive micro-jitter delay before hitting the internal IDE API
        // This prevents Google from fingerprinting the traffic velocity as a bot script, while keeping latency ultra-low.
        const microJitterMs = Math.floor(Math.random() * (400 - 150 + 1)) + 150;
        await new Promise(r => setTimeout(r, microJitterMs));

        while (attempt < maxAttempts) {
            response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${auth.access}`,
                    'Content-Type': 'application/json',
                    'User-Agent': 'antigravity/1.15.8 darwin/arm64',
                    'X-Goog-Api-Client': 'google-cloud-sdk vscode_cloudshelleditor/0.1',
                    'Client-Metadata': '{"ideType":"IDE_UNSPECIFIED","platform":"PLATFORM_UNSPECIFIED","pluginType":"GEMINI"}',
                    'anthropic-beta': 'interleaved-thinking-2025-05-14'
                },
                body: JSON.stringify(wrappedBody)
            });

            // Read body ONCE immediately — Node 22 native fetch throws "Body already read" if consumed twice
            const responseBody = await response.text();

            if (response.status === 429) {
                const currentModel = wrappedBody.model;
                // 429 RESOURCE_EXHAUSTED is often model-specific quota — switch model after 1 retry
                if (attempt === 0) {
                    // First 429: wait 5s and retry same model once
                    console.warn(`\n⚠️ [Agent] [AntigravityInternal] Rate limit (429) on ${currentModel}. Waiting 5s before retry...`);
                    await new Promise(r => setTimeout(r, 5000));
                } else {
                    // Subsequent 429: quota is model-specific — switch to next fallback model
                    const fallbacks = AntigravityInternalProvider.MODEL_FALLBACKS.filter(m => m !== currentModel);
                    const nextModel = fallbacks[attempt - 1] ?? fallbacks[fallbacks.length - 1] ?? 'gemini-2.5-flash';
                    console.warn(`⚠️  [Antigravity] ${currentModel} quota exhausted (429) — switching to ${nextModel}`);
                    wrappedBody.model = nextModel;
                }
                attempt++;
                continue;
            }

            if (!response.ok) {
                // 401: Token expired — clear stale auth and re-borrow from IDE
                if (response.status === 401 && !hasRetriedAuth) {
                    hasRetriedAuth = true;
                    const failedToken = auth.access.substring(0, 30);
                    console.warn(`⚠️  [Antigravity] 401 Unauthorized — clearing ALL auth caches and re-borrowing from IDE...`);
                    this.authState = null;
                    clearAuthState(); // Wipe .antigravity-auth.json + in-memory cache
                    auth = await this.ensureAuth();
                    if (auth.access.substring(0, 30) === failedToken) {
                        console.error(`[Antigravity] IDE returned same expired token — cannot recover. Is Antigravity IDE open and active?`);
                        throw new Error(`IDE API Error: 401 - Token expired. IDE has no fresh token. Open/restart Antigravity IDE to refresh the session.`);
                    }
                    attempt++;
                    continue;
                }
                // 404: Model not found on this endpoint — switch to next fallback
                if (response.status === 404) {
                    const currentModel = wrappedBody.model;
                    const fallbacks = AntigravityInternalProvider.MODEL_FALLBACKS.filter(m => m !== currentModel);
                    const nextModel = fallbacks[0] ?? 'gemini-2.5-flash';
                    console.warn(`⚠️  [Antigravity] ${currentModel} not found (404) — switching to ${nextModel}`);
                    wrappedBody.model = nextModel;
                    attempt++;
                    continue;
                }
                if (response.status === 503 && responseBody.includes('MODEL_CAPACITY_EXHAUSTED')) {
                    const currentModel = wrappedBody.model;
                    const fallbacks = AntigravityInternalProvider.MODEL_FALLBACKS.filter(m => m !== currentModel);
                    const nextModel = fallbacks[0] ?? 'gemini-2.5-flash';
                    console.warn(`⚠️  [Antigravity] ${currentModel} capacity exhausted — switching to ${nextModel}`);
                    wrappedBody.model = nextModel;
                    attempt++;
                    continue;
                }
                throw new Error(`Internal IDE API Error: ${response.status} - ${responseBody.substring(0, 500)}`);
            }
            streamText = responseBody;
            break;
        }

        if (!streamText) {
            throw new Error(`Internal IDE API Error: Rate limit retries exhausted.`);
        }
        const lines = streamText.split('\n');

        let finalText = "";
        let usage: TokenUsage | undefined;

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const dataStr = line.substring(6).trim();
                    if (!dataStr) continue;
                    const parsed = JSON.parse(dataStr);

                    if (parsed.response?.candidates?.[0]?.content?.parts) {
                        for (const part of parsed.response.candidates[0].content.parts) {
                            if (part.thought) {
                                finalText += part.text;
                            } else if (part.text) {
                                finalText += part.text;
                            }
                        }
                    }

                    if (parsed.response?.usageMetadata) {
                        usage = {
                            promptTokens: parsed.response.usageMetadata.promptTokenCount || 0,
                            completionTokens: parsed.response.usageMetadata.candidatesTokenCount || 0,
                            totalTokens: parsed.response.usageMetadata.totalTokenCount || 0,
                        };
                    }
                } catch (e) { }
            }
        }

        if (usage) {
            console.log(JSON.stringify({ type: 'usage', model: this.model, usage, agentId: agentId || 'gateway' }));
            return { text: finalText, usage };
        }

        return { text: finalText };
    }

    async generateStructuredOutputs<T>(
        messages: ChatMessage[],
        schema: Record<string, any>,
        agentId?: string
    ): Promise<T> {

        console.log(`[Agent] [AntigravityInternal] Sending structured request to ${this.model}...`);
        let auth = await this.ensureAuth();
        const formatted = this.formatMessages(messages);

        if (formatted.contents.length > 0) {
            const lastMsg = formatted.contents[formatted.contents.length - 1]!;
            if (lastMsg.parts && lastMsg.parts.length > 0) {
                const lastPart = lastMsg.parts[0]!;
                if (lastPart.text !== undefined) {
                    lastPart.text += `\n\nYou must return ONLY valid JSON matching this schema: ${JSON.stringify(schema)}`;
                }
            }
        }

        const url = `${auth.endpoint}/v1internal:streamGenerateContent?alt=sse`;

        const requestPayload: any = {
            contents: formatted.contents,
            generationConfig: {
                maxOutputTokens: 8192,
                temperature: 0.1
            }
        };
        if (formatted.systemInstruction) {
            requestPayload.systemInstruction = formatted.systemInstruction;
        }

        const wrappedBody = {
            project: auth!.projectId,
            model: this.model,
            userAgent: "vscode_cloudshelleditor",
            requestType: "chat",
            requestId: randomUUID(),
            request: requestPayload,
        };

        let response!: Response;
        let streamText = '';
        let attempt = 0;
        const maxAttempts = 5;
        let hasRetriedAuth = false;

        // Log payload size for context bloat monitoring
        const payloadSizeKB = (JSON.stringify(requestPayload).length / 1024).toFixed(1);
        console.log(`[Context] Structured payload size: ${payloadSizeKB}KB (${formatted.contents.length} parts)`);

        // Stealth Mode: Add a proactive human-like delay before hitting the internal IDE API
        // to prevent Google from fingerprinting the traffic as an automated bot script.
        const stealthDelayMs = Math.floor(Math.random() * (1500 - 500 + 1)) + 500;
        await new Promise(r => setTimeout(r, stealthDelayMs));

        while (attempt < maxAttempts) {
            response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${auth.access}`,
                    'Content-Type': 'application/json',
                    'User-Agent': 'antigravity/1.15.8 darwin/arm64',
                    'X-Goog-Api-Client': 'google-cloud-sdk vscode_cloudshelleditor/0.1',
                    'Client-Metadata': '{"ideType":"IDE_UNSPECIFIED","platform":"PLATFORM_UNSPECIFIED","pluginType":"GEMINI"}',
                },
                body: JSON.stringify(wrappedBody)
            });

            // Read body ONCE immediately — Node 22 native fetch throws "Body already read" if consumed twice
            const responseBody = await response.text();

            if (response.status === 429) {
                const currentModel = wrappedBody.model;
                if (attempt === 0) {
                    console.warn(`\n⚠️ [Agent] [AntigravityInternal] Rate limit (429) on ${currentModel}. Waiting 5s before retry...`);
                    await new Promise(r => setTimeout(r, 5000));
                } else {
                    const fallbacks = AntigravityInternalProvider.MODEL_FALLBACKS.filter(m => m !== currentModel);
                    const nextModel = fallbacks[attempt - 1] ?? fallbacks[fallbacks.length - 1] ?? 'gemini-2.5-flash';
                    console.warn(`⚠️  [Antigravity] ${currentModel} quota exhausted (429) — switching to ${nextModel}`);
                    wrappedBody.model = nextModel;
                }
                attempt++;
                continue;
            }

            if (!response.ok) {
                // 401: Token expired — clear stale auth and re-borrow from IDE
                if (response.status === 401 && !hasRetriedAuth) {
                    hasRetriedAuth = true;
                    const failedToken = auth.access.substring(0, 30);
                    console.warn(`⚠️  [Antigravity] 401 Unauthorized — clearing ALL auth caches and re-borrowing from IDE...`);
                    this.authState = null;
                    clearAuthState(); // Wipe .antigravity-auth.json + in-memory cache
                    auth = await this.ensureAuth();
                    if (auth.access.substring(0, 30) === failedToken) {
                        console.error(`[Antigravity] IDE returned same expired token — cannot recover. Is Antigravity IDE open and active?`);
                        throw new Error(`IDE API Error: 401 - Token expired. IDE has no fresh token. Open/restart Antigravity IDE to refresh the session.`);
                    }
                    attempt++;
                    continue;
                }
                // 404: Model not found on this endpoint — switch to next fallback
                if (response.status === 404) {
                    const currentModel = wrappedBody.model;
                    const fallbacks = AntigravityInternalProvider.MODEL_FALLBACKS.filter(m => m !== currentModel);
                    const nextModel = fallbacks[0] ?? 'gemini-2.5-flash';
                    console.warn(`⚠️  [Antigravity] ${currentModel} not found (404) — switching to ${nextModel}`);
                    wrappedBody.model = nextModel;
                    attempt++;
                    continue;
                }
                if (response.status === 503 && responseBody.includes('MODEL_CAPACITY_EXHAUSTED')) {
                    const currentModel = wrappedBody.model;
                    const fallbacks = AntigravityInternalProvider.MODEL_FALLBACKS.filter(m => m !== currentModel);
                    const nextModel = fallbacks[0] ?? 'gemini-2.5-flash';
                    console.warn(`⚠️  [Antigravity] ${currentModel} capacity exhausted — switching to ${nextModel}`);
                    wrappedBody.model = nextModel;
                    attempt++;
                    continue;
                }
                throw new Error(`Internal IDE API Error: ${response.status} - ${responseBody.substring(0, 500)}`);
            }
            streamText = responseBody;
            break;
        }

        if (!streamText) {
            throw new Error(`Internal IDE API Error: Rate limit retries exhausted.`);
        }
        const lines = streamText.split('\n');

        let finalText = "";
        let usage: TokenUsage | undefined;

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const dataStr = line.substring(6).trim();
                    if (!dataStr) continue;
                    const parsed = JSON.parse(dataStr);

                    if (parsed.response?.candidates?.[0]?.content?.parts) {
                        for (const part of parsed.response.candidates[0].content.parts) {
                            if (part.text) finalText += part.text;
                        }
                    }

                    if (parsed.response?.usageMetadata) {
                        usage = {
                            promptTokens: parsed.response.usageMetadata.promptTokenCount || 0,
                            completionTokens: parsed.response.usageMetadata.candidatesTokenCount || 0,
                            totalTokens: parsed.response.usageMetadata.totalTokenCount || 0,
                        };
                    }
                } catch (e) { }
            }
        }

        if (usage) {
            console.log(JSON.stringify({ type: 'usage', model: this.model, usage, agentId: agentId || 'gateway' }));
        }

        try {
            // Evaluate and extract via AST string tokenization bypass
            const extractAndRepair = (text: string) => {
                const { jsonrepair } = require('jsonrepair');

                // 1. AST string tokenization bypass
                // We bypass AST vulnerabilities by explicitly extracting all top-level keys
                try {
                    const cleanJSON = text.trim();
                    const firstBrace = cleanJSON.indexOf('{');
                    const lastBrace = cleanJSON.lastIndexOf('}');
                    let jsonStr = cleanJSON.substring(firstBrace, lastBrace + 1);

                    // Regex to broadly capture standard agent keys
                    const keys = ["thought", "action", "command", "target", "args", "filename", "content", "message", "to", "subject", "body", "summary_of_findings", "result"];

                    const extracted: Record<string, string> = {};

                    for (const key of keys) {
                        const keyMatch = new RegExp(`"${key}"\\s*:\\s*"([\\s\\S]*?)"(?:\\s*,\\s*"[A-Za-z_]+"|\\s*})`, 'i').exec(jsonStr);
                        if (keyMatch && keyMatch[1]) {
                            let rawValue = keyMatch[1];
                            rawValue = rawValue.replace(/(?<!\\)"/g, '\\"');
                            rawValue = rawValue.replace(/\n/g, '\\n').replace(/\r/g, '\\r').replace(/\t/g, '\\t');
                            extracted[key] = rawValue;
                        }
                    }

                    if (Object.keys(extracted).length === 0) throw new Error("No keys matched regex");

                    const rebuiltParts = Object.entries(extracted).map(([k, v]) => `"${k}": "${v}"`);
                    const rebuiltJSON = `{ ${rebuiltParts.join(", ")} }`;

                    return JSON.parse(rebuiltJSON) as T;
                } catch (e) {
                    // Ultimate fallback
                    const cleanJSON = text.trim();
                    const firstBrace = cleanJSON.indexOf('{');
                    const lastBrace = cleanJSON.lastIndexOf('}');
                    let jsonStr = cleanJSON.substring(firstBrace, lastBrace + 1);
                    return JSON.parse(jsonrepair(jsonStr)) as T;
                }
            };

            return extractAndRepair(finalText);
        } catch (e) {
            console.error("Failed JSON parse:", finalText);
            throw new Error(`Failed to parse Internal IDE JSON: ${e}`);
        }
    }
}
