# Windows 11용 주식 분석 시스템 시작 스크립트
# 최신 PowerShell 기능 활용

Write-Host "=== 주식 분석 시스템 시작 (Windows 11) ===" -ForegroundColor Green

# 현재 디렉토리를 스크립트 위치로 설정
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 상위 디렉토리로 이동 (프로젝트 루트)
Set-Location ..

# Python 확인 (최신 Python 3.8+ 권장)
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python 버전: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Python이 설치되지 않았습니다. Python 3.8 이상을 설치해주세요." -ForegroundColor Red
    exit 1
}

# Node.js 확인 (최신 LTS 권장)
try {
    $nodeVersion = node --version
    Write-Host "Node.js 버전: $nodeVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Node.js가 설치되지 않았습니다. Node.js LTS를 설치해주세요." -ForegroundColor Red
    exit 1
}

# 가상환경 확인 및 생성
$venvPath = ".\backend\venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvPath)) {
    Write-Host "가상환경을 생성합니다..." -ForegroundColor Yellow
    if (Test-Path ".\backend\venv") {
        Remove-Item ".\backend\venv" -Recurse -Force
    }
    python -m venv backend\venv
}

# 백엔드 의존성 설치
Write-Host "백엔드 의존성을 설치합니다..." -ForegroundColor Cyan
& ".\backend\venv\Scripts\Activate.ps1"
pip install --upgrade pip
pip install -r backend\requirements.txt

# 프론트엔드 의존성 설치
Write-Host "프론트엔드 의존성을 설치합니다..." -ForegroundColor Cyan
if (-not (Test-Path ".\frontend\node_modules")) {
    Set-Location frontend
    npm install
    Set-Location ..
}

# 환경 변수 파일 확인
if (-not (Test-Path ".env")) {
    Write-Host "경고: .env 파일이 없습니다. 데이터베이스 연결을 설정해주세요." -ForegroundColor Yellow
    Write-Host "예시:" -ForegroundColor Yellow
    Write-Host "DATABASE_URL=postgresql://username:password@host:port/database" -ForegroundColor Gray
    Write-Host "TEST_DATABASE_URL=postgresql://username:password@host:port/test_database" -ForegroundColor Gray
}

# 백엔드 서버 시작 (새 PowerShell 창)
Write-Host "백엔드 서버를 시작합니다..." -ForegroundColor Green
$backendCommand = "cd '$((Get-Location).Path)'; .\backend\venv\Scripts\Activate.ps1; python -m backend.app"
Start-Process powershell -ArgumentList '-NoExit', '-Command', $backendCommand -WindowStyle Normal

# 잠시 대기
Start-Sleep -Seconds 3

# 프론트엔드 서버 시작 (새 PowerShell 창)
Write-Host "프론트엔드 서버를 시작합니다..." -ForegroundColor Green
$frontendCommand = "cd '$((Get-Location).Path)\frontend'; npm run serve"
Start-Process powershell -ArgumentList '-NoExit', '-Command', $frontendCommand -WindowStyle Normal

Write-Host "=== 서버 시작 완료 ===" -ForegroundColor Green
Write-Host "백엔드 서버: http://localhost:5001" -ForegroundColor Cyan
Write-Host "프론트엔드 서버: http://localhost:8080" -ForegroundColor Cyan
Write-Host "브라우저에서 http://localhost:8080 을 열어주세요." -ForegroundColor Yellow

# 브라우저 자동 열기 (Windows 11 기능)
try {
    Start-Process "http://localhost:8080"
    Write-Host "브라우저가 자동으로 열렸습니다." -ForegroundColor Green
} catch {
    Write-Host "브라우저를 수동으로 열어주세요." -ForegroundColor Yellow
} 