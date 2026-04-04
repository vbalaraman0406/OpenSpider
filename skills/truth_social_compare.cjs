const fs = require('fs');
const path = require('path');

async function main() {
    // Read WhatsApp JIDs from command-line arguments
    const jids = process.argv.slice(2);
    if (jids.length === 0) {
        console.error('No WhatsApp JIDs provided. Usage: node truth_social_compare.cjs <JID1> <JID2> ...');
        process.exit(1);
    }

    // Read the posts from trump_temp_posts.json (written in the skills directory)
    const postsPath = path.join(__dirname, 'trump_temp_posts.json');
    let posts = [];
    try {
        const data = fs.readFileSync(postsPath, 'utf8');
        posts = JSON.parse(data);
        console.log(`Read ${posts.length} posts from ${postsPath}`);
    } catch (err) {
        console.error(`Error reading ${postsPath}:`, err.message);
        process.exit(1);
    }

    if (posts.length === 0) {
        console.log('No posts found to process. Exiting.');
        return;
    }

    // Use the OpenSpider API URL and key injected by the sandbox executor
    const apiUrl = process.env.OPENSPIDER_API_URL || 'http://localhost:4001';
    const apiKey = process.env.OPENSPIDER_API_KEY || process.env.DASHBOARD_API_KEY;

    if (!apiKey) {
        console.error('Warning: OPENSPIDER_API_KEY is not set in the environment.');
    }

    // Format message payload
    console.log('Processing posts:');
    let msgText = `🚨 *Trump Truth Social Monitor*\n_Top ${posts.length} recent organic posts_\n\n`;
    posts.forEach((post, index) => {
        console.log(`Post ${index + 1}: Text: "${post.text}", Time: "${post.time}"`);
        msgText += `*${index + 1}. (${post.time})*\n${post.text}\n\n`;
    });
    msgText += `_Automated alert powered by OpenSpider_ 🕷️`;

    // Actually send WhatsApp alerts over API
    console.log(`\nDispatching actual WhatsApp alerts via OpenSpider Gateway API (${apiUrl}):`);
    for (const jid of jids) {
        console.log(`- ${jid}`);
        try {
            const resp = await fetch(`${apiUrl}/api/whatsapp/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': apiKey
                },
                body: JSON.stringify({ to: jid, text: msgText })
            });
            const result = await resp.json();
            if (resp.ok) {
                console.log(`  ✅ Successfully sent to ${jid}`);
            } else {
                console.error(`  ❌ Failed to send to ${jid}:`, result.error || JSON.stringify(result));
            }
        } catch (e) {
            console.error(`  ❌ Network error contacting WhatsApp API for ${jid}:`, e.message);
        }
    }

    console.log('\nTask completed successfully.');
}

main();
