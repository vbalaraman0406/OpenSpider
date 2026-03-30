const https = require('https');

function fetch(url, headers) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      headers: headers || {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*'
      },
      rejectUnauthorized: false
    };
    const req = https.request(options, (res) => {
      let data = '';
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        resolve({redirect: res.headers.location, status: res.statusCode});
        return;
      }
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({data, status: res.statusCode}));
    });
    req.on('error', reject);
    req.setTimeout(15000, () => { req.destroy(); reject(new Error('timeout')); });
    req.end();
  });
}

async function main() {
  console.log('=== SEARCHING REDFIN ===');
  
  // First, find Vancouver WA on Redfin by searching
  try {
    const searchUrl = 'https://www.redfin.com/stingray/do/location-autocomplete?location=Vancouver%20WA&v=2';
    const result = await fetch(searchUrl, {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      'Accept': '*/*',
      'Referer': 'https://www.redfin.com/'
    });
    let raw = result.data;
    if (raw.startsWith('{}&&')) raw = raw.substring(4);
    console.log('Autocomplete response (' + result.status + '): ' + raw.substring(0, 500));
  } catch(e) {
    console.log('Autocomplete error: ' + e.message);
  }
  
  // Try direct Redfin GIS API with broader search using lat/lng bounds for Vancouver WA area
  try {
    const gisUrl = 'https://www.redfin.com/stingray/api/gis?al=1&market=portland&num_homes=100&ord=days-on-redfin-asc&page_number=1&poly=-122.85%2045.55%2C-122.3%2045.55%2C-122.3%2045.85%2C-122.85%2045.85%2C-122.85%2045.55&sf=1,2,3,5,6,7&min_price=0&max_price=600000&num_beds=5&num_baths=2&min_year_built=2017&v=8';
    const result = await fetch(gisUrl, {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      'Accept': '*/*',
      'Referer': 'https://www.redfin.com/'
    });
    let raw = result.data;
    if (raw.startsWith('{}&&')) raw = raw.substring(4);
    console.log('GIS response status: ' + result.status + ', length: ' + raw.length);
    if (raw.length > 50) {
      try {
        const data = JSON.parse(raw);
        const homes = (data.payload && data.payload.homes) || [];
        console.log('Found ' + homes.length + ' homes in Vancouver WA area');
        homes.forEach(h => {
          const price = (h.price && h.price.value) || h.price || 'N/A';
          const beds = h.beds || 'N/A';
          const baths = h.baths || 'N/A';
          const sqft = (h.sqFt && h.sqFt.value) || h.sqFt || 'N/A';
          const yr = (h.yearBuilt && h.yearBuilt.value) || h.yearBuilt || 'N/A';
          const street = (h.streetLine && h.streetLine.value) || h.streetLine || '';
          const city = h.city || '';
          const zip = h.zip || '';
          const urlPath = h.url || '';
          console.log('  $' + price + ' | ' + beds + 'bd/' + baths + 'ba | ' + sqft + 'sqft | ' + yr + ' | ' + street + ', ' + city + ' | https://www.redfin.com' + urlPath);
        });
      } catch(e) {
        console.log('JSON parse error: ' + e.message);
        console.log('First 300 chars: ' + raw.substring(0, 300));
      }
    } else {
      console.log('Response too short: ' + raw);
    }
  } catch(e) {
    console.log('GIS error: ' + e.message);
  }
}

main().catch(e => console.log('Fatal: ' + e.message));
