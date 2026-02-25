import { GoogleGenAI } from '@google/genai';
import { LLMProvider, ChatMessage } from '../BaseProvider';

export class AntigravityProvider implements LLMProvider {
    private client: GoogleGenAI;
    private model: string;

    constructor() {
        this.client = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
        // Default to gemini-2.5-flash as it is extremely fast and capable
        this.model = 'gemini-2.5-flash';
    }

    private formatMessages(messages: ChatMessage[]) {
        // Standardize to Gemini's expected format if needed,
        // though the SDK handles basic role conversion well.
        let systemInstruction = '';
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

    async generateResponse(messages: ChatMessage[]): Promise<string> {
        const { contents, systemInstruction } = this.formatMessages(messages);

        const response = await this.client.models.generateContent({
            model: this.model,
            contents,
            config: {
                systemInstruction: systemInstruction || undefined,
            }
        });

        return response.text || '';
    }

    async generateStructuredOutputs<T>(
        messages: ChatMessage[],
        schema: Record<string, any>
    ): Promise<T> {
        const { contents, systemInstruction } = this.formatMessages(messages);

        const response = await this.client.models.generateContent({
            model: this.model,
            contents,
            config: {
                systemInstruction: systemInstruction || undefined,
                responseMimeType: 'application/json',
                responseSchema: schema,
            }
        });

        try {
            if (!response.text) throw new Error("Empty response from Antigravity");
            return JSON.parse(response.text) as T;
        } catch (e) {
            throw new Error(`Failed to parse Antigravity JSON: ${e}`);
        }
    }
}
