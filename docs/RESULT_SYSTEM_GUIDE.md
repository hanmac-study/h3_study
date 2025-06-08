# 📊 H3 Study 결과 파일 시스템 가이드

## 🎯 개요

H3 학습 프로젝트의 모든 성능 테스트 결과를 체계적으로 관리하기 위한 새로운 결과 파일 시스템입니다.

## 🏗️ 시스템 구조

### 기본 원칙
1. **중앙집중식 관리**: 모든 결과 파일을 `result/` 폴더에 집중
2. **실행파일별 분류**: 각 스크립트별로 별도 하위 폴더
3. **타임스탬프 기반 식별**: 실행 시점으로 고유 식별자 생성
4. **확장 가능한 구조**: 새로운 테스트 추가 시 쉽게 확장

### 폴더 구조
```
h3_study/
├── result/                              # 📁 모든 결과 파일 저장소
│   ├── hexagon_vs_square_performance/   # 🔄 메모리 기반 성능 비교
│   ├── h3_advance_with_pg/              # 🐘 PostgreSQL 기반 비교
│   ├── [future_test_name]/              # 🚀 향후 추가될 테스트들
│   └── README.md                        # 📖 결과 파일 가이드
├── performance/                         # 📝 테스트 스크립트들
└── [기타 프로젝트 파일들]
```

## 🏷️ 파일 명명 규칙

### 실행 ID 형식
```
run_YYYYMMDD_HHMMSS
예: run_20241208_143022
```

### 파일명 형식
```
{실행ID}_{파일유형}.{확장자}
예: run_20241208_143022_performance_report.json
```

## 📋 테스트별 결과 파일

### 1. hexagon_vs_square_performance.py

**위치**: `result/hexagon_vs_square_performance/`

| 파일 | 설명 | 활용 |
|------|------|------|
| `{run_id}_performance_report.json` | 상세 수치 데이터 | 프로그래밍 분석 |
| `{run_id}_comprehensive_performance_comparison.png` | 12개 차트 대시보드 | 시각적 분석 |
| `{run_id}_dashboard_data.json` | 요약 및 권장사항 | 웹 대시보드 |
| `{run_id}_execution_summary.html` | 실행 요약 리포트 | 빠른 확인 |

### 2. h3_advance_with_pg.py

**위치**: `result/h3_advance_with_pg/`

| 파일 | 설명 | 활용 |
|------|------|------|
| `{run_id}_h3_postgres_results.json` | CRUD 성능 데이터 | DB 최적화 |
| `{run_id}_h3_vs_square_postgres_performance.png` | CRUD 비교 차트 | 성능 분석 |

## 🚀 사용 방법

### 1. 테스트 실행
```bash
# 성능 비교 테스트
python performance/hexagon_vs_square_performance.py

# PostgreSQL 테스트 (DB 설정 필요)
python h3_advance_with_pg.py
```

### 2. 결과 확인
```bash
# 최신 결과 확인
ls -la result/hexagon_vs_square_performance/

# HTML 요약 보기 (macOS)
open result/hexagon_vs_square_performance/run_*_execution_summary.html
```

### 3. 프로그래밍 분석
```python
import json
import pandas as pd
from datetime import datetime

# 최신 결과 로드
def load_latest_results(test_name):
    import glob
    pattern = f"result/{test_name}/run_*_performance_report.json"
    files = sorted(glob.glob(pattern))
    if files:
        with open(files[-1]) as f:
            return json.load(f)
    return None

# 사용 예시
results = load_latest_results('hexagon_vs_square_performance')
if results:
    print(f"인덱싱 성능: H3 {results['indexing_performance']['h3_times']}")
```

## 🔧 고급 활용

### 1. 성능 트렌드 분석
```python
def analyze_performance_trend(test_name, metric_path):
    """여러 실행 결과의 성능 트렌드 분석"""
    import glob
    import json
    
    files = sorted(glob.glob(f"result/{test_name}/run_*_performance_report.json"))
    
    trends = []
    for file in files:
        with open(file) as f:
            data = json.load(f)
        
        # 파일명에서 타임스탬프 추출
        timestamp = file.split('_')[1] + '_' + file.split('_')[2].split('_')[0]
        
        # metric_path를 통해 원하는 메트릭 추출
        metric_value = data
        for key in metric_path.split('.'):
            metric_value = metric_value[key]
        
        trends.append({
            'timestamp': timestamp,
            'value': metric_value
        })
    
    return trends

# 사용 예시
trend = analyze_performance_trend(
    'hexagon_vs_square_performance', 
    'aggregation_performance.speed_ratio'
)
```

### 2. 자동 리포트 생성
```python
def generate_comparison_report():
    """여러 테스트 결과를 비교하는 리포트 생성"""
    
    # 메모리 기반 결과
    memory_results = load_latest_results('hexagon_vs_square_performance')
    
    # DB 기반 결과 (있는 경우)
    db_results = load_latest_results('h3_advance_with_pg')
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'memory_test': memory_results,
        'database_test': db_results,
        'summary': {
            'recommended_approach': 'H3' if memory_results else 'Unknown'
        }
    }
    
    return report
```

## 🧹 관리 및 정리

### 1. 오래된 결과 정리
```bash
# 30일 이상 된 결과 파일 삭제
find result/ -name "run_*" -mtime +30 -delete

# 특정 날짜 이전 결과 삭제
find result/ -name "run_202412*" -delete
```

### 2. 결과 백업
```bash
# 중요한 결과를 별도로 백업
cp -r result/hexagon_vs_square_performance/run_20241208_143022* backup/
```

### 3. 공간 사용량 확인
```bash
# 결과 폴더 크기 확인
du -sh result/

# 테스트별 크기 확인
du -sh result/*/
```

## ✨ 장점

1. **체계적 관리**: 모든 결과가 한 곳에 정리됨
2. **추적 가능성**: 타임스탬프로 실행 시점 추적
3. **버전 관리 친화적**: Git에서 결과 파일 제외
4. **확장성**: 새로운 테스트 추가 시 쉽게 확장
5. **자동화 친화적**: 스크립트로 쉽게 분석 가능

## 🔮 향후 계획

1. **웹 대시보드**: 결과 파일을 활용한 실시간 대시보드
2. **자동 알림**: 성능 저하 감지 시 알림 시스템
3. **CI/CD 통합**: 지속적 성능 모니터링
4. **클라우드 저장**: 결과 파일 클라우드 백업

---

이 시스템으로 H3 학습 프로젝트의 모든 결과물을 효율적으로 관리하고 분석할 수 있습니다.