import os
import sys
from playwright.sync_api import sync_playwright

# Playwright 브라우저 경로 설정
if getattr(sys, 'frozen', False):
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '0'

AUTH_PATH = 'auth.json'

def check_login_status(page):
    try:
        # 주문 목록 페이지 접속 시도하여 로그인 여부 확인
        page.goto('https://my.coupang.com/purchase/list', wait_until='domcontentloaded', timeout=10000)
        return 'login.coupang.com' not in page.url
    except:
        return False

def check_session():
    """기존 auth.json 세션의 유효성을 검사합니다."""
    if not os.path.exists(AUTH_PATH):
        return False
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True, channel="chrome")
            context = browser.new_context(storage_state=AUTH_PATH)
            page = context.new_page()
            is_valid = check_login_status(page)
            browser.close()
            return is_valid
        except:
            return False

def save_session():
    """디버깅 포트로 열린 브라우저에 연결하여 인증 정보를 저장합니다."""
    with sync_playwright() as p:
        try:
            print("\n[연결] 실행 중인 브라우저에 접속 시도 중...")
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            default_context = browser.contexts[0]
            page = default_context.pages[0] if default_context.pages else default_context.new_page()
            page.goto("https://www.coupang.com/")
            
            # 로그아웃 버튼이 있거나 세션 체크를 통과하면 저장
            if '로그아웃' in page.content() or check_login_status(page):
                default_context.storage_state(path=AUTH_PATH)
                browser.close()
                return True
            browser.close()
            return False
        except Exception as e:
            print(f"❌ 연결 실패: {e}")
            return False

if __name__ == "__main__":
    # 'save' 인자가 전달되면 인증 정보 저장 모드로 동작
    if len(sys.argv) > 1 and sys.argv[1] == "save":
        if save_session():
            print(f"✅ 인증 정보 저장 완료! ({AUTH_PATH})")
            sys.exit(0)
        else:
            print("❌ 실패: 로그인이 감지되지 않았습니다.")
            sys.exit(1)
    # 인자가 없으면 단순 세션 체크만 수행
    else:
        if check_session():
            print("✅ 기존 세션이 유효합니다.")
            sys.exit(0)
        else:
            print("⚠️ 세션이 만료되었거나 정보가 없습니다.")
            sys.exit(1)