/**
 * CaptchaSolver — Self-hosted AI vision CAPTCHA solver
 *
 * When a CAPTCHA is detected by detectBotProtection(), this module:
 *   1. Screenshots the CAPTCHA region
 *   2. Sends it to the vision LLM with type-specific prompts
 *   3. Parses the LLM's response (click coordinates, grid cells, text)
 *   4. Executes the solution via ghost-cursor (human-like Bézier movements)
 *   5. Retries up to 3 times, falls back gracefully
 *
 * Handles: reCAPTCHA v2, hCaptcha, Cloudflare Turnstile, text CAPTCHAs
 */
import { Page, ElementHandle, Frame } from 'playwright-core';
import { Cursor } from 'ghost-cursor-playwright';
import { getProvider } from '../llm';
import { ChatMessage, ContentPart } from '../llm/BaseProvider';

/** Random human-like delay */
const humanDelay = (min = 400, max = 1200): Promise<void> =>
    new Promise(r => setTimeout(r, min + Math.floor(Math.random() * (max - min))));

/** Random jitter for mouse movements */
const jitter = (base: number, range = 5): number =>
    base + Math.floor(Math.random() * range * 2) - range;

// ─── CAPTCHA Type Detection ────────────────────────────────────────────────

export interface CaptchaInfo {
    type: 'recaptcha_checkbox' | 'recaptcha_image' | 'hcaptcha_checkbox' | 'hcaptcha_image' |
          'cloudflare_turnstile' | 'cloudflare_js' | 'text_captcha' | 'generic_verification' | 'unknown';
    /** The iframe or element containing the CAPTCHA */
    frame?: Frame;
    /** Bounding box of the CAPTCHA element on the page */
    bounds?: { x: number; y: number; width: number; height: number };
    /** Instruction text (e.g., "Select all images with traffic lights") */
    instruction?: string;
}

/**
 * Detect and classify the CAPTCHA type on the current page.
 */
async function identifyCaptcha(page: Page): Promise<CaptchaInfo> {
    // ── Cloudflare "Checking your browser" (JS challenge, auto-solves) ──
    const bodyText = await page.evaluate(() =>
        (document.body?.innerText || '').substring(0, 2000).toLowerCase()
    ).catch(() => '');

    if (bodyText.includes('just a moment') && bodyText.includes('checking your browser')) {
        return { type: 'cloudflare_js' };
    }

    // ── Check iframes for CAPTCHA providers ──
    const frames = page.frames();
    for (const frame of frames) {
        const url = frame.url().toLowerCase();

        // reCAPTCHA
        if (url.includes('recaptcha/api2/anchor') || url.includes('recaptcha/enterprise/anchor')) {
            return { type: 'recaptcha_checkbox', frame };
        }
        if (url.includes('recaptcha/api2/bframe') || url.includes('recaptcha/enterprise/bframe')) {
            // This is the image challenge frame
            const instruction = await frame.evaluate(() => {
                const el = document.querySelector('.rc-imageselect-desc-no-canonical, .rc-imageselect-desc');
                return el?.textContent?.trim() || '';
            }).catch(() => '');
            return { type: 'recaptcha_image', frame, instruction };
        }

        // hCaptcha
        if (url.includes('hcaptcha.com/captcha/checkbox')) {
            return { type: 'hcaptcha_checkbox', frame };
        }
        if (url.includes('hcaptcha.com/captcha/challenge')) {
            const instruction = await frame.evaluate(() => {
                const el = document.querySelector('.prompt-text');
                return el?.textContent?.trim() || '';
            }).catch(() => '');
            return { type: 'hcaptcha_image', frame, instruction };
        }

        // Cloudflare Turnstile
        if (url.includes('challenges.cloudflare.com')) {
            return { type: 'cloudflare_turnstile', frame };
        }
    }

    // ── Text CAPTCHA (image + text input) ──
    const hasTextCaptcha = await page.evaluate(() => {
        const imgs = document.querySelectorAll('img[src*="captcha"], img[alt*="captcha"], img.captcha');
        const inputs = document.querySelectorAll('input[name*="captcha"], input[id*="captcha"]');
        return imgs.length > 0 && inputs.length > 0;
    }).catch(() => false);

    if (hasTextCaptcha) {
        return { type: 'text_captcha' };
    }

    // ── Generic verification page ──
    if (bodyText.includes('verify you are human') || bodyText.includes('are you a robot') || bodyText.includes('please verify')) {
        return { type: 'generic_verification' };
    }

    return { type: 'unknown' };
}

