-- H3 vs Square Grid 성능 비교를 위한 테이블 생성 스크립트
-- 데이터베이스: h3_study
-- 스키마: hanmac-study

-- 데이터베이스 생성 (필요시)
-- CREATE DATABASE h3_study;

-- PostGIS 확장 설치 (선택사항, 고급 공간 기능 필요시)
-- CREATE EXTENSION IF NOT EXISTS postgis;

-- 스키마 생성 (존재하지 않을 경우)
CREATE SCHEMA IF NOT EXISTS "hanmac-study";

-- 기존 테이블 삭제
DROP TABLE IF EXISTS "hanmac-study".locations_h3 CASCADE;
DROP TABLE IF EXISTS "hanmac-study".locations_square CASCADE;

-- H3 기반 위치 데이터 테이블
CREATE TABLE "hanmac-study".locations_h3 (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    h3_index VARCHAR(20) NOT NULL,
    h3_resolution INT NOT NULL,
    category VARCHAR(50),
    value DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 사각형 그리드 기반 위치 데이터 테이블
CREATE TABLE "hanmac-study".locations_square (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    grid_x INT NOT NULL,
    grid_y INT NOT NULL,
    grid_resolution INT NOT NULL,
    category VARCHAR(50),
    value DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- H3 테이블 인덱스
CREATE INDEX idx_h3_index ON "hanmac-study".locations_h3(h3_index);
CREATE INDEX idx_h3_category ON "hanmac-study".locations_h3(category);
CREATE INDEX idx_h3_lat_lng ON "hanmac-study".locations_h3(lat, lng);
CREATE INDEX idx_h3_value ON "hanmac-study".locations_h3(value);
CREATE INDEX idx_h3_created_at ON "hanmac-study".locations_h3(created_at);

-- 복합 인덱스 (자주 함께 사용되는 컬럼들)
CREATE INDEX idx_h3_index_category ON "hanmac-study".locations_h3(h3_index, category);
CREATE INDEX idx_h3_category_value ON "hanmac-study".locations_h3(category, value);

-- 사각형 그리드 테이블 인덱스
CREATE INDEX idx_square_grid ON "hanmac-study".locations_square(grid_x, grid_y);
CREATE INDEX idx_square_category ON "hanmac-study".locations_square(category);
CREATE INDEX idx_square_lat_lng ON "hanmac-study".locations_square(lat, lng);
CREATE INDEX idx_square_value ON "hanmac-study".locations_square(value);
CREATE INDEX idx_square_created_at ON "hanmac-study".locations_square(created_at);

-- 복합 인덱스
CREATE INDEX idx_square_grid_category ON "hanmac-study".locations_square(grid_x, grid_y, category);
CREATE INDEX idx_square_category_value ON "hanmac-study".locations_square(category, value);

-- 통계 수집을 위한 뷰 (선택사항)
CREATE OR REPLACE VIEW "hanmac-study".v_h3_statistics AS
SELECT 
    h3_index,
    COUNT(*) as location_count,
    COUNT(DISTINCT category) as category_count,
    AVG(value) as avg_value,
    SUM(value) as total_value,
    MIN(value) as min_value,
    MAX(value) as max_value
FROM "hanmac-study".locations_h3
GROUP BY h3_index;

CREATE OR REPLACE VIEW "hanmac-study".v_square_statistics AS
SELECT 
    grid_x,
    grid_y,
    COUNT(*) as location_count,
    COUNT(DISTINCT category) as category_count,
    AVG(value) as avg_value,
    SUM(value) as total_value,
    MIN(value) as min_value,
    MAX(value) as max_value
FROM "hanmac-study".locations_square
GROUP BY grid_x, grid_y;

-- 업데이트 시간 자동 갱신을 위한 트리거 함수
CREATE OR REPLACE FUNCTION "hanmac-study".update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- H3 테이블 트리거
CREATE TRIGGER update_locations_h3_updated_at 
    BEFORE UPDATE ON "hanmac-study".locations_h3 
    FOR EACH ROW 
    EXECUTE FUNCTION "hanmac-study".update_updated_at_column();

-- 사각형 그리드 테이블 트리거
CREATE TRIGGER update_locations_square_updated_at 
    BEFORE UPDATE ON "hanmac-study".locations_square 
    FOR EACH ROW 
    EXECUTE FUNCTION "hanmac-study".update_updated_at_column();

-- 샘플 데이터 검증을 위한 체크 제약조건
ALTER TABLE "hanmac-study".locations_h3 
    ADD CONSTRAINT chk_h3_resolution CHECK (h3_resolution >= 0 AND h3_resolution <= 15);

ALTER TABLE "hanmac-study".locations_h3 
    ADD CONSTRAINT chk_h3_lat CHECK (lat >= -90 AND lat <= 90);

ALTER TABLE "hanmac-study".locations_h3 
    ADD CONSTRAINT chk_h3_lng CHECK (lng >= -180 AND lng <= 180);

ALTER TABLE "hanmac-study".locations_square 
    ADD CONSTRAINT chk_square_lat CHECK (lat >= -90 AND lat <= 90);

ALTER TABLE "hanmac-study".locations_square 
    ADD CONSTRAINT chk_square_lng CHECK (lng >= -180 AND lng <= 180);

-- 테이블 및 인덱스 통계 정보 확인 쿼리
/*
-- 테이블 크기 확인
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'hanmac-study'
AND tablename IN ('locations_h3', 'locations_square');

-- 인덱스 사용 통계
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'hanmac-study'
AND tablename IN ('locations_h3', 'locations_square')
ORDER BY idx_scan DESC;
*/