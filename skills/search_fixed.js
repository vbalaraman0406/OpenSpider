import https from 'https';
import fs from 'fs';

function fetchUrl(url, headers) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      headers: headers || {},
      rejectUnauthorized: false
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({data, status: res.statusCode, headers: res.headers}));
    });
    req.on('error', reject);
    req.setTimeout(20000, () => { req.destroy(); reject(new Error('timeout')); });
    req.end();
  });
}

async function main() {
  const allListings = [];
  
  console.log('=== REDFIN API - Vancouver WA Area ===');
  // Vancouver WA: 45.63, -122.67
  // Ridgefield: 45.82, -122.74
  // Battle Ground: 45.78, -122.53
  // Camas: 45.59, -122.42
  // Washougal: 45.58, -122.35
  // Brush Prairie: 45.73, -122.55
  // Bounding box: lat 45.55-45.85, lng -122.80 to -122.30
  const poly = '-122.80%2045.55%2C-122.30%2045.55%2C-122.30%2045.85%2C-122.80%2045.85%2C-122.80%2045.55';
  const gisUrl = 'https://www.redfin.com/stingray/api/gis?al=1&market=portland&num_homes=350&ord=days-on-redfin-asc&page_number=1&poly=' + poly + '&sf=1,2,3,5,6,7&min_price=0&max_price=600000&num_beds=5&num_baths=2&min_year_built=2017&v=8';
  const hdrs = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.redfin.com/'
  };
  
  try {
    const result = await fetchUrl(gisUrl, hdrs);
    let raw = result.data;
    if (raw.startsWith('{}&&')) raw = raw.substring(4);
    console.log('Status: ' + result.status + ', Length: ' + raw.length);
    
    if (raw.length > 50) {
      const data = JSON.parse(raw);
      const homes = (data.payload && data.payload.homes) || [];
      console.log('Total homes returned: ' + homes.length);
      
      homes.forEach((h, i) => {
        const price = typeof h.price === 'object' ? (h.price.value || 0) : (h.price || 0);
        const beds = h.beds || 0;
        const baths = h.baths || 0;
        const sqft = typeof h.sqFt === 'object' ? (h.sqFt.value || 0) : (h.sqFt || 0);
        const yr = typeof h.yearBuilt === 'object' ? (h.yearBuilt.value || 0) : (h.yearBuilt || 0);
        const street = typeof h.streetLine === 'object' ? (h.streetLine.value || '') : (h.streetLine || '');
        const city = h.city || '';
        const state = h.state || 'WA';
        const zip = h.zip || '';
        const urlPath = h.url || '';
        const lat = h.latLong ? h.latLong.latitude : '';
        const lng = h.latLong ? h.latLong.longitude : '';
        const bathsF = parseFloat(baths);
        const yrF = parseInt(yr);
        const bedsF = parseInt(beds);
        
        console.log((i+1) + '. $' + price + ' | ' + beds + 'bd/' + baths + 'ba | ' + sqft + 'sqft | ' + yr + ' | ' + street + ', ' + city + ' ' + state + ' | lat:' + lat + ' lng:' + lng);
        
        if (bedsF >= 5 && bathsF >= 2.5 && bathsF <= 3.0 && yrF >= 2017 && price <= 600000) {
          allListings.push({
            address: street + ', ' + city + ', ' + state + ' ' + zip,
            price: '$' + Number(price).toLocaleString(),
            beds: beds,
            baths: baths,
            sqft: sqft,
            year_built: yr,
            source: 'Redfin',
            link: 'https://www.redfin.com' + urlPath
          });
          console.log('  >>> MATCH!');
        }
      });
    }
  } catch(e) {
    console.log('Redfin error: ' + e.message);
  }
  
  console.log('\n=== RESULTS: ' + allListings.length + ' matching listings ===');
  allListings.forEach((l, i) => {
    console.log((i+1) + '. ' + l.address + ' | ' + l.price + ' | ' + l.beds + 'bd/' + l.baths + 'ba | ' + l.sqft + 'sqft | ' + l.year_built + ' | ' + l.source + ' | ' + l.link);
  });
  
  fs.writeFileSync('./listings_results.json', JSON.stringify(allListings, null, 2));
  console.log('Saved to listings_results.json');
}

main().catch(e => console.log('Fatal: ' + e.message));
