export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

export interface TokenUsage {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
}

export interface LLMProvider {
    /**
     * Optional string to identify the underlying provider type (e.g. 'antigravity-internal')
     */
    providerName?: string;

    /**
     * Generates a standard conversational response
     */
    generateResponse(messages: ChatMessage[]): Promise<{ text: string, usage?: TokenUsage }>;

    /**
     * Generates a structured JSON response based on the provided schema
     */
    generateStructuredOutputs<T>(
        messages: ChatMessage[],
        schema: Record<string, any>
    ): Promise<T>;
}
