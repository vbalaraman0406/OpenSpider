const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');

async function scrapeTrumpPosts() {
  try {
    const url = 'https://truthsocial.com/@realDonaldTrump';
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });
    
    const $ = cheerio.load(response.data);
    const posts = [];
    
    // Select article elements (adjust selector based on actual page structure)
    $('article').each((index, element) => {
      if (posts.length >= 5) return false; // Stop after 5 posts
      
      const text = $(element).text().trim();
      // Skip if contains indicators for sponsored, ad, or pinned (case-insensitive)
      const lowerText = text.toLowerCase();
      if (lowerText.includes('sponsored') || lowerText.includes('ad') || lowerText.includes('pinned')) {
        return; // Skip this post
      }
      
      if (text) {
        posts.push(text);
      }
    });
    
    // Save to file
    fs.writeFileSync('trump_temp_posts.json', JSON.stringify(posts, null, 2));
    console.log('Saved posts to trump_temp_posts.json:', posts);
    return posts;
  } catch (error) {
    console.error('Error scraping posts:', error.message);
    return [];
  }
}

// Run if called directly
if (require.main === module) {
  scrapeTrumpPosts().then(posts => {
    console.log('Extracted posts:', posts);
  });
}

module.exports = scrapeTrumpPosts;