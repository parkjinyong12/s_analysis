# Windows 7 호환성을 위한 주식 분석 시스템 시작 스크립트
# 실행 정책 확인 및 설정
Write-Host "=== 주식 분석 시스템 시작 ===" -ForegroundColor Green

# PowerShell 실행 정책 확인
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted") {
    Write-Host "PowerShell 실행 정책이 제한되어 있습니다. 임시로 변경합니다..." -ForegroundColor Yellow
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
}

# 현재 디렉토리를 스크립트 위치로 설정
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Python 가상환경 경로 확인
$venvPath = ".\backend\venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvPath)) {
    Write-Host "가상환경을 찾을 수 없습니다. 생성 중..." -ForegroundColor Yellow
    if (Test-Path ".\backend\venv") {
        Remove-Item ".\backend\venv" -Recurse -Force
    }
    python -m venv backend\venv
}

# Node.js 확인
try {
    $nodeVersion = node --version
    Write-Host "Node.js 버전: $nodeVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Node.js가 설치되지 않았습니다. Node.js를 설치해주세요." -ForegroundColor Red
    exit 1
}

# 백엔드 의존성 확인 및 설치
Write-Host "백엔드 의존성 확인 중..." -ForegroundColor Cyan
if (-not (Test-Path ".\backend\venv\Scripts\pip.exe")) {
    Write-Host "가상환경이 손상되었습니다. 재생성 중..." -ForegroundColor Yellow
    Remove-Item ".\backend\venv" -Recurse -Force
    python -m venv backend\venv
}

# 가상환경 활성화 및 의존성 설치
& ".\backend\venv\Scripts\Activate.ps1"
pip install -r backend\requirements.txt

# 프론트엔드 의존성 확인 및 설치
Write-Host "프론트엔드 의존성 확인 중..." -ForegroundColor Cyan
if (-not (Test-Path ".\frontend\node_modules")) {
    Write-Host "프론트엔드 의존성 설치 중..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

# 백엔드 서버 시작
Write-Host "백엔드 서버 시작 중..." -ForegroundColor Green
Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd '$scriptPath'; .\backend\venv\Scripts\Activate.ps1; python -m backend.app"

# 잠시 대기
Start-Sleep -Seconds 3

# 프론트엔드 서버 시작
Write-Host "프론트엔드 서버 시작 중..." -ForegroundColor Green
Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd '$scriptPath\frontend'; npm run serve"

Write-Host "=== 서버 시작 완료 ===" -ForegroundColor Green
Write-Host "백엔드 서버: http://localhost:5001" -ForegroundColor Cyan
Write-Host "프론트엔드 서버: http://localhost:8080" -ForegroundColor Cyan
Write-Host "브라우저에서 http://localhost:8080 을 열어주세요." -ForegroundColor Yellow

# 실행 정책 복원
if ($executionPolicy -eq "Restricted") {
    Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser -Force
    Write-Host "PowerShell 실행 정책을 원래대로 복원했습니다." -ForegroundColor Yellow
} 