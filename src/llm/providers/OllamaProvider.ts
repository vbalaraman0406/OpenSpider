import { Ollama } from 'ollama';
import { LLMProvider, ChatMessage } from '../BaseProvider';

export class OllamaProvider implements LLMProvider {
    private client: Ollama;
    private model: string;

    constructor() {
        this.client = new Ollama({ host: process.env.OLLAMA_URL || 'http://127.0.0.1:11434' });
        this.model = process.env.OLLAMA_MODEL || 'llama3';
    }

    async generateResponse(messages: ChatMessage[]): Promise<string> {
        const response = await this.client.chat({
            model: this.model,
            messages: messages.map(m => ({ role: m.role, content: m.content })),
        });

        return response.message.content;
    }

    async generateStructuredOutputs<T>(
        messages: ChatMessage[],
        schema: Record<string, any>
    ): Promise<T> {
        // Ollama supports structured outputs natively via the `format` parameter.
        const response = await this.client.chat({
            model: this.model,
            messages: messages.map(m => ({ role: m.role, content: m.content })),
            format: schema as any,
        });

        try {
            if (!response.message.content) throw new Error("Empty response from Ollama");
            return JSON.parse(response.message.content) as T;
        } catch (e) {
            throw new Error(`Failed to parse Ollama JSON: ${e}`);
        }
    }
}
