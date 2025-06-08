# H3 vs Square Grid PostgreSQL 성능 비교

H3 육각형 그리드와 전통적인 사각형 그리드의 PostgreSQL에서의 CRUD 성능을 비교 분석합니다.

## 📋 준비사항

### 1. PostgreSQL 설치 및 설정

PostgreSQL이 설치되어 있어야 합니다. (버전 12 이상 권장)

### 2. 데이터베이스 생성

```bash
# 방법 1: 커맨드라인에서
createdb h3_study

# 방법 2: PostgreSQL 콘솔에서
psql -U postgres
CREATE DATABASE h3_study;
\q
```

### 3. 테이블 생성

제공된 `table.sql` 파일을 실행하여 필요한 테이블과 인덱스를 생성합니다:

```bash
# 커맨드라인에서 실행
psql -U postgres -d h3_study -f table.sql

# 또는 pgAdmin에서 table.sql 파일 내용을 실행
```

### 4. Python 패키지 설치

```bash
pip install -r requirements.txt
```

## 🚀 실행 방법

### 기본 실행

```bash
python h3_advance_with_pg.py
```

### 데이터베이스 연결 정보 수정

파일 내 `main()` 함수에서 연결 정보를 수정할 수 있습니다:

```python
db_config = {
    'host': 'localhost',      # PostgreSQL 서버 주소
    'database': 'h3_study',    # 데이터베이스 이름
    'user': 'postgres',        # 사용자명
    'password': 'postgres',    # 비밀번호 (실제 비밀번호로 변경)
    'port': 5432              # 포트 번호
}
```

## 📊 테이블 구조

### locations_h3 테이블
- H3 인덱스 기반 위치 데이터 저장
- 주요 컬럼: h3_index, h3_resolution, lat, lng, category, value

### locations_square 테이블
- 사각형 그리드 기반 위치 데이터 저장
- 주요 컬럼: grid_x, grid_y, grid_resolution, lat, lng, category, value

## 🔍 성능 테스트 항목

1. **INSERT 성능**: 대량 데이터 삽입
2. **SELECT 성능**: 
   - 포인트 쿼리
   - 범위 쿼리
   - 집계 쿼리
3. **UPDATE 성능**: 단일/범위 업데이트
4. **DELETE 성능**: 대량 삭제
5. **공간 쿼리**: 
   - 주변 지역 검색
   - 경로상 데이터 검색

## 📈 결과물

- `h3_vs_square_postgres_performance.png`: 성능 비교 차트
- `h3_postgres_results.json`: 상세 성능 측정 결과

## 🛠️ 문제 해결

### 데이터베이스 연결 실패
- PostgreSQL 서비스가 실행 중인지 확인
- 연결 정보(사용자명, 비밀번호, 포트)가 올바른지 확인
- 방화벽 설정 확인

### 테이블이 없다는 오류
- `table.sql` 파일을 먼저 실행했는지 확인
- 올바른 데이터베이스에 연결했는지 확인

### 권한 오류
- 사용자에게 CREATE, INSERT, UPDATE, DELETE 권한이 있는지 확인

## 💡 주요 인사이트

1. **H3의 장점**:
   - 인근 검색(k-ring)에서 우수한 성능
   - 계층적 구조로 다양한 해상도 분석 가능
   - 공간 집계 쿼리에 최적화

2. **사각형 그리드의 장점**:
   - 단순한 범위 검색에서 경쟁력
   - 구현과 이해가 쉬움
   - 기존 좌표 체계와 호환성 좋음

3. **성능 최적화 팁**:
   - 적절한 인덱스 설계가 핵심
   - 배치 처리로 INSERT 성능 향상
   - 해상도 선택이 성능에 큰 영향