// ─── Screenshot Helpers ────────────────────────────────────────────────────

/**
 * Take a screenshot of the CAPTCHA area and return as base64 data URL.
 */
async function screenshotCaptcha(page: Page, info: CaptchaInfo): Promise<string> {
    let buffer: Buffer;

    if (info.frame) {
        // Screenshot the frame's parent element on the main page
        try {
            const frameElement = await info.frame.frameElement();
            buffer = (await frameElement.screenshot({ type: 'png' })) as Buffer;
        } catch {
            // Fallback to full page screenshot
            buffer = (await page.screenshot({ type: 'png', fullPage: false })) as Buffer;
        }
    } else {
        // Full viewport screenshot for text CAPTCHAs / generic verification
        buffer = (await page.screenshot({ type: 'png', fullPage: false })) as Buffer;
    }

    return `data:image/png;base64,${buffer.toString('base64')}`;
}

// ─── Vision LLM Integration ───────────────────────────────────────────────

/**
 * Send a screenshot to the vision LLM and get a solution.
 */
async function askVisionLLM(screenshot: string, captchaType: string, instruction?: string): Promise<any> {
    const provider = getProvider();

    let promptText: string;

    switch (captchaType) {
        case 'recaptcha_checkbox':
        case 'hcaptcha_checkbox':
        case 'cloudflare_turnstile':
            promptText = `You are helping solve a CAPTCHA challenge. This screenshot shows a ${captchaType.replace('_', ' ')} on a webpage.

Find the checkbox that needs to be clicked to verify "I'm not a robot" or complete the challenge.

Return ONLY a JSON object with the x,y pixel coordinates of the checkbox CENTER relative to the screenshot:
{"x": <number>, "y": <number>}

Do not include any other text or explanation.`;
            break;

        case 'recaptcha_image':
            promptText = `You are helping solve a reCAPTCHA image selection challenge.

The instruction says: "${instruction || 'Select matching images'}"

The image shows a grid of tiles (usually 3x3 or 4x4). Each tile is numbered left-to-right, top-to-bottom starting from 1.

Carefully analyze each tile and determine which ones match the instruction.

Return ONLY a JSON array of tile numbers that match. Example: [1, 4, 7]

If you're unsure about a tile, include it — it's better to over-select than under-select.
Do not include any other text or explanation.`;
            break;

        case 'hcaptcha_image':
            promptText = `You are helping solve an hCaptcha image selection challenge.

The instruction says: "${instruction || 'Select matching images'}"

The image shows a grid of tiles (usually 3x3). Each tile is numbered left-to-right, top-to-bottom starting from 1.

Carefully analyze each tile and determine which ones match the instruction.

Return ONLY a JSON array of tile numbers that match. Example: [2, 5, 8]

If you're unsure about a tile, include it.
Do not include any other text or explanation.`;
            break;

        case 'text_captcha':
            promptText = `This image contains a CAPTCHA with distorted text characters. Your job is to read the distorted text.

Return ONLY the text you see in the CAPTCHA image, nothing else. No quotes, no explanation.`;
            break;

        case 'generic_verification':
            promptText = `This screenshot shows a verification/CAPTCHA page. Analyze the page and determine what action is needed.

If there's a button to click (like "Verify" or "I'm not a robot"), return:
{"action": "click", "x": <number>, "y": <number>}

If there's text to enter, return:
{"action": "type", "text": "<the text>", "selector": "<CSS selector of the input>"}

If you can't determine the action, return:
{"action": "unknown"}

Return ONLY the JSON, no other text.`;
            break;

        default:
            promptText = `This screenshot shows a CAPTCHA or verification challenge. Analyze it and determine what needs to be done.
Return a JSON object describing the solution:
- For clicking: {"action": "click", "x": <number>, "y": <number>}
- For typing: {"action": "type", "text": "<text>"}
- For grid selection: {"action": "select", "tiles": [<tile numbers>]}
Return ONLY the JSON.`;
    }

    const content: ContentPart[] = [
        { type: 'text', text: promptText },
        { type: 'image_url', image_url: { url: screenshot } }
    ];

    const messages: ChatMessage[] = [
        { role: 'system', content: 'You are a precise computer vision assistant that analyzes screenshots. You return ONLY the requested JSON output, never explanations or markdown.' },
        { role: 'user', content }
    ];

    try {
        const response = await provider.generateResponse(messages);
        const text = response.text.trim();

        // Strip markdown code fences if present
        const cleaned = text
            .replace(/^```(?:json)?\s*/i, '')
            .replace(/\s*```$/i, '')
            .trim();

        try {
            return JSON.parse(cleaned);
        } catch {
            // For text CAPTCHAs, the response IS the text answer
            if (captchaType === 'text_captcha') {
                return { action: 'type', text: cleaned };
            }
            console.warn('[CaptchaSolver] LLM response was not valid JSON:', cleaned.substring(0, 200));
            return null;
        }
    } catch (err: any) {
        console.error('[CaptchaSolver] Vision LLM call failed:', err.message);
        return null;
    }
}

