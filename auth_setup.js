// const { chromium } = require('playwright-extra');
// const stealth = require('puppeteer-extra-plugin-stealth')();
// chromium.use(stealth);

// (async () => {
//   // 1. 실제 설치된 크롬 브라우저(channel: 'chrome')를 사용하면 더 안전합니다.
//   const browser = await chromium.launch({ 
//     headless: false,
//     channel: 'chrome' 
//   });
  
//   const context = await browser.newContext({
//     userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
//     viewport: { width: 1280, height: 800 }
//   });

//   const page = await context.newPage();
  
//   // 2. 곧바로 로그인 페이지로 가지 말고, 메인 페이지를 거쳐서 이동합니다.
//   await page.goto('https://www.coupang.com/');
//   await page.waitForTimeout(2000); // 잠시 대기
  
//   await page.goto('https://login.coupang.com/login/login.pang');
  
//   console.log('브라우저에서 로그인을 완료해 주세요.');
  
//   // 로그인 성공 후 메인으로 돌아올 때까지 무한 대기
//   await page.waitForURL('https://www.coupang.com/', { timeout: 0 });
  
//   await context.storageState({ path: 'auth.json' });
//   await browser.close();
//   console.log('인증 정보가 auth.json에 저장되었습니다.');
// })();


const { chromium } = require('playwright');

(async () => {
  try {
    // localhost 대신 127.0.0.1을 사용하여 IPv6 충돌 방지
    const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
    console.log('브라우저 연결 성공!');

    // 열려있는 브라우저의 첫 번째 컨텍스트와 페이지 가져오기
    const defaultContext = browser.contexts()[0];
    const page = defaultContext.pages()[0] || await defaultContext.newPage();

    // 쿠팡 로그인 상태인지 확인 (이미 로그인된 창에서 실행 권장)
    await page.goto('https://www.coupang.com/');
    
    // 세션 정보 저장
    await defaultContext.storageState({ path: 'auth.json' });
    console.log('인증 정보(auth.json) 저장 완료!');

    await browser.close();
  } catch (error) {
    console.error('연결 실패:', error);
  }
})();