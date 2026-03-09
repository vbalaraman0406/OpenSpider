import crypto from 'crypto';
import express from 'express';
import { Server } from 'http';
import open from 'open';
import fs from 'fs';
import path from 'path';
import os from 'os';

// Read from .env so credentials survive `git pull` / `openspider update`.
// Set ANTIGRAVITY_CLIENT_ID and ANTIGRAVITY_CLIENT_SECRET in your .env file.
const ANTIGRAVITY_CLIENT_ID = process.env.ANTIGRAVITY_CLIENT_ID || '';
const ANTIGRAVITY_CLIENT_SECRET = process.env.ANTIGRAVITY_CLIENT_SECRET || '';
const ANTIGRAVITY_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/cclog",
    "https://www.googleapis.com/auth/experimentsandconfigs"
];

const CODE_ASSIST_ENDPOINT_FALLBACKS = [
    "https://daily-cloudcode-pa.sandbox.googleapis.com",
    "https://autopush-cloudcode-pa.sandbox.googleapis.com",
    "https://cloudcode-pa.googleapis.com"
];

const CODE_ASSIST_HEADERS = {
    "User-Agent": "antigravity/1.15.8 darwin/arm64",
    "X-Goog-Api-Client": "google-cloud-sdk vscode_cloudshelleditor/0.1",
    "Client-Metadata": '{"ideType":"IDE_UNSPECIFIED","platform":"PLATFORM_UNSPECIFIED","pluginType":"GEMINI"}',
};

const AUTH_FILE_PATH = path.join(process.cwd(), '.antigravity-auth.json');
let cachedAuthState: AuthState | null = null; // In-memory cache to prevent repeated browser logins

export interface AuthState {
    access: string;
    refresh: string;
    expires: number;
    projectId: string;
    endpoint: string;
}

function base64URLEncode(buffer: Buffer): string {
    return buffer.toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}

