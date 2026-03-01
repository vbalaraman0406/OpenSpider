import { Router } from 'express';
import { logMemory } from '../memory';
import { ManagerAgent } from '../agents/ManagerAgent';

const router = Router();
const manager = new ManagerAgent();

router.post('/gmail', async (req, res) => {
    try {
        // Enforce basic auth parameter as required by documentation
        const token = req.query.token || req.headers['x-gog-token'];
        const configuredToken = process.env.OPENSPIDER_HOOK_TOKEN || 'OPENSPIDER_HOOK_TOKEN';

        if (token !== configuredToken) {
            return res.status(401).json({ error: "Unauthorized. Invalid Token." });
        }

        const payload = req.body;

        // Basic validation for Google Pub/Sub push format payload Structure
        if (!payload || !payload.message || !payload.message.data) {
            console.log("[GmailWebhook] Received malformed payload", payload);
            return res.status(400).json({ error: "Invalid Pub/Sub payload structure" });
        }

        // Decode base64 payload
        const decodedString = Buffer.from(payload.message.data, 'base64').toString('utf-8');
        let emailData;
        try {
            emailData = JSON.parse(decodedString);
        } catch (e) {
            console.error("[GmailWebhook] Failed to parse internal JSON data", decodedString);
            return res.status(400).json({ error: "Bad internal JSON layout" });
        }

        console.log(`[GmailWebhook] Received email: ID ${emailData.id}, Snippet: ${emailData.snippet || 'None'}`);

        // Limit the byte payload strictly as defined in documentation
        let bodySnippet = emailData.body || emailData.snippet || "No textual body sent.";
        const MAX_BYTES = 20000;

        if (Buffer.byteLength(bodySnippet, 'utf8') > MAX_BYTES) {
            console.log(`[GmailWebhook] Truncating payload from ${Buffer.byteLength(bodySnippet, 'utf8')} to ${MAX_BYTES} bytes`);
            bodySnippet = Buffer.from(bodySnippet, 'utf8').subarray(0, MAX_BYTES).toString('utf8');
        }

        // Add to session memory so frontend sees the inbound trigger
        const inboundMessage = `[SYSTEM TRIGGER: NEW GMAIL]\nFrom: ${emailData.from || 'Unknown'}\nSubject: ${emailData.subject || 'No Subject'}\n\n${bodySnippet}`;
        logMemory('User', inboundMessage); // Trick memory to think system act is user context

        // Broadcast a special event to connected WebSockets to auto-scroll UI if needed
        console.log({ type: 'webhook_event', source: 'gmail', data: emailData });

        // Let the manager agent decide what to do! Provide minimal envelope
        // using the agent process pattern inside server.ts 
        const prompt = `You have just received an automated Webhook trigger for a new Gmail message.\n\n${inboundMessage}\n\nTask: Evaluate this email. Formulate a useful plan or reply based on the contents.`;

        // We do this non-blocking (async without await) so the webhook immediately ACKs Google 
        // with 200 OK fast avoiding PubSub retries
        manager.processUserRequest(prompt).then((response) => {
            logMemory('Agent', response);
            console.log({ type: 'chat_response', data: response, timestamp: new Date().toISOString() });
        }).catch((err) => {
            console.error("[Gmail Webhook Agent Fault]", err);
        });

        res.status(200).json({ success: true, message: "Webhook accepted and processing initiated." });
    } catch (e: any) {
        console.error("[GmailWebhook] Fatal Error:", e.message);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

export default router;
