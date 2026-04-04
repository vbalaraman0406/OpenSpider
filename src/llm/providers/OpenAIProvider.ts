import { LLMProvider, ChatMessage, TokenUsage } from '../BaseProvider';

/**
 * OpenAI Structured Outputs require on every object schema:
 *  1. `additionalProperties: false`
 *  2. `required` must list every key in `properties`
 * This helper enforces both rules recursively.
 * Only used by OpenAIProvider — does not affect Antigravity/Gemini providers.
 */
function enforceAdditionalProperties(schema: Record<string, any>): Record<string, any> {
    if (typeof schema !== 'object' || schema === null) return schema;
    const result: Record<string, any> = { ...schema };
    if (result.type === 'object' || result.properties) {
        result.additionalProperties = false;
        if (result.properties) {
            // All property keys must be in required[]
            result.required = Object.keys(result.properties);
            result.properties = Object.fromEntries(
                Object.entries(result.properties).map(([k, v]) => [k, enforceAdditionalProperties(v as Record<string, any>)])
            );
        }
    }
    if (result.items) result.items = enforceAdditionalProperties(result.items);
    if (result.anyOf) result.anyOf = (result.anyOf as any[]).map(enforceAdditionalProperties);
    if (result.oneOf) result.oneOf = (result.oneOf as any[]).map(enforceAdditionalProperties);
    if (result.allOf) result.allOf = (result.allOf as any[]).map(enforceAdditionalProperties);
    return result;
}



export class OpenAIProvider implements LLMProvider {
    private apiKey: string;
    private model: string;
    private baseUrl: string;

    constructor(apiKey?: string, model?: string, baseUrl?: string) {
        this.apiKey = apiKey || process.env.OPENAI_API_KEY || '';
        this.model = model || process.env.OPENAI_MODEL || 'gpt-4o-mini';
        this.baseUrl = baseUrl || 'https://api.openai.com/v1';
    }

    async generateResponse(messages: ChatMessage[], agentId?: string, sessionKey?: string): Promise<{ text: string, usage?: TokenUsage }> {
        console.log(`[Agent] [OpenAI] Generating response using ${this.model}...`);
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
        const text = data.choices[0].message.content;
        let usage: TokenUsage | undefined;

        if (data.usage) {
            usage = {
                promptTokens: data.usage.prompt_tokens || 0,
                completionTokens: data.usage.completion_tokens || 0,
                totalTokens: data.usage.total_tokens || 0
            };
            console.log(JSON.stringify({ type: 'usage', model: this.model, usage, agentId: agentId || 'gateway', sessionKey: sessionKey || 'main' }));
            return { text, usage };
        }

        return { text };
    }

    async generateStructuredOutputs<T>(
        messages: ChatMessage[],
        schema: Record<string, any>,
        agentId?: string,
        sessionKey?: string
    ): Promise<T> {
        console.log(`[Agent] [OpenAI] Sending structured generation to ${this.model}...`);

        // OpenAI requires additionalProperties: false on every object in the schema
        const strictSchema = enforceAdditionalProperties(schema);

        const response = await fetch(`${this.baseUrl}/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify({
                model: this.model,
                messages: messages.map(m => ({ role: m.role, content: m.content })),
                response_format: { type: 'json_schema', json_schema: { name: 'schema', schema: strictSchema, strict: true } }
            })
        });

        if (!response.ok) {
            throw new Error(`OpenAI Structured Output Error: ${response.statusText} - ${await response.text()}`);
        }

        const data = await response.json();
        if (data.usage) {
            const usage = {
                promptTokens: data.usage.prompt_tokens || 0,
                completionTokens: data.usage.completion_tokens || 0,
                totalTokens: data.usage.total_tokens || 0
            };
            console.log(JSON.stringify({ type: 'usage', model: this.model, usage, agentId: agentId || 'gateway', sessionKey: sessionKey || 'main' }));
        }

        try {
            return JSON.parse(data.choices[0].message.content) as T;
        } catch (e) {
            throw new Error(`Failed to parse OpenAI JSON: ${e}`);
        }
    }
}
