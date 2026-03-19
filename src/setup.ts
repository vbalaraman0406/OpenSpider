import * as p from '@clack/prompts';
import { setTimeout } from 'node:timers/promises';
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import { GoogleGenAI } from '@google/genai';
import { onboardWhatsApp } from './whatsapp';


export async function runSetup() {
  console.clear();

  p.intro(`
   ____                   ____        _     __         
  / __ \\\\____  ___  ____  / __/____   (_)___/ /__  _____
 / / / / __ \\\\/ _ \\\\/ __ \\\\/\\\\ \\\\/ __ \\\\ / / __  / _ \\\\/ ___/
/ /_/ / /_/ /  __/ / / /___/ / /_/ // / /_/ /  __/ /    
\\\\____/ .___/\\\\___/_/ /_//____/ .___//_/\\\\__,_/\\\\___/_/     
    /_/                    /_/                          

🕷️ Welcome to OpenSpider Setup
`);
  const s = p.spinner();
  s.start('Checking environment configuration...');
  await setTimeout(1000);
  s.stop('Environment checked.');

  const rootDir = __dirname.endsWith('src') || __dirname.endsWith('dist') ? path.join(__dirname, '..') : __dirname;
  const envPath = path.join(rootDir, '.env');
  if (fs.existsSync(envPath)) {
    const override = await p.confirm({
      message: 'A .env file already exists. Do you want to overwrite it?',
      initialValue: false,
    });

    if (p.isCancel(override)) {
      p.cancel('Setup cancelled.');
      process.exit(0);
    }
    if (!override) {
      p.outro(`🕷️ Setup complete.Using existing.env file.`);
      return;
    }
  }

  const projectType = await p.select({
    message: 'Which main LLM provider will you use?',
    options: [
      { value: 'antigravity-internal', label: 'Google Antigravity (Internal IDE - Opus Support)', hint: 'Cloud' },
      { value: 'antigravity', label: 'Google Antigravity / Gemini', hint: 'Cloud' },
      { value: 'ollama', label: 'Ollama', hint: 'Local' },
      { value: 'openai', label: 'OpenAI', hint: 'Cloud' },
      { value: 'anthropic', label: 'Anthropic', hint: 'Cloud' },
      { value: 'custom', label: 'Custom OpenAI-compatible', hint: 'e.g. LM Studio' },
    ],
    initialValue: 'antigravity',
  });

  if (p.isCancel(projectType)) {
    p.cancel('Setup cancelled.');
    process.exit(0);
  }

  let envContent = `DEFAULT_PROVIDER=${projectType}\n\n`;

  if (projectType === 'antigravity-internal') {
    s.start('Initiating Internal IDE Authentication Flow...');
    try {
      // We import dynamically to avoid loading open/express if not needed
      const { loginToAntigravity } = require('./auth/antigravity');
      await loginToAntigravity();
      s.stop('Internal IDE Authentication successful!');
      envContent += `GEMINI_MODEL=claude-opus-4-6-thinking\n`;
    } catch (e: any) {
      s.stop(`Internal IDE Auth failed: ${e.message}`);
      console.warn('Continuing setup, but API calls will fail until you complete login.');
    }
  } else if (projectType === 'antigravity') {
    const authMethod = await p.select({
      message: 'How would you like to authenticate with Google Antigravity?',
      options: [
        { value: 'adc', label: 'Google IDE Login (Recommended)', hint: 'Never expires, uses Google Auth' },
        { value: 'apikey', label: 'API Key (Gemini Developer API)', hint: 'Standard' }
      ]
    });

    if (p.isCancel(authMethod)) {
      p.cancel('Setup cancelled.');
      process.exit(0);
    }

    let tempClient: GoogleGenAI | null = null;
    let apiKey = '';
    let vertexProject = '';
    let vertexLocation = '';

    if (authMethod === 'apikey') {
      apiKey = await p.text({
        message: 'Enter your Google Gemini API Key:',
        placeholder: 'AIzaSy...',
        validate(value) {
          if (value.length === 0) return `API Key is required!`;
        },
      }) as string;

      if (p.isCancel(apiKey)) {
        p.cancel('Setup cancelled.');
        process.exit(0);
      }
      envContent += `GEMINI_API_KEY = ${apiKey}\n`;
      tempClient = new GoogleGenAI({
        apiKey,
        httpOptions: {
          headers: {
            'User-Agent': 'Google Antigravity IDE',
            'x-goog-api-client': 'Google Antigravity IDE',
          }
        }
      });
    } else if (authMethod === 'adc') {
      const doAuth = await p.confirm({
        message: 'Do you need to authenticate with Google now? (Runs "gcloud auth application-default login")',
        initialValue: false,
      });

      if (p.isCancel(doAuth)) {
        p.cancel('Setup cancelled.');
        process.exit(0);
      }

      if (doAuth) {
        s.start('Running gcloud auth... Please check your browser.');
        try {
          execSync('gcloud auth application-default login', { stdio: 'inherit' });
          s.stop('Authentication successful.');
        } catch (e: any) {
          s.stop(`Authentication failed: ${e.message}`);
          console.warn('Continuing setup, but Gemini calls may fail if you are not authenticated.');
        }
      }

      envContent += `GEMINI_USE_ADC = true\n`;
      tempClient = new GoogleGenAI({});
    }

    if (tempClient) {
      s.start('Fetching available models from Google...');
      try {
        const resp = await tempClient.models.list();
        s.stop('Models fetched successfully.');

        const modelOptions: { value: string, label: string }[] = [];
        for await (const m of resp) {
          if (m.name) {
            modelOptions.push({
              value: m.name.replace('models/', ''),
              label: m.name.replace('models/', '')
            });
          }
        }

        // Sort with Gemini 2.5 Flash at the top if it exists
        modelOptions.sort((a, b) => {
          if (a.value.includes('gemini-2.5-flash')) return -1;
          if (b.value.includes('gemini-2.5-flash')) return 1;
          return a.value.localeCompare(b.value);
        });

        const selectedModel = await p.select({
          message: 'Choose your default Google Antigravity model:',
          options: modelOptions.length > 0 ? modelOptions : [{ value: 'gemini-2.5-flash', label: 'gemini-2.5-flash' }],
          initialValue: 'gemini-2.5-flash',
        });

        if (p.isCancel(selectedModel)) {
          p.cancel('Setup cancelled.');
          process.exit(0);
        }
        envContent += `GEMINI_MODEL = ${selectedModel}\n`;

      } catch (e: any) {
        s.stop(`Failed to fetch models: ${e.message}`);
        // Fallback
        envContent += `GEMINI_MODEL = gemini-2.5-flash\n`;
        console.log('Falling back to default model: gemini-2.5-flash');
      }
    } else {
      // Assume default model for Cookie auth
      envContent += `GEMINI_MODEL = gemini-2.5-pro\n`;
    }
  }

  if (projectType === 'ollama') {
    const url = await p.text({
      message: 'Enter your Ollama URL (Default: http://127.0.0.1:11434):',
      placeholder: 'http://127.0.0.1:11434',
      initialValue: 'http://127.0.0.1:11434',
    });

    const model = await p.text({
      message: 'Enter your preferred Ollama Model (e.g. qwen2.5-coder:32b, llama3.1):',
      placeholder: 'llama3',
    });

    if (p.isCancel(url) || p.isCancel(model)) {
      p.cancel('Setup cancelled.');
      process.exit(0);
    }
    envContent += `OLLAMA_URL = ${url}\n`;
    envContent += `OLLAMA_MODEL = ${model}\n`;
  }

  if (projectType === 'openai') {
    const key = await p.text({
      message: 'Enter your OpenAI API Key:',
      placeholder: 'sk-...',
      validate(value) { if (!value.startsWith('sk-')) return 'Key should start with sk-'; },
    }) as string;
    if (p.isCancel(key)) { p.cancel('Setup cancelled.'); process.exit(0); }
    envContent += `OPENAI_API_KEY = ${key}\n`;

    // Fetch live models from OpenAI
    s.start('Fetching available models from OpenAI...');
    let openaiModelOptions: { value: string; label: string; hint?: string }[] = [];
    try {
      const resp = await fetch('https://api.openai.com/v1/models', {
        headers: { Authorization: `Bearer ${key}` },
      });
      if (resp.ok) {
        const data: any = await resp.json();
        const gptModels = (data.data as any[])
          .map((m: any) => m.id as string)
          .filter((id: string) => id.startsWith('gpt-') || id.startsWith('o1') || id.startsWith('o3'))
          .sort((a: string, b: string) => b.localeCompare(a)); // newest first
        openaiModelOptions = gptModels.map((id: string) => ({ value: id, label: id }));
      }
      s.stop('Models fetched!');
    } catch (_) {
      s.stop('Could not fetch models — using curated list.');
    }

    if (openaiModelOptions.length === 0) {
      // Fallback curated list
      openaiModelOptions = [
        { value: 'gpt-4o',       label: 'gpt-4o',       hint: 'Recommended — fast & smart' },
        { value: 'gpt-4o-mini',  label: 'gpt-4o-mini',  hint: 'Cheapest' },
        { value: 'gpt-4-turbo',  label: 'gpt-4-turbo',  hint: '128k context' },
        { value: 'gpt-4',        label: 'gpt-4',        hint: 'Original GPT-4' },
        { value: 'o1',           label: 'o1',           hint: 'Deep reasoning' },
        { value: 'o1-mini',      label: 'o1-mini',      hint: 'Cheaper reasoning' },
        { value: 'o3-mini',      label: 'o3-mini',      hint: 'Latest reasoning model' },
      ];
    }

    const selectedOpenAIModel = await p.select({
      message: 'Choose your default OpenAI model:',
      options: openaiModelOptions,
      initialValue: 'gpt-4o',
    });
    if (p.isCancel(selectedOpenAIModel)) { p.cancel('Setup cancelled.'); process.exit(0); }
    envContent += `OPENAI_MODEL = ${selectedOpenAIModel}\n`;
  }

  if (projectType === 'anthropic') {
    const key = await p.text({
      message: 'Enter your Anthropic API Key:',
      placeholder: 'sk-ant-...',
    }) as string;
    if (p.isCancel(key)) { p.cancel('Setup cancelled.'); process.exit(0); }
    envContent += `ANTHROPIC_API_KEY = ${key}\n`;

    const anthropicModels: { value: string; label: string; hint?: string }[] = [
      { value: 'claude-opus-4-5',               label: 'claude-opus-4-5',               hint: 'Most capable' },
      { value: 'claude-3-5-sonnet-20241022',     label: 'claude-3-5-sonnet-20241022',     hint: 'Recommended' },
      { value: 'claude-3-5-haiku-20241022',      label: 'claude-3-5-haiku-20241022',      hint: 'Fastest & cheapest' },
      { value: 'claude-3-opus-20240229',         label: 'claude-3-opus-20240229',         hint: 'Powerful reasoning' },
      { value: 'claude-3-haiku-20240307',        label: 'claude-3-haiku-20240307',        hint: 'Budget' },
    ];

    const selectedAnthropicModel = await p.select({
      message: 'Choose your default Anthropic model:',
      options: anthropicModels,
      initialValue: 'claude-3-5-sonnet-20241022',
    });
    if (p.isCancel(selectedAnthropicModel)) { p.cancel('Setup cancelled.'); process.exit(0); }
    envContent += `ANTHROPIC_MODEL = ${selectedAnthropicModel}\n`;
  }

  if (projectType === 'custom') {
    const url = await p.text({
      message: 'Enter the Custom OpenAI API Base URL:',
      placeholder: 'http://localhost:1234/v1',
    });
    const key = await p.text({
      message: 'Enter API Key (leave blank if none):',
      placeholder: 'Bearer ...',
    });
    const model = await p.text({
      message: 'Enter preferred model name:',
      placeholder: 'local-model',
    });
    if (p.isCancel(url) || p.isCancel(key) || p.isCancel(model)) {
      p.cancel('Setup cancelled.');
      process.exit(0);
    }
    envContent += `CUSTOM_API_URL = ${url}\n`;
    envContent += `CUSTOM_API_KEY = ${key}\n`;
    envContent += `CUSTOM_MODEL = ${model}\n`;
  }

  const persona = await p.text({
    message: 'Define the Agent Persona (e.g. "You are an expert code intelligence who writes clean React."):',
    placeholder: 'You are a helpful multi-agent assistant...',
    initialValue: 'You are a helpful multi-agent assistant designed to write excellent code and utilize terminals.'
  });

  if (p.isCancel(persona)) {
    p.cancel('Setup cancelled.');
    process.exit(0);
  }

  envContent += `AGENT_PERSONA = "${persona}"\n\n`;

  const fallback = await p.text({
    message: 'Enter a Fallback Model to use if the primary model fails (e.g. gpt-4o-mini, gemini-flash), or leave blank for none:',
    placeholder: 'gemini-2.5-flash',
  });

  if (!p.isCancel(fallback) && fallback) {
    envContent += `FALLBACK_MODEL = ${fallback}\n`;
  }

  envContent += await promptForBackupModels();

  const scanQr = await p.confirm({
    message: 'Would you like to connect your WhatsApp account now?',
    initialValue: true,
  });

  if (p.isCancel(scanQr)) {
    p.cancel('Setup cancelled.');
    process.exit(0);
  }

  envContent += `ENABLE_WHATSAPP = ${scanQr}\n`;

  // Auto-generate secure tokens for dashboard and webhook if not already set
  const crypto = require('node:crypto');
  const dashboardKey = process.env.DASHBOARD_API_KEY || crypto.randomBytes(32).toString('hex');
  const hookToken = process.env.OPENSPIDER_HOOK_TOKEN || crypto.randomBytes(32).toString('hex');

  envContent += `DASHBOARD_API_KEY = ${dashboardKey}\n`;
  envContent += `OPENSPIDER_HOOK_TOKEN = ${hookToken}\n\n`;

  // Keys managed by this wizard — these will be freshly set above, so we skip duplicates from old .env
  const WIZARD_MANAGED_KEYS = new Set([
    'DEFAULT_PROVIDER', 'OPENAI_API_KEY', 'OPENAI_MODEL', 'GEMINI_API_KEY', 'GEMINI_MODEL',
    'GEMINI_USE_ADC', 'ANTHROPIC_API_KEY', 'ANTHROPIC_MODEL', 'OLLAMA_MODEL', 'CUSTOM_API_URL',
    'CUSTOM_API_KEY', 'CUSTOM_MODEL', 'AGENT_PERSONA', 'FALLBACK_MODEL', 'ENABLE_WHATSAPP',
    'DASHBOARD_API_KEY', 'OPENSPIDER_HOOK_TOKEN', 'PORT',
    'NVIDIA_API_KEY_1', 'NVIDIA_MODEL_1', 'NVIDIA_API_KEY_2', 'NVIDIA_MODEL_2',
    'DEEPSEEK_API_KEY', 'DEEPSEEK_MODEL',
  ]);
  // Preserve any manually-set keys (e.g. ANTIGRAVITY_CLIENT_ID, ANTIGRAVITY_CLIENT_SECRET, PORT overrides)
  if (fs.existsSync(envPath)) {
    const existingLines = fs.readFileSync(envPath, 'utf-8').split('\n');
    const preserved: string[] = [];
    for (const line of existingLines) {
      const key = (line.split('=')[0] ?? '').trim().replace(/^export\s+/, '');
      if (key && !key.startsWith('#') && !WIZARD_MANAGED_KEYS.has(key)) {
        preserved.push(line);
      }
    }
    if (preserved.length > 0) {
      envContent += '\n# Preserved custom settings\n' + preserved.join('\n') + '\n';
    }
  }

  s.start('Writing configuration to .env');
  fs.writeFileSync(envPath, envContent);

  await setTimeout(500);
  s.stop('.env configured successfully!');

  if (scanQr) {
    try {
      await onboardWhatsApp();
      console.log('\n✅ WhatsApp connected successfully!');
    } catch (e: any) {
      console.error(`\n❌ WhatsApp connection failed: ${e.message}`);
    }
  }

  p.outro(`🕷️ Setup complete! You can change these settings in the .env file anytime. Run 'openspider gateway' and 'openspider tui'.`);
}

