# Windows 실행 가이드

## 🖥️ Windows 버전별 실행 스크립트

프로젝트에는 Windows 7과 Windows 11용 실행 스크립트가 각각 준비되어 있습니다.

### 📁 폴더 구조
```
s_analysis/
├── windows7/          # Windows 7용 스크립트
│   ├── start_all.ps1  # PowerShell 스크립트
│   ├── start_all.bat  # 배치 파일
│   └── README.md      # Windows 7 설정 가이드
├── windows11/         # Windows 11용 스크립트
│   ├── start_all.ps1  # PowerShell 스크립트
│   ├── start_all.bat  # 배치 파일
│   └── README.md      # Windows 11 설정 가이드
└── WINDOWS_SETUP.md   # 이 파일
```

## 🚀 빠른 시작

### Windows 7 사용자
1. `windows7/` 폴더로 이동
2. `start_all.bat` 파일을 **관리자 권한으로 실행**
3. 자세한 가이드는 `windows7/README.md` 참조

### Windows 11 사용자
1. `windows11/` 폴더로 이동
2. `start_all.ps1` 파일을 **관리자 권한으로 실행**
3. 자세한 가이드는 `windows11/README.md` 참조

## 📋 공통 사전 요구사항

### 1. Python 설치
- **Windows 7**: Python 3.7 이상
- **Windows 11**: Python 3.8 이상 권장
- [Python 공식 사이트](https://www.python.org/downloads/)

### 2. Node.js 설치
- **Windows 7**: Node.js 14 이상
- **Windows 11**: Node.js 16 이상 권장
- [Node.js 공식 사이트](https://nodejs.org/)

### 3. PostgreSQL 설정
- 데이터베이스 연결 정보가 필요합니다
- 프로젝트 루트에 `.env` 파일 생성:

```env
DATABASE_URL=postgresql://username:password@host:port/database
TEST_DATABASE_URL=postgresql://username:password@host:port/test_database
SECRET_KEY=devkey
FLASK_ENV=development
FLASK_DEBUG=true
```

## 🔧 버전별 차이점

| 기능 | Windows 7 | Windows 11 |
|------|-----------|------------|
| PowerShell 실행 정책 | 자동 처리 | 기본 지원 |
| 경로 제한 | 자동 해결 | 최신 기능 활용 |
| 브라우저 자동 실행 | 수동 | 자동 |
| 성능 최적화 | 기본 | 고급 |
| 오류 처리 | 기본 | 향상된 |

## ⚠️ 주의사항

### Windows 7 특별 고려사항
- PowerShell 실행 정책 제한
- 긴 경로명 지원 제한
- 레거시 시스템 호환성

### Windows 11 특별 고려사항
- 최신 기능 활용
- 향상된 보안 정책
- 더 나은 성능

## 🆘 문제 해결

### 공통 문제
1. **Python/Node.js 미설치**: 공식 사이트에서 다운로드
2. **포트 충돌**: `netstat -ano | findstr :포트번호`
3. **권한 문제**: 관리자 권한으로 실행

### 버전별 문제
- **Windows 7**: `windows7/README.md` 참조
- **Windows 11**: `windows11/README.md` 참조

## 📞 지원

문제가 발생하면 다음 정보와 함께 문의해주세요:
- Windows 버전 (7/11)
- Python 버전
- Node.js 버전
- 오류 메시지
- 사용한 스크립트 파일명 