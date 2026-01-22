@echo off
set /p limit="리뷰를 남길 목표 상품 개수를 입력하세요: "
node index.js %limit%
pause