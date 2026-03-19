import { LLMProvider, ChatMessage, TokenUsage } from '../BaseProvider';

/**
 * NVIDIA NIM Provider — OpenAI-compatible API at integrate.api.nvidia.com
 * Used as a backup/fallback when the primary model hits rate limits or errors.
 *
 * Supports structured JSON output via system prompt injection + manual parsing
 * (NVIDIA models may not support OpenAI's strict JSON schema mode).
 */
export class NvidiaProvider implements LLMProvider {
    private apiKey: string;
    private model: string;
    private baseUrl: string;

    constructor(apiKey: string, model: string) {
        this.apiKey = apiKey;
        this.model = model;
        this.baseUrl = 'https://integrate.api.nvidia.com/v1';
    }

    async generateResponse(messages: ChatMessage[], agentId?: string): Promise<{ text: string, usage?: TokenUsage }> {
        console.log(`[Agent] [NVIDIA] Generating response using ${this.model}...`);

        const response = await fetch(`${this.baseUrl}/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify({
                model: this.model,
                messages: messages.map(m => ({ role: m.role, content: m.content })),
                temperature: 0.6,
                top_p: 0.95,
                max_tokens: 4096
            })
        });

        if (!response.ok) {
            const errBody = await response.text();
            throw new Error(`NVIDIA API Error (${response.status}): ${response.statusText} - ${errBody}`);
        }

        const data = await response.json();
        const text = data.choices?.[0]?.message?.content || '';
        if (data.usage) {
            const usage: TokenUsage = {
                promptTokens: data.usage.prompt_tokens || 0,
                completionTokens: data.usage.completion_tokens || 0,
                totalTokens: data.usage.total_tokens || 0
            };
            console.log(JSON.stringify({ type: 'usage', model: this.model, usage, agentId: agentId || 'gateway' }));
            return { text, usage };
        }

        return { text };
    }

    async generateStructuredOutputs<T>(
        messages: ChatMessage[],
        schema: Record<string, any>,
        agentId?: string
    ): Promise<T> {
        console.log(`[Agent] [NVIDIA] Sending structured generation to ${this.model}...`);

        // NVIDIA models may not support OpenAI's strict JSON schema mode.
        // Instead, we inject the schema into the system prompt and request JSON output,
        // then parse the response manually — same strategy as the Antigravity/Gemini provider.
        const schemaInstruction = `\n\nYou MUST respond with ONLY a valid JSON object matching this schema:\n${JSON.stringify(schema, null, 2)}\n\nReturn ONLY the JSON — no markdown code fences, no explanation, no text before or after.`;

        const augmentedMessages = messages.map((m, i) => {
            if (m.role === 'system' && i === 0) {
                const content = typeof m.content === 'string' ? m.content : JSON.stringify(m.content);
                return { ...m, content: content + schemaInstruction };
            }
            return m;
        });

        // If no system message exists, prepend one with the schema
        if (!messages.some(m => m.role === 'system')) {
            augmentedMessages.unshift({ role: 'system', content: schemaInstruction.trim() });
        }

        const response = await fetch(`${this.baseUrl}/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify({
                model: this.model,
                messages: augmentedMessages.map(m => ({ role: m.role, content: m.content })),
                temperature: 0.6,
                top_p: 0.95,
                max_tokens: 16384
            })
        });

        if (!response.ok) {
            const errBody = await response.text();
            throw new Error(`NVIDIA Structured Output Error (${response.status}): ${response.statusText} - ${errBody}`);
        }

        const data = await response.json();

        if (data.usage) {
            const usage = {
                promptTokens: data.usage.prompt_tokens || 0,
                completionTokens: data.usage.completion_tokens || 0,
                totalTokens: data.usage.total_tokens || 0
            };
            console.log(JSON.stringify({ type: 'usage', model: this.model, usage, agentId: agentId || 'gateway' }));
        }

        const rawContent = data.choices?.[0]?.message?.content || '';

        try {
            // Strip <think>...</think> reasoning tags that Nemotron models emit
            let cleanJSON = rawContent.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
            // Remove markdown code fences if present
            cleanJSON = cleanJSON.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/i, '');
            // Extract first JSON object or array (fixed regex: [\s\S] not [\\s\S])
            const jsonMatch = cleanJSON.match(/[\{\[][\s\S]*[\}\]]/);
            if (jsonMatch) {
                cleanJSON = jsonMatch[0];
            }
            if (!cleanJSON) {
                throw new Error('No JSON content found in response');
            }
            return JSON.parse(cleanJSON) as T;
        } catch (e) {
            console.error('[NVIDIA] Failed JSON parse. Raw response (first 800 chars):', rawContent.substring(0, 800));
            throw new Error(`Failed to parse NVIDIA JSON response: ${e}`);
        }
    }
}