// ─── Solution Execution ────────────────────────────────────────────────────

/**
 * Click at specific coordinates using ghost-cursor for human-like movement.
 */
async function clickAtCoords(page: Page, cursor: Cursor | null, x: number, y: number): Promise<void> {
    if (cursor) {
        try {
            // Ghost cursor moves in Bézier curves — very human-like
            await (cursor as any).moveTo({ x: jitter(x), y: jitter(y) });
            await humanDelay(100, 300);
            await (cursor as any).click({ x: jitter(x, 2), y: jitter(y, 2) });
        } catch {
            // Fallback to direct click
            await page.mouse.click(jitter(x), jitter(y));
        }
    } else {
        await page.mouse.move(jitter(x), jitter(y), { steps: 10 + Math.floor(Math.random() * 15) });
        await humanDelay(100, 300);
        await page.mouse.click(jitter(x), jitter(y));
    }
    await humanDelay(800, 1500);
}

/**
 * Click on specific grid tiles in a CAPTCHA frame.
 */
async function clickGridTiles(page: Page, frame: Frame, cursor: Cursor | null, tiles: number[]): Promise<void> {
    // Determine grid dimensions from the frame
    const gridInfo = await frame.evaluate(() => {
        // reCAPTCHA grid
        const rcTable = document.querySelector('.rc-imageselect-table-33, .rc-imageselect-table-44, .rc-imageselect-table-42');
        if (rcTable) {
            const cells = rcTable.querySelectorAll('td');
            const firstCell = cells[0];
            if (firstCell) {
                const rect = firstCell.getBoundingClientRect();
                const rows = rcTable.querySelectorAll('tr').length;
                const cols = (rcTable.querySelector('tr') as HTMLTableRowElement)?.cells?.length || 3;
                return { cellWidth: rect.width, cellHeight: rect.height, rows, cols, offsetX: rect.x, offsetY: rect.y };
            }
        }

        // hCaptcha grid
        const hcGrid = document.querySelector('.task-grid');
        if (hcGrid) {
            const cells = hcGrid.querySelectorAll('.task-image');
            const firstCell = cells[0];
            if (firstCell) {
                const rect = firstCell.getBoundingClientRect();
                const cols = Math.round(hcGrid.clientWidth / rect.width);
                const rows = Math.round(cells.length / cols);
                return { cellWidth: rect.width, cellHeight: rect.height, rows, cols, offsetX: rect.x, offsetY: rect.y };
            }
        }

        return null;
    }).catch(() => null);

    if (!gridInfo) {
        console.warn('[CaptchaSolver] Could not determine grid layout');
        return;
    }

    // Get the frame's position on the main page
    const frameElement = await frame.frameElement();
    const frameBox = await frameElement.boundingBox();
    if (!frameBox) return;

    // Click each matching tile with human-like delays between clicks
    for (const tileNum of tiles) {
        const row = Math.floor((tileNum - 1) / gridInfo.cols);
        const col = (tileNum - 1) % gridInfo.cols;

        // Calculate absolute coordinates on the main page
        const x = frameBox.x + gridInfo.offsetX + (col * gridInfo.cellWidth) + (gridInfo.cellWidth / 2);
        const y = frameBox.y + gridInfo.offsetY + (row * gridInfo.cellHeight) + (gridInfo.cellHeight / 2);

        console.log(`  [CaptchaSolver] Clicking tile ${tileNum} at (${Math.round(x)}, ${Math.round(y)})`);
        await clickAtCoords(page, cursor, x, y);
        await humanDelay(600, 1200); // Human pause between tile selections
    }
}

