import puppeteer from 'puppeteer';
import fs from 'fs/promises';

async function scrapeTrumpPosts() {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://truthsocial.com/@realDonaldTrump', { waitUntil: 'networkidle2' });
  
  // Scroll down to render feed
  await page.evaluate(() => window.scrollBy(0, 1000));
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Extract post texts
  const posts = await page.evaluate(() => {
    const postElements = Array.from(document.querySelectorAll('article'));
    return postElements.slice(0, 5).map(el => {
      const text = el.innerText.trim();
      // Filter out 'Sponsored' or 'Pinned Truth'
      if (text.includes('Sponsored') || text.includes('Pinned Truth')) return null;
      return text;
    }).filter(Boolean);
  });
  
  await browser.close();
  return posts;
}

async function main() {
  try {
    const posts = await scrapeTrumpPosts();
    if (posts.length === 0) {
      console.log('No posts found.');
      return;
    }
    
    // Read last seen post
    let lastSeen = '';
    try {
      lastSeen = await fs.readFile('trump_last_seen.txt', 'utf8');
    } catch (err) {
      // File missing or empty
    }
    
    // Find new posts (those above lastSeen in the list)
    const lastSeenIndex = posts.indexOf(lastSeen.trim());
    let newPosts = [];
    if (lastSeenIndex === -1 || lastSeen === '') {
      // Last-seen post not found or file empty, assume only topmost post is new
      newPosts = [posts[0]];
    } else {
      newPosts = posts.slice(0, lastSeenIndex);
    }
    
    if (newPosts.length === 0) {
      console.log('No new posts.');
      return;
    }
    
    // Update high-water mark with newest topmost post
    await fs.writeFile('trump_last_seen.txt', posts[0]);
    
    // Prepare WhatsApp message
    const message = `*🚨 New Trump Truth Social Post(s) 🚨*

${newPosts.join('\n\n---\n\n')}`;
    console.log('New posts found. WhatsApp message prepared.');
    console.log('Message content:', message);
    console.log('Targets: 14156249639@s.whatsapp.net, 16507965072@s.whatsapp.net, 120363423852747118@g.us, 14156905841@s.whatsapp.net');
    
    // Output new posts for tool use
    console.log('NEW_POSTS_START');
    newPosts.forEach((post, i) => console.log(`Post ${i + 1}: ${post}`));
    console.log('NEW_POSTS_END');
  } catch (error) {
    console.error('Error:', error);
  }
}

main();
