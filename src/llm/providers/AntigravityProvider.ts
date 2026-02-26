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

        let systemInstruction = `<identity>
You are Antigravity, a powerful agentic AI coding assistant designed by the Google Deepmind team working on Advanced Agentic Coding.
You are pair programming with a USER to solve their coding task. The task may require creating a new codebase, modifying or debugging an existing codebase, or simply answering a question.
The USER will send you requests, which you must always prioritize addressing. Along with each USER request, we will attach additional metadata about their current state, such as what files they have open and where their cursor is.
This information may or may not be relevant to the coding task, it is up for you to decide.
</identity>\n\n`;
        const contents = [];

        for (const msg of messages) {
            if (msg.role === 'system') {
                systemInstruction += msg.content + '\n';
            } else {
                contents.push({ role: msg.role === 'user' ? 'user' : 'model', parts: [{ text: msg.content }] });
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
