/**
 * OpenSpider API Authentication Middleware
 *
 * Validates the X-API-Key header (or Authorization: Bearer <key>) on all
 * protected API routes.  The key is stored in DASHBOARD_API_KEY env var.
 *
 * WebSocket auth: The client must send the key as a query param on connect:
 *   ws://localhost:4001/?apiKey=<key>
 * The server validates this before adding the client to the broadcast set.
 *
 * Public (unauthenticated) routes:
 *   GET  /api/health   – needed so external health checks don't need the key
 *   POST /hooks/gmail  – has its own token-based auth
 */

import { Request, Response, NextFunction } from 'express';
import { IncomingMessage } from 'http';
import { URL } from 'url';

/**
 * Retrieve the configured API key.  Throws a clear startup error if missing.
 */
export function getApiKey(): string {
    const key = process.env.DASHBOARD_API_KEY;
    if (!key || key.trim().length < 32) {
        throw new Error(
            '[Security] DASHBOARD_API_KEY is not set or is too short (min 32 chars). ' +
            'Add it to your .env file and restart.'
        );
    }
    return key.trim();
}

/**
 * Express middleware: rejects requests that do not supply the correct API key.
 * Accepts it via:
 *   - Header:  X-API-Key: <key>
 *   - Header:  Authorization: Bearer <key>
 */
export function apiKeyAuth(req: Request, res: Response, next: NextFunction): void {
    try {
        const expected = getApiKey();

        const fromHeader = req.headers['x-api-key'] as string | undefined;
        const authHeader = req.headers['authorization'] as string | undefined;
        const fromBearer = authHeader?.startsWith('Bearer ') ? authHeader.slice(7) : undefined;
        const supplied = fromHeader || fromBearer;

        if (!supplied || supplied !== expected) {
            res.status(401).json({ error: 'Unauthorized. Provide a valid X-API-Key header.' });
            return;
        }
        next();
    } catch (err: any) {
        res.status(500).json({ error: err.message });
    }
}

/**
 * WebSocket upgrade validator.
 * Usage: call before adding a ws client to the broadcast set.
 * Returns true if the connection is authorized.
 */
export function validateWsConnection(req: IncomingMessage): boolean {
    try {
        const expected = getApiKey();
        // Parse query string from the request URL
        const baseUrl = `http://localhost${req.url || '/'}`;
        const url = new URL(baseUrl);
        const supplied = url.searchParams.get('apiKey');
        return supplied === expected;
    } catch {
        return false;
    }
}
