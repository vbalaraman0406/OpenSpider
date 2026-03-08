const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const contexts = browser.contexts();
  const page = contexts[0].pages()[0];
  
  // Try to click on Lawson by evaluating JS in the page
  await page.evaluate(() => {
    const items = document.querySelectorAll('*');
    for (const item of items) {
      if (item.children.length === 0 && item.textContent.trim() === 'LAWSON') {
        item.click();
        console.log('Clicked LAWSON element');
        break;
      }
    }
  });
  
  await page.waitForTimeout(1500);
  
  // Check if detail panel changed to Lawson
  const detailText = await page.evaluate(() => {
    const buttons = document.querySelectorAll('button');
    const texts = [];
    buttons.forEach(b => texts.push(b.textContent.trim()));
    const allText = document.body.innerText.substring(0, 500);
    return JSON.stringify({buttons: texts.slice(0,10), page: allText});
  });
  console.log(detailText);
  
  await browser.close();
})();