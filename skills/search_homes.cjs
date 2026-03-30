const https = require('https');

function fetchUrl(url, headers) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      headers: headers || {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': '*/*'
      },
      rejectUnauthorized: false
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({data, status: res.statusCode, headers: res.headers}));
    });
    req.on('error', reject);
    req.setTimeout(15000, () => { req.destroy(); reject(new Error('timeout')); });
    req.end();
  });
}

async function main() {
  const allListings = [];
  
  console.log('=== SEARCHING REDFIN API ===');
  
  // Search using lat/lng polygon for Vancouver WA area (includes Ridgefield, Battle Ground, Camas, Washougal, Brush Prairie)
  try {
    const gisUrl = 'https://www.redfin.com/stingray/api/gis?al=1&market=portland&num_homes=100&ord=days-on-redfin-asc&page_number=1&poly=-122.85%2045.55%2C-122.3%2045.55%2C-122.3%2045.85%2C-122.85%2045.85%2C-122.85%2045.55&sf=1,2,3,5,6,7&min_price=0&max_price=600000&num_beds=5&num_baths=2&min_year_built=2017&v=8';
    const hdrs = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept': '*/*',
      'Referer': 'https://www.redfin.com/'
    };
    const result = await fetchUrl(gisUrl, hdrs);
    let raw = result.data;
    if (raw.startsWith('{}&&')) raw = raw.substring(4);
    console.log('GIS status: ' + result.status + ', length: ' + raw.length);
    if (raw.length > 50) {
      try {
        const data = JSON.parse(raw);
        const homes = (data.payload && data.payload.homes) || [];
        console.log('Found ' + homes.length + ' homes in Vancouver WA area');
        homes.forEach(h => {
          const price = (h.price && h.price.value) || h.price || 0;
          const beds = h.beds || 0;
          const baths = h.baths || 0;
          const sqft = (h.sqFt && h.sqFt.value) || h.sqFt || 0;
          const yr = (h.yearBuilt && h.yearBuilt.value) || h.yearBuilt || 0;
          const street = (h.streetLine && h.streetLine.value) || h.streetLine || '';
          const city = h.city || '';
          const zip = h.zip || '';
          const urlPath = h.url || '';
          // Filter: 2.5-3 baths and year >= 2017
          const bathsF = parseFloat(baths);
          const yrF = parseInt(yr);
          if (bathsF < 2.5 || bathsF > 3.0) return;
          if (yrF < 2017) return;
          const listing = {
            address: street + ', ' + city + ', WA ' + zip,
            price: price,
            beds: beds,
            baths: baths,
            sqft: sqft,
            year_built: yr,
            source: 'Redfin',
            link: 'https://www.redfin.com' + urlPath
          };
          allListings.push(listing);
          console.log('  $' + price + ' | ' + beds + 'bd/' + baths + 'ba | ' + sqft + 'sqft | ' + yr + ' | ' + street + ', ' + city);
        });
      } catch(e) {
        console.log('JSON parse error: ' + e.message);
        console.log('First 500 chars: ' + raw.substring(0, 500));
      }
    } else {
      console.log('Short response: ' + raw.substring(0, 200));
    }
  } catch(e) {
    console.log('GIS error: ' + e.message);
  }
  
  console.log('\nTotal listings found: ' + allListings.length);
  
  // Save results
  const fs = require('fs');
  fs.writeFileSync('listings_results.json', JSON.stringify(allListings, null, 2));
  console.log('Results saved to listings_results.json');
}

main().catch(e => console.log('Fatal: ' + e.message));
