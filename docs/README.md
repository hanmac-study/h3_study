# H3 Study Project

Uber H3 라이브러리를 활용한 공간 분석 학습 프로젝트입니다.

## 프로젝트 구조

```
h3_study/
├── src/                    # 소스 코드
│   ├── basics/            # 기본 학습 모듈
│   │   └── h3_basics.py   # H3 기본 기능 학습
│   ├── advanced/          # 고급 학습 모듈
│   │   ├── h3_advanced.py # H3 고급 기능 학습
│   │   └── h3_practical_examples.py # 실무 활용 예제
│   ├── database/          # 데이터베이스 관련
│   │   └── h3_advance_with_pg.py # PostgreSQL 연동
│   └── performance/       # 성능 분석
│       ├── hexagon_vs_square_performance.py # 육각형 vs 사각형 비교
│       └── database_optimization_study.py # DB 최적화 연구
├── docs/                  # 문서
├── result/               # 결과 파일 (자동 생성)
├── sql/                  # SQL 스크립트
│   └── table.sql         # 테이블 스키마
├── requirements.txt      # 파이썬 의존성
└── pyproject.toml       # 프로젝트 설정
```

## 시작하기

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 실행 방법

#### 기본 학습
```bash
python src/basics/h3_basics.py
```

#### 고급 학습
```bash
python src/advanced/h3_advanced.py
```

#### 실무 예제
```bash
python src/advanced/h3_practical_examples.py
```

#### PostgreSQL 연동 (데이터베이스 설정 필요)
```bash
# 데이터베이스 생성
createdb h3_study

# 테이블 생성
psql -U postgres -d h3_study -f sql/table.sql

# 스크립트 실행
python src/database/h3_advance_with_pg.py
```

## 결과 파일

- 모든 결과는 `result/` 폴더에 저장됩니다
- 각 스크립트별로 별도 폴더가 생성됩니다
- 파일명에는 실행 시간이 포함됩니다 (형식: `filename_yymmdd_hhmmss.ext`)

## 문서

- [학습 가이드](docs/LEARNING_GUIDE.md)
- [PostgreSQL 설정 가이드](docs/README_POSTGRES.md)
- [결과 시스템 가이드](docs/RESULT_SYSTEM_GUIDE.md)
- [성능 분석 문서](docs/performance/)