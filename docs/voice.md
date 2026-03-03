# Voice Messages

OpenSpider supports **voice-in, voice-out** interaction via WhatsApp. Users can send voice messages to the agent, which are transcribed and processed, and the agent can respond with voice notes.

## How It Works

### Voice Input (User → Agent)

1. User sends a WhatsApp voice message (`.ogg` audio)
2. OpenSpider downloads the audio file
3. Audio is converted from OGG to WAV using `ffmpeg`
4. **OpenAI Whisper** (local) transcribes the audio to text
5. The transcription is passed to the Manager agent as `[Voice Message] <text>`
6. The Manager creates a single task for a voice reply

### Voice Output (Agent → User)

1. The agent uses the `send_voice` tool
2. **ElevenLabs API** synthesizes text-to-speech audio
3. Audio is converted to OGG/Opus format (WhatsApp-compatible)
4. The voice note is sent back via WhatsApp as a `ptt` (push-to-talk) message

## Configuration

### ElevenLabs Setup

Voice responses require an [ElevenLabs](https://elevenlabs.io) API key.

**File:** `voice_config.json`

```json
{
  "elevenLabsApiKey": "sk_...",
  "defaultVoice": "Rachel",
  "model": "eleven_monolingual_v1"
}
```

| Field | Description |
|---|---|
| `elevenLabsApiKey` | Your ElevenLabs API key |
| `defaultVoice` | Voice name (e.g. `Rachel`, `Adam`, `Bella`) |
| `model` | TTS model to use |

### Dashboard Configuration

You can also configure voice settings from the dashboard:

1. Go to **Channels** → **WhatsApp** → Click **Configure**
2. Scroll to the **Voice Settings** section
3. Enter your ElevenLabs API key
4. Select a voice from the dropdown
5. Use the **Test** button to preview the voice

### Dependencies

Voice features require these external tools:

| Tool | Purpose | Install |
|---|---|---|
| `ffmpeg` | Audio format conversion | `brew install ffmpeg` |
| `ffprobe` | Audio metadata inspection | Included with ffmpeg |
| `whisper` | Speech-to-text transcription | `pip install openai-whisper` |

::: tip Auto-install
OpenSpider checks for `ffmpeg` and `whisper` on startup and prompts to install them if missing.
:::

## Single Voice Reply Rule

To prevent duplicate voice responses, the Manager agent is instructed to create **exactly one task** for voice replies. When a voice message is received, the system prompt includes:

```
[SYSTEM: The user sent a voice message. You MUST reply using send_voice tool to send a voice note back. Do NOT reply with text only.]
```

The agent's text reply is automatically suppressed when a voice note is sent alongside it.

## Troubleshooting

### Voice note not received

1. Check that `ffmpeg` is installed: `which ffmpeg`
2. Verify ElevenLabs API key is valid
3. Check server logs for audio conversion errors

### Transcription fails

1. Verify `whisper` is installed: `which whisper`
2. Check available disk space (Whisper downloads models on first use)
3. Large files may take longer — check logs for progress

### Duplicate voice replies

If you hear two voice notes for one message, check that the Manager's `IDENTITY.md` contains the single-task voice rule.
