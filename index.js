// index.js
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'; 

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

const instructionPath = path.join(__dirname, 'systemInstruction.txt');
const systemInstructionText = fs.readFileSync(instructionPath, 'utf8');

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const targetLimit = parseInt(process.argv[2], 10) || 5; // 목표 처리 수

// --- [인간 모사 헬퍼 함수들] ---

const waitHumanLike = async (page, min = 1000, max = 3000) => {
    const timeout = Math.floor(Math.random() * (max - min + 1) + min);
    await page.waitForTimeout(timeout);
};

async function humanMoveAndClick(page, locator) {
    await locator.scrollIntoViewIfNeeded();
    const box = await locator.boundingBox();
    
    if (box) {
        const targetX = box.x + box.width / 2 + (Math.random() * 10 - 5);
        const targetY = box.y + box.height / 2 + (Math.random() * 10 - 5);
        
        await page.mouse.move(targetX, targetY, { steps: 20 });
        await waitHumanLike(page, 300, 600); 
        
        await page.mouse.down();
        await waitHumanLike(page, 50, 150);
        await page.mouse.up();
    } else {
        await locator.click({ force: true });
    }
}

(async () => {
    const browser = await chromium.launch({ 
        headless: false,
        args: ['--disable-blink-features=AutomationControlled'] 
    }); 
    const context = await browser.newContext({ storageState: 'auth.json' });
    const page = await context.newPage();

    let processedCount = 0; // 처리된 상품 수를 저장할 변수

    console.log(`🚀 총 ${targetLimit}개의 상품 리뷰 작성을 시작합니다.`);

    while (processedCount < targetLimit) {
        console.log(`\n🔄 [${processedCount + 1}/${targetLimit}] 리뷰 목록 불러오는 중...`);
        await page.goto('https://my.coupang.com/productreview/reviewable');
        await waitHumanLike(page, 2000, 4000);

        const itemLocator = page.locator('.my-review__writable__list').first();
        const itemCount = await itemLocator.count();

        if (itemCount === 0) {
            console.log('✅ 더 이상 작성할 리뷰가 없습니다.');
            break;
        }

        const item = itemLocator;
        const productName = await item.locator('.my-review__writable__content-title').innerText();
        console.log(`📦 현재 처리 상품: ${productName}`);

        try {
            // 1. Gemini 리뷰 생성 (환경변수 모델 사용)
            const modelName = process.env.GEMINI_API_VERSION || "gemini-2.0-flash";
            const model = genAI.getGenerativeModel({ 
                model: modelName, 
                systemInstruction: systemInstructionText 
            });

            const result = await model.generateContent(`상품명 '${productName}'에 대한 리뷰를 작성해줘.`);
            const reviewText = result.response.text();
            console.log(`🤖 리뷰 생성 성공 (Model: ${modelName})`);

            // 2. 리뷰 작성 버튼 클릭
            const writeButton = item.locator('button:has-text("리뷰 작성하기")');
            await humanMoveAndClick(page, writeButton);
            
            // 3. 모달 내 별점/설문 처리
            await page.waitForSelector('.my-review__modify__star__content__value', { state: 'visible' });
            await waitHumanLike(page, 1500, 2500);

            await page.evaluate(() => {
                const stars = document.querySelectorAll(".my-review__modify__star__content__value");
                if (stars && stars[4]) stars[4].click();

                const surveys = document.querySelectorAll('.review-intake-form__check-options .radio-survey');
                surveys.forEach(survey => {
                    const radios = survey.querySelectorAll('input[type="radio"]');
                    if (radios && radios[1]) radios[1].click();
                });
            });
            console.log('⭐ 별점 및 설문 선택 완료');

            // 4. 리뷰 텍스트 입력
            const textareaSelector = 'textarea.my-review__modify__review__content__text-area';
            // await page.fill(textareaSelector, reviewText);
            const textarea = page.locator(textareaSelector);
            await textarea.focus();
            await page.keyboard.type(reviewText, { delay: Math.random() * 50 + 50 }); // 글자당 50~100ms 지연

            console.log('✍️ 리뷰 텍스트 입력 완료');
            
            await waitHumanLike(page, 3000, 6000); 

            // 5. 등록 버튼 클릭
            const submitSelector = 'button.submit-button._review-submit';
            const submitButton = page.locator(submitSelector);
            
            await page.evaluate((sel) => {
                const btn = document.querySelector(sel);
                if (btn) btn.disabled = false;
            }, submitSelector);

            console.log('🚀 등록 버튼 클릭...');
            await humanMoveAndClick(page, submitButton);

            processedCount++; // 성공 시 카운트 증가
            console.log(`✅ ${productName} 등록 완료! (현재 ${processedCount}개 완료)`);

            if (processedCount < targetLimit) {
                const restTime = Math.floor(Math.random() * 10000 + 20000); 
                console.log(`💤 다음 상품 전 ${restTime/1000}초간 대기합니다...`);
                await page.waitForTimeout(restTime);
            }

        } catch (error) {
            console.error(`❌ 오류 발생:`, error);
            console.log('안전을 위해 10초 대기 후 다음 시도를 진행합니다.');
            await page.waitForTimeout(10000);
        }
    }

    console.log(`\n🎉 목표 수량(${targetLimit}개)을 모두 달성했습니다.`);
    await browser.close();
})();