# Backend (Flask)

## 폴더 구조 (확장성 고려)

```
backend/
├── app.py                # 앱 진입점
├── config.py             # 환경설정
├── extensions.py         # 확장 객체 (db, cors 등)
├── models/               # DB 모델
│   └── user.py
├── views/                # API/컨트롤러
│   └── user.py
├── services/             # 비즈니스 로직
│   └── user_service.py
└── venv/                 # 가상환경
```

## 개발 환경 준비 (Windows)

1. 가상환경 활성화
```
backend\venv\Scripts\Activate
```
2. 패키지 설치 (최초 1회)
```
pip install flask flask_sqlalchemy flask_cors
```
3. DB 초기화 (최초 1회)
```
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
... 
>>> exit()
```
4. 서버 실행
```
python app.py
``` 