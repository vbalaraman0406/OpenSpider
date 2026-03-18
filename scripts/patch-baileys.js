#!/usr/bin/env node
/**
 * Baileys 6.17.16 Group Messaging Patch
 * 
 * Patches messages-send.js to make assertSessions resilient to 406 errors.
 * When sending group messages, Baileys tries to assert sessions with all
 * participant devices in a single batch IQ query. If ANY device JID is
 * problematic (e.g. a companion device whose pre-keys can't be fetched),
 * the entire query fails with "not-acceptable" (406) and the message never sends.
 *
 * This patch:
 * 1. Wraps batch assertSessions in try/catch
 * 2. Falls back to one-by-one session assertion, skipping failing JIDs
 * 3. Un-marks skipped JIDs from senderKeyMap so they're retried on next send
 * 
 * Run automatically via postinstall or manually: node scripts/patch-baileys.js
 */

const fs = require('fs');
const path = require('path');

const TARGET = path.join(
  __dirname, '..', 'node_modules', '@whiskeysockets', 'baileys',
  'lib', 'Socket', 'messages-send.js'
);

if (!fs.existsSync(TARGET)) {
  console.log('[patch-baileys] Baileys not installed, skipping patch.');
  process.exit(0);
}

let code = fs.readFileSync(TARGET, 'utf-8');

// Check if already patched
if (code.includes('BAILEYS-PATCH')) {
  console.log('[patch-baileys] Already patched, skipping.');
  process.exit(0);
}

// Find the pattern: await assertSessions(senderKeyJids, false);
// followed by: const result = await createParticipantNodes(senderKeyJids, senderKeyMsg, extraAttrs);
const ORIGINAL = `                    await assertSessions(senderKeyJids, false);
                    const result = await createParticipantNodes(senderKeyJids, senderKeyMsg, extraAttrs);
                    shouldIncludeDeviceIdentity = shouldIncludeDeviceIdentity || result.shouldIncludeDeviceIdentity;
                    participants.push(...result.nodes);`;

const PATCHED = `                    // [BAILEYS-PATCH] Resilient session assertion for group sends.
                    // Falls back to one-by-one if batch fails (e.g. 406 not-acceptable).
                    let validSenderKeyJids = senderKeyJids;
                    try {
                        await assertSessions(senderKeyJids, false);
                    } catch (batchErr) {
                        console.warn(\`[BAILEYS-PATCH] Batch assertSessions failed: \${batchErr.message || batchErr}. Trying one-by-one...\`);
                        validSenderKeyJids = [];
                        for (const skJid of senderKeyJids) {
                            try {
                                await assertSessions([skJid], false);
                                validSenderKeyJids.push(skJid);
                            } catch (singleErr) {
                                console.warn(\`[BAILEYS-PATCH] Skipping \${skJid}: \${singleErr.message || singleErr}\`);
                                // Un-mark from senderKeyMap so Baileys retries on next send
                                delete senderKeyMap[skJid];
                            }
                        }
                        console.log(\`[BAILEYS-PATCH] \${validSenderKeyJids.length}/\${senderKeyJids.length} sessions established successfully\`);
                    }
                    if (validSenderKeyJids.length) {
                        const result = await createParticipantNodes(validSenderKeyJids, senderKeyMsg, extraAttrs);
                        shouldIncludeDeviceIdentity = shouldIncludeDeviceIdentity || result.shouldIncludeDeviceIdentity;
                        participants.push(...result.nodes);
                    }`;

if (!code.includes(ORIGINAL)) {
  console.log('[patch-baileys] Target pattern not found (Baileys version may not need this patch). Skipping.');
  process.exit(0);
}

code = code.replace(ORIGINAL, PATCHED);
fs.writeFileSync(TARGET, code, 'utf-8');
console.log('[patch-baileys] ✅ Patched messages-send.js for resilient group session assertion.');
