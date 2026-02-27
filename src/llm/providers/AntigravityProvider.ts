import { GoogleGenAI } from '@google/genai';
import { LLMProvider, ChatMessage, TokenUsage } from '../BaseProvider';

export class AntigravityProvider implements LLMProvider {
    private client?: GoogleGenAI;
    private model: string;

    constructor() {
        if (process.env.GEMINI_USE_ADC === 'true') {
            console.log("🔒 [Antigravity] Using Google IDE Authentication (Application Default Credentials)");
            this.client = new GoogleGenAI({
                httpOptions: {
                    headers: {
                        'User-Agent': 'Google Antigravity IDE',
                        'x-goog-api-client': 'Google Antigravity IDE'
                    }
                }
            });
        } else if (process.env.VERTEX_PROJECT && process.env.VERTEX_LOCATION) {
            this.client = new GoogleGenAI({
                vertexai: true,
                project: process.env.VERTEX_PROJECT,
                location: process.env.VERTEX_LOCATION,
                httpOptions: {
                    headers: {
                        'User-Agent': 'Google Antigravity IDE',
                        'x-goog-api-client': 'Google Antigravity IDE'
                    }
                }
            });
        } else if (process.env.GEMINI_API_KEY) {
            this.client = new GoogleGenAI({
                apiKey: process.env.GEMINI_API_KEY as string,
                httpOptions: {
                    headers: {
                        'User-Agent': 'Google Antigravity IDE',
                        'x-goog-api-client': 'Google Antigravity IDE'
                    }
                }
            });
        } else {
            console.warn("⚠️ [Antigravity] No authentication method found. Ensure you run 'openspider onboard'.");
        }

        // Use the selected model or fallback
        this.model = process.env.GEMINI_MODEL || 'gemini-2.5-flash';
    }

    private formatMessages(messages: ChatMessage[]) {
        // Standardize to Gemini's expected format if needed,
        // though the SDK handles basic role conversion well.

        let systemInstruction = '';
        const contents = [];

        for (const msg of messages) {
            if (msg.role === 'system') {
                systemInstruction += (typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)) + '\n';
            } else {
                let parts: any[] = [];
                if (Array.isArray(msg.content)) {
                    parts = msg.content.map(p => {
                        if (p.type === 'text') return { text: p.text };
                        if (p.type === 'image_url') {
                            const [mimePart, b64] = p.image_url.url.split(',');
                            const mimeType = mimePart?.split(':')[1]?.split(';')[0] || 'image/jpeg';
                            return { inlineData: { mimeType, data: b64 } };
                        }
                        return null;
                    }).filter(Boolean);
                } else {
                    parts = [{ text: msg.content }];
                }
                contents.push({ role: msg.role === 'user' ? 'user' : 'model', parts });
            }
        }

        return { contents, systemInstruction };
    }

    async generateResponse(messages: ChatMessage[]): Promise<{ text: string, usage?: TokenUsage }> {
        console.log(`[Agent] [Antigravity] Generating response using ${this.model}...`);

        const { contents, systemInstruction } = this.formatMessages(messages);

        const response = await this.client!.models.generateContent({
            model: this.model,
            contents,
            config: {
                ...(systemInstruction ? { systemInstruction } : {})
            }
        });

        const text = response.text || '';

        if (response.usageMetadata) {
            const usage = {
                promptTokens: response.usageMetadata.promptTokenCount || 0,
                completionTokens: response.usageMetadata.candidatesTokenCount || 0,
                totalTokens: response.usageMetadata.totalTokenCount || 0,
            };
            console.log(JSON.stringify({ type: 'usage', model: this.model, usage }));
            return { text, usage };
        }

        return { text };
    }

    async generateStructuredOutputs<T>(
        messages: ChatMessage[],
        schema: Record<string, any>
    ): Promise<T> {

        const { contents, systemInstruction } = this.formatMessages(messages);
        console.log(`[Agent] [Antigravity] Sending structured generation to ${this.model}...`);

        const response = await this.client!.models.generateContent({
            model: this.model,
            contents,
            config: {
                ...(systemInstruction ? { systemInstruction } : {}),
                responseMimeType: 'application/json',
                responseSchema: schema,
            }
        });

        if (response.usageMetadata) {
            const usage = {
                promptTokens: response.usageMetadata.promptTokenCount || 0,
                completionTokens: response.usageMetadata.candidatesTokenCount || 0,
                totalTokens: response.usageMetadata.totalTokenCount || 0,
            };
            console.log(JSON.stringify({ type: 'usage', model: this.model, usage }));
        }

        try {
            if (!response.text) throw new Error("Empty response from Antigravity");
            return JSON.parse(response.text) as T;
        } catch (e) {
            throw new Error(`Failed to parse Antigravity JSON: ${e}`);
        }
    }
}