/**
 * Click the checkbox inside a CAPTCHA iframe (reCAPTCHA/hCaptcha/Turnstile).
 */
async function clickCheckbox(page: Page, frame: Frame, cursor: Cursor | null): Promise<void> {
    // Get frame position on page
    const frameElement = await frame.frameElement();
    const frameBox = await frameElement.boundingBox();
    if (!frameBox) return;

    // Find the checkbox inside the frame
    const checkboxPos = await frame.evaluate(() => {
        // reCAPTCHA
        const rcCheckbox = document.querySelector('.recaptcha-checkbox-border, .recaptcha-checkbox');
        if (rcCheckbox) {
            const rect = rcCheckbox.getBoundingClientRect();
            return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
        }

        // hCaptcha
        const hcCheckbox = document.querySelector('#checkbox');
        if (hcCheckbox) {
            const rect = hcCheckbox.getBoundingClientRect();
            return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
        }

        // Cloudflare Turnstile
        const cfCheckbox = document.querySelector('input[type="checkbox"], .cb-i');
        if (cfCheckbox) {
            const rect = cfCheckbox.getBoundingClientRect();
            return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
        }

        // Generic: center of the frame
        return { x: 30, y: 30 };
    }).catch(() => ({ x: 30, y: 30 }));

    const absX = frameBox.x + checkboxPos.x;
    const absY = frameBox.y + checkboxPos.y;

    console.log(`  [CaptchaSolver] Clicking checkbox at (${Math.round(absX)}, ${Math.round(absY)})`);
    await clickAtCoords(page, cursor, absX, absY);
}

/**
 * After clicking a checkbox, check if an image challenge appeared.
 */
async function checkForImageChallenge(page: Page): Promise<CaptchaInfo | null> {
    await humanDelay(2000, 3000);

    const frames = page.frames();
    for (const frame of frames) {
        const url = frame.url().toLowerCase();
        if (url.includes('recaptcha/api2/bframe') || url.includes('recaptcha/enterprise/bframe')) {
            const instruction = await frame.evaluate(() => {
                const el = document.querySelector('.rc-imageselect-desc-no-canonical, .rc-imageselect-desc');
                return el?.textContent?.trim() || '';
            }).catch(() => '');
            if (instruction) {
                return { type: 'recaptcha_image', frame, instruction };
            }
        }
        if (url.includes('hcaptcha.com/captcha/challenge')) {
            const instruction = await frame.evaluate(() => {
                const el = document.querySelector('.prompt-text');
                return el?.textContent?.trim() || '';
            }).catch(() => '');
            if (instruction) {
                return { type: 'hcaptcha_image', frame, instruction };
            }
        }
    }
    return null;
}

/**
 * Click the "Verify" / "Submit" button in a CAPTCHA image challenge.
 */
async function clickVerifyButton(page: Page, frame: Frame, cursor: Cursor | null): Promise<void> {
    const frameElement = await frame.frameElement();
    const frameBox = await frameElement.boundingBox();
    if (!frameBox) return;

    const btnPos = await frame.evaluate(() => {
        // reCAPTCHA verify button
        const rcVerify = document.querySelector('#recaptcha-verify-button, .verify-button-holder button');
        if (rcVerify) {
            const rect = rcVerify.getBoundingClientRect();
            return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
        }

        // hCaptcha submit button
        const hcSubmit = document.querySelector('.button-submit');
        if (hcSubmit) {
            const rect = hcSubmit.getBoundingClientRect();
            return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
        }

        return null;
    }).catch(() => null);

    if (btnPos) {
        const absX = frameBox.x + btnPos.x;
        const absY = frameBox.y + btnPos.y;
        console.log(`  [CaptchaSolver] Clicking verify button at (${Math.round(absX)}, ${Math.round(absY)})`);
        await humanDelay(500, 1000);
        await clickAtCoords(page, cursor, absX, absY);
    }
}

