// usage: node render.js out.mp4            -> full render
//        node render.js --stills 2,6,12    -> PNG stills for review
const { chromium } = require('playwright-core');
const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

const CHROME = path.join(os.homedir(), 'AppData/Local/ms-playwright/chromium-1243/chrome-win64/chrome.exe');
const FFMPEG = process.env.FFMPEG;
const FPS = 30;

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(__dirname, process.env.COMP || 'comp.html'));
  await page.evaluate(() => window.ready);
  const dur = await page.evaluate(() => window.DURATION);

  if (process.argv[2] === '--stills') {
    for (const t of process.argv[3].split(',').map(Number)) {
      await page.evaluate(t => seek(t), t);
      await page.screenshot({ path: path.join(__dirname, `still_${process.env.COMP ? 'g' : ''}${t}.png`) });
    }
  } else {
    const out = process.argv[2] || 'out.mp4';
    const ff = spawn(FFMPEG, ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', process.env.CRF || '18', '-preset', 'slow', '-movflags', '+faststart', out],
      { stdio: ['pipe', 'inherit', 'inherit'] });
    const n = Math.round(dur * FPS);
    for (let i = 0; i < n; i++) {
      await page.evaluate(t => seek(t), i / FPS);
      ff.stdin.write(await page.screenshot({ type: 'png' }));
      if (i % 90 === 0) console.log(`frame ${i}/${n}`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
