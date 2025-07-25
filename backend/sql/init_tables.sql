-- Stock Analysis Database 초기화 스크립트
-- 실행 방법: SQLite 콘솔에서 .read backend/sql/init_tables.sql

-- 주식 목록 테이블 생성
CREATE TABLE IF NOT EXISTS stock_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code VARCHAR(20) NOT NULL UNIQUE,
    stock_name VARCHAR(100) NOT NULL,
    init_date VARCHAR(10),
    institution_accum_init INTEGER NOT NULL DEFAULT 0,
    foreigner_accum_init INTEGER NOT NULL DEFAULT 0
);

-- 주식 투자자별 거래 데이터 테이블 생성
CREATE TABLE IF NOT EXISTS stock_investor_trading (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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

-- 기존 테이블들 (참고용)
-- users 테이블은 SQLAlchemy로 자동 생성
-- tb_sample 테이블은 SQLAlchemy로 자동 생성

-- 샘플 데이터 삽입 (선택사항)
-- INSERT INTO stock_list (stock_code, stock_name, init_date, institution_accum_init, foreigner_accum_init) 
-- VALUES 
--     ('005930', '삼성전자', '2024-01-01', 1000, 2000),
--     ('000660', 'SK하이닉스', '2024-01-01', 800, 1500),
--     ('035420', 'NAVER', '2024-01-01', 600, 1200);

-- INSERT INTO stock_investor_trading (stock_code, stock_name, trade_date, close_price, institution_net_buy, foreigner_net_buy, institution_accum, foreigner_accum, institution_trend_signal, institution_trend_score, foreigner_trend_signal, foreigner_trend_score)
-- VALUES 
--     ('005930', '삼성전자', '2024-01-01', 70000, 100, -50, 1100, 1950, '상승', 0.8, '하락', -0.3),
--     ('005930', '삼성전자', '2024-01-02', 71000, 200, 100, 1300, 2050, '상승', 0.9, '상승', 0.5),
--     ('000660', 'SK하이닉스', '2024-01-01', 120000, -50, 200, 750, 1700, '하락', -0.4, '상승', 0.7); 