import { google } from 'googleapis';

export class GmailService {
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

    const clientId = process.env.GMAIL_CLIENT_ID;
    const clientSecret = process.env.GMAIL_CLIENT_SECRET;
    const refreshToken = process.env.GMAIL_REFRESH_TOKEN;

    if (!clientId || !clientSecret || !refreshToken) {
      throw new Error(
        'Missing Gmail OAuth2 credentials. Set GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, and GMAIL_REFRESH_TOKEN in .env'
      );
    }

    this.oauth2Client = new google.auth.OAuth2(clientId, clientSecret, 'urn:ietf:wg:oauth:2.0:oob');
    this.oauth2Client.setCredentials({ refresh_token: refreshToken });
    this.gmail = google.gmail({ version: 'v1', auth: this.oauth2Client });
    this.initialized = true;
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
}
