const fs = require('fs');

const userString = `{"thought":"Google found a link for 'Fazzolari Construction Vancouver Washington'. Let me follow that Google search link to get more details. Also, Google Maps seems to have some data. Let me write a script to follow the Google search result and extract the actual business listing details.","action":"write_script","filename":"search_fazzolari7.py","content":"import requests\\nfrom bs4 import BeautifulSoup\\nimport json\\nimport re\\n\\nheaders = {\\n 'User-Agent':`;

const regex = /\{/g;
let match;
while ((match = regex.exec(userString)) !== null) {
    console.log(`Found "{" at position ${match.index}`);
    console.log(`Context: ${userString.substring(match.index - 20, match.index + 20).replace(/\\n/g, '\\\\n')}`);
}
