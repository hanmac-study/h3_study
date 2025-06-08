# -*- coding: utf-8 -*-
"""
H3와 PostgreSQL을 활용한 고급 학습 모듈
H3 육각형 vs 사각형 그리드의 CRUD 및 성능 차이를 PostgreSQL에서 비교 분석합니다.
"""

import h3
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
import time
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import platform
import os

# 한글 폰트 설정
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = ['AppleGothic']
elif platform.system() == 'Windows':
    plt.rcParams['font.family'] = ['Malgun Gothic']
else:  # Linux
    plt.rcParams['font.family'] = ['DejaVu Sans']

plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지


class H3PostgresAdvanced:
    """H3와 PostgreSQL을 활용한 고급 분석 클래스"""
    
    def __init__(self, db_config=None):
        """초기화"""
        print("🐘 H3 + PostgreSQL 고급 학습을 시작합니다!")
        
        # 기본 DB 설정 (로컬 PostgreSQL)
        if db_config is None:
            self.db_config = {
                'host': 'localhost',
                'database': 'h3_study',
                'user': 'postgres',
                'password': 'postgres',
                'port': 5432
            }
        else:
            self.db_config = db_config
            
        self.conn = None
        self.cursor = None
        self.results = {}
        
        # 결과 파일 경로 설정 (현재 파일 위치를 기준으로 프로젝트 루트 계산)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))  # src/database/ -> 프로젝트 루트
        
        # 스크립트 이름으로 폴더 생성
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        self.result_dir = os.path.join(self.project_root, 'result', script_name)
        
        # 결과 디렉토리 생성
        os.makedirs(self.result_dir, exist_ok=True)
        print(f"📁 결과 파일 저장 경로: {self.result_dir}")
        
        # 타임스탬프로 고유 식별자 생성
        self.timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        self.run_id = f"run_{self.timestamp}"
        
    def connect_db(self):
        """데이터베이스 연결"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            print(f"✅ PostgreSQL 연결 성공: {self.db_config['database']}")
            return True
        except Exception as e:
            print(f"❌ PostgreSQL 연결 실패: {e}")
            print("\n💡 다음 명령으로 데이터베이스를 생성하세요:")
            print("   createdb h3_study")
            print("   또는 PostgreSQL에서: CREATE DATABASE h3_study;")
            return False
            
    def check_tables(self):
        """테이블 존재 여부 확인"""
        print("\n=== 데이터베이스 테이블 확인 ===")
        
        # 테이블 존재 확인
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'hanmac-study' 
            AND table_name IN ('locations_h3', 'locations_square')
            ORDER BY table_name;
        """)
        
        tables = self.cursor.fetchall()
        
        if len(tables) < 2:
            print("❌ 필요한 테이블이 없습니다!")
            print("\n다음 명령으로 테이블을 생성하세요:")
            print("   psql -U postgres -d h3_study -f table.sql")
            print("\n또는 pgAdmin에서 table.sql 파일을 실행하세요.")
            return False
        
        print("✅ 필요한 테이블이 모두 존재합니다:")
        for table in tables:
            print(f"   - {table[0]}")
            
        # 데이터 존재 여부 확인
        self.cursor.execute('SELECT COUNT(*) FROM "hanmac-study".locations_h3')
        h3_count = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM "hanmac-study".locations_square')
        square_count = self.cursor.fetchone()[0]
        
        print(f"\n현재 데이터 개수:")
        print(f"   - locations_h3: {h3_count:,}개")
        print(f"   - locations_square: {square_count:,}개")
        
        if h3_count > 0 or square_count > 0:
            response = input("\n기존 데이터가 있습니다. 삭제하고 새로 생성하시겠습니까? (y/n): ")
            if response.lower() == 'y':
                self.cursor.execute('TRUNCATE TABLE "hanmac-study".locations_h3, "hanmac-study".locations_square RESTART IDENTITY;')
                self.conn.commit()
                print("✅ 기존 데이터가 삭제되었습니다.")
        
        return True
        
    def generate_test_data(self, n_records=100000):
        """테스트 데이터 생성"""
        print(f"\n=== 테스트 데이터 생성 ({n_records:,}개) ===")
        
        np.random.seed(42)
        
        # 서울 주요 지역 중심점들 (실제 상권)
        centers = [
            {'name': '강남', 'lat': 37.5172, 'lng': 127.0473, 'weight': 0.3},
            {'name': '홍대', 'lat': 37.5567, 'lng': 126.9241, 'weight': 0.2},
            {'name': '명동', 'lat': 37.5636, 'lng': 126.9826, 'weight': 0.2},
            {'name': '신촌', 'lat': 37.5585, 'lng': 126.9389, 'weight': 0.15},
            {'name': '잠실', 'lat': 37.5133, 'lng': 127.1000, 'weight': 0.15},
        ]
        
        categories = ['restaurant', 'cafe', 'store', 'office', 'hospital']
        test_data = []
        
        for i in range(n_records):
            # 가중치 기반 중심점 선택
            center = np.random.choice(centers, p=[c['weight'] for c in centers])
            
            # 중심점 주변에 정규분포로 데이터 생성
            lat = np.random.normal(center['lat'], 0.01)
            lng = np.random.normal(center['lng'], 0.01)
            
            # H3 인덱스 생성 (해상도 8)
            h3_index = h3.geo_to_h3(lat, lng, 8)
            
            # 사각형 그리드 인덱스 생성
            grid_size = 0.001  # 약 100m
            grid_x = int(lng / grid_size)
            grid_y = int(lat / grid_size)
            
            record = {
                'id': i + 1,
                'name': f'Location_{i+1:06d}',
                'lat': lat,
                'lng': lng,
                'h3_index': h3_index,
                'h3_resolution': 8,
                'grid_x': grid_x,
                'grid_y': grid_y,
                'grid_resolution': 8,
                'category': np.random.choice(categories),
                'value': np.random.uniform(10000, 100000),
                'created_at': datetime.now() - timedelta(days=np.random.randint(0, 365))
            }
            test_data.append(record)
            
        print(f"✅ 테스트 데이터 {len(test_data):,}개가 생성되었습니다.")
        return test_data
    
    def test_insert_performance(self, test_data):
        """INSERT 성능 테스트"""
        print("\n=== INSERT 성능 테스트 ===")
        
        # 샘플 데이터 (처음 10000개만)
        sample_data = test_data[:10000]
        
        # H3 테이블 INSERT 테스트
        print("\nH3 테이블 INSERT 테스트...")
        h3_values = [(d['name'], d['lat'], d['lng'], d['h3_index'], 
                      d['h3_resolution'], d['category'], d['value'], 
                      d['created_at']) for d in sample_data]
        
        start_time = time.time()
        execute_values(
            self.cursor,
            """INSERT INTO "hanmac-study".locations_h3 
               (name, lat, lng, h3_index, h3_resolution, category, value, created_at) 
               VALUES %s""",
            h3_values
        )
        self.conn.commit()
        h3_insert_time = time.time() - start_time
        
        # 사각형 그리드 테이블 INSERT 테스트
        print("사각형 그리드 테이블 INSERT 테스트...")
        square_values = [(d['name'], d['lat'], d['lng'], d['grid_x'], 
                          d['grid_y'], d['grid_resolution'], d['category'], 
                          d['value'], d['created_at']) for d in sample_data]
        
        start_time = time.time()
        execute_values(
            self.cursor,
            """INSERT INTO "hanmac-study".locations_square 
               (name, lat, lng, grid_x, grid_y, grid_resolution, category, value, created_at) 
               VALUES %s""",
            square_values
        )
        self.conn.commit()
        square_insert_time = time.time() - start_time
        
        print(f"\nINSERT 성능 결과 (10,000개):")
        print(f"  H3 테이블: {h3_insert_time:.3f}초")
        print(f"  사각형 테이블: {square_insert_time:.3f}초")
        print(f"  성능 비율: H3가 {square_insert_time/h3_insert_time:.2f}배 {'빠름' if h3_insert_time < square_insert_time else '느림'}")
        
        self.results['insert'] = {
            'h3_time': h3_insert_time,
            'square_time': square_insert_time,
            'record_count': len(sample_data)
        }
        
        return h3_insert_time, square_insert_time
    
    def test_select_performance(self):
        """SELECT 성능 테스트"""
        print("\n=== SELECT 성능 테스트 ===")
        
        test_cases = [
            {
                'name': '포인트 쿼리',
                'h3_query': """
                    SELECT * FROM "hanmac-study".locations_h3 
                    WHERE h3_index = %s
                """,
                'square_query': """
                    SELECT * FROM "hanmac-study".locations_square 
                    WHERE grid_x = %s AND grid_y = %s
                """,
                'h3_params': ['8830e1d8c1fffff'],
                'square_params': [127047, 37517]
            },
            {
                'name': '범위 쿼리',
                'h3_query': """
                    SELECT COUNT(*), AVG(value), category
                    FROM "hanmac-study".locations_h3 
                    WHERE h3_index IN %s
                    GROUP BY category
                """,
                'square_query': """
                    SELECT COUNT(*), AVG(value), category
                    FROM "hanmac-study".locations_square 
                    WHERE grid_x BETWEEN %s AND %s 
                    AND grid_y BETWEEN %s AND %s
                    GROUP BY category
                """,
                'h3_params': None,  # 동적 생성
                'square_params': [127040, 127050, 37510, 37520]
            },
            {
                'name': '집계 쿼리',
                'h3_query': """
                    SELECT h3_index, COUNT(*) as cnt, 
                           SUM(value) as total, AVG(value) as avg
                    FROM "hanmac-study".locations_h3
                    GROUP BY h3_index
                    HAVING COUNT(*) > 5
                    ORDER BY cnt DESC
                    LIMIT 100
                """,
                'square_query': """
                    SELECT grid_x, grid_y, COUNT(*) as cnt,
                           SUM(value) as total, AVG(value) as avg
                    FROM "hanmac-study".locations_square
                    GROUP BY grid_x, grid_y
                    HAVING COUNT(*) > 5
                    ORDER BY cnt DESC
                    LIMIT 100
                """,
                'h3_params': [],
                'square_params': []
            }
        ]
        
        results = []
        
        for test in test_cases:
            print(f"\n{test['name']} 테스트...")
            
            # H3 쿼리 - 범위 쿼리를 위한 특별 처리
            if test['name'] == '범위 쿼리':
                # 중심점에서 k=2 거리의 H3 셀들
                center_h3 = h3.geo_to_h3(37.5172, 127.0473, 8)
                h3_cells = list(h3.k_ring(center_h3, 2))
                test['h3_params'] = [tuple(h3_cells)]
            
            # H3 쿼리 실행
            start_time = time.time()
            self.cursor.execute(test['h3_query'], test['h3_params'])
            h3_results = self.cursor.fetchall()
            h3_time = time.time() - start_time
            
            # 사각형 쿼리 실행
            start_time = time.time()
            self.cursor.execute(test['square_query'], test['square_params'])
            square_results = self.cursor.fetchall()
            square_time = time.time() - start_time
            
            print(f"  H3: {len(h3_results)}개 결과, {h3_time:.4f}초")
            print(f"  사각형: {len(square_results)}개 결과, {square_time:.4f}초")
            print(f"  성능: H3가 {square_time/h3_time:.2f}배 {'빠름' if h3_time < square_time else '느림'}")
            
            results.append({
                'test_name': test['name'],
                'h3_time': h3_time,
                'square_time': square_time,
                'h3_count': len(h3_results),
                'square_count': len(square_results)
            })
        
        self.results['select'] = results
        return results
    
    def test_update_performance(self):
        """UPDATE 성능 테스트"""
        print("\n=== UPDATE 성능 테스트 ===")
        
        # 테스트 1: 단일 셀 업데이트
        print("\n단일 셀 업데이트 테스트...")
        
        # H3 단일 셀
        h3_index = h3.geo_to_h3(37.5172, 127.0473, 8)
        start_time = time.time()
        self.cursor.execute("""
            UPDATE "hanmac-study".locations_h3 
            SET value = value * 1.1 
            WHERE h3_index = %s
        """, (h3_index,))
        self.conn.commit()
        h3_single_time = time.time() - start_time
        
        # 사각형 단일 셀
        grid_x, grid_y = 127047, 37517
        start_time = time.time()
        self.cursor.execute("""
            UPDATE "hanmac-study".locations_square 
            SET value = value * 1.1 
            WHERE grid_x = %s AND grid_y = %s
        """, (grid_x, grid_y))
        self.conn.commit()
        square_single_time = time.time() - start_time
        
        print(f"  H3: {h3_single_time:.4f}초")
        print(f"  사각형: {square_single_time:.4f}초")
        
        # 테스트 2: 범위 업데이트
        print("\n범위 업데이트 테스트...")
        
        # H3 범위 (k=1 인근 셀들)
        h3_cells = list(h3.k_ring(h3_index, 1))
        start_time = time.time()
        self.cursor.execute("""
            UPDATE "hanmac-study".locations_h3 
            SET value = value * 1.05 
            WHERE h3_index IN %s
        """, (tuple(h3_cells),))
        self.conn.commit()
        h3_range_time = time.time() - start_time
        
        # 사각형 범위
        start_time = time.time()
        self.cursor.execute("""
            UPDATE "hanmac-study".locations_square 
            SET value = value * 1.05 
            WHERE grid_x BETWEEN %s AND %s 
            AND grid_y BETWEEN %s AND %s
        """, (grid_x-2, grid_x+2, grid_y-2, grid_y+2))
        self.conn.commit()
        square_range_time = time.time() - start_time
        
        print(f"  H3: {h3_range_time:.4f}초")
        print(f"  사각형: {square_range_time:.4f}초")
        
        self.results['update'] = {
            'single': {
                'h3_time': h3_single_time,
                'square_time': square_single_time
            },
            'range': {
                'h3_time': h3_range_time,
                'square_time': square_range_time
            }
        }
        
        return h3_single_time, square_single_time, h3_range_time, square_range_time
    
    def test_delete_performance(self):
        """DELETE 성능 테스트"""
        print("\n=== DELETE 성능 테스트 ===")
        
        # 먼저 삭제할 데이터를 복사
        print("삭제 테스트를 위한 데이터 복사 중...")
        self.cursor.execute("""
            INSERT INTO "hanmac-study".locations_h3 (name, lat, lng, h3_index, h3_resolution, category, value)
            SELECT name || '_copy', lat, lng, h3_index, h3_resolution, category, value
            FROM "hanmac-study".locations_h3
            WHERE category = 'restaurant'
        """)
        
        self.cursor.execute("""
            INSERT INTO "hanmac-study".locations_square (name, lat, lng, grid_x, grid_y, grid_resolution, category, value)
            SELECT name || '_copy', lat, lng, grid_x, grid_y, grid_resolution, category, value
            FROM "hanmac-study".locations_square
            WHERE category = 'restaurant'
        """)
        self.conn.commit()
        
        # H3 삭제 테스트
        print("\nH3 삭제 테스트...")
        start_time = time.time()
        self.cursor.execute("""
            DELETE FROM "hanmac-study".locations_h3 
            WHERE name LIKE '%_copy'
        """)
        self.conn.commit()
        h3_delete_time = time.time() - start_time
        deleted_h3 = self.cursor.rowcount
        
        # 사각형 삭제 테스트
        print("사각형 삭제 테스트...")
        start_time = time.time()
        self.cursor.execute("""
            DELETE FROM "hanmac-study".locations_square 
            WHERE name LIKE '%_copy'
        """)
        self.conn.commit()
        square_delete_time = time.time() - start_time
        deleted_square = self.cursor.rowcount
        
        print(f"\n삭제 성능 결과:")
        print(f"  H3: {deleted_h3}개 삭제, {h3_delete_time:.4f}초")
        print(f"  사각형: {deleted_square}개 삭제, {square_delete_time:.4f}초")
        
        self.results['delete'] = {
            'h3_time': h3_delete_time,
            'square_time': square_delete_time,
            'h3_count': deleted_h3,
            'square_count': deleted_square
        }
        
        return h3_delete_time, square_delete_time
    
    def test_spatial_queries(self):
        """공간 쿼리 성능 테스트"""
        print("\n=== 공간 쿼리 성능 테스트 ===")
        
        # 테스트 1: 특정 지점 주변 검색
        center_lat, center_lng = 37.5172, 127.0473
        
        print("\n주변 검색 쿼리 테스트...")
        
        # H3 방식: k-ring 사용
        center_h3 = h3.geo_to_h3(center_lat, center_lng, 8)
        nearby_h3 = list(h3.k_ring(center_h3, 2))
        
        start_time = time.time()
        self.cursor.execute("""
            SELECT category, COUNT(*) as cnt, AVG(value) as avg_value
            FROM "hanmac-study".locations_h3
            WHERE h3_index IN %s
            GROUP BY category
            ORDER BY cnt DESC
        """, (tuple(nearby_h3),))
        h3_nearby_results = self.cursor.fetchall()
        h3_nearby_time = time.time() - start_time
        
        # 사각형 방식: 범위 검색
        grid_size = 0.001
        center_grid_x = int(center_lng / grid_size)
        center_grid_y = int(center_lat / grid_size)
        radius = 3  # 그리드 단위
        
        start_time = time.time()
        self.cursor.execute("""
            SELECT category, COUNT(*) as cnt, AVG(value) as avg_value
            FROM "hanmac-study".locations_square
            WHERE grid_x BETWEEN %s AND %s
            AND grid_y BETWEEN %s AND %s
            GROUP BY category
            ORDER BY cnt DESC
        """, (center_grid_x - radius, center_grid_x + radius,
              center_grid_y - radius, center_grid_y + radius))
        square_nearby_results = self.cursor.fetchall()
        square_nearby_time = time.time() - start_time
        
        print(f"  H3 k-ring: {len(h3_nearby_results)}개 카테고리, {h3_nearby_time:.4f}초")
        print(f"  사각형 범위: {len(square_nearby_results)}개 카테고리, {square_nearby_time:.4f}초")
        
        # 테스트 2: 경로상의 셀 찾기
        print("\n경로 검색 쿼리 테스트...")
        
        # 강남역에서 잠실역까지
        start_point = (37.4979, 127.0276)
        end_point = (37.5133, 127.1000)
        
        # 경로상의 H3 셀들
        path_h3_cells = set()
        steps = 20
        for i in range(steps + 1):
            lat = start_point[0] + (end_point[0] - start_point[0]) * i / steps
            lng = start_point[1] + (end_point[1] - start_point[1]) * i / steps
            path_h3_cells.add(h3.geo_to_h3(lat, lng, 8))
            # 경로 주변도 포함
            for neighbor in h3.k_ring(h3.geo_to_h3(lat, lng, 8), 1):
                path_h3_cells.add(neighbor)
        
        start_time = time.time()
        self.cursor.execute("""
            SELECT COUNT(*), SUM(value)
            FROM "hanmac-study".locations_h3
            WHERE h3_index IN %s
        """, (tuple(path_h3_cells),))
        h3_path_result = self.cursor.fetchone()
        h3_path_time = time.time() - start_time
        
        print(f"  H3 경로: {len(path_h3_cells)}개 셀, {h3_path_time:.4f}초")
        print(f"    결과: {h3_path_result[0]}개 위치, 총 가치 {h3_path_result[1]:,.0f}")
        
        self.results['spatial'] = {
            'nearby': {
                'h3_time': h3_nearby_time,
                'square_time': square_nearby_time
            },
            'path': {
                'h3_time': h3_path_time,
                'h3_cells': len(path_h3_cells)
            }
        }
        
        return h3_nearby_time, square_nearby_time
    
    def visualize_results(self):
        """결과 시각화"""
        print("\n=== 성능 비교 시각화 ===")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. CRUD 성능 비교
        ax1 = axes[0, 0]
        operations = ['INSERT', 'SELECT', 'UPDATE', 'DELETE']
        h3_times = [
            self.results.get('insert', {}).get('h3_time', 0),
            np.mean([r['h3_time'] for r in self.results.get('select', [])]) if self.results.get('select') else 0,
            np.mean([self.results.get('update', {}).get('single', {}).get('h3_time', 0),
                     self.results.get('update', {}).get('range', {}).get('h3_time', 0)]),
            self.results.get('delete', {}).get('h3_time', 0)
        ]
        square_times = [
            self.results.get('insert', {}).get('square_time', 0),
            np.mean([r['square_time'] for r in self.results.get('select', [])]) if self.results.get('select') else 0,
            np.mean([self.results.get('update', {}).get('single', {}).get('square_time', 0),
                     self.results.get('update', {}).get('range', {}).get('square_time', 0)]),
            self.results.get('delete', {}).get('square_time', 0)
        ]
        
        x = np.arange(len(operations))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, h3_times, width, label='H3', color='#3498db')
        bars2 = ax1.bar(x + width/2, square_times, width, label='Square Grid', color='#e74c3c')
        
        ax1.set_xlabel('작업 유형')
        ax1.set_ylabel('실행 시간 (초)')
        ax1.set_title('CRUD 작업 성능 비교')
        ax1.set_xticks(x)
        ax1.set_xticklabels(operations)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 막대 위에 값 표시
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}', ha='center', va='bottom', fontsize=8)
        
        # 2. SELECT 쿼리 상세 비교
        ax2 = axes[0, 1]
        if self.results.get('select'):
            select_types = [r['test_name'] for r in self.results['select']]
            h3_select_times = [r['h3_time'] for r in self.results['select']]
            square_select_times = [r['square_time'] for r in self.results['select']]
            
            x = np.arange(len(select_types))
            bars1 = ax2.bar(x - width/2, h3_select_times, width, label='H3', color='#3498db')
            bars2 = ax2.bar(x + width/2, square_select_times, width, label='Square Grid', color='#e74c3c')
            
            ax2.set_xlabel('쿼리 유형')
            ax2.set_ylabel('실행 시간 (초)')
            ax2.set_title('SELECT 쿼리 유형별 성능')
            ax2.set_xticks(x)
            ax2.set_xticklabels(select_types, rotation=15)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # 3. 성능 비율 분석
        ax3 = axes[1, 0]
        if any(h3_times) and any(square_times):
            ratios = [s/h if h > 0 else 0 for h, s in zip(h3_times, square_times)]
            colors = ['#2ecc71' if r > 1 else '#e74c3c' for r in ratios]
            
            bars = ax3.bar(operations, ratios, color=colors, alpha=0.7)
            ax3.axhline(y=1, color='black', linestyle='--', alpha=0.5)
            ax3.set_xlabel('작업 유형')
            ax3.set_ylabel('성능 비율 (Square/H3)')
            ax3.set_title('H3 대비 Square Grid 성능 비율')
            ax3.grid(True, alpha=0.3)
            
            # 막대 위에 비율 표시
            for bar, ratio in zip(bars, ratios):
                height = bar.get_height()
                label = f'{ratio:.2f}x\n{"H3 우수" if ratio > 1 else "Square 우수"}'
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        label, ha='center', va='bottom', fontsize=8)
        
        # 4. 데이터 분포
        ax4 = axes[1, 1]
        self.cursor.execute("""
            SELECT h3_index, COUNT(*) as cnt
            FROM "hanmac-study".locations_h3
            GROUP BY h3_index
            ORDER BY cnt DESC
            LIMIT 20
        """)
        h3_dist = self.cursor.fetchall()
        
        if h3_dist:
            counts = [row[1] for row in h3_dist]
            ax4.bar(range(len(counts)), counts, color='#3498db', alpha=0.7)
            ax4.set_xlabel('H3 셀 (상위 20개)')
            ax4.set_ylabel('데이터 개수')
            ax4.set_title('H3 셀별 데이터 분포')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        chart_file = os.path.join(self.result_dir, f"h3_vs_square_postgres_performance_{self.timestamp}.png")
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"✅ 성능 비교 차트가 저장되었습니다: {chart_file}")
    
    def generate_report(self):
        """종합 리포트 생성"""
        print("\n" + "="*60)
        print("📊 H3 vs Square Grid PostgreSQL 성능 비교 리포트")
        print("="*60)
        
        # INSERT 성능
        if 'insert' in self.results:
            print(f"\n🔹 INSERT 성능:")
            print(f"   H3: {self.results['insert']['h3_time']:.3f}초")
            print(f"   Square: {self.results['insert']['square_time']:.3f}초")
            ratio = self.results['insert']['square_time'] / self.results['insert']['h3_time']
            print(f"   결과: H3가 {ratio:.2f}배 {'빠름' if ratio > 1 else '느림'}")
        
        # SELECT 성능
        if 'select' in self.results:
            print(f"\n🔹 SELECT 성능:")
            for result in self.results['select']:
                print(f"   {result['test_name']}:")
                print(f"     H3: {result['h3_time']:.4f}초 ({result['h3_count']}개)")
                print(f"     Square: {result['square_time']:.4f}초 ({result['square_count']}개)")
                ratio = result['square_time'] / result['h3_time'] if result['h3_time'] > 0 else 0
                print(f"     결과: H3가 {ratio:.2f}배 {'빠름' if ratio > 1 else '느림'}")
        
        # UPDATE 성능
        if 'update' in self.results:
            print(f"\n🔹 UPDATE 성능:")
            print(f"   단일 업데이트:")
            print(f"     H3: {self.results['update']['single']['h3_time']:.4f}초")
            print(f"     Square: {self.results['update']['single']['square_time']:.4f}초")
            print(f"   범위 업데이트:")
            print(f"     H3: {self.results['update']['range']['h3_time']:.4f}초")
            print(f"     Square: {self.results['update']['range']['square_time']:.4f}초")
        
        # DELETE 성능
        if 'delete' in self.results:
            print(f"\n🔹 DELETE 성능:")
            print(f"   H3: {self.results['delete']['h3_count']}개, {self.results['delete']['h3_time']:.4f}초")
            print(f"   Square: {self.results['delete']['square_count']}개, {self.results['delete']['square_time']:.4f}초")
        
        # 공간 쿼리 성능
        if 'spatial' in self.results:
            print(f"\n🔹 공간 쿼리 성능:")
            print(f"   주변 검색:")
            print(f"     H3: {self.results['spatial']['nearby']['h3_time']:.4f}초")
            print(f"     Square: {self.results['spatial']['nearby']['square_time']:.4f}초")
        
        print(f"\n💡 주요 인사이트:")
        print(f"   1. H3는 인근 검색과 공간 집계에서 우수한 성능을 보입니다.")
        print(f"   2. 사각형 그리드는 단순 범위 검색에서 경쟁력이 있습니다.")
        print(f"   3. H3의 계층적 구조는 다양한 해상도 분석에 유리합니다.")
        print(f"   4. 인덱스 설계가 두 방식 모두에서 중요합니다.")
        
        # JSON 결과 저장
        results_file = os.path.join(self.result_dir, f"{self.run_id}_h3_postgres_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n📄 상세 결과가 저장되었습니다: {results_file}")
    
    def close_connection(self):
        """데이터베이스 연결 종료"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("\n✅ PostgreSQL 연결이 종료되었습니다.")


def main():
    """메인 실행 함수"""
    print("🚀 H3 + PostgreSQL 고급 학습 시작!")
    
    # DB 연결 정보 (필요시 수정)
    db_config = {
        'host': 'localhost',
        'database': 'h3_study',
        'user': 'postgres',
        'password': 'postgres',  # 실제 비밀번호로 변경
        'port': 5432
    }
    
    analyzer = H3PostgresAdvanced(db_config)
    
    # 데이터베이스 연결
    if not analyzer.connect_db():
        print("\n데이터베이스 연결에 실패했습니다. 설정을 확인하세요.")
        return
    
    try:
        # 테이블 확인
        if not analyzer.check_tables():
            return
        
        # 테스트 데이터 생성
        test_data = analyzer.generate_test_data(50000)  # 5만개로 테스트
        
        # 성능 테스트 실행
        analyzer.test_insert_performance(test_data)
        analyzer.test_select_performance()
        analyzer.test_update_performance()
        analyzer.test_delete_performance()
        analyzer.test_spatial_queries()
        
        # 결과 시각화
        analyzer.visualize_results()
        
        # 종합 리포트
        analyzer.generate_report()
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 연결 종료
        analyzer.close_connection()
    
    print("\n✅ H3 + PostgreSQL 고급 학습이 완료되었습니다!")


if __name__ == "__main__":
    main()