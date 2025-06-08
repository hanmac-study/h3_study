# Claude Code 설정

## 프로젝트 개요
이 프로젝트는 Uber H3 라이브러리를 활용한 공간 분석 학습 프로젝트입니다.

## 프로젝트 구조
- `src/`: 모든 소스 코드 (카테고리별로 정리)
- `docs/`: 프로젝트 문서
- `result/`: 스크립트 실행 결과 (자동 생성)
- `sql/`: 데이터베이스 스키마

## 코딩 규칙
- 모든 주석과 문서는 한국어로 작성
- 코드 내 설명은 반드시 한글로 작성
- 프로젝트 루트 경로는 `os.path.abspath(os.path.join(current_dir, '..', '..'))` 패턴 사용
- 결과 파일은 `result/{script_name}/` 폴더에 타임스탬프와 함께 저장

## 실행 방법
```bash
# 기본 학습
python src/basics/h3_basics.py

# 고급 학습  
python src/advanced/h3_advanced.py

# 성능 분석
python src/performance/hexagon_vs_square_performance.py
```

## 주의사항
- 새 파일 생성 시 반드시 필요한 경우에만 생성
- 기존 파일 수정을 우선으로 함
- 문서 파일은 명시적 요청 시에만 생성

## 의존성
- Python 3.8+
- h3, folium, pandas, matplotlib, seaborn, psycopg2, numpy