export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

export interface LLMProvider {
    /**
     * Generates a standard conversational response
     */
    generateResponse(messages: ChatMessage[]): Promise<string>;

    /**
     * Generates a structured JSON response based on the provided schema
     */
    generateStructuredOutputs<T>(
        messages: ChatMessage[],
        schema: Record<string, any>
    ): Promise<T>;
}
