const { chromium } = require('playwright');
const fs = require('fs');
const https = require('https');
const path = require('path');

const downloadFile = (url, dest) => {
  return new Promise((resolve, reject) => {
    if (!url) {
      resolve();
      return;
    }
    const file = fs.createWriteStream(dest);
    https.get(url, (response) => {
      response.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => {});
      reject(err);
    });
  });
};

const formatFilename = (name) => {
  return name.toLowerCase().replace(/[^a-z0-9]/g, '-') + '.png';
};

(async () => {
  console.log('Launching browser...');
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  // Scrape Drivers
  console.log('Navigating to F1 drivers page...');
  await page.goto('https://www.formula1.com/en/drivers', { waitUntil: 'domcontentloaded', timeout: 60000 });
  
  const drivers = await page.evaluate(() => {
    const panels = document.querySelectorAll('.f1-driver-snippet');
    const results = [];
    panels.forEach(p => {
      const nameEl = p.querySelector('.f1-heading');
      const imgEl = p.querySelector('picture img');
      if (nameEl && imgEl) {
        // Grab the name and clean it up (assuming First Last format)
        let name = nameEl.innerText.trim().replace(/\n/g, ' ');
        // Find highest quality image
        let src = imgEl.src;
        if (imgEl.hasAttribute('data-src')) src = imgEl.getAttribute('data-src');
        results.push({ name, src });
      }
    });
    return results;
  });

  console.log(`Found ${drivers.length} drivers on formula1.com`);
  for (const driver of drivers) {
    const filename = path.join(__dirname, 'public', 'assets', 'drivers', formatFilename(driver.name));
    if (!fs.existsSync(filename)) {
      console.log(`Downloading ${driver.name}...`);
      await downloadFile(driver.src, filename).catch(console.error);
    }
  }

  // Scrape Teams
  console.log('\nNavigating to F1 teams page...');
  await page.goto('https://www.formula1.com/en/teams', { waitUntil: 'domcontentloaded', timeout: 60000 });
  
  const teams = await page.evaluate(() => {
    const panels = document.querySelectorAll('.f1-team-snippet');
    const results = [];
    panels.forEach(p => {
      const nameEl = p.querySelector('.f1-heading');
      // The car image is usually the second picture or has a specific class
      const imgEls = p.querySelectorAll('picture img');
      
      let carImg = Array.from(imgEls).find(img => img.src.includes('car') || img.alt.includes('car'));
      if (!carImg && imgEls.length > 0) carImg = imgEls[0]; // fallback
      
      if (nameEl && carImg) {
        let name = nameEl.innerText.trim();
        let src = carImg.src;
        if (carImg.hasAttribute('data-src')) src = carImg.getAttribute('data-src');
        results.push({ name, src });
      }
    });
    return results;
  });

  console.log(`Found ${teams.length} teams on formula1.com`);
  for (const team of teams) {
    // We map formula1.com official team names to our expected JSON names
    const nameMap = {
      'Red Bull Racing': 'Oracle Red Bull Racing',
      'Ferrari': 'Scuderia Ferrari',
      'McLaren': 'McLaren F1 Team',
      'Mercedes': 'Mercedes-AMG Petronas',
      'Aston Martin': 'Aston Martin Aramco',
      'Alpine': 'BWT Alpine F1 Team',
      'Williams': 'Williams Racing',
      'Haas': 'MoneyGram Haas F1',
      'RB': 'Racing Bulls',
      'Kick Sauber': 'Audi F1 Team', // Projecting 2026 takeover
    };
    
    let targetName = nameMap[team.name] || team.name;
    const filename = path.join(__dirname, 'public', 'assets', 'teams', formatFilename(targetName));
    if (!fs.existsSync(filename)) {
      console.log(`Downloading ${targetName} car...`);
      await downloadFile(team.src, filename).catch(console.error);
    }
  }

  await browser.close();
  console.log('Finished scraping formula1.com!');
})();