export async function promptForBackupModels(): Promise<string> {
  let envContent = '';

  const configureBackups = await p.confirm({
    message: 'Do you want to configure Backup Models? (Highly recommended. Used automatically if primary model hits rate limits or fails)',
    initialValue: true,
  });

  if (!p.isCancel(configureBackups) && configureBackups) {
    // DeepSeek Backup
    const wantsDeepSeek = await p.confirm({
      message: 'Configure DeepSeek (Backup 1 - Recommended)?',
      initialValue: true,
    });
    
    if (!p.isCancel(wantsDeepSeek) && wantsDeepSeek) {
        const deepseekKey = await p.text({
          message: 'Enter DeepSeek API Key:',
          placeholder: 'sk-...',
          validate(value) { if (!value.startsWith('sk-')) return 'DeepSeek keys start with sk-'; },
        }) as string;
        
        if (!p.isCancel(deepseekKey)) {
          envContent += `DEEPSEEK_API_KEY = ${deepseekKey}\n`;
          const deepseekModel = await p.text({
            message: 'Enter DeepSeek Model:',
            placeholder: 'deepseek-chat',
            initialValue: 'deepseek-chat',
          }) as string;
          if (!p.isCancel(deepseekModel)) envContent += `DEEPSEEK_MODEL = ${deepseekModel}\n`;
        }
    }

    // NVIDIA Backup Models
    const configureNvidia = await p.confirm({
      message: 'Configure NVIDIA models (Backup 2 & 3)?',
      initialValue: false,
    });

    if (!p.isCancel(configureNvidia) && configureNvidia) {
      const nvidiaKey1 = await p.text({
        message: 'Enter NVIDIA API Key for Backup 2:',
        placeholder: 'nvapi-...',
        validate(value) { if (!value.startsWith('nvapi-')) return 'NVIDIA keys start with nvapi-'; },
      }) as string;
      if (!p.isCancel(nvidiaKey1)) {
        const nvidiaModel1 = await p.text({
          message: 'Enter NVIDIA Model for Backup 2:',
          placeholder: 'nvidia/llama-3.1-nemotron-ultra-253b-v1',
          initialValue: 'nvidia/llama-3.1-nemotron-ultra-253b-v1',
        }) as string;
        if (!p.isCancel(nvidiaModel1)) {
          envContent += `NVIDIA_API_KEY_1 = ${nvidiaKey1}\n`;
          envContent += `NVIDIA_MODEL_1 = ${nvidiaModel1}\n`;
        }
      }

      const addSecond = await p.confirm({
        message: 'Add an additional NVIDIA backup model (Backup 3)?',
        initialValue: false,
      });

      if (!p.isCancel(addSecond) && addSecond) {
        const nvidiaKey2 = await p.text({
          message: 'Enter NVIDIA API Key for Backup 3:',
          placeholder: 'nvapi-...',
          validate(value) { if (!value.startsWith('nvapi-')) return 'NVIDIA keys start with nvapi-'; },
        }) as string;
        if (!p.isCancel(nvidiaKey2)) {
          const nvidiaModel2 = await p.text({
            message: 'Enter NVIDIA Model for Backup 3:',
            placeholder: 'nvidia/llama-3.1-nemotron-ultra-253b-v1',
            initialValue: 'nvidia/llama-3.1-nemotron-ultra-253b-v1',
          }) as string;
          if (!p.isCancel(nvidiaModel2)) {
            envContent += `NVIDIA_API_KEY_2 = ${nvidiaKey2}\n`;
            envContent += `NVIDIA_MODEL_2 = ${nvidiaModel2}\n`;
          }
        }
      }
    }
  }
  
  return envContent;
}

// Allow running this script directly
if (require.main === module) {
  runSetup().catch(console.error);
}
