const { chromium } = require('playwright');
const fs = require('fs');
const readline = require('readline');

const authPath = 'auth.json';

// 터미널 입력을 기다리는 유틸리티
function waitEnter(msg) {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    return new Promise(resolve => rl.question(msg, answer => { rl.close(); resolve(answer); }));
}

async function run() {
    console.log('[LOG] 프로그램 시작...');

    // 1. 기존 파일 확인 및 유효성 검사
    if (fs.existsSync(authPath)) {
        console.log(`[LOG] '${authPath}' 파일을 발견했습니다. 유효성을 검사합니다...`);
        try {
            const browser = await chromium.launch({ headless: true });
            console.log('[LOG] 검증용 임시 브라우저 실행 성공');
            
            const context = await browser.newContext({ storageState: authPath });
            const page = await context.newPage();
            
            console.log('[LOG] 쿠팡 접속 시도 중...');
            await page.goto('https://my.coupang.com/purchase/list', { waitUntil: 'domcontentloaded', timeout: 10000 });
            
            const currentUrl = page.url();
            console.log(`[LOG] 현재 URL: ${currentUrl}`);

            if (!currentUrl.includes('login.coupang.com')) {
                console.log('✅ [결과] 기존 세션이 유효합니다. 자동화를 시작합니다.');
                await browser.close();
                return;
            }
            console.log('[LOG] 세션이 만료되어 재인증이 필요합니다.');
            await browser.close();
        } catch (e) {
            console.log(`[ERROR] 유효성 검사 중 에러 발생: ${e.message}`);
        }
    } else {
        console.log(`[LOG] '${authPath}' 파일이 없습니다. 새로 생성을 시작합니다.`);
    }

    // 2. 사용자 안내
    console.log('\n' + '='.repeat(50));
    console.log('1. CMD창을 열고 아래 명령어를 입력하세요:');
    console.log('   netstat -ano | findstr :9222');
    console.log('2. 만약 데이터가 있다면 모든 크롬창을 꺼야합니다. (아래 명령어를 수행하면 모든 크롬창이 꺼집니다):');
    console.log('   taskkill /F /IM chrome.exe /T');
    console.log('2. 다음 명령어를 실행하세요:');
    console.log('   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\\temp\\chrome_debug" --no-first-run');
    console.log('3. 쿠팡 홈페이지에 로그인 한 후 아래 명령어를 수행하세요 (결과가 없으면 위의 과정을 재처리하세요):');
    console.log('   netstat -ano | findstr :9222');
    console.log('='.repeat(50));

    await waitEnter('\n👉 위 단계를 모두 마쳤다면 [엔터]를 눌러주세요...');

    // 3. CDP 연결 및 저장 (사용자 성공 코드 기반)
    try {
        console.log('[LOG] http://127.0.0.1:9222 에 연결을 시도합니다...');
        const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
        console.log('[LOG] 브라우저 연결 성공!');

        const contexts = browser.contexts();
        console.log(`[LOG] 활성화된 컨텍스트 수: ${contexts.length}`);
        
        const defaultContext = contexts[0];
        const pages = defaultContext.pages();
        console.log(`[LOG] 열려있는 페이지 수: ${pages.length}`);

        const page = pages[0] || await defaultContext.newPage();
        console.log(`[LOG] 대상 페이지 URL: ${page.url()}`);

        console.log('[LOG] 인증 정보를 추출하여 저장 중...');
        await defaultContext.storageState({ path: authPath });
        
        console.log(`✅ [결과] '${authPath}' 저장 완료!`);
        await browser.close();
        console.log('[LOG] 브라우저 연결을 해제하고 종료합니다.');
    } catch (error) {
        console.error('\n❌ [ERROR] 연결 최종 실패');
        console.error(`메시지: ${error.message}`);
        console.error('팁: 크롬이 9222 포트로 정말 띄워져 있는지 확인하세요.');
        process.exit(1);
    }
}

run();