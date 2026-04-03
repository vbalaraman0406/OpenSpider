const twilio = require('twilio');

/**
 * OpenSpider Dynamic Voice Calling Skill
 * Executes natively in the skills sandbox to ping the OpenSpider WebRTC Gateway.
 */
async function triggerVoiceCall() {
    // 1. Parse Arguments passed by the OpenSpider Agent via DynamicExecutor
    const argsRaw = process.argv.slice(2).join(' ');
    if (!argsRaw) {
        throw new Error('Missing arguments. Usage: node voice_call.js \'{"phoneNumber": "+123456789", "task": "Task description"}\'');
    }

    let params;
    try {
        params = JSON.parse(argsRaw);
    } catch (e) {
        throw new Error('Invalid JSON arguments provided to voice_call.js');
    }

    const { phoneNumber, task } = params;

    // 2. Load API Configuration directly from OpenSpider core environment
    const accountSid = process.env.TWILIO_ACCOUNT_SID;
    const authToken = process.env.TWILIO_AUTH_TOKEN;
    const twilioNumber = process.env.TWILIO_PHONE_NUMBER;
    const publicUrl = process.env.PUBLIC_URL;

    if (!accountSid || !authToken || !twilioNumber || !publicUrl) {
        throw new Error('Voice calling is disabled. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, and PUBLIC_URL in .env.');
    }

    const client = twilio(accountSid, authToken);

    // 3. Dispatch the call to the OpenSpider WebHook
    console.log(`[Voice Skill] Instructing Twilio to dial ${phoneNumber}...`);
    
    // Add custom header/query to tell the OpenSpider endpoint what the AI should accomplish
    const twimlWebhookUrl = `${publicUrl}/openclaw/twiml?task=${encodeURIComponent(task)}`;
    
    try {
        const call = await client.calls.create({
            url: twimlWebhookUrl,
            to: phoneNumber,
            from: twilioNumber
        });
        console.log(`[Voice Skill] Call successfully dispatched! Twilio Call SID: ${call.sid}`);
    } catch (err) {
        console.error(`[Voice Skill] Twilio Dispatch Error: ${err.message}`);
        process.exit(1);
    }
}

triggerVoiceCall();
