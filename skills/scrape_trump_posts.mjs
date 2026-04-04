import puppeteer from 'puppeteer';
import fs from 'fs';

async function scrapeTrumpPosts() {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    await page.goto('https://truthsocial.com/@realDonaldTrump', { waitUntil: 'networkidle2' });
    await page.waitForSelector('article', { timeout: 10000 });
    
    const posts = await page.evaluate(() => {
      const articles = Array.from(document.querySelectorAll('article'));
      const organicPosts = [];
      
      for (const article of articles) {
        if (article.textContent.includes('Sponsored') || article.textContent.includes('Ad') || article.textContent.includes('Pinned')) {
          continue;
        }
        const postText = article.textContent.trim();
        if (postText) {
          organicPosts.push(postText);
        }
        if (organicPosts.length >= 5) {
          break;
        }
      }
      return organicPosts;
    });
    
    fs.writeFileSync('trump_temp_posts.json', JSON.stringify(posts, null, 2));
    console.log('Saved posts to trump_temp_posts.json:', posts);
    await browser.close();
    return posts;
  } catch (error) {
    console.error('Error scraping posts:', error);
    await browser.close();
    return [];
  }
}

// Run the function
scrapeTrumpPosts().then(posts => {
  console.log('Extracted posts:', posts);
});