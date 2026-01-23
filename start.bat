@REM @echo off
@REM set /p limit="리뷰를 남길 목표 상품 개수를 입력하세요: "
@REM node index.js %limit%
@REM pause

@echo off
echo.
echo ******************************************
echo    STEP 1: 사용자 인증 및 세션 확인
echo ******************************************
node auth_setup.js

:: auth_setup.js가 에러로 종료된 경우 중단
if %errorlevel% neq 0 (
    echo.
    echo ? 인증 과정에서 문제가 발생하여 중단되었습니다.
    pause
    exit /b
)

echo.
echo ******************************************
echo    STEP 2: 쿠팡 리뷰 자동화 프로세스 시작
echo ******************************************
set /p limit="처리할 목표 리뷰 개수를 입력하세요: "
:: 수집된 세션 정보를 활용해 메인 로직 실행
node index.js %limit%

echo.
echo 모든 작업이 완료되었습니다.
pause