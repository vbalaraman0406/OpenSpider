import { LLMProvider, ChatMessage } from '../BaseProvider';

export class OpenAIProvider implements LLMProvider {
    private apiKey: string;
    private model: string;
    private baseUrl: string;

    constructor(apiKey?: string, model?: string, baseUrl?: string) {
        this.apiKey = apiKey || process.env.OPENAI_API_KEY || '';
        this.model = model || process.env.OPENAI_MODEL || 'gpt-4o-mini';
        this.baseUrl = baseUrl || 'https://api.openai.com/v1';
    }

    async generateResponse(messages: ChatMessage[]): Promise<string> {
        const response = await fetch(`${this.baseUrl}/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify({
                model: this.model,
                messages: messages.map(m => ({ role: m.role, content: m.content }))
            })
        });

        if (!response.ok) {
            throw new Error(`OpenAI API Error: ${response.statusText} - ${await response.text()}`);
        }

        const data = await response.json();
        return data.choices[0].message.content;
    }

    async generateStructuredOutputs<T>(
        messages: ChatMessage[],
        schema: Record<string, any>
    ): Promise<T> {
        const response = await fetch(`${this.baseUrl}/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify({
                model: this.model,
                messages: messages.map(m => ({ role: m.role, content: m.content })),
                response_format: { type: 'json_schema', json_schema: { name: 'schema', schema, strict: true } }
            })
        });

        if (!response.ok) {
            throw new Error(`OpenAI Structured Output Error: ${response.statusText} - ${await response.text()}`);
        }

        const data = await response.json();
        try {
            return JSON.parse(data.choices[0].message.content) as T;
        } catch (e) {
            throw new Error(`Failed to parse OpenAI JSON: ${e}`);
        }
    }
}
