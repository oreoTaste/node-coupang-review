import os
import json
from playwright.sync_api import sync_playwright
import os
import sys

# [핵심 추가] Playwright가 임시 폴더가 아닌 시스템 전역 브라우저 경로를 사용하게 함
if getattr(sys, 'frozen', False):
    # EXE로 실행 중일 때
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '0'

AUTH_PATH = 'auth.json'

def check_login_status(page):
    try:
        # 주문 목록 페이지 접속 시도
        page.goto('https://my.coupang.com/purchase/list', wait_until='domcontentloaded', timeout=10000)
        # 로그인 페이지로 리다이렉트 되었는지 확인
        return 'login.coupang.com' not in page.url
    except:
        return False

def run_setup():
    with sync_playwright() as p:
        # 1. 기존 세션 유효성 확인
        if os.path.exists(AUTH_PATH):
            print(f"\n[LOG] '{AUTH_PATH}' 파일을 확인 중...")
            browser = p.chromium.launch(headless=True, channel="chrome")
            context = browser.new_context(storage_state=AUTH_PATH)
            page = context.new_page()
            
            if check_login_status(page):
                print("✅ 기존 세션이 유효합니다.")
                browser.close()
                return
            print("⚠️ 세션이 만료되었습니다.")
            browser.close()

        # 2. 안내 메시지
        print("\n" + "="*60)
        print("🔐 쿠팡 로그인 인증 설정")
        print("="*60)
        print("1. 모든 크롬 창을 닫으세요.")
        print("2. [윈도우+R] -> 아래 명령어 입력:")
        print("   chrome.exe --remote-debugging-port=9222 --user-data-dir=\"C:\\temp\\chrome_debug\"")
        print("3. 크롬에서 로그인 후 엔터를 누르세요.")
        print("="*60)
        
        input("\n👉 로그인을 완료했다면 [엔터]를 눌러주세요...")

        # 3. CDP 연결 및 저장
        try:
            print("\n[연결] 브라우저에 접속 중...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            default_context = browser.contexts[0]
            
            # 쿠팡 페이지로 이동하여 최종 확인
            page = default_context.pages[0] if default_context.pages else default_context.new_page()
            page.goto("https://www.coupang.com/")
            
            if '로그아웃' in page.content() or check_login_status(page):
                default_context.storage_state(path=AUTH_PATH)
                print(f"✅ 인증 정보 저장 완료! ({AUTH_PATH})")
            else:
                print("❌ 실패: 로그인이 감지되지 않았습니다.")
            
            browser.close()
        except Exception as e:
            print(f"\n❌ 연결 실패: {e}")

if __name__ == "__main__":
    run_setup()