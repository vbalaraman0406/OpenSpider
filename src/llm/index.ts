import { LLMProvider } from './BaseProvider';
import { AntigravityProvider } from './providers/AntigravityProvider';
import { OllamaProvider } from './providers/OllamaProvider';
import { OpenAIProvider } from './providers/OpenAIProvider';
import { CustomOpenAIProvider } from './providers/CustomOpenAIProvider';
import { AnthropicProvider } from './providers/AnthropicProvider';
import { AntigravityInternalProvider } from './providers/AntigravityInternalProvider';
import { NvidiaProvider } from './providers/NvidiaProvider';
import { DeepSeekProvider } from './providers/DeepSeekProvider';

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
            case 'nvidia-1': {
                const k = process.env.NVIDIA_API_KEY_1;
                const m = process.env.NVIDIA_MODEL_1;
                if (k && m) return new NvidiaProvider(k, m);
                console.warn('nvidia-1 requested but NVIDIA_API_KEY_1/NVIDIA_MODEL_1 not set. Falling back to Ollama.');
                return new OllamaProvider();
            }
            case 'nvidia-2': {
                const k = process.env.NVIDIA_API_KEY_2;
                const m = process.env.NVIDIA_MODEL_2;
                if (k && m) return new NvidiaProvider(k, m);
                console.warn('nvidia-2 requested but NVIDIA_API_KEY_2/NVIDIA_MODEL_2 not set. Falling back to Ollama.');
                return new OllamaProvider();
            }
            case 'deepseek': {
                const k = process.env.DEEPSEEK_API_KEY;
                const m = process.env.DEEPSEEK_MODEL || 'deepseek-chat';
                if (k) return new DeepSeekProvider(k, m);
                console.warn('deepseek requested but DEEPSEEK_API_KEY not set. Falling back to Ollama.');
                return new OllamaProvider();
            }
            default:
                console.warn(`Unknown provider ${p}, falling back to Ollama.`);
                return new OllamaProvider();
        }
    };

    const primaryProvider = instantiateProvider(provider);

    // If this is an explicit override (e.g. a fallback being instantiated), skip chaining
    if (modelNameOverride) {
        return primaryProvider;
    }

    // ═══════════════════════════════════════════════════════════════
    // MULTI-LEVEL FALLBACK CHAIN
    // Build an ordered list of fallback providers to try when the
    // primary fails. Order: FALLBACK_MODEL → NVIDIA 1 → NVIDIA 2
    // ═══════════════════════════════════════════════════════════════
    const fallbackProviders: { provider: LLMProvider; label: string }[] = [];

    // 1. Legacy single-model fallback (FALLBACK_MODEL env var)
    const fallbackModel = process.env.FALLBACK_MODEL;
    if (fallbackModel) {
        let fallbackProviderName = 'ollama';
        if (fallbackModel.includes('gemini') || fallbackModel.includes('learnlm')) fallbackProviderName = 'antigravity';
        else if (fallbackModel.includes('claude-opus-4-6') || fallbackModel.includes('thinking')) fallbackProviderName = 'antigravity-internal';
        else if (fallbackModel.includes('gpt') || fallbackModel.includes('o1') || fallbackModel.includes('o3')) fallbackProviderName = 'openai';
        else if (fallbackModel.includes('claude')) fallbackProviderName = 'anthropic';

        // Temporarily swap the env var so the provider constructor picks up the right model
        const envKeyMap: Record<string, string> = {
            'antigravity': 'GEMINI_MODEL',
            'antigravity-internal': 'GEMINI_MODEL',
            'openai': 'OPENAI_MODEL',
            'anthropic': 'ANTHROPIC_MODEL',
            'ollama': 'OLLAMA_MODEL'
        };
        const envKey = envKeyMap[fallbackProviderName] || '';
        const originalValue = envKey ? process.env[envKey] : undefined;
        if (envKey) process.env[envKey] = fallbackModel;

        try {
            fallbackProviders.push({
                provider: instantiateProvider(fallbackProviderName),
                label: `${fallbackProviderName}/${fallbackModel}`
            });
        } finally {
            // Restore original env var
            if (envKey) {
                if (originalValue !== undefined) {
                    process.env[envKey] = originalValue;
                } else {
                    delete process.env[envKey];
                }
            }
        }
    }

    // 2. DeepSeek Backup Model
    const deepseekKey = process.env.DEEPSEEK_API_KEY;
    const deepseekModel = process.env.DEEPSEEK_MODEL || 'deepseek-chat';
    if (deepseekKey) {
        fallbackProviders.push({
            provider: new DeepSeekProvider(deepseekKey, deepseekModel),
            label: `deepseek/${deepseekModel}`
        });
    }

    // 3. NVIDIA Backup Model 1
    const nvidiaKey1 = process.env.NVIDIA_API_KEY_1;
    const nvidiaModel1 = process.env.NVIDIA_MODEL_1;
    if (nvidiaKey1 && nvidiaModel1) {
        fallbackProviders.push({
            provider: new NvidiaProvider(nvidiaKey1, nvidiaModel1),
            label: `nvidia/${nvidiaModel1}`
        });
    }

    // 3. NVIDIA Backup Model 2
    const nvidiaKey2 = process.env.NVIDIA_API_KEY_2;
    const nvidiaModel2 = process.env.NVIDIA_MODEL_2;
    if (nvidiaKey2 && nvidiaModel2) {
        fallbackProviders.push({
            provider: new NvidiaProvider(nvidiaKey2, nvidiaModel2),
            label: `nvidia/${nvidiaModel2}`
        });
    }

    // If no fallbacks are configured, return the primary directly
    if (fallbackProviders.length === 0) {
        return primaryProvider;
    }

    // Log the fallback chain at startup
    const chainLabels = [`primary/${provider}`, ...fallbackProviders.map(f => f.label)];
    console.log(`[LLM] Fallback chain: ${chainLabels.join(' → ')}`);

    // Proxy the provider to intercept API calls and cascade through fallbacks
    return new Proxy(primaryProvider, {
        get(target, prop, receiver) {
            const origMethod = target[prop as keyof LLMProvider];
            if (typeof origMethod === 'function') {
                return async function (...args: any[]) {
                    // Try primary first
                    try {
                        return await (origMethod as Function).apply(target, args);
                    } catch (primaryError: any) {
                        console.warn(`\n⚠️ [LLM] Primary model failed: ${primaryError.message?.substring(0, 200)}`);

                        // Cascade through fallbacks in order
                        for (let i = 0; i < fallbackProviders.length; i++) {
                            const fb = fallbackProviders[i]!;
                            console.log(`[LLM] Trying fallback ${i + 1}/${fallbackProviders.length}: ${fb.label}...`);

                            try {
                                const fallbackMethod = fb.provider[prop as keyof LLMProvider];
                                if (typeof fallbackMethod === 'function') {
                                    return await (fallbackMethod as Function).apply(fb.provider, args);
                                }
                            } catch (fallbackError: any) {
                                console.warn(`⚠️ [LLM] Fallback ${fb.label} also failed: ${fallbackError.message?.substring(0, 200)}`);
                                // Continue to next fallback
                            }
                        }

                        // All fallbacks exhausted — rethrow the original error
                        console.error(`❌ [LLM] All ${fallbackProviders.length} fallback(s) exhausted. Rethrowing primary error.`);
                        throw primaryError;
                    }
                };
            }
            return Reflect.get(target, prop, receiver);
        }
    });
}
