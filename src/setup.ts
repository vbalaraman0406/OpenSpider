import * as p from '@clack/prompts';
import { setTimeout } from 'node:timers/promises';
import fs from 'node:fs';
import path from 'node:path';

export async function runSetup() {
  console.clear();

  p.intro(`🕷️ Welcome to Openspider Setup`);

  const s = p.spinner();
  s.start('Checking environment configuration...');
  await setTimeout(1000);
  s.stop('Environment checked.');

  const envPath = path.join(process.cwd(), '.env');
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
      p.outro(`🕷️ Setup complete. Using existing .env file.`);
      return;
    }
  }

  const projectType = await p.select({
    message: 'Which main LLM provider will you use?',
    options: [
      { value: 'antigravity', label: 'Google Antigravity / Gemini', hint: 'Cloud' },
      { value: 'ollama', label: 'Ollama', hint: 'Local' },
      { value: 'openai', label: 'OpenAI', hint: 'Cloud' },
      { value: 'anthropic', label: 'Anthropic', hint: 'Cloud' },
      { value: 'custom', label: 'Custom OpenAI-compatible', hint: 'e.g. LM Studio' },
    ],
  });

  if (p.isCancel(projectType)) {
    p.cancel('Setup cancelled.');
    process.exit(0);
  }

  let envContent = `DEFAULT_PROVIDER=${projectType}\n\n`;

  if (projectType === 'antigravity') {
    const key = await p.text({
      message: 'Enter your Google Gemini API Key:',
      placeholder: 'AIzaSy...',
      validate(value) {
        if (value.length === 0) return `API Key is required!`;
      },
    });

    if (p.isCancel(key)) {
      p.cancel('Setup cancelled.');
      process.exit(0);
    }
    envContent += `GEMINI_API_KEY=${key}\n`;
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
    envContent += `OLLAMA_URL=${url}\n`;
    envContent += `OLLAMA_MODEL=${model}\n`;
  }

  if (projectType === 'openai') {
    const key = await p.text({
      message: 'Enter your OpenAI API Key:',
      placeholder: 'sk-...',
    });
    if (p.isCancel(key)) {
      p.cancel('Setup cancelled.');
      process.exit(0);
    }
    envContent += `OPENAI_API_KEY=${key}\n`;
  }
  
  if (projectType === 'anthropic') {
    const key = await p.text({
      message: 'Enter your Anthropic API Key:',
      placeholder: 'sk-ant-...',
    });
    if (p.isCancel(key)) {
      p.cancel('Setup cancelled.');
      process.exit(0);
    }
    envContent += `ANTHROPIC_API_KEY=${key}\n`;
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
    envContent += `CUSTOM_API_URL=${url}\n`;
    envContent += `CUSTOM_API_KEY=${key}\n`;
    envContent += `CUSTOM_MODEL=${model}\n`;
  }

  s.start('Writing configuration to .env');
  fs.writeFileSync(envPath, envContent);
  await setTimeout(500);
  s.stop('.env configured successfully!');

  p.outro(`🕷️ Setup complete! You can change these settings in the .env file anytime.`);
}

// Allow running this script directly
if (require.main === module) {
  runSetup().catch(console.error);
}
