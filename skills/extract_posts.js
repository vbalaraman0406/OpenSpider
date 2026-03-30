// JavaScript to extract posts from Truth Social aggregator page
// This script will be executed via browse_web execute_js command
// It extracts post elements, timestamps, and content, then returns as JSON

function extractPosts() {
    const posts = [];
    // Adjust selectors based on actual page structure
    // Common selectors for posts: div with classes containing 'post', 'tweet', 'status', etc.
    const postElements = document.querySelectorAll('div[class*="post"], div[class*="tweet"], div[class*="status"], div[class*="item"]');
    
    postElements.forEach((post, index) => {
        // Extract timestamp
        let timestamp = null;
        const timeElement = post.querySelector('time');
        if (timeElement && timeElement.getAttribute('datetime')) {
            timestamp = timeElement.getAttribute('datetime');
        } else {
            const timeText = post.querySelector('span[class*="time"], span[class*="date"]');
            if (timeText) {
                timestamp = timeText.innerText.trim();
            }
        }
        
        // Extract content
        let content = '';
        const contentElement = post.querySelector('div[class*="content"], div[class*="text"], div[class*="body"]');
        if (contentElement) {
            content = contentElement.innerText.trim();
        } else {
            content = post.innerText.trim();
        }
        
        // Extract topic/summary (e.g., hashtags)
        let topic = 'Not specified';
        const hashtagElements = post.querySelectorAll('a[class*="hashtag"]');
        if (hashtagElements.length > 0) {
            topic = Array.from(hashtagElements).map(tag => tag.innerText.trim()).join(', ');
        } else {
            // Use first 20 characters as summary
            topic = content.substring(0, 20) + (content.length > 20 ? '...' : '');
        }
        
        if (timestamp) {
            posts.push({
                timestamp: timestamp,
                topic: topic,
                content: content
            });
        }
    });
    
    return JSON.stringify(posts);
}

return extractPosts();