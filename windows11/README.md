# Windows 11 실행 가이드

## 🚀 Windows 11 최적화된 실행 환경

Windows 11의 최신 기능을 활용하여 더욱 안정적이고 빠른 실행을 제공합니다.

## 📋 사전 요구사항

### 1. Python 설치
- **Python 3.8 이상** 권장 (최신 기능 지원)
- [Python 공식 사이트](https://www.python.org/downloads/)에서 다운로드
- 설치 시 "Add Python to PATH" 옵션 체크

### 2. Node.js 설치
- **Node.js 16 이상** 권장 (LTS 버전)
- [Node.js 공식 사이트](https://nodejs.org/)에서 다운로드

### 3. PostgreSQL 설정
- PostgreSQL 데이터베이스 연결 정보 설정
- `.env` 파일 생성:

```env
DATABASE_URL=postgresql://username:password@host:port/database
TEST_DATABASE_URL=postgresql://username:password@host:port/test_database
SECRET_KEY=devkey
FLASK_ENV=development
FLASK_DEBUG=true
```

## 🎯 실행 방법

### 방법 1: PowerShell 스크립트 (권장)
```powershell
# 관리자 권한으로 PowerShell 실행
.\start_all.ps1
```

### 방법 2: 배치 파일
```cmd
# 관리자 권한으로 명령 프롬프트 실행
start_all.bat
```

### 방법 3: 수동 실행
```powershell
# 백엔드
cd backend
.\venv\Scripts\Activate.ps1
python -m app

# 프론트엔드 (새 터미널)
cd frontend
npm run serve
```

## ✨ Windows 11 특별 기능

### 1. 자동 브라우저 실행
- 서버 시작 후 자동으로 브라우저가 열립니다
- `http://localhost:8080`으로 자동 접속

### 2. 최신 PowerShell 기능
- 향상된 오류 처리
- 더 나은 성능과 안정성
- 색상 출력 지원

### 3. 향상된 사용자 경험
- 실시간 진행 상황 표시
- 자동 의존성 설치
- 스마트 경로 처리

## 🔧 문제 해결

### PowerShell 실행 정책 오류
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 포트 충돌
```powershell
# 포트 사용 확인
netstat -ano | findstr :5001
netstat -ano | findstr :8080

# 프로세스 종료
taskkill /PID [프로세스ID] /F
```

### 가상환경 문제
```powershell
# 가상환경 재생성
Remove-Item backend\venv -Recurse -Force
python -m venv backend\venv
```

## 📊 성능 최적화

### 1. 메모리 사용량 최적화
- Node.js 메모리 제한 설정
- Python 가상환경 최적화

### 2. 시작 시간 단축
- 의존성 캐싱
- 병렬 설치 지원

### 3. 안정성 향상
- 자동 재시작 기능
- 오류 복구 메커니즘

## 🆘 지원

문제가 발생하면 다음 정보와 함께 문의해주세요:
- Windows 11 버전
- Python 버전
- Node.js 버전
- 오류 메시지
- 시스템 사양 