// ─── Main Solver ───────────────────────────────────────────────────────────

export class CaptchaSolver {
    private static MAX_ATTEMPTS = 3;

    /**
     * Attempt to solve a CAPTCHA on the current page.
     * Returns true if solved successfully, false if all attempts failed.
     */
    static async solve(page: Page, reason: string, cursor: Cursor | null): Promise<boolean> {
        console.log(`\n🧩 [CaptchaSolver] CAPTCHA detected: "${reason}". Starting AI vision solver...`);

        for (let attempt = 1; attempt <= this.MAX_ATTEMPTS; attempt++) {
            console.log(`\n  [CaptchaSolver] Attempt ${attempt}/${this.MAX_ATTEMPTS}`);

            try {
                // Step 1: Identify CAPTCHA type
                const captchaInfo = await identifyCaptcha(page);
                console.log(`  [CaptchaSolver] Type: ${captchaInfo.type}`);

                // Step 2: Handle based on type
                const solved = await this.handleCaptchaType(page, cursor, captchaInfo);

                if (solved) {
                    // Step 3: Wait and verify the CAPTCHA is gone
                    await humanDelay(3000, 5000);

                    const stillBlocked = await this.isStillBlocked(page);
                    if (!stillBlocked) {
                        console.log(`  ✅ [CaptchaSolver] CAPTCHA solved successfully on attempt ${attempt}!`);
                        return true;
                    }
                    console.log(`  [CaptchaSolver] Page still blocked after attempt ${attempt}, retrying...`);
                }
            } catch (err: any) {
                console.error(`  [CaptchaSolver] Attempt ${attempt} error:`, err.message);
            }

            // Brief pause between attempts
            await humanDelay(2000, 4000);
        }

        console.log(`  ❌ [CaptchaSolver] All ${this.MAX_ATTEMPTS} attempts failed.`);
        return false;
    }

    /**
     * Handle a specific CAPTCHA type.
     */
    private static async handleCaptchaType(page: Page, cursor: Cursor | null, info: CaptchaInfo): Promise<boolean> {
        switch (info.type) {
            case 'cloudflare_js': {
                // Cloudflare JS challenge auto-solves — just wait
                console.log('  [CaptchaSolver] Cloudflare JS challenge — waiting for auto-solve...');
                await humanDelay(6000, 10000);
                return true;
            }

            case 'recaptcha_checkbox':
            case 'hcaptcha_checkbox':
            case 'cloudflare_turnstile': {
                if (!info.frame) return false;

                // Click the checkbox
                await clickCheckbox(page, info.frame, cursor);

                // Check if an image challenge appeared
                const imageChallenge = await checkForImageChallenge(page);
                if (imageChallenge) {
                    console.log('  [CaptchaSolver] Image challenge appeared after checkbox click');
                    return await this.solveImageChallenge(page, cursor, imageChallenge);
                }

                return true;
            }

            case 'recaptcha_image':
            case 'hcaptcha_image': {
                return await this.solveImageChallenge(page, cursor, info);
            }

            case 'text_captcha': {
                return await this.solveTextCaptcha(page, cursor);
            }

            case 'generic_verification': {
                return await this.solveGenericVerification(page, cursor);
            }

            default: {
                // Unknown type — try generic vision approach
                return await this.solveGenericVerification(page, cursor);
            }
        }
    }

    /**
     * Solve an image grid challenge (reCAPTCHA/hCaptcha).
     */
    private static async solveImageChallenge(page: Page, cursor: Cursor | null, info: CaptchaInfo): Promise<boolean> {
        if (!info.frame) return false;

        // Screenshot the challenge
        const screenshot = await screenshotCaptcha(page, info);

        // Ask vision LLM
        console.log(`  [CaptchaSolver] Sending image challenge to vision LLM (instruction: "${info.instruction?.substring(0, 60)}")...`);
        const solution = await askVisionLLM(screenshot, info.type, info.instruction);

        if (!solution || !Array.isArray(solution)) {
            console.warn('  [CaptchaSolver] LLM did not return a valid tile array');
            return false;
        }

        console.log(`  [CaptchaSolver] LLM selected tiles: [${solution.join(', ')}]`);

        // Click the tiles
        await clickGridTiles(page, info.frame, cursor, solution);

        // Click verify/submit button
        await clickVerifyButton(page, info.frame, cursor);

        return true;
    }

