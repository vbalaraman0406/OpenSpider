const fs = require('fs');
const tempFile = 'trump_temp_posts.json';
const stateFile = 'trump_last_seen.txt';

let extractedPosts = JSON.parse(fs.readFileSync(tempFile, 'utf-8'));
let lastSeen = "";
try { lastSeen = fs.readFileSync(stateFile, 'utf-8').trim(); } catch(e) {}

const newPosts = [];
let latestText = "";

for (const post of extractedPosts) {
    if (!post) continue;
    const postText = typeof post === 'string' ? post.trim() : (post.text || '').trim();
    if (!postText) continue;
    
    console.log("postText:", postText.substring(0, 50));
    console.log("lastSeen:", lastSeen.substring(0, 50));
    console.log("Match?", postText === lastSeen);
    
    if (postText === lastSeen) break;
    if (!latestText) latestText = postText;
    newPosts.push(postText);
}
console.log("newPosts length:", newPosts.length);
