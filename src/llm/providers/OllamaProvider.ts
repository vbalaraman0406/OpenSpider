import { Ollama } from 'ollama';
import { LLMProvider, ChatMessage, TokenUsage } from '../BaseProvider';

export class OllamaProvider implements LLMProvider {
    private client: Ollama;
    private model: string;

    constructor() {
        this.client = new Ollama({ host: process.env.OLLAMA_URL || 'http://127.0.0.1:11434' });
        this.model = process.env.OLLAMA_MODEL || 'llama3';
    }

    async generateResponse(messages: ChatMessage[]): Promise<{ text: string, usage?: TokenUsage }> {
        console.log(`[Agent] [Ollama] Generating response using ${this.model}...`);
        const response = await this.client.chat({
            model: this.model,
            messages: messages.map(m => ({ role: m.role, content: m.content })),
        });

        const text = response.message.content;
        let usage: TokenUsage | undefined;

        if (response.prompt_eval_count !== undefined && response.eval_count !== undefined) {
            usage = {
                promptTokens: response.prompt_eval_count,
                completionTokens: response.eval_count,
                totalTokens: response.prompt_eval_count + response.eval_count
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
        console.log(`[Agent] [Ollama] Sending structured generation to ${this.model}...`);
        // Ollama supports structured outputs natively via the `format` parameter.
        const response = await this.client.chat({
            model: this.model,
            messages: messages.map(m => ({ role: m.role, content: m.content })),
            format: schema as any,
        });

        if (response.prompt_eval_count !== undefined && response.eval_count !== undefined) {
            const usage = {
                promptTokens: response.prompt_eval_count,
                completionTokens: response.eval_count,
                totalTokens: response.prompt_eval_count + response.eval_count
            };
            console.log(JSON.stringify({ type: 'usage', model: this.model, usage }));
        }

        try {
            if (!response.message.content) throw new Error("Empty response from Ollama");
            return JSON.parse(response.message.content) as T;
        } catch (e) {
            throw new Error(`Failed to parse Ollama JSON: ${e}`);
        }
    }
}
