import * as crypto from 'crypto';
import { google } from 'googleapis';
import * as fs from 'fs';
import * as path from 'path'; export class GmailService {
  private static instance: GmailService;
  private oauth2Client: any;
  private gmail: any;
  private initialized = false;

  private constructor() { }

  static getInstance(): GmailService {
    if (!GmailService.instance) {
      GmailService.instance = new GmailService();
    }
    return GmailService.instance;
  }

  private init(): void {
    if (this.initialized) return;

    // Determine the workspace directory relative to the project root
    let workspaceDir;

    // Check if we are running from a compiled binary that bundles assets differently, or typical process.cwd()
    if (fs.existsSync(path.join(process.cwd(), 'workspace'))) {
      workspaceDir = path.join(process.cwd(), 'workspace');
    } else {
      // Fallback for deeply nested runtime logic if process.cwd() isn't the root
      workspaceDir = __dirname.includes('dist')
        ? path.join(__dirname, '..', '..', 'workspace')
        : path.join(__dirname, '..', '..', 'workspace');
    }

    const credsPath = path.join(workspaceDir, 'gmail_credentials.json');
    const tokenPath = path.join(workspaceDir, 'gmail_token.json');

    if (!fs.existsSync(credsPath) || !fs.existsSync(tokenPath)) {
      throw new Error(
        `Missing Gmail OAuth JSON credentials. Please run 'openspider tools email setup' to authenticate.`
      );
    }

    try {
      const creds = JSON.parse(fs.readFileSync(credsPath, 'utf-8'));
      const token = JSON.parse(fs.readFileSync(tokenPath, 'utf-8'));

      const clientInfo = creds.installed || creds.web;
      if (!clientInfo || !clientInfo.client_id || !clientInfo.client_secret) {
        throw new Error('Invalid format in gmail_credentials.json.');
      }

      this.oauth2Client = new google.auth.OAuth2(
        clientInfo.client_id,
        clientInfo.client_secret,
        'urn:ietf:wg:oauth:2.0:oob'
      );

      this.oauth2Client.setCredentials({
        access_token: token.token,
        refresh_token: token.refresh_token,
        expiry_date: token.expiry ? new Date(token.expiry).getTime() : undefined,
      });

      this.gmail = google.gmail({ version: 'v1', auth: this.oauth2Client });
      this.initialized = true;
    } catch (err: any) {
      throw new Error(`Failed to parse Gmail OAuth files: ${err.message}`);
    }
  }

  private buildRawMessage(params: {
    to: string;
    subject: string;
    body: string;
    cc?: string;
    bcc?: string;
  }): string {
    const lines: string[] = [];
    lines.push('Content-Type: text/html; charset="UTF-8"');
    lines.push('MIME-Version: 1.0');
    lines.push(`To: ${params.to}`);
    if (params.cc) lines.push(`Cc: ${params.cc}`);
    if (params.bcc) lines.push(`Bcc: ${params.bcc}`);
    lines.push(`Subject: ${params.subject}`);
    lines.push('');
    lines.push(params.body);

    const raw = lines.join('\r\n');
    return Buffer.from(raw)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');
  }

  async readEmails(params?: { maxResults?: number; query?: string }): Promise<{ success: boolean; emails?: any[]; error?: string }> {
    try {
      this.init();

      const maxResults = params?.maxResults || 5;
      const q = params?.query || 'is:unread'; // Default to unread if no query is provided

      const res = await this.gmail.users.messages.list({
        userId: 'me',
        maxResults,
        q,
      });

      const messages = res.data.messages;
      if (!messages || messages.length === 0) {
        return { success: true, emails: [] };
      }

      const emailDetails = await Promise.all(
        messages.map(async (msg: any) => {
          const detail = await this.gmail.users.messages.get({
            userId: 'me',
            id: msg.id,
            format: 'full'
          });

          const headers = detail.data.payload.headers;
          const subjectHeader = headers.find((h: any) => h.name.toLowerCase() === 'subject');
          const fromHeader = headers.find((h: any) => h.name.toLowerCase() === 'from');
          const dateHeader = headers.find((h: any) => h.name.toLowerCase() === 'date');

          return {
            id: detail.data.id,
            threadId: detail.data.threadId,
            snippet: detail.data.snippet,
            subject: subjectHeader ? subjectHeader.value : 'No Subject',
            from: fromHeader ? fromHeader.value : 'Unknown',
            date: dateHeader ? dateHeader.value : 'Unknown'
          };
        })
      );

      return {
        success: true,
        emails: emailDetails,
      };
    } catch (err: any) {
      const status = err?.response?.status || err?.code;
      const message = err?.response?.data?.error?.message || err?.message || String(err);

      if (status === 403) {
        return {
          success: false,
          error: `Gmail API 403 Forbidden — OAuth token likely missing gmail.readonly scope. Re-authorize with expanded scopes. Detail: ${message}`,
        };
      }
      return {
        success: false,
        error: `Gmail API error (${status || 'unknown'}): ${message}`,
      };
    }
  }

  async sendEmail(params: {
    to: string;
    subject: string;
    body: string;
    cc?: string;
    bcc?: string;
  }): Promise<{ success: boolean; messageId?: string; error?: string }> {
    try {
      this.init();

      const raw = this.buildRawMessage(params);
      const hash = crypto.createHash('sha256').update(`${params.to}:${params.subject}:${params.body}`).digest('hex');
      const now = Date.now();
      if ((globalThis as any).recentSentEmails?.has(hash)) {
          const lastSent = (globalThis as any).recentSentEmails.get(hash)!;
          if (now - lastSent < 10 * 60 * 1000) {
              console.log(`[GmailService] 🛑 DEDUPLICATED: Suppressed identical email to ${params.to} sent less than 10 minutes ago.`);
              return { success: true, messageId: 'deduplicated' };
          }
      } else if (!(globalThis as any).recentSentEmails) {
          (globalThis as any).recentSentEmails = new Map<string, number>();
      }
      (globalThis as any).recentSentEmails.set(hash, now);
      
      for (const [k, v] of (globalThis as any).recentSentEmails.entries()) {
          if (now - v > 15 * 60 * 1000) (globalThis as any).recentSentEmails.delete(k);
      }

      const response = await this.gmail.users.messages.send({
        userId: 'me',
        requestBody: { raw },
      });

      return {
        success: true,
        messageId: response.data.id,
      };
    } catch (err: any) {
      const status = err?.response?.status || err?.code;
      const message = err?.response?.data?.error?.message || err?.message || String(err);

      if (status === 403) {
        return {
          success: false,
          error: `Gmail API 403 Forbidden — OAuth token likely missing gmail.send scope. Re-authorize with expanded scopes. Detail: ${message}`,
        };
      }
      if (status === 401) {
        return {
          success: false,
          error: `Gmail API 401 Unauthorized — refresh token may be expired or revoked. Detail: ${message}`,
        };
      }
      return {
        success: false,
        error: `Gmail API error (${status || 'unknown'}): ${message}`,
      };
    }
  }

  /**
   * Move an email to the Trash. Recoverable for 30 days.
   * Use this instead of permanent delete for safety.
   */
  async trashEmail(messageId: string): Promise<{ success: boolean; error?: string }> {
    try {
      this.init();
      await this.gmail.users.messages.trash({
        userId: 'me',
        id: messageId,
      });
      return { success: true };
    } catch (err: any) {
      const message = err?.response?.data?.error?.message || err?.message || String(err);
      return { success: false, error: `Gmail trash failed: ${message}` };
    }
  }
}
