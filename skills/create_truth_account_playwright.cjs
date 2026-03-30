const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

async function createTruthSocialAccount() {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // Generate temporary credentials
        const randomEmail = `truth_${Date.now()}@tempmail.com`; // Placeholder email
        const password = 'SecurePass123!';
        const username = `monitor_${Math.floor(Math.random() * 10000)}`;
        
        console.log(`Creating account with email: ${randomEmail}, username: ${username}`);
        
        // Navigate to Truth Social signup page
        await page.goto('https://truthsocial.com/sign-up', { waitUntil: 'networkidle' });
        
        // Fill signup form - adjust selectors based on actual page
        await page.fill('input[name="email"]', randomEmail);
        await page.fill('input[name="password"]', password);
        await page.fill('input[name="username"]', username);
        // Add other required fields if necessary (e.g., name)
        
        // Submit form
        await page.click('button[type="submit"]');
        await page.waitForNavigation({ waitUntil: 'networkidle' });
        
        // Save session cookies
        const cookies = await context.cookies();
        const sessionPath = path.join(__dirname, '../workspace/truth_social_session.json');
        fs.writeFileSync(sessionPath, JSON.stringify(cookies, null, 2));
        console.log(`Session saved to: ${sessionPath}`);
        
        // Verify login by checking feed
        await page.goto('https://truthsocial.com/feed');
        const title = await page.title();
        console.log(`Logged in successfully. Page title: ${title}`);
        
        return { email: randomEmail, username: username, sessionPath: sessionPath };
    } catch (error) {
        console.error('Error during account creation:', error);
        throw error;
    } finally {
        await browser.close();
    }
}

// Run if executed directly
if (require.main === module) {
    createTruthSocialAccount().then(result => {
        console.log('Account creation completed:', result);
    }).catch(err => {
        console.error('Account creation failed:', err);
        process.exit(1);
    });
}

module.exports = { createTruthSocialAccount };