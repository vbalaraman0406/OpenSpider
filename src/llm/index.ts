import { LLMProvider } from './BaseProvider';
import { AntigravityProvider } from './providers/AntigravityProvider';
import { OllamaProvider } from './providers/OllamaProvider';
import { OpenAIProvider } from './providers/OpenAIProvider';
import { CustomOpenAIProvider } from './providers/CustomOpenAIProvider';
import { AnthropicProvider } from './providers/AnthropicProvider';
import { AntigravityInternalProvider } from './providers/AntigravityInternalProvider';

export function getProvider(modelNameOverride?: string): LLMProvider {
    const provider = modelNameOverride || process.env.DEFAULT_PROVIDER || 'ollama';

    // Helper to instantiate the actual provider
    const instantiateProvider = (p: string): LLMProvider => {
        switch (p) {
            case 'antigravity':
                return new AntigravityProvider();
            case 'antigravity-internal':
                return new AntigravityInternalProvider();
            case 'ollama':
                return new OllamaProvider();
            case 'openai':
                return new OpenAIProvider();
            case 'anthropic':
                return new AnthropicProvider();
            case 'custom':
                return new CustomOpenAIProvider();
            default:
                console.warn(`Unknown provider ${p}, falling back to Ollama.`);
                return new OllamaProvider();
        }
    };

    const primaryProvider = instantiateProvider(provider);

    // Only wrap the primary provider if a fallback is configured and this isn't already the fallback
    const fallbackModel = process.env.FALLBACK_MODEL;
    if (!fallbackModel || modelNameOverride) {
        return primaryProvider;
    }

    // Proxy the provider to intercept API calls and retry with fallback
    return new Proxy(primaryProvider, {
        get(target, prop, receiver) {
            const origMethod = target[prop as keyof LLMProvider];
            if (typeof origMethod === 'function') {
                return async function (...args: any[]) {
                    try {
                        return await (origMethod as Function).apply(target, args);
                    } catch (error: any) {
                        console.warn(`\n⚠️ [Agent] Primary model failed: ${error.message}`);
                        console.log(`[Agent] Retrying with Fallback Model: ${fallbackModel}...`);

                        // We assume FALLBACK_MODEL is a string like 'gemini-2.5-flash'.
                        // For simplicity, we just use the AntigravityProvider for the fallback if 
                        // it looks like a Gemini model, OpenAI for gpt, Anthropic for claude, etc.
                        let fallbackProviderName = 'ollama';
                        if (fallbackModel.includes('gemini') || fallbackModel.includes('learnlm')) fallbackProviderName = 'antigravity';
                        else if (fallbackModel.includes('claude-opus-4-6') || fallbackModel.includes('thinking')) fallbackProviderName = 'antigravity-internal';
                        else if (fallbackModel.includes('gpt') || fallbackModel.includes('o1') || fallbackModel.includes('o3')) fallbackProviderName = 'openai';
                        else if (fallbackModel.includes('claude')) fallbackProviderName = 'anthropic';

                        // Temporarily set the environment variable so the fallback provider picks it up
                        const originalEnvMap: Record<string, string | undefined> = {
                            gemini: process.env.GEMINI_MODEL,
                            openai: process.env.OPENAI_MODEL,
                            anthropic: process.env.ANTHROPIC_MODEL,
                            ollama: process.env.OLLAMA_MODEL
                        };

                        if (fallbackProviderName === 'antigravity' || fallbackProviderName === 'antigravity-internal') process.env.GEMINI_MODEL = fallbackModel;
                        if (fallbackProviderName === 'openai') process.env.OPENAI_MODEL = fallbackModel;
                        if (fallbackProviderName === 'anthropic') process.env.ANTHROPIC_MODEL = fallbackModel;
                        if (fallbackProviderName === 'ollama') process.env.OLLAMA_MODEL = fallbackModel;

                        const fallbackProvider = instantiateProvider(fallbackProviderName);

                        try {
                            // Retry the exact same method on the fallback provider
                            const fallbackMethod = fallbackProvider[prop as keyof LLMProvider];
                            return await (fallbackMethod as Function).apply(fallbackProvider, args);
                        } finally {
                            // Restore original env vars
                            if (fallbackProviderName === 'antigravity' || fallbackProviderName === 'antigravity-internal') process.env.GEMINI_MODEL = originalEnvMap.gemini;
                            if (fallbackProviderName === 'openai') process.env.OPENAI_MODEL = originalEnvMap.openai;
                            if (fallbackProviderName === 'anthropic') process.env.ANTHROPIC_MODEL = originalEnvMap.anthropic;
                            if (fallbackProviderName === 'ollama') process.env.OLLAMA_MODEL = originalEnvMap.ollama;
                        }
                    }
                };
            }
            return Reflect.get(target, prop, receiver);
        }
    });
}
