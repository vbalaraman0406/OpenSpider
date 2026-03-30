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
  const hdrs = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.redfin.com/'
  };

  // Step 1: Find Vancouver WA region ID
  console.log('=== Finding Vancouver WA on Redfin ===');
  try {
    const autoUrl = 'https://www.redfin.com/stingray/do/location-autocomplete?location=Vancouver%2C%20WA&v=2';
    const result = await fetchUrl(autoUrl, hdrs);
    let raw = result.data;
    if (raw.startsWith('{}&&')) raw = raw.substring(4);
    console.log('Autocomplete status: ' + result.status);
    console.log('Response: ' + raw.substring(0, 1500));
  } catch(e) {
    console.log('Autocomplete error: ' + e.message);
  }

  // Step 2: Try multiple zip codes for Vancouver WA area
  const zips = ['98660','98661','98662','98663','98664','98665','98682','98683','98684','98685','98686'];
  const allListings = [];
  
  console.log('\n=== Searching by ZIP codes ===');
  for (const zip of zips) {
    try {
      const gisUrl = 'https://www.redfin.com/stingray/api/gis?al=1&market=portland&num_homes=50&ord=days-on-redfin-asc&page_number=1&region_id=' + zip + '&region_type=2&sf=1,2,3,5,6,7&min_price=0&max_price=600000&num_beds=5&num_baths=2&min_year_built=2017&v=8';
      const result = await fetchUrl(gisUrl, hdrs);
      let raw = result.data;
      if (raw.startsWith('{}&&')) raw = raw.substring(4);
      if (raw.length > 50) {
        const data = JSON.parse(raw);
        const homes = (data.payload && data.payload.homes) || [];
        console.log('ZIP ' + zip + ': ' + homes.length + ' homes');
        homes.forEach(h => {
          const price = typeof h.price === 'object' ? (h.price.value || 0) : (h.price || 0);
          const beds = h.beds || 0;
          const baths = h.baths || 0;
          const sqft = typeof h.sqFt === 'object' ? (h.sqFt.value || 0) : (h.sqFt || 0);
          const yr = typeof h.yearBuilt === 'object' ? (h.yearBuilt.value || 0) : (h.yearBuilt || 0);
          const street = typeof h.streetLine === 'object' ? (h.streetLine.value || '') : (h.streetLine || '');
          const city = h.city || '';
          const urlPath = h.url || '';
          const bathsF = parseFloat(baths);
          const yrF = parseInt(yr);
          
          if (bathsF >= 2.5 && bathsF <= 3.0 && yrF >= 2017) {
            allListings.push({
              address: street + ', ' + city + ', WA ' + (h.zip || zip),
              price: '$' + Number(price).toLocaleString(),
              beds: beds,
              baths: baths,
              sqft: sqft,
              year_built: yr,
              source: 'Redfin',
              link: 'https://www.redfin.com' + urlPath
            });
            console.log('  MATCH: $' + price + ' | ' + beds + 'bd/' + baths + 'ba | ' + sqft + 'sqft | ' + yr + ' | ' + street + ', ' + city);
          }
        });
      } else {
        console.log('ZIP ' + zip + ': no data');
      }
    } catch(e) {
      console.log('ZIP ' + zip + ': error - ' + e.message);
    }
  }
  
  // Also search Ridgefield, Battle Ground, Camas, Washougal zips
  const extraZips = ['98642','98604','98607','98671'];
  for (const zip of extraZips) {
    try {
      const gisUrl = 'https://www.redfin.com/stingray/api/gis?al=1&market=portland&num_homes=50&ord=days-on-redfin-asc&page_number=1&region_id=' + zip + '&region_type=2&sf=1,2,3,5,6,7&min_price=0&max_price=600000&num_beds=5&num_baths=2&min_year_built=2017&v=8';
      const result = await fetchUrl(gisUrl, hdrs);
      let raw = result.data;
      if (raw.startsWith('{}&&')) raw = raw.substring(4);
      if (raw.length > 50) {
        const data = JSON.parse(raw);
        const homes = (data.payload && data.payload.homes) || [];
        console.log('ZIP ' + zip + ': ' + homes.length + ' homes');
        homes.forEach(h => {
          const price = typeof h.price === 'object' ? (h.price.value || 0) : (h.price || 0);
          const beds = h.beds || 0;
          const baths = h.baths || 0;
          const sqft = typeof h.sqFt === 'object' ? (h.sqFt.value || 0) : (h.sqFt || 0);
          const yr = typeof h.yearBuilt === 'object' ? (h.yearBuilt.value || 0) : (h.yearBuilt || 0);
          const street = typeof h.streetLine === 'object' ? (h.streetLine.value || '') : (h.streetLine || '');
          const city = h.city || '';
          const urlPath = h.url || '';
          const bathsF = parseFloat(baths);
          const yrF = parseInt(yr);
          
          if (bathsF >= 2.5 && bathsF <= 3.0 && yrF >= 2017) {
            allListings.push({
              address: street + ', ' + city + ', WA ' + (h.zip || zip),
              price: '$' + Number(price).toLocaleString(),
              beds: beds,
              baths: baths,
              sqft: sqft,
              year_built: yr,
              source: 'Redfin',
              link: 'https://www.redfin.com' + urlPath
            });
            console.log('  MATCH: $' + price + ' | ' + beds + 'bd/' + baths + 'ba | ' + sqft + 'sqft | ' + yr + ' | ' + street + ', ' + city);
          }
        });
      } else {
        console.log('ZIP ' + zip + ': no data');
      }
    } catch(e) {
      console.log('ZIP ' + zip + ': error - ' + e.message);
    }
  }
  
  console.log('\n=== TOTAL MATCHES: ' + allListings.length + ' ===');
  allListings.forEach((l, i) => {
    console.log((i+1) + '. ' + l.address + ' | ' + l.price + ' | ' + l.beds + 'bd/' + l.baths + 'ba | ' + l.sqft + 'sqft | ' + l.year_built + ' | ' + l.link);
  });
  
  fs.writeFileSync('./listings_results.json', JSON.stringify(allListings, null, 2));
  console.log('Saved to listings_results.json');
}

main().catch(e => console.log('Fatal: ' + e.message));
