-- system_log 테이블에 누락된 컬럼들 추가
-- 기존 테이블이 있다면 컬럼을 추가하고, 없다면 새로 생성

-- 1. 기존 테이블이 있는지 확인하고 컬럼 추가
DO $$
BEGIN
    -- category 컬럼이 없으면 추가
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'system_log' AND column_name = 'category'
    ) THEN
        ALTER TABLE system_log ADD COLUMN category VARCHAR(50) NOT NULL DEFAULT 'SYSTEM';
    END IF;
    
    -- details 컬럼이 없으면 추가
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'system_log' AND column_name = 'details'
    ) THEN
        ALTER TABLE system_log ADD COLUMN details TEXT;
    END IF;
    
    -- user_id 컬럼이 없으면 추가
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'system_log' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE system_log ADD COLUMN user_id INTEGER;
    END IF;
    
    -- ip_address 컬럼이 없으면 추가
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'system_log' AND column_name = 'ip_address'
    ) THEN
        ALTER TABLE system_log ADD COLUMN ip_address VARCHAR(45);
    END IF;
    
    -- level 컬럼의 길이를 20으로 변경 (기존 10에서 확장)
    ALTER TABLE system_log ALTER COLUMN level TYPE VARCHAR(20);
    
    -- 불필요한 컬럼들 제거 (모델에 없는 컬럼들)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'system_log' AND column_name = 'module'
    ) THEN
        ALTER TABLE system_log DROP COLUMN module;
    END IF;
    
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'system_log' AND column_name = 'function_name'
    ) THEN
        ALTER TABLE system_log DROP COLUMN function_name;
    END IF;
    
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'system_log' AND column_name = 'line_number'
    ) THEN
        ALTER TABLE system_log DROP COLUMN line_number;
    END IF;
    
END $$;

-- 2. 인덱스 추가 (없다면)
CREATE INDEX IF NOT EXISTS idx_system_log_category ON system_log(category);
CREATE INDEX IF NOT EXISTS idx_system_log_level ON system_log(level);
CREATE INDEX IF NOT EXISTS idx_system_log_created_at ON system_log(created_at);

-- 3. 댓글 추가
COMMENT ON TABLE system_log IS '시스템 로그';
COMMENT ON COLUMN system_log.level IS '로그 레벨 (INFO, WARNING, ERROR)';
COMMENT ON COLUMN system_log.category IS '카테고리 (API, DATABASE, COLLECTOR, etc.)';
COMMENT ON COLUMN system_log.message IS '로그 메시지';
COMMENT ON COLUMN system_log.details IS '상세 정보 (JSON)';
COMMENT ON COLUMN system_log.user_id IS '사용자 ID';
COMMENT ON COLUMN system_log.ip_address IS 'IP 주소';
COMMENT ON COLUMN system_log.created_at IS '생성 시간'; 