import Anthropic from '@anthropic-ai/sdk';
import { LLMProvider, ChatMessage, TokenUsage } from '../BaseProvider';

export class AnthropicProvider implements LLMProvider {
    private client: Anthropic;
    private model: string;

    constructor() {
        this.client = new Anthropic({
            apiKey: process.env.ANTHROPIC_API_KEY as string,
        });
        this.model = process.env.ANTHROPIC_MODEL || 'claude-3-5-sonnet-20241022';
    }

    private formatMessages(messages: ChatMessage[]) {
        let systemInstruction = '';
        const formattedMessages: Anthropic.MessageParam[] = [];

        for (const msg of messages) {
            if (msg.role === 'system') {
                systemInstruction += (typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)) + '\n';
            } else {
                let formattedContent: any = msg.content;
                if (Array.isArray(msg.content)) {
                    formattedContent = msg.content.map(p => {
                        if (p.type === 'text') return { type: 'text', text: p.text };
                        if (p.type === 'image_url') {
                            const [mimePart, b64] = p.image_url.url.split(',');
                            const mimeType = (mimePart?.split(':')[1]?.split(';')[0] || 'image/jpeg') as any;
                            return { type: 'image', source: { type: 'base64', media_type: mimeType, data: b64 } };
                        }
                        return p;
                    });
                }

                formattedMessages.push({
                    role: msg.role === 'user' ? 'user' : 'assistant',
                    content: formattedContent
                });
            }
        }

        return { formattedMessages, systemInstruction };
    }

    async generateResponse(messages: ChatMessage[], agentId?: string, sessionKey?: string): Promise<{ text: string, usage?: TokenUsage }> {
        console.log(`[Agent] [Anthropic] Generating response using ${this.model}...`);
        const { formattedMessages, systemInstruction } = this.formatMessages(messages);

        const response = await this.client.messages.create({
            model: this.model,
            max_tokens: 8192,
            ...(systemInstruction ? { system: systemInstruction } : {}),
            messages: formattedMessages,
        });

        // The first block is usually text
        const textBlock = response.content.find(block => block.type === 'text');
        const text = textBlock && textBlock.type === 'text' ? textBlock.text : '';

        let usage: TokenUsage | undefined;
        if (response.usage) {
            usage = {
                promptTokens: response.usage.input_tokens,
                completionTokens: response.usage.output_tokens,
                totalTokens: response.usage.input_tokens + response.usage.output_tokens,
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
        console.log(`[Agent] [Anthropic] Sending structured generation to ${this.model}...`);
        const { formattedMessages, systemInstruction } = this.formatMessages(messages);

        // Anthropic structured output using tool_choice
        const response = await this.client.messages.create({
            model: this.model,
            max_tokens: 8192,
            ...(systemInstruction ? { system: systemInstruction } : {}),
            messages: formattedMessages,
            tools: [{
                name: 'generate_structured_response',
                description: 'Generate the final response as a structured object',
                // Explicitly cast to unknown then object, as the official SDK expects JSONSchema
                input_schema: schema as Anthropic.Tool.InputSchema
            }],
            tool_choice: { type: 'tool', name: 'generate_structured_response' }
        });

        if (response.usage) {
            const usage = {
                promptTokens: response.usage.input_tokens,
                completionTokens: response.usage.output_tokens,
                totalTokens: response.usage.input_tokens + response.usage.output_tokens,
            };
            console.log(JSON.stringify({ type: 'usage', model: this.model, usage, agentId: agentId || 'gateway', sessionKey: sessionKey || 'main' }));
        }

        const toolCall = response.content.find(block => block.type === 'tool_use');

        if (!toolCall || toolCall.type !== 'tool_use') {
            throw new Error("Anthropic Structured Output Error: Did not return a tool call");
        }

        try {
            // In the official SDK, input is returned as an object directly (not a string)
            return toolCall.input as T;
        } catch (e) {
            throw new Error(`Failed to extract Anthropic JSON: ${e}`);
        }
    }
}