async function fetchManagedProjectId(accessToken: string): Promise<{ projectId: string, endpoint: string }> {
    console.log("🕷️ Fetching Internal Google IDE Project ID via loadCodeAssist...");

    for (const baseEndpoint of CODE_ASSIST_ENDPOINT_FALLBACKS) {
        try {
            const url = `${baseEndpoint}/v1internal:loadCodeAssist`;
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    ...CODE_ASSIST_HEADERS,
                    "Authorization": `Bearer ${accessToken}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    metadata: {
                        ideType: "IDE_UNSPECIFIED",
                        platform: "PLATFORM_UNSPECIFIED",
                        pluginType: "GEMINI",
                    },
                }),
            });

            if (!response.ok) continue;

            const data: any = await response.json();
            let projectId = "";

            if (typeof data.cloudaicompanionProject === "string" && data.cloudaicompanionProject) {
                projectId = data.cloudaicompanionProject;
            } else if (
                data.cloudaicompanionProject &&
                typeof data.cloudaicompanionProject.id === "string" &&
                data.cloudaicompanionProject.id
            ) {
                projectId = data.cloudaicompanionProject.id;
            }

            if (projectId) {
                console.log(`✅ Internal Managed Project ID Found [${baseEndpoint}]: ${projectId}`);
                return { projectId, endpoint: baseEndpoint };
            }
        } catch (e) {
            // Ignore and move to next fallback
        }
    }

    // Non-fatal fallback: if the internal API is unavailable (e.g. account not enrolled in
    // Gemini Code Assist), use the production endpoint with an empty projectId.
    // The actual generate() calls may still succeed with cloud-platform scope alone.
    console.warn('[Antigravity] Could not resolve project ID from Code Assist endpoints — using production endpoint as fallback.');
    return { projectId: '', endpoint: 'https://cloudcode-pa.googleapis.com' };
}

async function exchangeCodeForAuth(code: string, codeVerifier: string, redirectUri: string): Promise<AuthState> {
    console.log("🕷️ Exchanging Authorization Code for Toolkit Token...");

    const tokenResponse = await fetch("https://oauth2.googleapis.com/token", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
            client_id: ANTIGRAVITY_CLIENT_ID,
            client_secret: ANTIGRAVITY_CLIENT_SECRET,
            code: code,
            code_verifier: codeVerifier,
            grant_type: "authorization_code",
            redirect_uri: redirectUri,
        }).toString(),
    });

    if (!tokenResponse.ok) {
        throw new Error(`Token exchange failed: ${await tokenResponse.text()}`);
    }

    const payload: any = await tokenResponse.json();
    const { projectId, endpoint } = await fetchManagedProjectId(payload.access_token);

    const authState: AuthState = {
        access: payload.access_token,
        refresh: payload.refresh_token,
        expires: Date.now() + payload.expires_in * 1000,
        projectId,
        endpoint
    };

    saveAuthState(authState);
    return authState;
}

export async function refreshAntigravityToken(state: AuthState): Promise<AuthState> {
    console.log("🕷️ Refreshing Google IDE Ext Token...");
    const refreshResponse = await fetch("https://oauth2.googleapis.com/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
            grant_type: "refresh_token",
            refresh_token: state.refresh,
            client_id: ANTIGRAVITY_CLIENT_ID,
            client_secret: ANTIGRAVITY_CLIENT_SECRET,
        }).toString(),
    });

    if (!refreshResponse.ok) {
        const body = await refreshResponse.text();
        // If the OAuth client itself is invalid/revoked, clear stale token so caller can do fresh browser login
        if (body.includes('invalid_client') || body.includes('invalid_grant')) {
            console.warn('[Antigravity] Token refresh failed (invalid_client/grant) — clearing stale auth for re-login.');
            try { fs.unlinkSync(AUTH_FILE_PATH); } catch (e) { }
        }
        throw new Error(`Failed to refresh token: ${body}`);
    }

    const payload: any = await refreshResponse.json();

    const newState = {
        ...state,
        access: payload.access_token,
        expires: Date.now() + payload.expires_in * 1000,
    };

    saveAuthState(newState);
    return newState;
}

export function loadAuthState(): AuthState | null {
    // Check in-memory cache first to avoid repeated file reads
    if (cachedAuthState && cachedAuthState.expires > Date.now()) return cachedAuthState;
    // Clear stale in-memory cache so callers re-borrow from IDE
    if (cachedAuthState && cachedAuthState.expires <= Date.now()) {
        cachedAuthState = null;
    }
    if (fs.existsSync(AUTH_FILE_PATH)) {
        try {
            const loaded = JSON.parse(fs.readFileSync(AUTH_FILE_PATH, 'utf-8'));
            // Don't cache expired tokens — let caller handle refresh
            if (loaded && loaded.expires > Date.now()) {
                cachedAuthState = loaded;
                return cachedAuthState;
            }
            return loaded; // Return expired state so caller can attempt refresh
        } catch (e) {
            return null;
        }
    }
    return null;
}

export function saveAuthState(state: AuthState) {
    cachedAuthState = state; // Update in-memory cache immediately
    fs.writeFileSync(AUTH_FILE_PATH, JSON.stringify(state, null, 2));
}

/** Wipe all cached auth — forces re-borrow from IDE on next login */
export function clearAuthState() {
    cachedAuthState = null;
    try { fs.unlinkSync(AUTH_FILE_PATH); } catch (_) { }
}

/**
 * TRUE STEALTH MODE: Read the live access token directly from the Antigravity IDE's
 * globalStorage SQLite database. This piggybacks on the IDE's existing authenticated
 * session — no OAuth browser flow needed.
 *
 * Uses better-sqlite3 for reliable parsing. Falls back to raw binary scan if the
 * native module is unavailable.
 */
async function borrowTokenFromIDE(): Promise<AuthState | null> {
    const homeDir = os.homedir();
    const dbCandidates = [
        path.join(homeDir, 'Library', 'Application Support', 'Antigravity', 'User', 'globalStorage', 'state.vscdb'),
        path.join(homeDir, '.config', 'Antigravity', 'User', 'globalStorage', 'state.vscdb'),
        path.join(homeDir, 'AppData', 'Roaming', 'Antigravity', 'User', 'globalStorage', 'state.vscdb'),
    ];

    // Keys to check in priority order — first match with a ya29. token wins
    const AUTH_KEYS = ['antigravityAuthStatus', 'antigravityUnifiedStateSync.oauthToken'];

    for (const dbPath of dbCandidates) {
        if (!fs.existsSync(dbPath)) continue;

        // ── Strategy 1: Raw binary scan (FAST, no lock contention) ────────────
        // Reads the file bytes directly — immune to SQLite WAL locks.
        // IMPORTANT: Use matchAll + take LAST match — SQLite files contain historical
        // records; the first ya29 match is often a stale old token, the latest is at the end.
        let accessToken = '';
        try {
            // Scan both the main DB and WAL file (if present) for the freshest token
            const filesToScan = [dbPath, dbPath + '-wal'].filter(f => fs.existsSync(f));
            const tokenPattern = /"apiKey"\s*:\s*"(ya29\.[^"\x00-\x1f]+)"/g;
            let latestToken = '';
            for (const file of filesToScan) {
                const raw = fs.readFileSync(file).toString('binary');
                for (const m of raw.matchAll(tokenPattern)) {
                    if (m[1]) latestToken = m[1]; // keep overwriting → last match wins
                }
            }
            if (latestToken) accessToken = latestToken;
        } catch (_) { /* Continue to SQLite fallback */ }

        // ── Strategy 2: better-sqlite3 (structured, if binary scan missed) ────
        if (!accessToken) {
            try {
                const Database = require('better-sqlite3') as typeof import('better-sqlite3');
                const db = new Database(dbPath, { readonly: true, fileMustExist: true, timeout: 2000 });

                for (const key of AUTH_KEYS) {
                    try {
                        const row = db.prepare("SELECT value FROM ItemTable WHERE key=?").get(key) as { value: string } | undefined;
                        if (!row) continue;
                        let raw = row.value;
                        try {
                            const parsed = JSON.parse(raw);
                            if (parsed && typeof parsed.apiKey === 'string' && parsed.apiKey.startsWith('ya29.')) {
                                accessToken = parsed.apiKey;
                                break;
                            }
                        } catch (_) { }
                        const m = raw.match(/"apiKey"\s*:\s*"(ya29\.[^"]+)"/);
                        if (m && m[1]) { accessToken = m[1]; break; }
                    } catch (_) { }
                }
                db.close();
            } catch (sqliteErr) {
                // better-sqlite3 unavailable, timed out, or binding failed
                console.warn('[Antigravity] SQLite read timed out or failed — using binary scan result if available');
            }
        }

        if (!accessToken || !accessToken.startsWith('ya29.')) continue;

        console.log('🕵️  [Antigravity] Borrowed live token from IDE session (stealth mode)');
        try {
            const { projectId, endpoint } = await fetchManagedProjectId(accessToken);
            const state: AuthState = {
                access: accessToken,
                refresh: '',
                expires: Date.now() + 55 * 60 * 1000, // 55 min — re-borrow before Google's 1hr expiry
                projectId,
                endpoint,
            };
            saveAuthState(state);
            return state;
        } catch (e) {
            // fetchManagedProjectId is non-fatal; token still valid for generate() calls
            const state: AuthState = {
                access: accessToken,
                refresh: '',
                expires: Date.now() + 55 * 60 * 1000,
                projectId: '',
                endpoint: 'https://cloudcode-pa.googleapis.com',
            };
            saveAuthState(state);
            return state;
        }
    }
    return null;
}

export async function loginToAntigravity(): Promise<AuthState> {
    if (!ANTIGRAVITY_CLIENT_ID) {
        throw new Error(
            'Antigravity credentials not configured. ' +
            'Add ANTIGRAVITY_CLIENT_ID to your .env file.'
        );
    }

    const existing = loadAuthState();
    if (existing) {
        if (existing.expires < Date.now()) {
            // Token expired — try OAuth refresh FIRST if we have a refresh token
            if (existing.refresh) {
                try {
                    return await refreshAntigravityToken(existing);
                } catch (e: any) {
                    console.warn('[Antigravity] OAuth refresh failed, falling back to IDE borrow...');
                }
            }
            // Fall back to IDE borrow with timeout (no refresh token, or refresh failed)
            const ideToken = await Promise.race([
                borrowTokenFromIDE(),
                new Promise<null>(r => setTimeout(() => r(null), 5000))
            ]);
            if (ideToken) return ideToken;

            // Last resort: fresh browser login
            console.warn('[Antigravity] All token sources exhausted, attempting fresh browser login...');
        } else {
            return existing;
        }
    }

    // No saved state — try IDE borrow with 5s timeout as a quick start
    const ideToken = await Promise.race([
        borrowTokenFromIDE(),
        new Promise<null>(r => setTimeout(() => r(null), 5000))
    ]);
    if (ideToken) return ideToken;

    console.log("🕷️ Initializing Internal Google IDE Authentication...");

    const state = crypto.randomBytes(32).toString('hex');
    const codeVerifier = base64URLEncode(crypto.randomBytes(32));
    const codeChallenge = base64URLEncode(crypto.createHash('sha256').update(codeVerifier).digest());

    const app = express();
    let server: Server;
    let authCode: string | null = null;
    let receivedState: string | null = null;

    return new Promise((resolve, reject) => {
        app.get('/oauth-callback', (req, res) => {
            authCode = req.query.code as string;
            receivedState = req.query.state as string;

            if (receivedState !== state) {
                res.send("<h1>Security Error: State mismatch!</h1>");
                return reject(new Error("State mismatch"));
            }

            res.send(`
                <html>
                <head><style>body { font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; background: #0f172a; color: white; }</style></head>
                <body>
                    <div style="text-align: center;">
                        <h1 style="color: #4ade80;">Authorization Successful!</h1>
                        <p>OpenSpider has extracted the internal IDE token. You can close this window and return to the terminal.</p>
                    </div>
                </body>
                </html>
            `);

            const port = (server.address() as any).port;
            const redirectUri = `http://localhost:${port}/oauth-callback`;

            server.close(async () => {
                try {
                    if (!authCode) throw new Error("No authorization code received.");
                    const authState = await exchangeCodeForAuth(authCode!, codeVerifier, redirectUri);
                    resolve(authState);
                } catch (e) {
                    reject(e);
                }
            });
        });

        server = app.listen(0, async () => {
            const port = (server.address() as any).port;
            const redirectUri = `http://localhost:${port}/oauth-callback`;

            const url = new URL("https://accounts.google.com/o/oauth2/v2/auth");
            url.searchParams.set("client_id", ANTIGRAVITY_CLIENT_ID);
            url.searchParams.set("response_type", "code");
            url.searchParams.set("redirect_uri", redirectUri);
            url.searchParams.set("scope", ANTIGRAVITY_SCOPES.join(" "));
            url.searchParams.set("code_challenge", codeChallenge);
            url.searchParams.set("code_challenge_method", "S256");
            url.searchParams.set("state", state);
            url.searchParams.set("access_type", "offline");
            url.searchParams.set("prompt", "consent");

            console.log("Opening browser to:", url.toString());
            await open(url.toString());
        });
    });
}
