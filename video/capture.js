// Record the fly wardrobe demo frame-perfect: rAF and performance.now run on a virtual clock.
// Frames are saved as <outdir>/<frame>.jpg (30fps, numbered from the destination click), at 3x pixel density.
// Needs the site served on :8765 (python -m http.server 8765 from the repo root).
// usage: node capture.js <scene> <fromSec> <toSec> <outdir>
const { chromium } = require('playwright-core');
const fs = require('fs'), path = require('path'), os = require('os');
const [scene, from, to, outdir] = process.argv.slice(2); const FPS = 30, DPR = 3;
(async () => {
  fs.mkdirSync(outdir, { recursive: true });
  const b = await chromium.launch({ executablePath: path.join(os.homedir(), 'AppData/Local/ms-playwright/chromium-1243/chrome-win64/chrome.exe'), args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: DPR });
  // the demo caps WebGL at 2x pixel ratio; lift the cap for capture only
  await p.route('**/demo/fly/index.html', async r => {
    const res = await r.fetch(); r.fulfill({ response: res, body: (await res.text()).replaceAll('Math.min(devicePixelRatio, 2)', 'devicePixelRatio') });
  });
  await p.addInitScript(() => {
    let now = 0, q = [], s = 42;
    performance.now = () => now;
    Math.random = () => (s = (s * 16807) % 2147483647) / 2147483647;
    window.requestAnimationFrame = cb => { q.push(cb); return q.length; };
    window.__tick = ms => { now += ms; const cbs = q; q = []; cbs.forEach(cb => cb(now)); };
  });
  await p.goto('http://localhost:8765/demo/fly/index.html');
  await p.addStyleTag({ content: '.backbar{display:none!important}' }); // hide the sticky back bar so framing matches the showreel crops
  await p.waitForFunction(() => document.getElementById('loading').classList.contains('done'), null, { timeout: 120000 });
  for (let i = 0; i < 30; i++) await p.evaluate(() => __tick(1000 / 30));
  await p.click(`button.go[data-go="${scene}"]`);
  for (let i = 0; i < to * FPS; i++) {
    await p.evaluate(() => __tick(1000 / 30));
    if (i < from * FPS) continue;
    await p.screenshot({ path: path.join(outdir, String(i + 1).padStart(4, '0') + '.jpg'), type: 'jpeg', quality: 90 });
    if (i % 30 === 0) console.log(scene, (i / FPS).toFixed(1));
  }
  await b.close();
})();
