@echo off
echo STEP 1: 사용자 인증 확인 중...

:: 1. 먼저 기존 세션이 유효한지 체크 (인자 없이 실행)
python auth_setup.py
if %errorlevel% equ 0 (
    echo 기존 세션이 유효하므로 바로 시작합니다.
    goto RUN_INDEX
)

echo.
echo ? 로그인이 필요합니다.
echo ----------------------------------------------------
echo 1. 현재 열려 있는 모든 크롬 창을 완전히 종료해주세요.
echo 2. 잠시 후 디버깅 모드로 크롬이 자동 실행됩니다.
echo ----------------------------------------------------
pause

:: 2. 디버깅 모드로 크롬 실행
start chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_debug"

echo.
echo 3. 새로 열린 크롬 창에서 쿠팡 로그인을 완료해 주세요.
set /p dummy="? 로그인을 완료했다면 이 창에서 [엔터]를 눌러주세요..."

:: 3. 로그인된 브라우저에서 인증 정보를 추출하여 저장 (save 인자 전달)
echo 인증 정보 저장 시도 중...
python auth_setup.py save
if %errorlevel% neq 0 (
    echo.
    echo ? 인증 저장에 실패했습니다. 로그인이 제대로 되었는지 확인 후 다시 시도해주세요.
    pause
    exit /b
)

:RUN_INDEX
echo.
echo STEP 2: 자동화 시작
set /p limit="목표 개수(숫자): "
python index.py %limit%
pause