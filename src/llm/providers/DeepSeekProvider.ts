import { OpenAIProvider } from './OpenAIProvider';
import { ChatMessage, TokenUsage } from '../BaseProvider';

/**
 * DeepSeek Provider — extends OpenAIProvider for basic chat,
 * but overrides generateStructuredOutputs since DeepSeek doesn't
 * support OpenAI's json_schema response_format.
 * Uses schema-in-prompt + json_object mode instead.
 */
export class DeepSeekProvider extends OpenAIProvider {
    constructor(apiKey: string, model: string) {
        super(apiKey, model, 'https://api.deepseek.com/v1');
    }

    async generateStructuredOutputs<T>(
        messages: ChatMessage[],
        schema: Record<string, any>,
        agentId?: string
    ): Promise<T> {
        // DeepSeek doesn't support json_schema — inject schema into system prompt
        // and use response_format: { type: "json_object" }
        const schemaInstruction = `\n\nYou MUST respond with ONLY a valid JSON object matching this schema:\n${JSON.stringify(schema, null, 2)}\n\nReturn ONLY the JSON — no markdown code fences, no explanation, no text before or after.`;

        const augmentedMessages = messages.map((m, i) => {
            if (m.role === 'system' && i === 0) {
                const content = typeof m.content === 'string' ? m.content : JSON.stringify(m.content);
                return { ...m, content: content + schemaInstruction };
            }
            return m;
        });

        if (!messages.some(m => m.role === 'system')) {
            augmentedMessages.unshift({ role: 'system', content: schemaInstruction.trim() });
        }

        console.log(`[Agent] [DeepSeek] Sending structured generation to ${(this as any).model}...`);

        const response = await fetch(`https://api.deepseek.com/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${(this as any).apiKey}`
            },
            body: JSON.stringify({
                model: (this as any).model,
                messages: augmentedMessages.map(m => ({ role: m.role, content: m.content })),
                response_format: { type: 'json_object' },
                temperature: 0.6,
                max_tokens: 8192
            })
        });

        if (!response.ok) {
            const errBody = await response.text();
            throw new Error(`DeepSeek Structured Output Error (${response.status}): ${response.statusText} - ${errBody}`);
        }

        const data = await response.json() as any;

        if (data.usage) {
            const usage: TokenUsage = {
                promptTokens: data.usage.prompt_tokens || 0,
                completionTokens: data.usage.completion_tokens || 0,
                totalTokens: data.usage.total_tokens || 0
            };
            console.log(JSON.stringify({ type: 'usage', model: (this as any).model, usage, agentId: agentId || 'gateway' }));
        }

        const rawContent = data.choices?.[0]?.message?.content || '';

        try {
            let cleanJSON = rawContent.trim();
            cleanJSON = cleanJSON.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/i, '');
            const jsonMatch = cleanJSON.match(/[\{\[][\s\S]*[\}\]]/);
            if (jsonMatch) {
                cleanJSON = jsonMatch[0];
            }
            if (!cleanJSON) {
                throw new Error('No JSON content found in response');
            }
            return JSON.parse(cleanJSON) as T;
        } catch (e) {
            console.error('[DeepSeek] Failed JSON parse. Raw (first 800 chars):', rawContent.substring(0, 800));
            throw new Error(`Failed to parse DeepSeek JSON response: ${e}`);
        }
    }
}
