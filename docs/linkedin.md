# LinkedIn Integration

OpenSpider includes **Pulse**, a LinkedIn Content Strategist agent that drafts, refines, and publishes LinkedIn posts on your behalf. With a mandatory approval workflow, nothing goes live without your say-so.

## Features

- **AI-powered content creation** — Pulse uses proven LinkedIn frameworks (Hook → Insight → CTA, Contrarian Take, Storytelling, Data-Driven)
- **Mandatory approval** — Every draft is sent to you via WhatsApp for review before publishing
- **Algorithm-optimized** — Formatting, hashtags, and CTAs tuned for maximum LinkedIn engagement
- **Multi-topic expertise** — Tech leadership, AI/ML, entrepreneurship, and cross-industry thought leadership

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| LinkedIn account | Personal profile (free tier is fine) |
| LinkedIn Company Page | Required by LinkedIn to create a Developer App — can be a minimal page |
| OpenSpider gateway | Must be running on `localhost:4001` |

## Step 1: Create a LinkedIn Company Page

LinkedIn requires a Company Page to associate with your Developer App. If you don't have one:

1. Go to [linkedin.com/company/setup](https://www.linkedin.com/company/setup/new/)
2. Choose **Company** → **Small business**
3. Fill in:
   - **Name**: Your company or personal brand name
   - **Website**: Your website URL
   - **Industry**: Your industry (e.g., Technology)
4. Check the verification box and click **Create page**

::: tip
This page is only needed to register the Developer App. All posts will go to your **personal profile**, not the company page.
:::

## Step 2: Create a LinkedIn Developer App

1. Go to [linkedin.com/developers/apps](https://www.linkedin.com/developers/apps)
2. Click **Create app**
3. Fill in the form:

| Field | Value |
|-------|-------|
| **App name** | `OpenSpider` (or any name) |
| **LinkedIn Page** | Search for and select the company page you created |
| **Privacy policy URL** | Your website URL (e.g., `https://yoursite.com`) |
| **App logo** | Upload any square image (100×100px minimum) |

4. Check **"I have read and agree to these terms"**
5. Click **Create app**

## Step 3: Request API Products

On your app's **Products** tab, click **"Request access"** for these two products:

| Product | Tier | Purpose |
|---------|------|---------|
| **Share on LinkedIn** | Default | Allows posting content to your profile |
| **Sign In with LinkedIn using OpenID Connect** | Standard | Allows OAuth authentication |

Both products are **instantly approved** — no review process needed.

::: warning
Do NOT request other products (Advertising API, Marketing API, etc.) — they require LinkedIn review and are not needed for posting.
:::

## Step 4: Configure OAuth Redirect

1. Go to the **Auth** tab of your LinkedIn app
2. Under **OAuth 2.0 settings**, find **"Authorized redirect URLs for your app"**
3. Click the pencil/edit icon and add:

```
http://localhost:4001/api/linkedin/callback
```

4. Click **Update**

## Step 5: Get Your Credentials

On the same **Auth** tab:

1. Copy your **Client ID** (visible by default)
2. Click the eye icon next to **Client Secret** to reveal and copy it

## Step 6: Add Credentials to OpenSpider

Add these to your `.env` file in the OpenSpider root:

```env
# LinkedIn API
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
```

Then restart the gateway:

```bash
pm2 restart openspider-gateway
```

## Step 7: Authenticate Your LinkedIn Account

Open this URL in your browser:

```
http://localhost:4001/api/linkedin/auth
```

This redirects you to LinkedIn's consent screen. Sign in with your **personal LinkedIn account** (not the company page) and authorize OpenSpider. You'll see a success page:

```
✅ LinkedIn Connected!
Authenticated as Your Name
```

::: tip
Tokens last **60 days**. When they expire, just visit the auth URL again to re-authenticate.
:::

## Usage

### Via WhatsApp or Dashboard Chat

Simply ask the agent to write a LinkedIn post:

```
Write a LinkedIn post about AI agents transforming enterprise software
```

OpenSpider's Manager will automatically route this to **Pulse** (the LinkedIn expert agent).

### Approval Workflow

Pulse follows a strict draft → approve → publish workflow:

1. **Pulse drafts** the post using proven LinkedIn content frameworks
2. **Sends you the draft** via WhatsApp for review
3. **You review** and either:
   - Reply **"approve"** or **"go"** → Pulse publishes to LinkedIn
   - Reply with **feedback** → Pulse revises and sends a new draft
4. **Post goes live** only after your explicit approval

### Check Connection Status

```bash
curl http://localhost:4001/api/linkedin/status \
  -H "x-api-key: YOUR_API_KEY"
```

Returns:
```json
{
  "authenticated": true,
  "name": "Your Name",
  "expiresIn": "59 days"
}
```

## Content Frameworks

Pulse uses these proven LinkedIn content frameworks:

| Framework | Best For | Example Hook |
|-----------|----------|-------------|
| **Hook → Insight → CTA** | Thought leadership | "I stopped using X and never looked back." |
| **Contrarian Take** | Engagement/debate | "Unpopular opinion: microservices are overrated." |
| **Story → Lesson** | Authentic connection | "3 years ago, I made a $2M mistake." |
| **Data-Driven Insight** | Authority building | "We analyzed 10,000 deploys. Here's what broke." |
| **List/Framework** | Tactical value | "7 signs your engineering culture is broken:" |

## Troubleshooting

### "Unauthorized" error when visiting `/api/linkedin/auth`
The OAuth routes should bypass API key auth. If you see this error, rebuild and restart:
```bash
npx tsc && npm run build && pm2 restart openspider-gateway
```

### "LinkedIn auth failed: invalid_redirect_uri"
Make sure you added `http://localhost:4001/api/linkedin/callback` exactly as shown in the Auth tab's redirect URLs.

### Token expired
Tokens last 60 days. Visit `http://localhost:4001/api/linkedin/auth` again to re-authenticate.

### "Not authenticated" when posting
Run the auth flow first (Step 7). Check status at `/api/linkedin/status`.
