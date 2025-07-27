# Backend (Flask)

## 폴더 구조 (확장성 고려)

```
backend/
├── app.py                # 앱 진입점
├── config.py             # 환경설정
├── extensions.py         # 확장 객체 (db, cors 등)
├── models/               # DB 모델
│   ├── user.py
│   ├── sample.py
│   ├── stock.py          # 주식 목록 모델
│   └── trading.py        # 주식 거래 데이터 모델
├── views/                # API/컨트롤러
│   ├── user.py
│   ├── sample.py
│   ├── stock.py          # 주식 REST API
│   └── trading.py        # 주식 거래 REST API
├── services/             # 비즈니스 로직
│   ├── user_service.py
│   ├── sample_service.py
│   ├── stock_service.py  # 주식 비즈니스 로직
│   ├── trading_service.py # 주식 거래 비즈니스 로직
│   └── data_collector.py # 데이터 수집 서비스
├── scripts/              # 실행 스크립트
│   └── collect_data.py   # 데이터 수집 스크립트
├── sql/                  # SQL 스크립트
│   └── init_tables.sql   # 테이블 생성 스크립트
└── venv/                 # 가상환경
```

## 데이터베이스 테이블

### stock_list 테이블
```sql
CREATE TABLE IF NOT EXISTS stock_list (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL UNIQUE,
    stock_name VARCHAR(100) NOT NULL,
    init_date VARCHAR(10), -- 상장일자
    institution_accum_init INTEGER NOT NULL DEFAULT 0,
    foreigner_accum_init INTEGER NOT NULL DEFAULT 0
);
```

### stock_investor_trading 테이블
```sql
CREATE TABLE IF NOT EXISTS stock_investor_trading (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100) NOT NULL,
    trade_date VARCHAR(10) NOT NULL,
    close_price INTEGER,
    institution_net_buy INTEGER,
    foreigner_net_buy INTEGER,
    institution_accum INTEGER,
    foreigner_accum INTEGER,
    institution_trend_signal VARCHAR(50),
    institution_trend_score REAL,
    foreigner_trend_signal VARCHAR(50),
    foreigner_trend_score REAL
);
```

### 기존 테이블들
- **users**: 사용자 정보 (SQLAlchemy 자동 생성)
- **tb_sample**: 샘플 데이터 (SQLAlchemy 자동 생성)

## 개발 환경 준비 (Windows)

1. 가상환경 활성화
```
backend\venv\Scripts\Activate
```
2. 패키지 설치 (최초 1회)
```
pip install flask flask_sqlalchemy flask_cors requests beautifulsoup4 pandas
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

## 데이터 수집

### 자동 데이터 수집
네이버 금융에서 주식 거래 데이터를 자동으로 수집하여 DB에 저장합니다.

```bash
# 전체 주식 데이터 수집 (3년간)
python backend/scripts/collect_data.py
```

### 수집되는 데이터
- **주식 기본 정보**: 코드, 이름
- **일별 거래 데이터**: 종가, 기관/외국인 순매수량
- **수집 기간**: 최근 3년간 데이터
- **대상 종목**: 시가총액 상위 50개 대형주

### 수집 기능
- **중복 방지**: 이미 존재하는 데이터는 스킵
- **에러 처리**: 네트워크 오류, 파싱 오류 등 안전하게 처리
- **로깅**: 수집 과정과 결과를 상세히 기록
- **진행률 표시**: 실시간 수집 상황 모니터링

## API 엔드포인트

### Stock CRUD (/stocks)
- `GET /stocks/` - 전체 주식 목록 조회
- `GET /stocks/<id>` - ID로 주식 조회
- `GET /stocks/code/<stock_code>` - 주식 코드로 조회
- `POST /stocks/` - 새 주식 생성
- `PUT /stocks/<id>` - 주식 정보 수정
- `DELETE /stocks/<id>` - 주식 삭제
- `GET /stocks/search?name=삼성&code=005` - 주식 검색
- `PUT /stocks/<id>/accum` - 누적 초기값 업데이트

### Trading CRUD (/trading)
- `GET /trading/` - 전체 거래 데이터 목록 조회
- `GET /trading/<id>` - ID로 거래 데이터 조회
- `GET /trading/stock/<stock_code>` - 주식 코드로 거래 데이터 조회
- `GET /trading/date-range?start_date=2024-01-01&end_date=2024-01-31&stock_code=005930` - 날짜 범위로 조회
- `POST /trading/` - 새 거래 데이터 생성
- `PUT /trading/<id>` - 거래 데이터 정보 수정
- `DELETE /trading/<id>` - 거래 데이터 삭제
- `GET /trading/search?name=삼성` - 거래 데이터 검색
- `PUT /trading/<id>/trend` - 트렌드 분석 데이터 업데이트

### Sample CRUD (/samples)
- `GET /samples/` - 전체 조회
- `POST /samples/` - 생성
- `PUT /samples/<id>` - 수정
- `DELETE /samples/<id>` - 삭제

### User CRUD (/users)
- `GET /users/` - 전체 조회
- `POST /users/` - 생성

## 사용 예시

### 데이터 수집 후 API 사용
```bash
# 1. 데이터 수집
python backend/scripts/collect_data.py

# 2. 서버 실행
python backend/app.py

# 3. API 호출 예시
curl http://localhost:5000/stocks/
curl http://localhost:5000/trading/stock/005930
curl "http://localhost:5000/trading/date-range?start_date=2024-01-01&end_date=2024-01-31"
``` 