    /**
     * Solve a text-based CAPTCHA.
     */
    private static async solveTextCaptcha(page: Page, cursor: Cursor | null): Promise<boolean> {
        const screenshot = await screenshotCaptcha(page, { type: 'text_captcha' });
        const solution = await askVisionLLM(screenshot, 'text_captcha');

        if (!solution || !solution.text) {
            console.warn('  [CaptchaSolver] LLM did not return CAPTCHA text');
            return false;
        }

        console.log(`  [CaptchaSolver] LLM read CAPTCHA text: "${solution.text}"`);

        // Find the input field and type the answer
        const inputSelector = await page.evaluate(() => {
            const inputs = document.querySelectorAll('input[name*="captcha"], input[id*="captcha"], input[placeholder*="captcha"]');
            if (inputs.length > 0) {
                const input = inputs[0] as HTMLInputElement;
                return input.id ? `#${input.id}` : (input.name ? `input[name="${input.name}"]` : 'input[type="text"]');
            }
            return null;
        }).catch(() => null);

        if (!inputSelector) {
            console.warn('  [CaptchaSolver] Could not find CAPTCHA input field');
            return false;
        }

        // Type with human-like delays
        await page.click(inputSelector);
        await humanDelay(200, 500);
        for (const char of solution.text) {
            await page.keyboard.type(char, { delay: 80 + Math.floor(Math.random() * 120) });
        }
        await humanDelay(500, 1000);

        // Try to submit
        await page.keyboard.press('Enter');
        return true;
    }

    /**
     * Solve a generic verification challenge using full-page vision analysis.
     */
    private static async solveGenericVerification(page: Page, cursor: Cursor | null): Promise<boolean> {
        const screenshot = await screenshotCaptcha(page, { type: 'generic_verification' });
        const solution = await askVisionLLM(screenshot, 'generic_verification');

        if (!solution || !solution.action || solution.action === 'unknown') {
            console.warn('  [CaptchaSolver] LLM could not determine verification action');
            return false;
        }

        if (solution.action === 'click' && solution.x && solution.y) {
            console.log(`  [CaptchaSolver] Clicking verification element at (${solution.x}, ${solution.y})`);
            await clickAtCoords(page, cursor, solution.x, solution.y);
            return true;
        }

        if (solution.action === 'type' && solution.text) {
            const selector = solution.selector || 'input[type="text"]';
            console.log(`  [CaptchaSolver] Typing "${solution.text}" into ${selector}`);
            await page.click(selector);
            await humanDelay(200, 500);
            for (const char of solution.text) {
                await page.keyboard.type(char, { delay: 80 + Math.floor(Math.random() * 120) });
            }
            await page.keyboard.press('Enter');
            return true;
        }

        return false;
    }

    /**
     * Check if the page is still blocked after a solve attempt.
     */
    private static async isStillBlocked(page: Page): Promise<boolean> {
        const check = await page.evaluate(() => {
            const body = document.body?.innerText?.toLowerCase() || '';
            const title = document.title?.toLowerCase() || '';

            // CAPTCHA indicators
            if (body.includes('verify you are human') || body.includes('are you a robot')) return true;
            if (body.includes('just a moment') && body.includes('checking your browser')) return true;

            // Check for CAPTCHA iframes
            const iframes = Array.from(document.querySelectorAll('iframe'));
            for (const iframe of iframes) {
                const src = (iframe as HTMLIFrameElement).src?.toLowerCase() || '';
                if (src.includes('recaptcha') || src.includes('hcaptcha')) {
                    // Check if the CAPTCHA is still visible/unchecked
                    const rect = iframe.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) return true;
                }
            }

            // Access denied / error pages
            if (title.includes('access denied') || title.includes('forbidden')) return true;
            if (body.length < 1500 && (title.includes('error') || body.includes('access denied'))) return true;

            return false;
        }).catch(() => false);

        return check;
    }
}
