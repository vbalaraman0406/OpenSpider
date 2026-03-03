#!/usr/bin/env python3
"""
OpenSpider Voice Message Skill — ElevenLabs TTS
Generates an audio file from text using ElevenLabs API and prints the file path.

Usage:
    python3 send_voice.py --text "Hello, how are you?" [--voice_id "21m00Tcm4TlvDq8ikWAM"]

Environment:
    ELEVENLABS_API_KEY  - Required API key
    ELEVENLABS_VOICE_ID - Optional default voice ID (fallback: Rachel)
"""

import argparse
import os
import sys
import json
import tempfile
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def text_to_speech(text: str, voice_id: str, api_key: str) -> str:
    """
    Call ElevenLabs TTS API and save the audio to a temp MP3 file.
    Returns the file path of the generated audio.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    payload = json.dumps({
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }).encode("utf-8")

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    req = Request(url, data=payload, headers=headers, method="POST")

    try:
        with urlopen(req, timeout=60) as response:
            if response.status != 200:
                error_body = response.read().decode("utf-8", errors="replace")
                print(f"ERROR: ElevenLabs API returned status {response.status}: {error_body}", file=sys.stderr)
                sys.exit(1)

            # Save audio to temp file
            tmp_file = os.path.join(tempfile.gettempdir(), f"openspider_tts_{os.getpid()}.mp3")
            with open(tmp_file, "wb") as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)

            return tmp_file

    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR: ElevenLabs API HTTP {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"ERROR: Failed to reach ElevenLabs API: {e.reason}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate voice audio from text using ElevenLabs TTS")
    parser.add_argument("--text", required=True, help="Text to convert to speech")
    parser.add_argument("--voice_id", default=None, help="ElevenLabs voice ID (default: Rachel)")
    args = parser.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Use provided voice_id, or env var, or default Rachel voice
    voice_id = args.voice_id or os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    print(f"Generating voice audio for text ({len(args.text)} chars) with voice {voice_id}...")
    audio_path = text_to_speech(args.text, voice_id, api_key)
    file_size = os.path.getsize(audio_path)
    print(f"AUDIO_FILE_PATH:{audio_path}")
    print(f"Audio file generated successfully ({file_size} bytes)")


if __name__ == "__main__":
    main()
