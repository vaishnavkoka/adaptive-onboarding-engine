
const { chromium } = require('playwright');

(async () => {
  const files = [
    '1_system_architecture.html',
    '2_data_flow.html',
    '3_ui_ux_logic.html'
  ];
  
  const browser = await chromium.launch();
  
  for (const file of files) {
    const page = await browser.newPage();
    await page.goto('file://' + process.cwd() + '/' + file, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    const pngFile = file.replace('.html', '.png');
    await page.screenshot({ path: pngFile, fullPage: true });
    console.log('✅ Created ' + pngFile);
  }
  
  await browser.close();
})();
