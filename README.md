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
- **연속 처리 제어**: 설정된 수량(예: 2개)만큼 리뷰를 작성하고 안전하게 종료합니다.

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
## 🛠️ 설치 및 설정
1. 필수 패키지 설치
사내 보안망 환경에서의 설치 오류를 방지하기 위해 SSL 검증을 우회하여 설치합니다.

```Bash
# SSL 검증 일시 해제 (필요시)
npm config set strict-ssl false

# 의존성 설치
npm install playwright @google/generative-ai dotenv
2. 브라우저 설치
인증서 오류가 발생할 경우 아래 명령어를 사용하세요.
```

```Bash
# Windows CMD 기준
set NODE_TLS_REJECT_UNAUTHORIZED=0 && npx playwright install
3. 환경 변수 설정 (.env)
프로젝트 루트에 .env 파일을 생성하고 아래 내용을 입력합니다.
```

```Plaintext
GEMINI_API_KEY=your_google_api_key_here
GEMINI_API_VERSION=gemini-2.0-flash-lite
```

## 🚀 사용 방법
단계 1: 세션 저장 (최초 1회)
브라우저를 열어 수동으로 로그인한 뒤 세션을 저장합니다. (디버깅 모드 활용 권장)

```Bash
node auth_setup.js
```
단계 2: 자동화 실행
Bash```
node index.js
```
프로그램이 실행되면 설정된 targetLimit 수량만큼 리뷰를 순차적으로 작성합니다.

각 상품 처리 후 아카마이 차단 방지를 위해 랜덤하게 휴식합니다.
```

## ⚠️ 주의 사항
```
1. 책임 제한: 본 도구는 교육 및 연구 목적으로 제작되었습니다. 자동화 도구 사용으로 인한 계정 제제 등 모든 책임은 사용자에게 있습니다.
2. 인증서 우회: NODE_TLS_REJECT_UNAUTHORIZED = '0' 설정은 보안 취약점을 유발할 수 있으므로 신뢰할 수 있는 네트워크 환경에서만 사용하십시오.
```
