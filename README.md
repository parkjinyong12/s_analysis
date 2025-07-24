# Stock Analysis Project

Flask(Backend) + Vue.js(Frontend)로 구성된 풀스택 웹 애플리케이션입니다.

## 📋 프로젝트 구조

```
stock-analysis/
├── backend/                # Flask REST API (Python)
│   ├── models/            # DB 모델 (SQLAlchemy)
│   ├── views/             # API 컨트롤러 (Blueprint)
│   ├── services/          # 비즈니스 로직
│   ├── extensions.py      # Flask 확장 객체
│   ├── config.py          # 환경 설정
│   └── app.py             # Flask 앱 진입점
├── frontend/              # Vue.js SPA (JavaScript)
│   ├── src/
│   │   ├── components/    # 공통 컴포넌트
│   │   ├── features/      # 기능별 컴포넌트
│   │   └── router/        # Vue Router 설정
│   └── package.json
└── start_all.ps1          # 백엔드+프론트엔드 동시 실행 스크립트
```

## 🚀 주요 기능

- **Sample CRUD 게시판**: 데이터 생성, 조회, 수정, 삭제
- **사이드바 네비게이션**: Sample, Sample2 페이지 전환
- **REST API**: Flask 기반 RESTful API
- **반응형 UI**: 현대적이고 깔끔한 디자인
- **확장성 고려**: MVC 패턴, 컴포넌트 기반 구조

## 🛠 기술 스택

### Backend
- **Python 3.x**
- **Flask**: 웹 프레임워크
- **Flask-SQLAlchemy**: ORM
- **Flask-CORS**: CORS 처리
- **SQLite**: 데이터베이스

### Frontend
- **Vue.js 3**: 프론트엔드 프레임워크
- **Vue Router 4**: 라우팅
- **Axios**: HTTP 클라이언트
- **CSS3**: 스타일링

## 📦 설치 및 실행

### 전체 프로젝트 클론
```bash
git clone https://github.com/parkjinyong12/s_analysis.git
cd s_analysis
```

### Backend 설정 (Windows)
```bash
# 가상환경 생성 및 활성화
python -m venv backend\venv
backend\venv\Scripts\Activate

# 패키지 설치
pip install flask flask_sqlalchemy flask_cors

# DB 초기화 (최초 1회)
python
>>> from backend.app import create_app
>>> from backend.extensions import db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()

# 서버 실행
python -m backend.app
```

### Frontend 설정
```bash
cd frontend

# 패키지 설치
npm install

# 개발 서버 실행
npm run serve
```

### 한번에 실행 (Windows PowerShell)
```powershell
# 프로젝트 루트에서
./start_all.ps1
```

## 🌐 접속 정보

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000

## 📡 API 엔드포인트

### Sample CRUD
- `GET /samples/` - 전체 조회
- `GET /samples/<id>` - 단일 조회
- `POST /samples/` - 생성
- `PUT /samples/<id>` - 수정
- `DELETE /samples/<id>` - 삭제

### User CRUD
- `GET /users/` - 전체 조회
- `POST /users/` - 생성

## 📱 화면 구성

1. **사이드바**: Sample, Sample2 메뉴
2. **Sample 게시판**: CRUD 기능이 포함된 테이블 형태
3. **Sample2 게시판**: Sample과 동일한 기능

## 🔧 개발 환경

- **OS**: Windows 10/11
- **Python**: 3.x
- **Node.js**: 16.x 이상
- **PowerShell**: 실행 스크립트 지원

## 📝 라이센스

MIT License

## 👨‍💻 개발자

- GitHub: [@parkjinyong12](https://github.com/parkjinyong12)

---

### 개발 참고사항

- Backend는 MVC 패턴으로 구성되어 확장성을 고려했습니다
- Frontend는 기능별 폴더 구조로 관리됩니다
- CORS 설정이 적용되어 개발 환경에서 API 연동이 원활합니다
- SQLite DB 파일은 backend 폴더에 자동 생성됩니다 