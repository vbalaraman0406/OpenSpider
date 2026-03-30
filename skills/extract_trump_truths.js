// Extract Trump's Truth Social posts from trumpstruth.org using DOM traversal
const posts = [];

// Get all elements that could potentially be a post container or part of a post
const allElements = document.querySelectorAll('div.col-md-12.col-lg-8.mx-auto.mb-4');

allElements.forEach(container => {
    const timestampSpan = container.querySelector('span.text-muted');
    const originalPostHeader = container.querySelector('span.font-weight-bold');

    if (timestampSpan && originalPostHeader && originalPostHeader.textContent.trim() === 'Original Post') {
        const timestampText = timestampSpan.textContent.trim();
        const timestamp = timestampText.replace('@realDonaldTrump · ', '').trim();

        let contentParts = [];
        let currentElement = originalPostHeader.nextElementSibling;

        while (currentElement) {
            // Stop if we hit the next post's timestamp or original post header
            if (currentElement.querySelector('span.text-muted') || currentElement.querySelector('span.font-weight-bold')) {
                break;
            }

            // Extract text from paragraph tags
            const paragraphs = currentElement.querySelectorAll('p');
            if (paragraphs.length > 0) {
                paragraphs.forEach(p => {
                    const text = p.textContent.trim();
                    if (text) contentParts.push(text);
                });
            } else {
                // Check for links
                const linkTitle = currentElement.querySelector('a.link-title');
                const linkUrl = currentElement.querySelector('a.link-url');
                if (linkTitle && linkUrl) {
                    contentParts.push(`${linkTitle.textContent.trim()}: ${linkUrl.href}`);
                } else {
                    const text = currentElement.textContent.trim();
                    if (text) contentParts.push(text);
                }
            }
            currentElement = currentElement.nextElementSibling;
        }
        
        const content = contentParts.join(' ').trim();
        if (content) {
            posts.push({ timestamp, content });
        }
    }
});

return JSON.stringify(posts, null, 2);