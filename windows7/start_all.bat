@echo off
chcp 65001 >nul
echo ========================================
echo    주식 분석 시스템 시작 (Windows 7)
echo ========================================
echo.

REM 현재 디렉토리를 스크립트 위치로 설정
cd /d "%~dp0"

REM Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되지 않았습니다.
    echo Python 3.7 이상을 설치해주세요.
    pause
    exit /b 1
)

REM Node.js 확인
node --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Node.js가 설치되지 않았습니다.
    echo Node.js 14 이상을 설치해주세요.
    pause
    exit /b 1
)

echo [정보] Python 및 Node.js 확인 완료

REM 가상환경 확인 및 생성
if not exist "backend\venv\Scripts\activate.bat" (
    echo [정보] 가상환경을 생성합니다...
    python -m venv backend\venv
    if errorlevel 1 (
        echo [오류] 가상환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
)

REM 가상환경 활성화 및 의존성 설치
echo [정보] 백엔드 의존성을 설치합니다...
call backend\venv\Scripts\activate.bat
pip install -r backend\requirements.txt

REM 프론트엔드 의존성 확인 및 설치
if not exist "frontend\node_modules" (
    echo [정보] 프론트엔드 의존성을 설치합니다...
    cd frontend
    npm install
    cd ..
)

echo.
echo [정보] 서버를 시작합니다...
echo.

REM 백엔드 서버 시작
echo [정보] 백엔드 서버 시작 중...
start "백엔드 서버" cmd /k "cd /d "%~dp0" && backend\venv\Scripts\activate.bat && python -m backend.app"

REM 잠시 대기
timeout /t 3 /nobreak >nul

REM 프론트엔드 서버 시작
echo [정보] 프론트엔드 서버 시작 중...
start "프론트엔드 서버" cmd /k "cd /d "%~dp0\frontend" && npm run serve"

echo.
echo ========================================
echo            서버 시작 완료
echo ========================================
echo 백엔드 서버: http://localhost:5001
echo 프론트엔드 서버: http://localhost:8080
echo.
echo 브라우저에서 http://localhost:8080 을 열어주세요.
echo.
pause 