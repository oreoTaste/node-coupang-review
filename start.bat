@echo off
echo STEP 1: 사용자 인증 확인
python auth_setup.py
if %errorlevel% neq 0 exit /b

echo.
echo STEP 2: 자동화 시작
set /p limit="목표 개수: "
python index.py %limit%
pause