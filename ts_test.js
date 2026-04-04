const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto('https://truthsocial.com/@realDonaldTrump', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(5000);
    const text = await page.evaluate(() => document.body.innerText);
    require('fs').writeFileSync('/tmp/ts_test.txt', text);
    console.log("Characters:", text.length);
    await browser.close();
})();
