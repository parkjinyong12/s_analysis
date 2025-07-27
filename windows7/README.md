# Windows 7 실행 가이드

## 📋 사전 요구사항

### 1. Python 설치
- **Python 3.7 이상** 설치 필요
- [Python 공식 사이트](https://www.python.org/downloads/)에서 다운로드
- 설치 시 "Add Python to PATH" 옵션 체크

### 2. Node.js 설치
- **Node.js 14 이상** 설치 필요
- [Node.js 공식 사이트](https://nodejs.org/)에서 LTS 버전 다운로드

### 3. PostgreSQL 설정
- PostgreSQL 데이터베이스 연결 정보가 필요합니다
- `.env` 파일에 다음 정보를 설정해주세요:

```env
DATABASE_URL=postgresql://postgres:비밀번호@서버주소:5432/데이터베이스명
TEST_DATABASE_URL=postgresql://postgres:비밀번호@서버주소:5432/테스트데이터베이스명
SECRET_KEY=devkey
FLASK_ENV=development
FLASK_DEBUG=true
```

## 🚀 실행 방법

### 방법 1: 배치 파일 사용 (권장)
1. `start_all.bat` 파일을 **관리자 권한으로 실행**
2. 자동으로 의존성 설치 및 서버 시작
3. 브라우저에서 `http://localhost:8080` 접속

### 방법 2: PowerShell 스크립트 사용
1. PowerShell을 **관리자 권한으로 실행**
2. 다음 명령어 실행:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\start_all.ps1
   ```

### 방법 3: 수동 실행
1. **백엔드 서버 시작**:
   ```cmd
   cd backend
   venv\Scripts\activate
   python -m app
   ```

2. **프론트엔드 서버 시작** (새 명령 프롬프트):
   ```cmd
   cd frontend
   npm install
   npm run serve
   ```

## ⚠️ Windows 7 특별 주의사항

### 1. PowerShell 실행 정책
- 기본적으로 스크립트 실행이 제한되어 있음
- 스크립트 실행 시 자동으로 정책 변경 후 복원

### 2. 경로 문제
- 긴 경로명 지원 제한
- 스크립트가 자동으로 경로 문제 해결

### 3. 문자 인코딩
- UTF-8 인코딩 사용으로 한글 표시 지원

### 4. 방화벽 설정
- Windows 방화벽에서 Python과 Node.js 허용 필요
- 첫 실행 시 방화벽 경고가 나타날 수 있음

## 🔧 문제 해결

### Python 오류
```
[오류] Python이 설치되지 않았습니다.
```
**해결방법**: Python 3.7 이상을 설치하고 PATH에 추가

### Node.js 오류
```
[오류] Node.js가 설치되지 않았습니다.
```
**해결방법**: Node.js 14 이상을 설치

### 가상환경 오류
```
[오류] 가상환경 생성에 실패했습니다.
```
**해결방법**: 
1. 관리자 권한으로 실행
2. Python venv 모듈 확인: `python -m venv --help`

### 포트 충돌
```
[오류] 포트가 이미 사용 중입니다.
```
**해결방법**:
1. `netstat -ano | findstr :5001` (백엔드 포트 확인)
2. `netstat -ano | findstr :8080` (프론트엔드 포트 확인)
3. 해당 프로세스 종료

### 데이터베이스 연결 오류
```
[오류] PostgreSQL 연결 실패
```
**해결방법**:
1. `.env` 파일의 연결 정보 확인
2. PostgreSQL 서버 실행 상태 확인
3. 방화벽 설정 확인

## 📞 지원

문제가 발생하면 다음 정보와 함께 문의해주세요:
- Windows 7 버전 (32bit/64bit)
- Python 버전
- Node.js 버전
- 오류 메시지 전체 내용 