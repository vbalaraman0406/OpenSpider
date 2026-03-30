const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function createTruthSocialAccount() {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    try {
        // Step 1: Generate a temporary email (using a simple random email for demo; in production, use a service like Temp-Mail API)
        const randomEmail = `truth_${Date.now()}@tempinbox.com`; // Placeholder; replace with real temp email if needed
        const password = 'SecurePass123!'; // Use a strong password
        const username = `trump_monitor_${Math.floor(Math.random() * 10000)}`;
        
        // Step 2: Navigate to Truth Social signup page
        await page.goto('https://truthsocial.com', { waitUntil: 'networkidle2' });
        
        // Click signup link - adjust selector based on actual page structure
        await page.waitForSelector('a[href*="/sign-up"]', { timeout: 10000 });
        await page.click('a[href*="/sign-up"]');
        
        // Fill signup form
        await page.waitForSelector('input[name="email"]', { timeout: 10000 });
        await page.type('input[name="email"]', randomEmail);
        await page.type('input[name="password"]', password);
        await page.type('input[name="username"]', username);
        // Add other required fields if any (e.g., name, birthdate) - adjust based on actual form
        
        // Submit form
        await page.click('button[type="submit"]');
        
        // Wait for signup to complete and redirect to logged-in page
        await page.waitForNavigation({ waitUntil: 'networkidle2' });
        
        // Step 3: Save session cookies
        const cookies = await page.cookies();
        const sessionPath = path.join(__dirname, '../workspace/truth_social_session.json');
        fs.writeFileSync(sessionPath, JSON.stringify(cookies, null, 2));
        
        console.log(`Account created with email: ${randomEmail}, username: ${username}`);
        console.log(`Session saved to: ${sessionPath}`);
        
        // Step 4: Verify login by checking a protected page (e.g., feed)
        await page.goto('https://truthsocial.com/feed', { waitUntil: 'networkidle2' });
        const pageTitle = await page.title();
        console.log(`Logged in successfully, page title: ${pageTitle}`);
        
    } catch (error) {
        console.error('Error during account creation:', error);
    } finally {
        await browser.close();
    }
}

// Run if script is executed directly
if (require.main === module) {
    createTruthSocialAccount();
}

module.exports = { createTruthSocialAccount };