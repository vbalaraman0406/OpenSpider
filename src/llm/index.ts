import { LLMProvider } from './BaseProvider';
import { AntigravityProvider } from './providers/AntigravityProvider';
import { OllamaProvider } from './providers/OllamaProvider';
import { OpenAIProvider } from './providers/OpenAIProvider';
import { CustomOpenAIProvider } from './providers/CustomOpenAIProvider';

export function getProvider(): LLMProvider {
    const provider = process.env.DEFAULT_PROVIDER || 'ollama';

    switch (provider) {
        case 'antigravity':
            return new AntigravityProvider();
        case 'ollama':
            return new OllamaProvider();
        case 'openai':
            return new OpenAIProvider();
        case 'custom':
            return new CustomOpenAIProvider();
        default:
            console.warn(`Unknown provider ${provider}, falling back to Ollama.`);
            return new OllamaProvider();
    }
}
