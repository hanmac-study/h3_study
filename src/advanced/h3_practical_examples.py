# -*- coding: utf-8 -*-
"""
H3 실무 활용 예제
실제 비즈니스 시나리오에서 H3를 활용하는 방법을 학습합니다.
"""

import h3
import folium
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns


class H3PracticalExamples:
    """H3 실무 활용 예제"""
    
    def __init__(self):
        """초기화"""
        print("💼 H3 실무 활용 예제를 시작합니다!")
        
    def example_1_delivery_service(self):
        """예제 1: 배달 서비스 최적화"""
        print("\n=== 예제 1: 배달 서비스 최적화 ===")
        
        # 배달 기사와 주문의 위치 데이터
        np.random.seed(42)
        
        # 서울 강남구 지역 좌표
        center_lat, center_lng = 37.5172, 127.0473
        
        # 배달 기사들 위치 (10명)
        drivers = []
        for i in range(10):
            lat = center_lat + np.random.normal(0, 0.01)
            lng = center_lng + np.random.normal(0, 0.01)
            drivers.append({
                'driver_id': f'D{i+1:02d}',
                'lat': lat,
                'lng': lng,
                'status': np.random.choice(['available', 'busy'], p=[0.6, 0.4])
            })
        
        # 주문들 위치 (50개)
        orders = []
        for i in range(50):
            lat = center_lat + np.random.normal(0, 0.02)
            lng = center_lng + np.random.normal(0, 0.02)
            orders.append({
                'order_id': f'O{i+1:03d}',
                'lat': lat,
                'lng': lng,
                'timestamp': datetime.now() - timedelta(minutes=np.random.randint(0, 60))
            })
        
        resolution = 8
        
        # H3 인덱스 추가
        for driver in drivers:
            driver['h3'] = h3.geo_to_h3(driver['lat'], driver['lng'], resolution)
        
        for order in orders:
            order['h3'] = h3.geo_to_h3(order['lat'], order['lng'], resolution)
        
        # 주문 매칭 알고리즘
        df_drivers = pd.DataFrame(drivers)
        df_orders = pd.DataFrame(orders)
        
        available_drivers = df_drivers[df_drivers['status'] == 'available']
        
        matches = []
        for _, order in df_orders.iterrows():
            best_driver = None
            min_distance = float('inf')
            
            for _, driver in available_drivers.iterrows():
                distance = h3.h3_distance(order['h3'], driver['h3'])
                if distance < min_distance:
                    min_distance = distance
                    best_driver = driver
            
            if best_driver is not None:
                matches.append({
                    'order_id': order['order_id'],
                    'driver_id': best_driver['driver_id'],
                    'h3_distance': min_distance
                })
        
        df_matches = pd.DataFrame(matches)
        print(f"총 {len(matches)}개 주문이 매칭되었습니다.")
        print("\n매칭 결과 (상위 10개):")
        print(df_matches.head(10).to_string(index=False))
        
        # 지역별 주문 밀도 분석
        order_density = df_orders.groupby('h3').size().reset_index(name='order_count')
        order_density = order_density.sort_values('order_count', ascending=False)
        
        print(f"\n주문 집중 지역 (상위 5개):")
        for _, row in order_density.head().iterrows():
            lat, lng = h3.h3_to_geo(row['h3'])
            print(f"H3: {row['h3'][:10]}... 주문 수: {row['order_count']} ({lat:.4f}, {lng:.4f})")
        
        return df_drivers, df_orders, df_matches
    
    def example_2_retail_analytics(self):
        """예제 2: 소매업 상권 분석"""
        print("\n=== 예제 2: 소매업 상권 분석 ===")
        
        # 가상의 매장 데이터
        stores = [
            {'store_id': 'S001', 'name': '강남점', 'lat': 37.5172, 'lng': 127.0473, 'type': '대형마트'},
            {'store_id': 'S002', 'name': '역삼점', 'lat': 37.5000, 'lng': 127.0364, 'type': '편의점'},
            {'store_id': 'S003', 'name': '논현점', 'lat': 37.5109, 'lng': 127.0227, 'type': '카페'},
            {'store_id': 'S004', 'name': '신사점', 'lat': 37.5240, 'lng': 127.0202, 'type': '편의점'},
            {'store_id': 'S005', 'name': '압구정점', 'lat': 37.5274, 'lng': 127.0402, 'type': '대형마트'},
        ]
        
        # 고객 방문 데이터 생성
        np.random.seed(42)
        visits = []
        
        for store in stores:
            # 각 매장 주변에 고객 방문 데이터 생성
            n_visits = np.random.randint(100, 500)
            
            for i in range(n_visits):
                # 매장 주변 반경에 고객 위치 생성
                radius = 0.01 if store['type'] == '편의점' else 0.02
                lat = store['lat'] + np.random.normal(0, radius)
                lng = store['lng'] + np.random.normal(0, radius)
                
                visits.append({
                    'visit_id': f"V{len(visits)+1:05d}",
                    'store_id': store['store_id'],
                    'customer_lat': lat,
                    'customer_lng': lng,
                    'visit_date': datetime.now() - timedelta(days=np.random.randint(0, 30)),
                    'amount': np.random.randint(5000, 100000)
                })
        
        df_stores = pd.DataFrame(stores)
        df_visits = pd.DataFrame(visits)
        
        resolution = 9
        
        # H3 인덱스 추가
        df_stores['h3'] = df_stores.apply(lambda row: h3.geo_to_h3(row['lat'], row['lng'], resolution), axis=1)
        df_visits['h3'] = df_visits.apply(lambda row: h3.geo_to_h3(row['customer_lat'], row['customer_lng'], resolution), axis=1)
        
        # 상권 분석
        trade_area_analysis = []
        
        for _, store in df_stores.iterrows():
            store_visits = df_visits[df_visits['store_id'] == store['store_id']]
            
            # 매장 중심에서 반경 내 H3 육각형들
            trade_area_hexes = h3.k_ring(store['h3'], 3)  # 3단계 반경
            
            # 상권 내 방문 데이터
            trade_area_visits = store_visits[store_visits['h3'].isin(trade_area_hexes)]
            
            analysis = {
                'store_id': store['store_id'],
                'store_name': store['name'],
                'store_type': store['type'],
                'trade_area_size': len(trade_area_hexes),
                'total_visits': len(store_visits),
                'trade_area_visits': len(trade_area_visits),
                'coverage_ratio': len(trade_area_visits) / len(store_visits) if len(store_visits) > 0 else 0,
                'avg_amount': store_visits['amount'].mean(),
                'total_revenue': store_visits['amount'].sum()
            }
            trade_area_analysis.append(analysis)
        
        df_analysis = pd.DataFrame(trade_area_analysis)
        print("매장별 상권 분석:")
        print(df_analysis.round(2).to_string(index=False))
        
        # 경쟁 매장 분석
        print(f"\n경쟁 매장 분석:")
        for i, store1 in df_stores.iterrows():
            for j, store2 in df_stores.iterrows():
                if i < j and store1['type'] == store2['type']:
                    distance = h3.h3_distance(store1['h3'], store2['h3'])
                    print(f"{store1['name']} ↔ {store2['name']}: H3 거리 {distance}")
        
        return df_stores, df_visits, df_analysis
    
    def example_3_real_estate_analysis(self):
        """예제 3: 부동산 시장 분석"""
        print("\n=== 예제 3: 부동산 시장 분석 ===")
        
        # 부동산 매물 데이터
        np.random.seed(42)
        
        # 서울 주요 지역별 기준 가격
        regions = {
            '강남구': {'center': (37.5172, 127.0473), 'base_price': 80000},
            '서초구': {'center': (37.4836, 127.0327), 'base_price': 70000},
            '송파구': {'center': (37.5146, 127.1059), 'base_price': 60000},
            '용산구': {'center': (37.5384, 126.9654), 'base_price': 65000},
            '마포구': {'center': (37.5664, 126.9020), 'base_price': 55000},
        }
        
        properties = []
        property_id = 1
        
        for region_name, region_data in regions.items():
            center_lat, center_lng = region_data['center']
            base_price = region_data['base_price']
            
            # 각 지역에 100개씩 매물 생성
            for i in range(100):
                lat = center_lat + np.random.normal(0, 0.01)
                lng = center_lng + np.random.normal(0, 0.01)
                
                # 가격 변동 (±30%)
                price_variation = np.random.uniform(0.7, 1.3)
                price_per_pyeong = base_price * price_variation
                
                size_pyeong = np.random.uniform(20, 50)
                total_price = price_per_pyeong * size_pyeong
                
                properties.append({
                    'property_id': f'P{property_id:03d}',
                    'region': region_name,
                    'lat': lat,
                    'lng': lng,
                    'size_pyeong': round(size_pyeong, 1),
                    'price_per_pyeong': round(price_per_pyeong),
                    'total_price': round(total_price),
                    'property_type': np.random.choice(['아파트', '오피스텔', '빌라'], p=[0.6, 0.3, 0.1])
                })
                property_id += 1
        
        df_properties = pd.DataFrame(properties)
        
        resolution = 8
        df_properties['h3'] = df_properties.apply(
            lambda row: h3.geo_to_h3(row['lat'], row['lng'], resolution), axis=1
        )
        
        # H3 육각형별 부동산 시장 분석
        market_analysis = df_properties.groupby('h3').agg({
            'property_id': 'count',
            'price_per_pyeong': ['mean', 'median', 'std'],
            'total_price': ['mean', 'median'],
            'size_pyeong': 'mean'
        }).round(2)
        
        market_analysis.columns = [
            '매물_수', '평단가_평균', '평단가_중간값', '평단가_표준편차',
            '총가격_평균', '총가격_중간값', '평균_크기'
        ]
        
        # 매물이 10개 이상인 지역만 분석
        significant_areas = market_analysis[market_analysis['매물_수'] >= 10]
        significant_areas = significant_areas.sort_values('평단가_평균', ascending=False)
        
        print("주요 지역별 부동산 시장 분석 (매물 10개 이상):")
        print(significant_areas.head(10).to_string())
        
        # 가격 핫스팟 분석
        print(f"\n가격 핫스팟 분석:")
        top_price_areas = significant_areas.head(3)
        
        for h3_index in top_price_areas.index:
            lat, lng = h3.h3_to_geo(h3_index)
            avg_price = top_price_areas.loc[h3_index, '평단가_평균']
            count = top_price_areas.loc[h3_index, '매물_수']
            
            # 해당 지역의 실제 매물들
            area_properties = df_properties[df_properties['h3'] == h3_index]
            region = area_properties['region'].iloc[0]
            
            print(f"H3: {h3_index[:10]}... ({region})")
            print(f"  위치: ({lat:.4f}, {lng:.4f})")
            print(f"  평균 평단가: {avg_price:,}만원")
            print(f"  매물 수: {count}개")
        
        # 지역간 가격 비교
        region_comparison = df_properties.groupby('region').agg({
            'price_per_pyeong': 'mean',
            'total_price': 'mean',
            'property_id': 'count'
        }).round(2)
        
        region_comparison.columns = ['평균_평단가', '평균_총가격', '매물_수']
        region_comparison = region_comparison.sort_values('평균_평단가', ascending=False)
        
        print(f"\n지역별 가격 비교:")
        print(region_comparison.to_string())
        
        return df_properties, market_analysis
    
    def example_4_transportation_analysis(self):
        """예제 4: 교통 데이터 분석"""
        print("\n=== 예제 4: 교통 데이터 분석 ===")
        
        # 지하철역 데이터 (강남구 일부)
        subway_stations = [
            {'station': '강남역', 'line': '2호선', 'lat': 37.4979, 'lng': 127.0276},
            {'station': '역삼역', 'line': '2호선', 'lat': 37.5000, 'lng': 127.0364},
            {'station': '선릉역', 'line': '2호선', 'lat': 37.5044, 'lng': 127.0491},
            {'station': '삼성역', 'line': '2호선', 'lat': 37.5089, 'lng': 127.0636},
            {'station': '신논현역', 'line': '9호선', 'lat': 37.5047, 'lng': 127.0244},
            {'station': '논현역', 'line': '7호선', 'lat': 37.5109, 'lng': 127.0227},
        ]
        
        df_stations = pd.DataFrame(subway_stations)
        
        # 버스 정류장 데이터 생성 (지하철역 주변)
        np.random.seed(42)
        bus_stops = []
        
        for i, station in enumerate(subway_stations):
            # 각 지하철역 주변에 5-8개의 버스 정류장 생성
            n_stops = np.random.randint(5, 9)
            
            for j in range(n_stops):
                lat = station['lat'] + np.random.normal(0, 0.005)
                lng = station['lng'] + np.random.normal(0, 0.005)
                
                bus_stops.append({
                    'stop_id': f'BS{len(bus_stops)+1:03d}',
                    'stop_name': f'{station["station"]} 버스정류장 {j+1}',
                    'lat': lat,
                    'lng': lng,
                    'nearby_station': station['station']
                })
        
        df_bus_stops = pd.DataFrame(bus_stops)
        
        resolution = 9
        
        # H3 인덱스 추가
        df_stations['h3'] = df_stations.apply(
            lambda row: h3.geo_to_h3(row['lat'], row['lng'], resolution), axis=1
        )
        df_bus_stops['h3'] = df_bus_stops.apply(
            lambda row: h3.geo_to_h3(row['lat'], row['lng'], resolution), axis=1
        )
        
        # 교통 접근성 분석
        accessibility_analysis = []
        
        # 분석 범위 설정 (강남구 대략적 영역)
        lat_min, lat_max = 37.49, 37.52
        lng_min, lng_max = 127.01, 127.07
        
        # 격자 샘플링
        step = 0.002
        sample_points = []
        
        for lat in np.arange(lat_min, lat_max, step):
            for lng in np.arange(lng_min, lng_max, step):
                sample_points.append({'lat': lat, 'lng': lng})
        
        df_samples = pd.DataFrame(sample_points)
        df_samples['h3'] = df_samples.apply(
            lambda row: h3.geo_to_h3(row['lat'], row['lng'], resolution), axis=1
        )
        
        # 각 샘플 지점에서 가장 가까운 지하철역까지의 거리
        for i, sample in df_samples.iterrows():
            min_subway_distance = float('inf')
            nearest_station = None
            
            for _, station in df_stations.iterrows():
                distance = h3.h3_distance(sample['h3'], station['h3'])
                if distance < min_subway_distance:
                    min_subway_distance = distance
                    nearest_station = station['station']
            
            # 가장 가까운 버스 정류장까지의 거리
            min_bus_distance = float('inf')
            nearest_bus_stop = None
            
            for _, bus_stop in df_bus_stops.iterrows():
                distance = h3.h3_distance(sample['h3'], bus_stop['h3'])
                if distance < min_bus_distance:
                    min_bus_distance = distance
                    nearest_bus_stop = bus_stop['stop_name']
            
            accessibility_analysis.append({
                'lat': sample['lat'],
                'lng': sample['lng'],
                'h3': sample['h3'],
                'subway_distance': min_subway_distance,
                'nearest_station': nearest_station,
                'bus_distance': min_bus_distance,
                'nearest_bus_stop': nearest_bus_stop,
                'accessibility_score': 10 - min(min_subway_distance + min_bus_distance, 10)
            })
        
        df_accessibility = pd.DataFrame(accessibility_analysis)
        
        # 접근성 등급 분류
        df_accessibility['accessibility_grade'] = pd.cut(
            df_accessibility['accessibility_score'],
            bins=[0, 3, 6, 8, 10],
            labels=['낮음', '보통', '좋음', '매우좋음']
        )
        
        grade_summary = df_accessibility['accessibility_grade'].value_counts()
        print("교통 접근성 등급별 지역 분포:")
        for grade, count in grade_summary.items():
            percentage = count / len(df_accessibility) * 100
            print(f"{grade}: {count}개 지역 ({percentage:.1f}%)")
        
        # 최고 접근성 지역
        top_accessibility = df_accessibility.nlargest(5, 'accessibility_score')
        print(f"\n최고 접근성 지역 (상위 5개):")
        for _, area in top_accessibility.iterrows():
            print(f"위치: ({area['lat']:.4f}, {area['lng']:.4f})")
            print(f"  접근성 점수: {area['accessibility_score']:.1f}")
            print(f"  가장 가까운 지하철: {area['nearest_station']} (거리: {area['subway_distance']})")
            print(f"  가장 가까운 버스: {area['nearest_bus_stop'][:20]}... (거리: {area['bus_distance']})")
        
        return df_stations, df_bus_stops, df_accessibility


def main():
    """메인 실행 함수"""
    print("💼 H3 실무 활용 예제 시작!")
    
    examples = H3PracticalExamples()
    
    # 예제 1: 배달 서비스
    examples.example_1_delivery_service()
    
    # 예제 2: 소매업 분석
    examples.example_2_retail_analytics()
    
    # 예제 3: 부동산 분석
    examples.example_3_real_estate_analysis()
    
    # 예제 4: 교통 분석
    examples.example_4_transportation_analysis()
    
    print("\n✅ H3 실무 활용 예제가 완료되었습니다!")


if __name__ == "__main__":
    main()