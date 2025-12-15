@echo off
chcp 65001
echo ========================================================
echo       신성EP 개발 샘플 통합 관리 시스템 시작 중...
echo ========================================================
echo.

:: Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python 또는 Pip가 설치되어 있지 않습니다.
    echo Python을 먼저 설치해주세요.
    pause
    exit /b
)

:: Install core dependencies if needed (optional, can remove if annoying)
echo [시스템 점검] 필요한 라이브러리를 확인합니다...
pip install streamlit pandas openpyxl xlsxwriter -q

:: Run the App
echo.
echo [실행] 시스템을 가동합니다. 잠시만 기다려주세요...
echo 브라우저 창이 열리면 로그인하여 사용하세요.
echo.
python -m streamlit run app.py

pause
