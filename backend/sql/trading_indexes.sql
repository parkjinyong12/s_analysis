-- 거래 데이터 조회 성능 최적화를 위한 인덱스 스크립트
-- 실행 방법: psql -h hostname -U username -d database_name -f backend/sql/trading_indexes.sql

-- ========================================
-- 1단계: 날짜 범위 조회 최적화 인덱스
-- ========================================

-- 날짜 범위 조회를 위한 기본 인덱스 (초기 단계)
-- trade_date만으로 조회할 때 사용
CREATE INDEX IF NOT EXISTS idx_trading_date_range 
ON stock_investor_trading(trade_date);

-- 날짜 범위 + 종가 조회를 위한 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_trading_date_close_price 
ON stock_investor_trading(trade_date, close_price);

-- 날짜 범위 + 기관/외국인 순매수 조회를 위한 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_trading_date_institution_net 
ON stock_investor_trading(trade_date, institution_net_buy);

CREATE INDEX IF NOT EXISTS idx_trading_date_foreigner_net 
ON stock_investor_trading(trade_date, foreigner_net_buy);

-- 날짜 범위 + 누적 매수 조회를 위한 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_trading_date_institution_accum 
ON stock_investor_trading(trade_date, institution_accum);

CREATE INDEX IF NOT EXISTS idx_trading_date_foreigner_accum 
ON stock_investor_trading(trade_date, foreigner_accum);

-- ========================================
-- 2단계: 종목별 + 날짜 범위 조회 최적화 인덱스
-- ========================================

-- 종목별 날짜 범위 조회를 위한 복합 인덱스 (주요 인덱스)
CREATE INDEX IF NOT EXISTS idx_trading_stock_date_range 
ON stock_investor_trading(stock_code, trade_date);

-- 종목별 날짜 범위 + 종가 조회를 위한 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_trading_stock_date_close 
ON stock_investor_trading(stock_code, trade_date, close_price);

-- 종목별 날짜 범위 + 기관/외국인 순매수 조회를 위한 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_trading_stock_date_institution_net 
ON stock_investor_trading(stock_code, trade_date, institution_net_buy);

CREATE INDEX IF NOT EXISTS idx_trading_stock_date_foreigner_net 
ON stock_investor_trading(stock_code, trade_date, foreigner_net_buy);

-- 종목별 날짜 범위 + 누적 매수 조회를 위한 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_trading_stock_date_institution_accum 
ON stock_investor_trading(stock_code, trade_date, institution_accum);

CREATE INDEX IF NOT EXISTS idx_trading_stock_date_foreigner_accum 
ON stock_investor_trading(stock_code, trade_date, foreigner_accum);

-- ========================================
-- 3단계: 고급 조회 최적화 인덱스
-- ========================================

-- 종목명으로도 조회할 수 있도록 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_trading_stock_name_date 
ON stock_investor_trading(stock_name, trade_date);

-- 트렌드 신호 조회를 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_trading_institution_trend 
ON stock_investor_trading(stock_code, trade_date, institution_trend_signal);

CREATE INDEX IF NOT EXISTS idx_trading_foreigner_trend 
ON stock_investor_trading(stock_code, trade_date, foreigner_trend_signal);

-- 트렌드 점수 조회를 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_trading_institution_score 
ON stock_investor_trading(stock_code, trade_date, institution_trend_score);

CREATE INDEX IF NOT EXISTS idx_trading_foreigner_score 
ON stock_investor_trading(stock_code, trade_date, foreigner_trend_score);

-- ========================================
-- 4단계: 부분 인덱스 (조건부 인덱스)
-- ========================================

-- 특정 조건을 만족하는 데이터만 인덱싱 (성능 최적화)
-- 기관 순매수가 있는 데이터만 인덱싱
CREATE INDEX IF NOT EXISTS idx_trading_institution_net_not_null 
ON stock_investor_trading(stock_code, trade_date) 
WHERE institution_net_buy IS NOT NULL;

-- 외국인 순매수가 있는 데이터만 인덱싱
CREATE INDEX IF NOT EXISTS idx_trading_foreigner_net_not_null 
ON stock_investor_trading(stock_code, trade_date) 
WHERE foreigner_net_buy IS NOT NULL;

-- 종가가 있는 데이터만 인덱싱
CREATE INDEX IF NOT EXISTS idx_trading_close_price_not_null 
ON stock_investor_trading(stock_code, trade_date) 
WHERE close_price IS NOT NULL;

-- ========================================
-- 5단계: 통계 및 분석용 인덱스
-- ========================================

-- 날짜별 통계 조회를 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_trading_date_stats 
ON stock_investor_trading(trade_date, close_price, institution_net_buy, foreigner_net_buy);

-- 종목별 통계 조회를 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_trading_stock_stats 
ON stock_investor_trading(stock_code, close_price, institution_net_buy, foreigner_net_buy);

-- ========================================
-- 인덱스 정보 확인 쿼리
-- ========================================

-- 생성된 인덱스 목록 확인
-- SELECT 
--     schemaname,
--     tablename,
--     indexname,
--     indexdef
-- FROM pg_indexes 
-- WHERE tablename = 'stock_investor_trading'
-- ORDER BY indexname;

-- 인덱스 사용 통계 확인
-- SELECT 
--     schemaname,
--     tablename,
--     indexname,
--     idx_scan,
--     idx_tup_read,
--     idx_tup_fetch
-- FROM pg_stat_user_indexes 
-- WHERE tablename = 'stock_investor_trading'
-- ORDER BY idx_scan DESC;

-- ========================================
-- 인덱스 최적화 권장사항
-- ========================================

/*
1. 초기 단계 (데이터가 적을 때):
   - idx_trading_date_range
   - idx_trading_stock_date_range

2. 성장 단계 (데이터가 증가할 때):
   - 모든 기본 복합 인덱스 추가
   - 부분 인덱스 고려

3. 성숙 단계 (대용량 데이터):
   - 통계 인덱스 추가
   - 정기적인 인덱스 재구성 (REINDEX)
   - 사용하지 않는 인덱스 제거

4. 성능 모니터링:
   - pg_stat_user_indexes 테이블로 인덱스 사용률 확인
   - 느린 쿼리 분석 및 인덱스 튜닝
*/ 