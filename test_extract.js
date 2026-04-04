const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
chromium.use(stealth);

(async () => {
    console.log("Launching browser...");
    const browser = await chromium.launch({ headless: true });
    
    // mimic user agent
    const context = await browser.newContext({
        viewport: { width: 1280, height: 10000 }, // huge viewport
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    
    const page = await context.newPage();
    console.log("Navigating to Truth Social...");
    const response = await page.goto('https://truthsocial.com/@realDonaldTrump', { waitUntil: 'load', timeout: 30000 });
    
    console.log("Status:", response.status());
    console.log("Waiting for rendering (5 seconds)...");
    await page.waitForTimeout(5000);
    
    console.log("Executing strict DOM Purge logic...");
    const extractedText = await page.evaluate(() => {
        const tempDiv = document.createElement('div');
        Object.assign(tempDiv.style, { position: 'absolute', left: '-9999px', top: '-9999px', width: '800px' });
        
        const clone = document.createElement('div');
        clone.innerHTML = document.body.innerHTML;
        
        const unwanted = 'script, style, noscript, iframe, svg, canvas, video, audio, map, area, ' +
                         'nav, footer, header, aside, .cookie-banner, .popup, .modal, ' +
                         '[class*="ad-container"], [class*="advertisement"], [class*="sponsored"], [id*="google_ads"], ' + 
                         '[role="navigation"], [role="banner"], [role="contentinfo"], [role="complementary"]';
                         
        clone.querySelectorAll(unwanted).forEach(el => el.remove());
        
        // The Fix!
        clone.querySelectorAll('*').forEach(el => {
            if (el instanceof HTMLElement) {
                el.style.contentVisibility = 'visible';
            }
        });
        
        tempDiv.appendChild(clone);
        document.body.appendChild(tempDiv);
        
        const cleanedText = tempDiv.innerText;
        document.body.removeChild(tempDiv);
        return cleanedText || '';
    });
    
    console.log(`Extracted Payload Length: ${extractedText.length} characters\n`);
    
    if (extractedText.includes("JD Vance") || extractedText.includes("FRAUD")) {
        console.log("SUCCESS: JD Vance post found natively in the DOM output!");
    } else {
        console.log("FAILURE: Second post missing!");
    }
    
    require('fs').writeFileSync('ts_test_result.txt', extractedText.substring(0, 1500));
    await browser.close();
})();
