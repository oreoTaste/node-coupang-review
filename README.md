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
1 단계: 크롬 디버깅 모드 실행 (필수)
auth_setup.js는 실행 중인 브라우저의 원격 디버깅 포트에 접속하여 세션을 저장합니다. 모든 크롬 창을 닫은 뒤, 터미널에서 아래 명령어로 크롬을 실행하세요.

Windows:
```Bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

macOS:
```Bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

2 단계: 세션 저장 (최초 1회)
디버깅 모드로 열린 크롬 창에서 쿠팡에 접속하여 로그인을 완료합니다.

로그인이 완료된 상태에서 프로젝트 터미널에 아래 스크립트를 실행합니다.

```Bash
node auth_setup.js
성공 시 루트 디렉토리에 auth.json 파일이 생성되며 인증 정보가 저장됩니다.
```

3 단계: 자동화 실행
세션이 준비되면 아래 명령어로 리뷰 작성을 시작합니다.

```Bash
node index.js
프로그램 실행 후 목표 수량을 입력하면 Gemini AI가 상품명에 맞춰 리뷰를 생성하고 자동으로 등록합니다. 각 상품 처리 사이에는 차단 방지를 위한 랜덤 휴식 시간이 포함됩니다.
```

## ⚠️ 주의 사항
```
1. 책임 제한: 본 도구는 교육 및 연구 목적으로 제작되었습니다. 자동화 도구 사용으로 인한 계정 제제 등 모든 책임은 사용자에게 있습니다.
2. 인증서 우회: NODE_TLS_REJECT_UNAUTHORIZED = '0' 설정은 보안 취약점을 유발할 수 있으므로 신뢰할 수 있는 네트워크 환경에서만 사용하십시오.
```
