import crypto from 'crypto';
import express from 'express';
import { Server } from 'http';
import open from 'open';
import fs from 'fs';
import path from 'path';

const ANTIGRAVITY_CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com";
const ANTIGRAVITY_CLIENT_SECRET = "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";
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
    throw new Error("Failed to resolve Antigravity account info via loadCodeAssist endpoints.");
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
        throw new Error(`Failed to refresh token: ${await refreshResponse.text()}`);
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
    if (fs.existsSync(AUTH_FILE_PATH)) {
        try {
            return JSON.parse(fs.readFileSync(AUTH_FILE_PATH, 'utf-8'));
        } catch (e) {
            return null;
        }
    }
    return null;
}

export function saveAuthState(state: AuthState) {
    fs.writeFileSync(AUTH_FILE_PATH, JSON.stringify(state, null, 2));
}

export async function loginToAntigravity(): Promise<AuthState> {
    const existing = loadAuthState();
    if (existing) {
        if (existing.expires < Date.now()) {
            return await refreshAntigravityToken(existing);
        }
        return existing;
    }

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
