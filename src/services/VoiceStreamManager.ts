import { WebSocket } from 'ws';

export function handleTwilioWebSocket(twilioWs: WebSocket, req: any) {
    const openaiApiKey = process.env.OPENAI_API_KEY;
    if (!openaiApiKey) {
        console.error('[VoiceStream] Missing OPENAI_API_KEY. Terminating call.');
        twilioWs.close();
        return;
    }

    // Connect securely to OpenAI's deep webRTC realtime boundary
    const openaiWs = new WebSocket('wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview', {
        headers: {
            "Authorization": "Bearer " + openaiApiKey,
            "OpenAI-Beta": "realtime=v1"
        }
    });
    
    let streamSid: string | null = null;
    let initialTask: string | null = null;

    openaiWs.on('open', () => {
        console.log('[VoiceStream] Authenticated with OpenAI Realtime Node.');
    });

    twilioWs.on('message', (message: string) => {
        try {
            const msg = JSON.parse(message);
            if (msg.event === 'start') {
                streamSid = msg.start.streamSid;
                initialTask = msg.start.customParameters?.task || "You are an AI assistant.";
                console.log(`[VoiceStream] Twilio inbound stream initialized. SID: ${streamSid}`);
                console.log(`[VoiceStream] Loaded Objective: ${initialTask}`);
                
                // Establish connection schema with OpenAI
                const sessionUpdate = {
                    type: 'session.update',
                    session: {
                        turn_detection: { type: 'server_vad' }, // Let OpenAI handle silence detection natively
                        input_audio_format: 'g711_ulaw',        // Natively matches Twilio PCM 8000Hz 
                        output_audio_format: 'g711_ulaw',       // Natively matches Twilio PCM 8000Hz
                        voice: 'alloy',
                        instructions: `You are 'OpenClaw', an AI assistant making a phone call for your user.\n\nYOUR OBJECTIVE: ${initialTask}\n\nRULES:\n- You are talking on the phone to a real human.\n- Speak naturally with human pacing. Do not output anything other than spoken words.\n- Listen closely, answer questions, and when the task is complete, politely say goodbye and hang up.`,
                        modalities: ["text", "audio"],
                        temperature: 0.6
                    }
                };
                openaiWs.send(JSON.stringify(sessionUpdate));

                // Force OpenAI to say hello to kick off the interaction
                openaiWs.send(JSON.stringify({
                    type: 'response.create',
                    response: {
                        instructions: "Say hello and ask who you are speaking to to begin the call."
                    }
                }));

            } else if (msg.event === 'media') {
                // Buffer audio payload into OpenAI pipeline
                if (openaiWs.readyState === WebSocket.OPEN) {
                    const audioAppend = {
                        type: 'input_audio_buffer.append',
                        audio: msg.media.payload
                    };
                    openaiWs.send(JSON.stringify(audioAppend));
                }
            } else if (msg.event === 'stop') {
                console.log('[VoiceStream] Twilio hung up.');
                openaiWs.close();
            }
        } catch (e) {
            console.error('[VoiceStream] Error processing Twilio chunk:', e);
        }
    });

    openaiWs.on('message', (data: any) => {
        try {
            const response = JSON.parse(data.toString());
            
            // Forward TTS synthesis back down to Twilio
            if (response.type === 'response.audio.delta' && response.delta) {
                if (streamSid && twilioWs.readyState === WebSocket.OPEN) {
                    const mediaEvent = {
                        event: 'media',
                        streamSid: streamSid,
                        media: { payload: response.delta }
                    };
                    twilioWs.send(JSON.stringify(mediaEvent));
                }
            }
            
            // If OpenAI detects user speech (interruption), immediately halt Twilio audio queue
            if (response.type === 'input_audio_buffer.speech_started') {
                 if (streamSid && twilioWs.readyState === WebSocket.OPEN) {
                    const clearEvent = { event: 'clear', streamSid: streamSid };
                    twilioWs.send(JSON.stringify(clearEvent));
                 }
            }
        } catch (e) {
            console.error('[VoiceStream] Error parsing OpenAI message:', e);
        }
    });

    openaiWs.on('close', () => {
        console.log('[VoiceStream] OpenAI bridge closed.');
        if (twilioWs.readyState === WebSocket.OPEN) twilioWs.close();
    });

    openaiWs.on('error', (err) => {
        console.error('[VoiceStream] OpenAI WebSocket Error:', err);
    });
}
