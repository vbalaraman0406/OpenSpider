const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
chromium.use(stealth);

(async () => {
    const browser = await chromium.launch({ headless: true });
    // Normal viewport
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 }, 
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    
    const page = await context.newPage();
    await page.goto('https://truthsocial.com/@realDonaldTrump', { waitUntil: 'load', timeout: 30000 });
    await page.waitForTimeout(5000);
    
    // THE ZOOM TRICK!
    await page.evaluate(() => {
        document.body.style.zoom = '0.1'; // 10% zoom
    });
    
    // Give React 2 seconds to fire Intersection observers and mount new posts!
    await page.waitForTimeout(2000);
    
    const extractedText = await page.evaluate(() => {
        const tempDiv = document.createElement('div');
        Object.assign(tempDiv.style, { position: 'absolute', left: '-9999px', top: '-9999px', width: '800px', zoom: '1' });
        
        const clone = document.createElement('div');
        clone.innerHTML = document.body.innerHTML;
        
        const unwanted = 'script, style, noscript, iframe, svg, canvas, video, audio, map, area, nav, footer, header, aside, .cookie-banner, .popup, .modal, [class*="ad-container"], [class*="advertisement"], [class*="sponsored"], [id*="google_ads"], [role="navigation"], [role="banner"], [role="contentinfo"], [role="complementary"]';
        clone.querySelectorAll(unwanted).forEach(el => el.remove());
        
        clone.querySelectorAll('*').forEach(el => {
            if (el instanceof HTMLElement) el.style.contentVisibility = 'visible';
        });
        
        tempDiv.appendChild(clone);
        document.body.appendChild(tempDiv);
        const cleanedText = tempDiv.innerText;
        document.body.removeChild(tempDiv);
        
        // Restore zoom
        document.body.style.zoom = '1';
        
        return cleanedText || '';
    });
    
    console.log(`Zoomed Viewport Length: ${extractedText.length}`);
    require('fs').writeFileSync('ts_test_zoom.txt', extractedText.substring(0, 1500));
    await browser.close();
})();
