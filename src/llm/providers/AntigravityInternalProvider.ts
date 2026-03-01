import { LLMProvider, ChatMessage, TokenUsage } from '../BaseProvider';
import { loginToAntigravity, AuthState } from '../../auth/antigravity';
import { randomUUID } from 'crypto';

export class AntigravityInternalProvider implements LLMProvider {
    public providerName = 'antigravity-internal';
    private model: string;
    private authState: AuthState | null = null;

    constructor() {
        this.model = process.env.GEMINI_MODEL || 'claude-opus-4-6-thinking';
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

    private formatMessages(messages: ChatMessage[]) {
        let systemInstruction = '';

        const contents = [];

        for (const msg of messages) {
            if (msg.role === 'system') {
                systemInstruction += (typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)) + '\n';
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

        if (systemInstruction) {
            let injected = false;
            if (contents.length > 0 && contents[0]!.role === 'user') {
                const firstUser = contents[0]!;
                if (firstUser.parts && firstUser.parts.length > 0) {
                    const firstPart = firstUser.parts[0]!;
                    if (firstPart.text !== undefined) {
                        firstPart.text = systemInstruction + firstPart.text;
                        injected = true;
                    }
                }
            }
            if (!injected) {
                contents.unshift({ role: 'user', parts: [{ text: systemInstruction + "Please acknowledge." }] });
                contents.unshift({ role: 'model', parts: [{ text: "Acknowledged." }] });
            }
        }

        return contents;
    }

    async generateResponse(messages: ChatMessage[], agentId?: string): Promise<{ text: string, usage?: TokenUsage }> {
        console.log(`[Agent] [AntigravityInternal] Generating response using ${this.model}...`);
        const auth = await this.ensureAuth();
        const contents = this.formatMessages(messages);

        const url = `${auth.endpoint}/v1internal:streamGenerateContent?alt=sse`;

        const requestPayload = {
            contents,
            generationConfig: {
                thinkingConfig: {
                    include_thoughts: true,
                    thinking_budget: 16384
                },
                maxOutputTokens: 64000
            }
        };

        const wrappedBody = {
            project: auth!.projectId,
            model: this.model,
            userAgent: "vscode_cloudshelleditor",
            requestType: "chat",
            requestId: randomUUID(),
            request: requestPayload,
        };

        let response: Response | undefined;
        let attempt = 0;
        const maxAttempts = 5;

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
                    'anthropic-beta': 'interleaved-thinking-2025-05-14'
                },
                body: JSON.stringify(wrappedBody)
            });

            if (response.status === 429) {
                const errBody = await response.text();
                let sleepMs = 2000; // Default 2 second fallback

                try {
                    const errData = JSON.parse(errBody);
                    // Extract quotaResetDelay from the highly nested cloudcode-pa.googleapis.com metadata
                    const details = errData.error?.details || [];
                    for (const detail of details) {
                        if (detail.metadata?.quotaResetDelay) {
                            const delayStr = detail.metadata.quotaResetDelay; // "974.96105ms" or "1.5s"
                            if (delayStr.endsWith('ms')) {
                                sleepMs = parseFloat(delayStr);
                            } else if (delayStr.endsWith('s')) {
                                sleepMs = parseFloat(delayStr) * 1000;
                            }
                        } else if (detail.retryDelay) {
                            const delayStr = detail.retryDelay; // "0.974961050s"
                            if (delayStr.endsWith('s')) {
                                sleepMs = parseFloat(delayStr) * 1000;
                            }
                        }
                    }
                } catch (e) { }

                console.warn(`\n⚠️ [Agent] [AntigravityInternal] Rate limit exceeded (429). Sleeping for ${Math.ceil(sleepMs / 1000)}s before retry ${attempt + 1}/${maxAttempts}...`);
                await new Promise(r => setTimeout(r, sleepMs + 250)); // Add 250ms buffer
                attempt++;
                continue;
            }

            if (!response.ok) {
                const errBody = await response.text();
                throw new Error(`Internal IDE API Error: ${response.status} - ${errBody}`);
            }
            break;
        }

        if (!response) {
            throw new Error(`Internal IDE API Error: Rate limit retries exhausted.`);
        }

        const streamText = await response.text();
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
        const auth = await this.ensureAuth();
        const contents = this.formatMessages(messages);

        if (contents.length > 0) {
            const lastMsg = contents[contents.length - 1]!;
            if (lastMsg.parts && lastMsg.parts.length > 0) {
                const lastPart = lastMsg.parts[0]!;
                if (lastPart.text !== undefined) {
                    lastPart.text += `\n\nYou must return ONLY valid JSON matching this schema: ${JSON.stringify(schema)}`;
                }
            }
        }

        const url = `${auth.endpoint}/v1internal:streamGenerateContent?alt=sse`;

        const requestPayload = {
            contents,
            generationConfig: {
                maxOutputTokens: 8192,
                temperature: 0.1
            }
        };

        const wrappedBody = {
            project: auth!.projectId,
            model: this.model,
            userAgent: "vscode_cloudshelleditor",
            requestType: "chat",
            requestId: randomUUID(),
            request: requestPayload,
        };

        let response: Response | undefined;
        let attempt = 0;
        const maxAttempts = 5;

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

            if (response.status === 429) {
                const errBody = await response.text();
                let sleepMs = 2000; // Default 2 second fallback

                try {
                    const errData = JSON.parse(errBody);
                    // Extract quotaResetDelay from the highly nested cloudcode-pa.googleapis.com metadata
                    const details = errData.error?.details || [];
                    for (const detail of details) {
                        if (detail.metadata?.quotaResetDelay) {
                            const delayStr = detail.metadata.quotaResetDelay; // "974.96105ms" or "1.5s"
                            if (delayStr.endsWith('ms')) {
                                sleepMs = parseFloat(delayStr);
                            } else if (delayStr.endsWith('s')) {
                                sleepMs = parseFloat(delayStr) * 1000;
                            }
                        } else if (detail.retryDelay) {
                            const delayStr = detail.retryDelay; // "0.974961050s"
                            if (delayStr.endsWith('s')) {
                                sleepMs = parseFloat(delayStr) * 1000;
                            }
                        }
                    }
                } catch (e) { }

                console.warn(`\n⚠️ [Agent] [AntigravityInternal] Rate limit exceeded (429). Sleeping for ${Math.ceil(sleepMs / 1000)}s before retry ${attempt + 1}/${maxAttempts}...`);
                await new Promise(r => setTimeout(r, sleepMs + 250)); // Add 250ms buffer
                attempt++;
                continue;
            }

            if (!response.ok) {
                const errBody = await response.text();
                throw new Error(`Internal IDE API Error: ${response.status} - ${errBody}`);
            }
            break;
        }

        if (!response) {
            throw new Error(`Internal IDE API Error: Rate limit retries exhausted.`);
        }

        const streamText = await response.text();
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
