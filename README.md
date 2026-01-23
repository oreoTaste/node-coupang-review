# 🤖 Coupang Review Automation (Gemini AI & Playwright)

이 프로젝트는 **Gemini API**와 **Playwright**를 결합하여 쿠팡의 '작성 가능한 리뷰'를 자동으로 작성해주는 도구입니다. 단순한 자동화를 넘어, 보안 솔루션(Akamai) 우회를 위해 인간의 행동 패턴을 모사하도록 설계되었습니다.

---

## ✨ 핵심 기능

- **Gemini AI 리뷰 생성**: 상품명을 기반으로 `systemInstruction.txt`에 정의된 페르소나에 맞춰 리뷰를 자동 생성합니다.
- **인간 모사 로직 (Anti-Bot)**:
  - **부드러운 마우스 이동**: 버튼 클릭 전 커서를 부드러운 궤적으로 이동시킵니다.
  - **랜덤 지연 시간**: 동작 사이에 무작위 대기 시간을 주어 기계적인 패턴을 제거합니다.
  - **직접 이벤트 발송**: `evaluate`를 통해 브라우저 내부에서 클릭 이벤트를 강제 발생시켜 정확도를 높입니다.
- **환경 변수 관리**: 모델 버전(`GEMINI_API_VERSION`)과 API 키를 `.env` 파일에서 간편하게 관리합니다.
- **연속 처리 제어**: 설정된 수량만큼 리뷰를 작성하고 안전하게 종료합니다.

---

## 📂 프로젝트 구조

```text
coupang-review-bot/
├── auth.json               # 쿠팡 로그인 세션 정보 (자동 생성)
├── auth_setup.js           # 초기 로그인 및 세션 저장 스크립트
├── index.js                # 메인 리뷰 자동화 실행 스크립트
├── .env                    # API 키 및 모델 설정
├── systemInstruction.txt   # Gemini 리뷰 작성 지침 (프롬프트)
└── package.json            # 의존성 관리 파일
```
아래는 요청하신 설치 및 설정과 사용 방법 섹션의 수정된 Markdown 내용입니다.

## 🛠️ 설치 및 설정
필수 패키지 설치 사내 보안망 환경에서의 설치 오류를 방지하기 위해 SSL 검증을 우회하여 설치합니다.

```Bash
# SSL 검증 일시 해제 (필수 아님)
npm config set strict-ssl false

# 의존성 설치
npm install playwright @google/generative-ai dotenv
브라우저 설치 인증서 오류가 발생할 경우 아래 명령어를 사용하여 브라우저를 수동으로 설치하세요.
```

```Bash
# Windows CMD 기준
set NODE_TLS_REJECT_UNAUTHORIZED=0 && npx playwright install
환경 변수 설정 (.env) 프로젝트 루트에 .env 파일을 생성하고 아래 내용을 입력합니다.
```

```Plaintext
GEMINI_API_KEY=your_google_api_key_here
GEMINI_API_VERSION=gemini-2.0-flash-lite
```

## 🚀 사용 방법
1단계: 크롬 종료 및 디버깅 모드 실행
가장 중요한 단계입니다. 기존의 모든 크롬 창이 닫혀 있어야 디버깅 포트(9222)가 정상적으로 열립니다.

1. 모든 크롬 종료: CMD창에 아래 명령어를 입력하여 잔류 프로세스를 제거합니다.

```Bash
taskkill /F /IM chrome.exe /T
```

2. 디버깅 모드로 실행: 아래 명령어를 복사하여 크롬을 실행합니다. (독립된 데이터 경로를 사용하여 충돌을 방지합니다.)
```Bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_debug" --no-first-run
```

2단계: 쿠팡 로그인
새로 열린 크롬 창에서 쿠팡에 접속하여 로그인을 완료합니다. 마이쿠팡 페이지까지 이동하여 세션이 활성화된 것을 확인하세요.

3단계: 통합 실행 (start.bat)
이제 모든 준비가 끝났습니다. 프로젝트 폴더 내의 start.bat을 실행합니다.

- STEP 1 (인증): auth_setup.js가 기존 세션을 확인하거나 9222 포트에 연결하여 auth.json을 갱신합니다.
- STEP 2 (자동화): 인증이 완료되면 목표 리뷰 개수를 입력받아 리뷰 작성을 시작합니다.


## ⚠️ 주의 사항
```
1. 책임 제한: 본 도구는 교육 및 연구 목적으로 제작되었습니다. 자동화 도구 사용으로 인한 계정 제제 등 모든 책임은 사용자에게 있습니다.
2. 인증서 우회: NODE_TLS_REJECT_UNAUTHORIZED = '0' 설정은 보안 취약점을 유발할 수 있으므로 신뢰할 수 있는 네트워크 환경에서만 사용하십시오.
```
