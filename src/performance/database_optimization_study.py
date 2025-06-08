# -*- coding: utf-8 -*-
"""
H3 데이터베이스 최적화 연구
H3 인덱스를 데이터베이스에서 효과적으로 활용하는 방법을 연구합니다.
"""
import os

import h3
import pandas as pd
import numpy as np
import sqlite3
import time
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


class H3DatabaseOptimization:
    """H3 데이터베이스 최적화 연구 클래스"""
    
    def __init__(self, db_path=None):
        """초기화"""
        print("🗄️ H3 데이터베이스 최적화 연구를 시작합니다!")
        
        # 프로젝트 루트 경로 설정
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))  # src/performance/ -> 프로젝트 루트
        
        if db_path is None:
            self.db_path = os.path.join(self.project_root, "result", "performance", "h3_test.db")
        else:
            self.db_path = db_path
            
        # result 디렉토리 생성
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = None
        self.results = {}
        
    def setup_database(self):
        """데이터베이스 초기 설정"""
        print("\n=== 데이터베이스 설정 ===")
        
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # H3 테이블 생성
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations_h3 (
            id INTEGER PRIMARY KEY,
            name TEXT,
            lat REAL,
            lng REAL,
            h3_index TEXT,
            h3_resolution INTEGER,
            category TEXT,
            value REAL,
            created_at TEXT
        )
        ''')
        
        # 전통적인 위경도 테이블 생성
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations_traditional (
            id INTEGER PRIMARY KEY,
            name TEXT,
            lat REAL,
            lng REAL,
            category TEXT,
            value REAL,
            created_at TEXT
        )
        ''')
        
        # 사각형 그리드 테이블 생성
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations_grid (
            id INTEGER PRIMARY KEY,
            name TEXT,
            lat REAL,
            lng REAL,
            grid_x INTEGER,
            grid_y INTEGER,
            grid_resolution INTEGER,
            category TEXT,
            value REAL,
            created_at TEXT
        )
        ''')
        
        self.conn.commit()
        print("데이터베이스 테이블이 생성되었습니다.")
        
        return cursor
    
    def generate_test_data(self, n_records=100000):
        """테스트 데이터 생성"""
        print(f"\n=== 테스트 데이터 생성 ({n_records:,}개) ===")
        
        np.random.seed(42)
        
        # 서울 지역 좌표 생성
        lats = np.random.uniform(37.4, 37.7, n_records)
        lngs = np.random.uniform(126.8, 127.2, n_records)
        
        # 카테고리와 값 생성
        categories = ['restaurant', 'cafe', 'store', 'office', 'hospital']
        test_data = []
        
        for i in range(n_records):
            lat, lng = lats[i], lngs[i]
            
            # H3 인덱스 생성 (해상도 8)
            h3_index = h3.geo_to_h3(lat, lng, 8)
            
            # 사각형 그리드 인덱스 생성
            grid_size = 0.001
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
                'value': np.random.uniform(1, 1000),
                'created_at': datetime.now().isoformat()
            }
            test_data.append(record)
        
        print(f"테스트 데이터 {len(test_data):,}개가 생성되었습니다.")
        return test_data
    
    def insert_test_data(self, test_data):
        """테스트 데이터 삽입"""
        print("\n=== 테스트 데이터 삽입 ===")
        
        cursor = self.conn.cursor()
        
        # 기존 데이터 삭제
        cursor.execute("DELETE FROM locations_h3")
        cursor.execute("DELETE FROM locations_traditional")
        cursor.execute("DELETE FROM locations_grid")
        
        # H3 테이블에 데이터 삽입
        start_time = time.time()
        for record in test_data:
            cursor.execute('''
            INSERT INTO locations_h3 
            (id, name, lat, lng, h3_index, h3_resolution, category, value, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['id'], record['name'], record['lat'], record['lng'],
                record['h3_index'], record['h3_resolution'], record['category'],
                record['value'], record['created_at']
            ))
        h3_insert_time = time.time() - start_time
        
        # 전통적인 테이블에 데이터 삽입
        start_time = time.time()
        for record in test_data:
            cursor.execute('''
            INSERT INTO locations_traditional 
            (id, name, lat, lng, category, value, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['id'], record['name'], record['lat'], record['lng'],
                record['category'], record['value'], record['created_at']
            ))
        traditional_insert_time = time.time() - start_time
        
        # 그리드 테이블에 데이터 삽입
        start_time = time.time()
        for record in test_data:
            cursor.execute('''
            INSERT INTO locations_grid 
            (id, name, lat, lng, grid_x, grid_y, grid_resolution, category, value, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['id'], record['name'], record['lat'], record['lng'],
                record['grid_x'], record['grid_y'], record['grid_resolution'],
                record['category'], record['value'], record['created_at']
            ))
        grid_insert_time = time.time() - start_time
        
        self.conn.commit()
        
        print(f"데이터 삽입 성능:")
        print(f"  H3 테이블: {h3_insert_time:.3f}초")
        print(f"  전통적 테이블: {traditional_insert_time:.3f}초")
        print(f"  그리드 테이블: {grid_insert_time:.3f}초")
        
        return h3_insert_time, traditional_insert_time, grid_insert_time
    
    def create_indexes(self):
        """인덱스 생성"""
        print("\n=== 인덱스 생성 ===")
        
        cursor = self.conn.cursor()
        
        # H3 인덱스들
        start_time = time.time()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_h3_index ON locations_h3(h3_index)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_h3_resolution ON locations_h3(h3_resolution)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_h3_category ON locations_h3(category)")
        h3_index_time = time.time() - start_time
        
        # 전통적인 인덱스들
        start_time = time.time()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trad_lat ON locations_traditional(lat)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trad_lng ON locations_traditional(lng)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trad_lat_lng ON locations_traditional(lat, lng)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trad_category ON locations_traditional(category)")
        traditional_index_time = time.time() - start_time
        
        # 그리드 인덱스들
        start_time = time.time()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_grid_x ON locations_grid(grid_x)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_grid_y ON locations_grid(grid_y)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_grid_xy ON locations_grid(grid_x, grid_y)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_grid_category ON locations_grid(category)")
        grid_index_time = time.time() - start_time
        
        self.conn.commit()
        
        print(f"인덱스 생성 시간:")
        print(f"  H3 인덱스: {h3_index_time:.3f}초")
        print(f"  전통적 인덱스: {traditional_index_time:.3f}초")
        print(f"  그리드 인덱스: {grid_index_time:.3f}초")
        
        return h3_index_time, traditional_index_time, grid_index_time
    
    def test_point_queries(self):
        """포인트 쿼리 성능 테스트"""
        print("\n=== 포인트 쿼리 성능 테스트 ===")
        
        cursor = self.conn.cursor()
        
        # 테스트 포인트들
        test_points = [
            (37.5665, 126.9780),  # 서울 시청
            (37.4979, 127.0276),  # 강남역
            (37.5567, 126.9241),  # 홍대입구역
        ]
        
        h3_times = []
        traditional_times = []
        grid_times = []
        
        for i, (lat, lng) in enumerate(test_points):
            print(f"\n테스트 포인트 {i+1}: ({lat}, {lng})")
            
            # H3 쿼리
            h3_index = h3.geo_to_h3(lat, lng, 8)
            
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM locations_h3 WHERE h3_index = ?", (h3_index,))
            h3_result = cursor.fetchone()[0]
            h3_time = time.time() - start_time
            h3_times.append(h3_time)
            
            # 전통적인 쿼리 (범위 검색)
            radius = 0.01  # 대략 1km
            start_time = time.time()
            cursor.execute('''
            SELECT COUNT(*) FROM locations_traditional 
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
            ''', (lat - radius, lat + radius, lng - radius, lng + radius))
            traditional_result = cursor.fetchone()[0]
            traditional_time = time.time() - start_time
            traditional_times.append(traditional_time)
            
            # 그리드 쿼리
            grid_size = 0.001
            grid_x = int(lng / grid_size)
            grid_y = int(lat / grid_size)
            
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM locations_grid WHERE grid_x = ? AND grid_y = ?", 
                         (grid_x, grid_y))
            grid_result = cursor.fetchone()[0]
            grid_time = time.time() - start_time
            grid_times.append(grid_time)
            
            print(f"  H3: {h3_result}개 결과, {h3_time:.4f}초")
            print(f"  전통적: {traditional_result}개 결과, {traditional_time:.4f}초")
            print(f"  그리드: {grid_result}개 결과, {grid_time:.4f}초")
        
        avg_h3 = sum(h3_times) / len(h3_times)
        avg_traditional = sum(traditional_times) / len(traditional_times)
        avg_grid = sum(grid_times) / len(grid_times)
        
        print(f"\n포인트 쿼리 평균 성능:")
        print(f"  H3: {avg_h3:.4f}초")
        print(f"  전통적: {avg_traditional:.4f}초")
        print(f"  그리드: {avg_grid:.4f}초")
        
        self.results['point_queries'] = {
            'h3_times': h3_times,
            'traditional_times': traditional_times,
            'grid_times': grid_times,
            'avg_h3': avg_h3,
            'avg_traditional': avg_traditional,
            'avg_grid': avg_grid
        }
        
        return h3_times, traditional_times, grid_times
    
    def test_range_queries(self):
        """범위 쿼리 성능 테스트"""
        print("\n=== 범위 쿼리 성능 테스트 ===")
        
        cursor = self.conn.cursor()
        
        # 테스트 범위들
        test_ranges = [
            {'name': '강남구', 'lat_min': 37.495, 'lat_max': 37.520, 'lng_min': 127.020, 'lng_max': 127.070},
            {'name': '마포구', 'lat_min': 37.540, 'lat_max': 37.580, 'lng_min': 126.890, 'lng_max': 126.940},
            {'name': '송파구', 'lat_min': 37.500, 'lat_max': 37.530, 'lng_min': 127.090, 'lng_max': 127.130},
        ]
        
        h3_times = []
        traditional_times = []
        grid_times = []
        
        for range_info in test_ranges:
            print(f"\n테스트 범위: {range_info['name']}")
            
            # H3 범위 쿼리
            start_time = time.time()
            
            # 범위를 커버하는 H3 셀들 찾기
            h3_cells = set()
            lat_step = 0.005
            lng_step = 0.005
            
            lat = range_info['lat_min']
            while lat <= range_info['lat_max']:
                lng = range_info['lng_min']
                while lng <= range_info['lng_max']:
                    h3_index = h3.geo_to_h3(lat, lng, 8)
                    h3_cells.add(h3_index)
                    lng += lng_step
                lat += lat_step
            
            # IN 쿼리로 H3 셀들 검색
            placeholders = ','.join(['?' for _ in h3_cells])
            cursor.execute(f"SELECT COUNT(*) FROM locations_h3 WHERE h3_index IN ({placeholders})", 
                         list(h3_cells))
            h3_result = cursor.fetchone()[0]
            h3_time = time.time() - start_time
            h3_times.append(h3_time)
            
            # 전통적인 범위 쿼리
            start_time = time.time()
            cursor.execute('''
            SELECT COUNT(*) FROM locations_traditional 
            WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
            ''', (range_info['lat_min'], range_info['lat_max'], 
                  range_info['lng_min'], range_info['lng_max']))
            traditional_result = cursor.fetchone()[0]
            traditional_time = time.time() - start_time
            traditional_times.append(traditional_time)
            
            # 그리드 범위 쿼리
            start_time = time.time()
            
            grid_size = 0.001
            grid_x_min = int(range_info['lng_min'] / grid_size)
            grid_x_max = int(range_info['lng_max'] / grid_size)
            grid_y_min = int(range_info['lat_min'] / grid_size)
            grid_y_max = int(range_info['lat_max'] / grid_size)
            
            cursor.execute('''
            SELECT COUNT(*) FROM locations_grid 
            WHERE grid_x BETWEEN ? AND ? AND grid_y BETWEEN ? AND ?
            ''', (grid_x_min, grid_x_max, grid_y_min, grid_y_max))
            grid_result = cursor.fetchone()[0]
            grid_time = time.time() - start_time
            grid_times.append(grid_time)
            
            print(f"  H3: {h3_result}개 결과, {h3_time:.4f}초 ({len(h3_cells)}개 셀)")
            print(f"  전통적: {traditional_result}개 결과, {traditional_time:.4f}초")
            print(f"  그리드: {grid_result}개 결과, {grid_time:.4f}초")
        
        avg_h3 = sum(h3_times) / len(h3_times)
        avg_traditional = sum(traditional_times) / len(traditional_times)
        avg_grid = sum(grid_times) / len(grid_times)
        
        print(f"\n범위 쿼리 평균 성능:")
        print(f"  H3: {avg_h3:.4f}초")
        print(f"  전통적: {avg_traditional:.4f}초")
        print(f"  그리드: {avg_grid:.4f}초")
        
        self.results['range_queries'] = {
            'h3_times': h3_times,
            'traditional_times': traditional_times,
            'grid_times': grid_times,
            'avg_h3': avg_h3,
            'avg_traditional': avg_traditional,
            'avg_grid': avg_grid
        }
        
        return h3_times, traditional_times, grid_times
    
    def test_aggregation_queries(self):
        """집계 쿼리 성능 테스트"""
        print("\n=== 집계 쿼리 성능 테스트 ===")
        
        cursor = self.conn.cursor()
        
        # H3 집계 쿼리
        start_time = time.time()
        cursor.execute('''
        SELECT h3_index, category, COUNT(*) as count, AVG(value) as avg_value, SUM(value) as sum_value
        FROM locations_h3 
        GROUP BY h3_index, category
        HAVING count > 5
        ORDER BY count DESC
        LIMIT 100
        ''')
        h3_results = cursor.fetchall()
        h3_time = time.time() - start_time
        
        # 전통적인 집계 (위경도 기반 그룹핑)
        start_time = time.time()
        cursor.execute('''
        SELECT 
            ROUND(lat, 2) as lat_group, 
            ROUND(lng, 2) as lng_group, 
            category, 
            COUNT(*) as count, 
            AVG(value) as avg_value, 
            SUM(value) as sum_value
        FROM locations_traditional 
        GROUP BY lat_group, lng_group, category
        HAVING count > 5
        ORDER BY count DESC
        LIMIT 100
        ''')
        traditional_results = cursor.fetchall()
        traditional_time = time.time() - start_time
        
        # 그리드 집계 쿼리
        start_time = time.time()
        cursor.execute('''
        SELECT grid_x, grid_y, category, COUNT(*) as count, AVG(value) as avg_value, SUM(value) as sum_value
        FROM locations_grid 
        GROUP BY grid_x, grid_y, category
        HAVING count > 5
        ORDER BY count DESC
        LIMIT 100
        ''')
        grid_results = cursor.fetchall()
        grid_time = time.time() - start_time
        
        print(f"집계 쿼리 성능:")
        print(f"  H3: {len(h3_results)}개 결과, {h3_time:.4f}초")
        print(f"  전통적: {len(traditional_results)}개 결과, {traditional_time:.4f}초")
        print(f"  그리드: {len(grid_results)}개 결과, {grid_time:.4f}초")
        
        # 상위 결과 출력
        print(f"\nH3 집계 상위 5개:")
        for row in h3_results[:5]:
            print(f"  {row[0][:10]}... {row[1]}: {row[2]}개, 평균값 {row[3]:.1f}")
        
        self.results['aggregation_queries'] = {
            'h3_time': h3_time,
            'traditional_time': traditional_time,
            'grid_time': grid_time,
            'h3_result_count': len(h3_results),
            'traditional_result_count': len(traditional_results),
            'grid_result_count': len(grid_results)
        }
        
        return h3_time, traditional_time, grid_time
    
    def test_neighbor_queries(self):
        """인근 셀 쿼리 성능 테스트"""
        print("\n=== 인근 셀 쿼리 성능 테스트 ===")
        
        cursor = self.conn.cursor()
        
        # 테스트 중심점
        center_lat, center_lng = 37.5665, 126.9780
        center_h3 = h3.geo_to_h3(center_lat, center_lng, 8)
        
        # H3 인근 셀 쿼리
        neighbor_distances = [1, 2, 3]
        h3_neighbor_times = []
        
        for k in neighbor_distances:
            start_time = time.time()
            
            # k 거리 내 모든 H3 셀들
            neighbor_cells = h3.k_ring(center_h3, k)
            
            # IN 쿼리로 인근 셀들의 데이터 검색
            placeholders = ','.join(['?' for _ in neighbor_cells])
            cursor.execute(f'''
            SELECT category, COUNT(*) as count, AVG(value) as avg_value
            FROM locations_h3 
            WHERE h3_index IN ({placeholders})
            GROUP BY category
            ''', list(neighbor_cells))
            h3_neighbor_results = cursor.fetchall()
            h3_neighbor_time = time.time() - start_time
            h3_neighbor_times.append(h3_neighbor_time)
            
            print(f"H3 k={k} 인근 쿼리: {len(h3_neighbor_results)}개 카테고리, {h3_neighbor_time:.4f}초")
        
        # 전통적인 인근 영역 쿼리 (원형)
        traditional_neighbor_times = []
        
        for radius in [0.01, 0.02, 0.03]:  # 대략 1km, 2km, 3km
            start_time = time.time()
            
            cursor.execute('''
            SELECT category, COUNT(*) as count, AVG(value) as avg_value
            FROM locations_traditional 
            WHERE (lat - ?) * (lat - ?) + (lng - ?) * (lng - ?) <= ? * ?
            GROUP BY category
            ''', (center_lat, center_lat, center_lng, center_lng, radius, radius))
            traditional_neighbor_results = cursor.fetchall()
            traditional_neighbor_time = time.time() - start_time
            traditional_neighbor_times.append(traditional_neighbor_time)
            
            print(f"전통적 반경={radius:.2f} 쿼리: {len(traditional_neighbor_results)}개 카테고리, {traditional_neighbor_time:.4f}초")
        
        # 그리드 인근 셀 쿼리
        grid_size = 0.001
        center_grid_x = int(center_lng / grid_size)
        center_grid_y = int(center_lat / grid_size)
        
        grid_neighbor_times = []
        
        for grid_radius in [10, 20, 30]:  # 그리드 셀 단위
            start_time = time.time()
            
            cursor.execute('''
            SELECT category, COUNT(*) as count, AVG(value) as avg_value
            FROM locations_grid 
            WHERE grid_x BETWEEN ? AND ? AND grid_y BETWEEN ? AND ?
            GROUP BY category
            ''', (center_grid_x - grid_radius, center_grid_x + grid_radius,
                  center_grid_y - grid_radius, center_grid_y + grid_radius))
            grid_neighbor_results = cursor.fetchall()
            grid_neighbor_time = time.time() - start_time
            grid_neighbor_times.append(grid_neighbor_time)
            
            print(f"그리드 반경={grid_radius} 쿼리: {len(grid_neighbor_results)}개 카테고리, {grid_neighbor_time:.4f}초")
        
        avg_h3 = sum(h3_neighbor_times) / len(h3_neighbor_times)
        avg_traditional = sum(traditional_neighbor_times) / len(traditional_neighbor_times)
        avg_grid = sum(grid_neighbor_times) / len(grid_neighbor_times)
        
        print(f"\n인근 셀 쿼리 평균 성능:")
        print(f"  H3: {avg_h3:.4f}초")
        print(f"  전통적: {avg_traditional:.4f}초")
        print(f"  그리드: {avg_grid:.4f}초")
        
        self.results['neighbor_queries'] = {
            'h3_times': h3_neighbor_times,
            'traditional_times': traditional_neighbor_times,
            'grid_times': grid_neighbor_times,
            'avg_h3': avg_h3,
            'avg_traditional': avg_traditional,
            'avg_grid': avg_grid
        }
        
        return h3_neighbor_times, traditional_neighbor_times, grid_neighbor_times
    
    def generate_database_report(self):
        """데이터베이스 성능 종합 리포트"""
        print("\n" + "="*60)
        print("🗄️ H3 데이터베이스 성능 종합 리포트")
        print("="*60)
        
        # 포인트 쿼리 성능
        if 'point_queries' in self.results:
            data = self.results['point_queries']
            print(f"\n🎯 포인트 쿼리 성능:")
            print(f"   H3: {data['avg_h3']:.4f}초")
            print(f"   전통적: {data['avg_traditional']:.4f}초")
            print(f"   그리드: {data['avg_grid']:.4f}초")
            
            best = min(data['avg_h3'], data['avg_traditional'], data['avg_grid'])
            if data['avg_h3'] == best:
                print(f"   ✅ H3가 가장 빠름")
            elif data['avg_grid'] == best:
                print(f"   ✅ 그리드가 가장 빠름")
            else:
                print(f"   ✅ 전통적 방법이 가장 빠름")
        
        # 범위 쿼리 성능
        if 'range_queries' in self.results:
            data = self.results['range_queries']
            print(f"\n📍 범위 쿼리 성능:")
            print(f"   H3: {data['avg_h3']:.4f}초")
            print(f"   전통적: {data['avg_traditional']:.4f}초")
            print(f"   그리드: {data['avg_grid']:.4f}초")
            
            best = min(data['avg_h3'], data['avg_traditional'], data['avg_grid'])
            if data['avg_h3'] == best:
                print(f"   ✅ H3가 가장 빠름")
            elif data['avg_grid'] == best:
                print(f"   ✅ 그리드가 가장 빠름")
            else:
                print(f"   ✅ 전통적 방법이 가장 빠름")
        
        # 집계 쿼리 성능
        if 'aggregation_queries' in self.results:
            data = self.results['aggregation_queries']
            print(f"\n📊 집계 쿼리 성능:")
            print(f"   H3: {data['h3_time']:.4f}초")
            print(f"   전통적: {data['traditional_time']:.4f}초")
            print(f"   그리드: {data['grid_time']:.4f}초")
            
            best = min(data['h3_time'], data['traditional_time'], data['grid_time'])
            if data['h3_time'] == best:
                print(f"   ✅ H3가 가장 빠름")
            elif data['grid_time'] == best:
                print(f"   ✅ 그리드가 가장 빠름")
            else:
                print(f"   ✅ 전통적 방법이 가장 빠름")
        
        # 인근 셀 쿼리 성능
        if 'neighbor_queries' in self.results:
            data = self.results['neighbor_queries']
            print(f"\n🔄 인근 셀 쿼리 성능:")
            print(f"   H3: {data['avg_h3']:.4f}초")
            print(f"   전통적: {data['avg_traditional']:.4f}초")
            print(f"   그리드: {data['avg_grid']:.4f}초")
            
            best = min(data['avg_h3'], data['avg_traditional'], data['avg_grid'])
            if data['avg_h3'] == best:
                print(f"   ✅ H3가 가장 빠름")
            elif data['avg_grid'] == best:
                print(f"   ✅ 그리드가 가장 빠름")
            else:
                print(f"   ✅ 전통적 방법이 가장 빠름")
        
        print(f"\n🎯 데이터베이스 활용 권장사항:")
        print(f"   • H3 인덱스는 공간 집계와 인근 검색에 매우 효과적입니다.")
        print(f"   • 정확한 포인트 쿼리에는 전통적인 B-tree 인덱스도 경쟁력이 있습니다.")
        print(f"   • 사각형 그리드는 구현이 간단하지만 공간 효율성이 떨어집니다.")
        print(f"   • 복합 인덱스 (H3 + 카테고리)를 활용하면 더 나은 성능을 얻을 수 있습니다.")
        
        # 결과를 JSON 파일로 저장
        report_file = os.path.join(self.project_root, "result", "performance", "database_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 상세 결과가 저장되었습니다: {report_file}")
        
        return self.results
    
    def close_database(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
        print("데이터베이스 연결이 종료되었습니다.")


def main():
    """메인 실행 함수"""
    print("🗄️ H3 데이터베이스 최적화 연구 시작!")
    
    db_optimizer = H3DatabaseOptimization()
    
    try:
        # 데이터베이스 설정
        db_optimizer.setup_database()
        
        # 테스트 데이터 생성 및 삽입
        test_data = db_optimizer.generate_test_data(50000)  # 테스트를 위해 줄임
        db_optimizer.insert_test_data(test_data)
        
        # 인덱스 생성
        db_optimizer.create_indexes()
        
        # 성능 테스트들
        db_optimizer.test_point_queries()
        db_optimizer.test_range_queries()
        db_optimizer.test_aggregation_queries()
        db_optimizer.test_neighbor_queries()
        
        # 종합 리포트 생성
        db_optimizer.generate_database_report()
        
    finally:
        # 데이터베이스 연결 종료
        db_optimizer.close_database()
    
    print("\n✅ H3 데이터베이스 최적화 연구가 완료되었습니다!")


if __name__ == "__main__":
    main()