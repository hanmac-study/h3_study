# H3 Study Project

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Uber H3 라이브러리를 활용한 공간 분석 학습 프로젝트입니다.

## 📋 프로젝트 개요

이 프로젝트는 Uber H3 라이브러리의 다양한 기능을 체계적으로 학습하고, 실무에서 활용할 수 있는 공간 분석 기법을 습득하기 위한 종합 학습 플랫폼입니다.

### 🎯 학습 목표

- H3 라이브러리의 기본 개념과 사용법 익히기
- 공간 데이터 분석을 위한 고급 기법 학습
- 데이터베이스와의 연동을 통한 대용량 공간 데이터 처리
- 성능 최적화 기법 및 벤치마킹

## 🏗️ 프로젝트 구조

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
│   ├── LEARNING_GUIDE.md  # 학습 가이드
│   ├── README_POSTGRES.md # PostgreSQL 설정 가이드
│   ├── RESULT_SYSTEM_GUIDE.md # 결과 시스템 가이드
│   └── performance/       # 성능 분석 문서
├── result/               # 결과 파일 (자동 생성)
├── sql/                  # SQL 스크립트
│   └── table.sql         # 테이블 스키마
├── requirements.txt      # Python 의존성
├── pyproject.toml       # 프로젝트 설정
└── CLAUDE.md            # Claude Code 설정
```

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/hanmac-study/h3_study.git
cd h3_study
```

### 2. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 학습 실행

#### 🌟 기본 학습 (추천 시작점)
```bash
python src/basics/h3_basics.py
```

#### 🔥 고급 학습
```bash
python src/advanced/h3_advanced.py
```

#### 💼 실무 예제
```bash
python src/advanced/h3_practical_examples.py
```

#### ⚡ 성능 분석
```bash
python src/performance/hexagon_vs_square_performance.py
```

#### 🗄️ PostgreSQL 연동 (선택사항)
```bash
# 데이터베이스 생성
createdb h3_study

# 테이블 생성
psql -U postgres -d h3_study -f sql/table.sql

# 스크립트 실행
python src/database/h3_advance_with_pg.py
```

## 📊 결과 파일

- 모든 결과는 `result/` 폴더에 저장됩니다
- 각 스크립트별로 별도 폴더가 생성됩니다
- 파일명에는 실행 시간이 포함됩니다 (형식: `filename_yymmdd_hhmmss.ext`)

**결과 파일 예시:**
```
result/
├── h3_advanced/
│   ├── advanced_spatial_analysis_250608_154423.html
│   ├── aggregation_analysis_250608_154423.png
│   └── ...
└── hexagon_vs_square_performance/
    ├── run_20250608_154443_comprehensive_performance_comparison.png
    └── ...
```

## 📚 문서

- [📖 학습 가이드](docs/LEARNING_GUIDE.md) - 단계별 학습 진행 방법
- [🐘 PostgreSQL 설정 가이드](docs/README_POSTGRES.md) - 데이터베이스 연동 설정
- [📈 결과 시스템 가이드](docs/RESULT_SYSTEM_GUIDE.md) - 결과 파일 활용 방법
- [⚡ 성능 분석 문서](docs/performance/) - 성능 최적화 관련 자료

## 🛠️ 기술 스택

- **Python 3.8+**
- **핵심 라이브러리:**
  - `h3` - Uber H3 지오스페이셜 인덱싱 시스템
  - `folium` - 인터랙티브 지도 시각화
  - `pandas` - 데이터 분석 및 처리
  - `matplotlib` / `seaborn` - 데이터 시각화
  - `psycopg2` - PostgreSQL 연동
  - `numpy` - 수치 연산

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🙏 감사의 말

- [Uber H3](https://h3geo.org/) - 강력한 지오스페이셜 인덱싱 시스템
- [Folium](https://folium.readthedocs.io/) - 아름다운 지도 시각화 도구
- [Claude Code](https://claude.ai/code) - AI 기반 코드 생성 및 최적화

---

**Made with ❤️ by [hanmac-study](https://github.com/hanmac-study)**