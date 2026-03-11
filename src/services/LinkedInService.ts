/**
 * LinkedInService — OAuth2 + Share API integration
 *
 * Handles:
 * 1. OAuth2 authorization flow (code → token exchange)
 * 2. Token persistence and auto-refresh
 * 3. User profile retrieval (URN for posting)
 * 4. Creating text posts on the authenticated user's LinkedIn profile
 */
import fs from 'node:fs';
import path from 'node:path';

const TOKENS_FILE = path.join(process.cwd(), 'workspace', 'linkedin_tokens.json');
const REDIRECT_URI = `http://localhost:${process.env.PORT || 4001}/api/linkedin/callback`;

interface LinkedInTokens {
    access_token: string;
    expires_in: number;
    refresh_token?: string;
    refresh_token_expires_in?: number;
    scope: string;
    token_type: string;
    obtained_at: number; // epoch ms
    user_sub?: string;   // LinkedIn member URN (sub from userinfo)
    user_name?: string;  // Display name
}

export class LinkedInService {
    private static instance: LinkedInService;
    private tokens: LinkedInTokens | null = null;

    private constructor() {
        this.loadTokens();
    }

    static getInstance(): LinkedInService {
        if (!this.instance) this.instance = new LinkedInService();
        return this.instance;
    }

    private loadTokens() {
        try {
            if (fs.existsSync(TOKENS_FILE)) {
                this.tokens = JSON.parse(fs.readFileSync(TOKENS_FILE, 'utf-8'));
            }
        } catch (e) {
            console.error('[LinkedIn] Failed to load tokens:', e);
        }
    }

    private saveTokens() {
        try {
            const dir = path.dirname(TOKENS_FILE);
            if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
            fs.writeFileSync(TOKENS_FILE, JSON.stringify(this.tokens, null, 2));
        } catch (e) {
            console.error('[LinkedIn] Failed to save tokens:', e);
        }
    }

    isAuthenticated(): boolean {
        if (!this.tokens) return false;
        const elapsed = Date.now() - this.tokens.obtained_at;
        const expiresMs = (this.tokens.expires_in || 3600) * 1000;
        return elapsed < expiresMs;
    }

    getAuthUrl(): string {
        const clientId = process.env.LINKEDIN_CLIENT_ID;
        if (!clientId) throw new Error('LINKEDIN_CLIENT_ID not set in .env');

        const scopes = 'openid profile w_member_social';
        const state = Math.random().toString(36).substring(2, 15);

        return `https://www.linkedin.com/oauth/v2/authorization?` +
            `response_type=code&` +
            `client_id=${encodeURIComponent(clientId)}&` +
            `redirect_uri=${encodeURIComponent(REDIRECT_URI)}&` +
            `scope=${encodeURIComponent(scopes)}&` +
            `state=${state}`;
    }

    async handleCallback(code: string): Promise<{ success: boolean; name?: string; error?: string }> {
        const clientId = process.env.LINKEDIN_CLIENT_ID;
        const clientSecret = process.env.LINKEDIN_CLIENT_SECRET;
        if (!clientId || !clientSecret) return { success: false, error: 'LinkedIn credentials not configured' };

        try {
            // 1. Exchange code for token
            const tokenRes = await fetch('https://www.linkedin.com/oauth/v2/accessToken', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    grant_type: 'authorization_code',
                    code,
                    redirect_uri: REDIRECT_URI,
                    client_id: clientId,
                    client_secret: clientSecret,
                }).toString(),
            });

            if (!tokenRes.ok) {
                const errText = await tokenRes.text();
                return { success: false, error: `Token exchange failed: ${errText}` };
            }

            const tokenData = await tokenRes.json();

            this.tokens = {
                ...tokenData,
                obtained_at: Date.now(),
            } as LinkedInTokens;

            // 2. Fetch user profile (OpenID Connect userinfo)
            const profileRes = await fetch('https://api.linkedin.com/v2/userinfo', {
                headers: { Authorization: `Bearer ${this.tokens.access_token}` },
            });

            if (profileRes.ok && this.tokens) {
                const profile = await profileRes.json();
                this.tokens.user_sub = profile.sub;
                this.tokens.user_name = profile.name || `${profile.given_name} ${profile.family_name}`;
            }

            this.saveTokens();
            return { success: true, name: this.tokens?.user_name || 'LinkedIn User' };
        } catch (e: any) {
            return { success: false, error: e.message };
        }
    }

    /**
     * Create a text post on the authenticated user's LinkedIn profile.
     */
    async createPost(text: string): Promise<{ success: boolean; postId?: string; error?: string }> {
        if (!this.tokens || !this.isAuthenticated()) {
            return { success: false, error: 'Not authenticated. Visit /api/linkedin/auth to connect.' };
        }

        const authorUrn = this.tokens.user_sub;
        if (!authorUrn) {
            return { success: false, error: 'No LinkedIn user URN found. Re-authenticate.' };
        }

        try {
            const payload = {
                author: `urn:li:person:${authorUrn}`,
                lifecycleState: 'PUBLISHED',
                specificContent: {
                    'com.linkedin.ugc.ShareContent': {
                        shareCommentary: {
                            text: text,
                        },
                        shareMediaCategory: 'NONE',
                    },
                },
                visibility: {
                    'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC',
                },
            };

            const res = await fetch('https://api.linkedin.com/v2/ugcPosts', {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${this.tokens.access_token}`,
                    'Content-Type': 'application/json',
                    'X-Restli-Protocol-Version': '2.0.0',
                },
                body: JSON.stringify(payload),
            });

            if (!res.ok) {
                const errText = await res.text();
                return { success: false, error: `LinkedIn API error (${res.status}): ${errText}` };
            }

            const postId = res.headers.get('x-restli-id') || 'unknown';
            return { success: true, postId };
        } catch (e: any) {
            return { success: false, error: e.message };
        }
    }

    getProfile(): { name: string; sub: string } | null {
        if (!this.tokens) return null;
        return {
            name: this.tokens.user_name || 'Unknown',
            sub: this.tokens.user_sub || '',
        };
    }

    getTokenStatus(): { authenticated: boolean; name?: string; expiresIn?: string } {
        if (!this.tokens || !this.isAuthenticated()) {
            return { authenticated: false };
        }
        const elapsed = Date.now() - this.tokens.obtained_at;
        const remaining = (this.tokens.expires_in * 1000) - elapsed;
        const days = Math.floor(remaining / (1000 * 60 * 60 * 24));
        return {
            authenticated: true,
            name: this.tokens.user_name || 'Unknown',
            expiresIn: `${days} days`,
        };
    }
}
