-- PostgreSQL Database Schema for Stock Analysis System
-- 실행 방법: psql -h hostname -U username -d database_name -f backend/sql/postgresql_schema.sql

-- 주식 목록 테이블 생성
CREATE TABLE IF NOT EXISTS stock_list (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL UNIQUE,
    stock_name VARCHAR(100) NOT NULL,
    init_date VARCHAR(10),
    institution_accum_init INTEGER NOT NULL DEFAULT 0,
    foreigner_accum_init INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 주식 투자자별 거래 데이터 테이블 생성
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
    foreigner_trend_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 데이터 히스토리 테이블 생성
CREATE TABLE IF NOT EXISTS data_history (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER,
    action VARCHAR(20) NOT NULL,
    field_name VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 시스템 로그 테이블 생성
CREATE TABLE IF NOT EXISTS system_log (
    id SERIAL PRIMARY KEY,
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    module VARCHAR(50),
    function_name VARCHAR(100),
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
-- 주식 코드 인덱스
CREATE INDEX IF NOT EXISTS idx_stock_list_stock_code ON stock_list(stock_code);

-- 거래 데이터 인덱스들 (기본 인덱스)
CREATE INDEX IF NOT EXISTS idx_stock_investor_trading_stock_code ON stock_investor_trading(stock_code);
CREATE INDEX IF NOT EXISTS idx_stock_investor_trading_trade_date ON stock_investor_trading(trade_date);
CREATE INDEX IF NOT EXISTS idx_stock_investor_trading_stock_date ON stock_investor_trading(stock_code, trade_date);
CREATE INDEX IF NOT EXISTS idx_stock_investor_trading_date_stock ON stock_investor_trading(trade_date, stock_code);

-- 거래 데이터 조회 성능 최적화 인덱스 (추가)
-- 날짜 범위 조회 최적화
CREATE INDEX IF NOT EXISTS idx_trading_date_range ON stock_investor_trading(trade_date);
CREATE INDEX IF NOT EXISTS idx_trading_date_close_price ON stock_investor_trading(trade_date, close_price);

-- 종목별 날짜 범위 조회 최적화
CREATE INDEX IF NOT EXISTS idx_trading_stock_date_range ON stock_investor_trading(stock_code, trade_date);
CREATE INDEX IF NOT EXISTS idx_trading_stock_date_close ON stock_investor_trading(stock_code, trade_date, close_price);

-- 기관/외국인 순매수 조회 최적화
CREATE INDEX IF NOT EXISTS idx_trading_stock_date_institution_net ON stock_investor_trading(stock_code, trade_date, institution_net_buy);
CREATE INDEX IF NOT EXISTS idx_trading_stock_date_foreigner_net ON stock_investor_trading(stock_code, trade_date, foreigner_net_buy);

-- 히스토리 인덱스들
CREATE INDEX IF NOT EXISTS idx_data_history_table_name ON data_history(table_name);
CREATE INDEX IF NOT EXISTS idx_data_history_created_at ON data_history(created_at);
CREATE INDEX IF NOT EXISTS idx_data_history_action ON data_history(action);

-- 시스템 로그 인덱스들
CREATE INDEX IF NOT EXISTS idx_system_log_level ON system_log(level);
CREATE INDEX IF NOT EXISTS idx_system_log_created_at ON system_log(created_at);

-- 제약 조건 추가
-- 거래 데이터의 주식 코드와 날짜 조합은 유니크해야 함
ALTER TABLE stock_investor_trading 
ADD CONSTRAINT uk_stock_investor_trading_stock_date 
UNIQUE (stock_code, trade_date);

-- 업데이트 트리거 함수 생성
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 업데이트 트리거 생성
CREATE TRIGGER update_stock_list_updated_at 
    BEFORE UPDATE ON stock_list 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stock_investor_trading_updated_at 
    BEFORE UPDATE ON stock_investor_trading 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 댓글 추가
COMMENT ON TABLE stock_list IS '주식 목록 정보';
COMMENT ON TABLE stock_investor_trading IS '주식 투자자별 거래 데이터';
COMMENT ON TABLE data_history IS '데이터 변경 히스토리';
COMMENT ON TABLE system_log IS '시스템 로그';

COMMENT ON COLUMN stock_list.stock_code IS '주식 코드';
COMMENT ON COLUMN stock_list.stock_name IS '주식명';
COMMENT ON COLUMN stock_list.init_date IS '상장일자';
COMMENT ON COLUMN stock_list.institution_accum_init IS '기관 누적 초기값';
COMMENT ON COLUMN stock_list.foreigner_accum_init IS '외국인 누적 초기값';

COMMENT ON COLUMN stock_investor_trading.stock_code IS '주식 코드';
COMMENT ON COLUMN stock_investor_trading.stock_name IS '주식명';
COMMENT ON COLUMN stock_investor_trading.trade_date IS '거래 날짜 (YYYY-MM-DD)';
COMMENT ON COLUMN stock_investor_trading.close_price IS '종가';
COMMENT ON COLUMN stock_investor_trading.institution_net_buy IS '기관 순매수';
COMMENT ON COLUMN stock_investor_trading.foreigner_net_buy IS '외국인 순매수';
COMMENT ON COLUMN stock_investor_trading.institution_accum IS '기관 누적 매수';
COMMENT ON COLUMN stock_investor_trading.foreigner_accum IS '외국인 누적 매수'; 