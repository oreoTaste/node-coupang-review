import os
import sys
import ssl
import time
import random
import requests
import warnings
import urllib3
import html  # HTML 엔티티 변환을 위해 추가
from dotenv import load_dotenv

# [핵심 추가] Playwright가 임시 폴더가 아닌 시스템 전역 브라우저 경로를 사용하게 함
if getattr(sys, 'frozen', False):
    # EXE로 실행 중일 때
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '0'

# 1. 모든 경고 메시지 무시
warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# [핵심] EXE 실행 환경과 일반 실행 환경 모두에서 파일 경로를 정확히 찾는 함수
def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # EXE 실행 시: EXE 파일이 위치한 실제 폴더 경로
        base_path = os.path.dirname(sys.executable)
    else:
        # 일반 실행 시: 현재 스크립트가 있는 폴더 경로
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 파일 경로 정의
instruction_path = get_resource_path('systemInstruction.txt')
env_path = get_resource_path('.env')
auth_path = get_resource_path('auth.json')


# 2. SSL 검증을 무시하는 환경 변수 설정
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'

# 3. 전역 SSL 컨텍스트 수정 (재귀 오류 방지를 위해 표준 방식으로 변경)
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

# 4. requests 라이브러리 verify=False 강제 설정 (안전한 방식)
# 모든 requests 세션이 생성될 때 자동으로 SSL 검증을 끄도록 설정합니다.
old_session_init = requests.Session.__init__
def new_session_init(self, *args, **kwargs):
    old_session_init(self, *args, **kwargs)
    self.verify = False
requests.Session.__init__ = new_session_init

# --- 라이브러리 로드 ---
import google.generativeai as genai
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# 환경 변수 로드
if os.path.exists(env_path):
    load_dotenv(env_path)

# Gemini 설정
api_keys = [
    os.getenv("GEMINI_API_KEY1"),
    os.getenv("GEMINI_API_KEY2"),
    os.getenv("GEMINI_API_KEY3")
]

# None 값(설정 안 된 키) 제외 필터링
valid_keys = [k for k in api_keys if k]

# 랜덤하게 하나 선택
if valid_keys:
    genai.configure(
        api_key=random.choice(valid_keys),
        transport='rest'
    )
else:
    print("❌ 오류: 설정된 API 키가 없습니다.")


# 시스템 지시문 로드
if os.path.exists(instruction_path):
    with open(instruction_path, 'r', encoding='utf-8') as f:
        system_instruction = f.read()
else:
    print(f"❌ 오류: {instruction_path} 파일을 찾을 수 없습니다.")
    sys.exit(1)

def wait_human_like(min_s=1.5, max_s=3.5):
    time.sleep(random.uniform(min_s, max_s))

def run_automation(target_limit):
    with sync_playwright() as p:
        print(f"🚀 리뷰 작성을 시작합니다. (목표: {target_limit}개)")
        
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'], channel="chrome")

        # [핵심] ignore_https_errors=True 추가: 브라우저 레벨에서 SSL 오류 무시
        context = browser.new_context(
            storage_state='auth.json',
            ignore_https_errors=True 
        )
        page = context.new_page()
        # 기본 타임아웃을 60초로 증가
        page.set_default_timeout(60000)

        processed_count = 0
        while processed_count < target_limit:
            print(f"\n🔄 [{processed_count + 1}/{target_limit}] 진행 중...")
            try:
                # [수정] wait_until='domcontentloaded'로 변경 (networkidle보다 안정적)
                page.goto('https://my.coupang.com/productreview/reviewable', wait_until='domcontentloaded')
                wait_human_like(2, 4)

                # 차단 확인
                content = page.content()
                if "Access Denied" in content or "접속이 제한" in content:
                    print("❌ 쿠팡으로부터 접속이 차단되었습니다.")
                    page.screenshot(path="blocked_error.png")
                    break

                # 리스트 대기
                list_selector = '.my-review__writable__list'
                page.wait_for_selector(list_selector, state='visible', timeout=20000)

                item = page.locator(list_selector).first
                product_name = item.locator('.my-review__writable__content-title').inner_text().strip()
                print(f"📦 상품명: {product_name}")

                # Gemini 리뷰 생성
                model = genai.GenerativeModel(
                    model_name=os.getenv("GEMINI_API_VERSION", "gemini-2.0-flash"),
                    system_instruction=system_instruction
                )
                response = model.generate_content(f"상품명 '{product_name}'에 대한 리뷰를 작성해줘.")

                # HTML 엔티티를 일반 문자로 변환 (예: &#39; -> ')
                review_text = html.unescape(response.text.replace('```', '').strip())
                print("🤖 리뷰 생성 성공")

                # 리뷰 작성 프로세스
                item.get_by_text("리뷰 작성하기").click()
                page.wait_for_selector('.my-review__modify__star__content__value', state='visible')
                wait_human_like(1, 2)

                # 별점 및 설문 선택
                stars = page.locator('.my-review__modify__star__content__value')
                stars.nth(3 if random.random() < 0.3 else 4).click()

                surveys = page.locator('.review-intake-form__check-options .radio-survey')
                for i in range(surveys.count()):
                    radios = surveys.nth(i).locator('input[type="radio"]')
                    if radios.count() >= 2:
                        radios.nth(0 if random.random() < 0.4 else 1).click(force=True)

                # 텍스트 입력 및 제출
                textarea = page.locator('textarea.my-review__modify__review__content__text-area')
                textarea.press_sequentially(review_text, delay=random.randint(50, 150))
                wait_human_like(2, 5)

                page.evaluate("document.querySelector('button.submit-button._review-submit').disabled = false")
                page.locator('button.submit-button._review-submit').click()

                processed_count += 1
                print(f"✅ {product_name} 등록 완료!")
                
                if processed_count < target_limit:
                    sleep_time = random.randint(25, 45)
                    print(f"💤 {sleep_time}초간 휴식...")
                    time.sleep(sleep_time)

            except Exception as e:
                print(f"❌ 프로세스 오류 발생: {e}")
                page.screenshot(path=f"error_log_{int(time.time())}.png")
                time.sleep(5)

        browser.close()

if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run_automation(limit)