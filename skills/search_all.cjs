const https = require('https');
const fs = require('fs');

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
  // Broader polygon covering Vancouver, Ridgefield, Battle Ground, Camas, Washougal, Brush Prairie
  // Lat: 45.55 to 45.90, Lng: -122.85 to -122.20
  const poly = '-122.85%2045.50%2C-122.15%2045.50%2C-122.15%2045.90%2C-122.85%2045.90%2C-122.85%2045.50';
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
      
      // Log ALL homes to see what we're getting
      homes.forEach((h, i) => {
        const price = (h.price && h.price.value) || h.price || 0;
        const beds = h.beds || 0;
        const baths = h.baths || 0;
        const sqft = (h.sqFt && h.sqFt.value) || h.sqFt || 0;
        const yr = (h.yearBuilt && h.yearBuilt.value) || h.yearBuilt || 0;
        const street = (h.streetLine && h.streetLine.value) || h.streetLine || '';
        const city = h.city || '';
        const zip = h.zip || '';
        const urlPath = h.url || '';
        const bathsF = parseFloat(baths);
        const yrF = parseInt(yr);
        const bedsF = parseInt(beds);
        
        console.log((i+1) + '. $' + price + ' | ' + beds + 'bd/' + baths + 'ba | ' + sqft + 'sqft | ' + yr + ' | ' + street + ', ' + city + ' ' + zip);
        
        // Filter: 5+ beds, 2.5-3 baths, year >= 2017, price <= 600000
        if (bedsF >= 5 && bathsF >= 2.5 && bathsF <= 3.0 && yrF >= 2017 && price <= 600000) {
          allListings.push({
            address: street + ', ' + city + ', WA ' + zip,
            price: '$' + price.toLocaleString(),
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
  
  // Now try Zillow API
  console.log('\n=== ZILLOW API ===');
  try {
    const zillowUrl = 'https://www.zillow.com/search/GetSearchPageState.htm?searchQueryState=%7B%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22north%22%3A45.90%2C%22south%22%3A45.50%2C%22east%22%3A-122.15%2C%22west%22%3A-122.85%7D%2C%22filterState%22%3A%7B%22beds%22%3A%7B%22min%22%3A5%7D%2C%22baths%22%3A%7B%22min%22%3A2%7D%2C%22price%22%3A%7B%22max%22%3A600000%7D%2C%22built%22%3A%7B%22min%22%3A%222017%22%7D%2C%22sort%22%3A%7B%22value%22%3A%22days%22%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%7D%7D&wants=%7B%22cat1%22%3A%5B%22listResults%22%5D%7D&requestId=1';
    const zhdrs = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept': '*/*',
      'Referer': 'https://www.zillow.com/'
    };
    const result = await fetchUrl(zillowUrl, zhdrs);
    console.log('Zillow status: ' + result.status + ', Length: ' + result.data.length);
    if (result.data.length > 100) {
      try {
        const zdata = JSON.parse(result.data);
        const cat1 = zdata.cat1 || {};
        const searchResults = cat1.searchResults || cat1.searchList || {};
        const listResults = searchResults.listResults || [];
        console.log('Zillow listings: ' + listResults.length);
        listResults.forEach((l, i) => {
          const addr = l.address || l.streetAddress || '';
          const price = l.unformattedPrice || l.price || '';
          const beds = l.beds || '';
          const baths = l.baths || '';
          const sqft = l.area || l.sqft || '';
          const link = l.detailUrl || '';
          console.log((i+1) + '. ' + addr + ' | $' + price + ' | ' + beds + 'bd/' + baths + 'ba | ' + sqft + 'sqft | ' + link);
          
          const bathsF = parseFloat(baths);
          if (bathsF >= 2.5 && bathsF <= 3.0) {
            allListings.push({
              address: addr,
              price: typeof price === 'number' ? '$' + price.toLocaleString() : price,
              beds: beds,
              baths: baths,
              sqft: sqft,
              year_built: 'N/A',
              source: 'Zillow',
              link: link.startsWith('http') ? link : 'https://www.zillow.com' + link
            });
            console.log('  >>> MATCH!');
          }
        });
      } catch(e) {
        console.log('Zillow JSON error: ' + e.message);
        console.log('First 500: ' + result.data.substring(0, 500));
      }
    }
  } catch(e) {
    console.log('Zillow error: ' + e.message);
  }
  
  console.log('\n=== FINAL RESULTS: ' + allListings.length + ' matching listings ===');
  allListings.forEach((l, i) => {
    console.log((i+1) + '. ' + l.address + ' | ' + l.price + ' | ' + l.beds + 'bd/' + l.baths + 'ba | ' + l.sqft + 'sqft | ' + l.year_built + ' | ' + l.source + ' | ' + l.link);
  });
  
  fs.writeFileSync('listings_results.json', JSON.stringify(allListings, null, 2));
  console.log('Saved to listings_results.json');
}

main().catch(e => console.log('Fatal: ' + e.message));
