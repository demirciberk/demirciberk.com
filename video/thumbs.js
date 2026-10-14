// Generate the 16:10 project thumbnails used on the homepage (assets/thumbs/*.jpg, 1440x900).
// Needs the site served on :8765 (python -m http.server 8765 from the repo root).
// usage: node video/thumbs.js [fly|koku|cv-sender|medical ...]   (no args = all four)
const { chromium } = require('playwright-core');
const fs = require('fs'), path = require('path'), os = require('os');
const OUT = path.join(__dirname, '..', 'assets', 'thumbs');
const BASE = 'http://localhost:8765/demo/';
// per-shot viewport [w, h, deviceScaleFactor]; every combination renders 1440x900 (16:10)
const VP = { fly: [1200, 750, 1.2], koku: [1200, 750, 1.2], 'cv-sender': [1200, 750, 1.2], medical: [1100, 688, 1440 / 1100] };
const HIDE_BAR = '.backbar { display: none !important; }';

const shots = {
  async fly(p) {
    await p.goto(BASE + 'fly/index.html');
    await p.waitForFunction(() => document.getElementById('loading').classList.contains('done'), null, { timeout: 120000 });
    await p.addStyleTag({ content: HIDE_BAR });
    await p.click('button.go[data-go="club"]');
    await p.waitForTimeout(+process.env.FLY_MS || 25000); // airborne, plume trail and picks visible
    await p.evaluate(() => document.getElementById('world').scrollIntoView({ block: 'start' }));
    await p.waitForTimeout(300);
  },
  async koku(p) {
    await p.goto(BASE + 'koku/index.html');
    await p.waitForSelector('#final li');
    await p.addStyleTag({ content: HIDE_BAR });
    await p.evaluate(() => scrollTo(0, 70));
  },
  async 'cv-sender'(p) {
    await p.goto(BASE + 'cv-sender/index.html');
    await p.waitForSelector('#list button');
    await p.addStyleTag({ content: HIDE_BAR });
    // pick the first scored company that has a drafted email and a real industry
    const n = await p.locator('#list button').count();
    for (let i = 0; i < n; i++) {
      await p.locator('#list button').nth(i).click();
      if (await p.locator('.mail').count() && !(await p.locator('#detail p').first().innerText()).startsWith('Unknown')) break;
    }
    // scroll so the company list and the whole detail panel (with the drafted email starting) fill the frame
    await p.evaluate((o) => scrollTo(0, document.querySelector('#list').getBoundingClientRect().top + scrollY - o), +process.env.CV_O || 20);
  },
  async medical(p) {
    await p.goto(BASE + 'medical/index.html');
    await p.addStyleTag({ content: HIDE_BAR });
    await p.fill('[name=age]', '45'); await p.fill('[name=bmi]', '31.5'); await p.fill('[name=children]', '2');
    await p.selectOption('[name=smoker]', 'yes'); await p.selectOption('[name=region]', 'northeast');
    await p.evaluate((y) => { document.activeElement.blur(); scrollTo(0, y); }, +process.env.MED_Y || 60);
  },
};

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const names = process.argv.slice(2).length ? process.argv.slice(2) : Object.keys(shots);
  const b = await chromium.launch({ executablePath: path.join(os.homedir(), 'AppData/Local/ms-playwright/chromium-1243/chrome-win64/chrome.exe'), args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  for (const n of names) {
    const [vw, vh, dpr] = VP[n];
    const p = await b.newPage({ viewport: { width: vw, height: vh }, deviceScaleFactor: dpr });
    await shots[n](p);
    await p.waitForTimeout(400);
    await p.screenshot({ path: path.join(OUT, n + '.jpg'), type: 'jpeg', quality: 80 });
    console.log(n, fs.statSync(path.join(OUT, n + '.jpg')).size);
    await p.close();
  }
  await b.close();
})();
