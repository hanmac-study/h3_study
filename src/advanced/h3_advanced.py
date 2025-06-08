# -*- coding: utf-8 -*-
"""
H3 고급 학습 모듈
H3의 고급 기능들과 실무 활용 사례를 학습합니다.
"""
import os

import h3
import folium
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import json
import platform

# 한글 폰트 설정
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = ['AppleGothic']
elif platform.system() == 'Windows':
    plt.rcParams['font.family'] = ['Malgun Gothic']
else:  # Linux
    plt.rcParams['font.family'] = ['DejaVu Sans']

plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지


class H3AdvancedLearning:
    """H3 고급 기능 학습을 위한 클래스"""

    def __init__(self):
        """초기화"""
        print("🔥 H3 고급 학습을 시작합니다!")

        # 프로젝트 루트 경로 설정
        import os
        from datetime import datetime
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))  # src/advanced/ -> 프로젝트 루트
        
        # 스크립트 이름으로 폴더 생성
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        self.result_dir = os.path.join(self.project_root, 'result', script_name)
        
        # result 디렉토리가 없으면 생성
        os.makedirs(self.result_dir, exist_ok=True)
        
        # 타임스탬프 생성
        self.timestamp = datetime.now().strftime("%y%m%d_%H%M%S")

    def step_6_spatial_analysis(self):
        """6단계: 공간 분석"""
        print("\n=== 6단계: 공간 분석 ===")

        # 서울의 주요 지점들
        locations = {
            '강남역': (37.4979, 127.0276),
            '홍대입구': (37.5567, 126.9241),
            '명동': (37.5636, 126.9826),
            '이태원': (37.5344, 126.9943),
            '잠실': (37.5133, 127.1000)
        }

        resolution = 7
        location_hexes = {}

        # 각 지점의 H3 인덱스 생성
        for name, (lat, lng) in locations.items():
            hex_id = h3.geo_to_h3(lat, lng, resolution)
            location_hexes[name] = hex_id
            print(f"{name}: {hex_id}")

        # 지점들 간 거리 계산
        print("\n지점간 H3 거리:")
        points = list(location_hexes.items())
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                name1, hex1 = points[i]
                name2, hex2 = points[j]
                distance = h3.h3_distance(hex1, hex2)
                print(f"{name1} ↔ {name2}: {distance} H3 거리")

        # Folium 지도에 주요 지점들 시각화
        center_lat = sum(lat for lat, lng in locations.values()) / len(locations)
        center_lng = sum(lng for lat, lng in locations.values()) / len(locations)

        m = folium.Map(location=[center_lat, center_lng], zoom_start=11)

        # 각 지점을 지도에 마커로 추가
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        for i, (name, (lat, lng)) in enumerate(locations.items()):
            folium.Marker(
                location=[lat, lng],
                popup=f"{name}\nH3: {location_hexes[name]}",
                tooltip=name,
                icon=folium.Icon(color=colors[i], icon='info-sign')
            ).add_to(m)

            # H3 육각형 경계도 표시
            hex_boundary = h3.h3_to_geo_boundary(location_hexes[name])
            folium_coords = [[lat, lng] for lat, lng in hex_boundary]
            folium.Polygon(
                locations=folium_coords,
                color=colors[i],
                fill=True,
                fillOpacity=0.2,
                popup=f"{name} H3 영역"
            ).add_to(m)

        map_file = os.path.join(self.result_dir, f"advanced_spatial_analysis_{self.timestamp}.html")
        m.save(map_file)
        print(f"\n지점 분석 지도가 저장되었습니다: {map_file}")

        return location_hexes

    def step_7_aggregation_analysis(self):
        """7단계: 데이터 집계 분석"""
        print("\n=== 7단계: 데이터 집계 분석 ===")

        # 가상의 배달 주문 데이터 생성
        np.random.seed(42)
        n_orders = 1000

        # 서울 중심부 좌표 범위
        lat_min, lat_max = 37.45, 37.65
        lng_min, lng_max = 126.85, 127.15

        orders = []
        for i in range(n_orders):
            lat = np.random.uniform(lat_min, lat_max)
            lng = np.random.uniform(lng_min, lng_max)
            amount = np.random.randint(10000, 50000)  # 주문 금액
            orders.append({
                'order_id': i,
                'lat': lat,
                'lng': lng,
                'amount': amount
            })

        df = pd.DataFrame(orders)

        # H3 인덱스 추가
        resolution = 8
        df['h3_index'] = df.apply(lambda row: h3.geo_to_h3(row['lat'], row['lng'], resolution), axis=1)

        # H3 육각형별 집계
        aggregated = df.groupby('h3_index').agg({
            'order_id': 'count',
            'amount': ['sum', 'mean']
        }).round(2)

        aggregated.columns = ['주문_수', '총_금액', '평균_금액']
        aggregated = aggregated.sort_values('주문_수', ascending=False)

        print("상위 10개 H3 육각형별 주문 현황:")
        print(aggregated.head(10).to_string())

        # 핫스팟 분석 (주문이 많은 지역의 인근 육각형들)
        top_hex = aggregated.index[0]
        hotspot_area = h3.k_ring(top_hex, 2)
        hotspot_orders = df[df['h3_index'].isin(hotspot_area)]

        print(f"\n📍 최고 핫스팟 지역 ({top_hex}) 주변 분석:")
        print(f"핫스팟 지역 내 총 주문 수: {len(hotspot_orders)}")
        print(f"핫스팟 지역 내 총 매출: {hotspot_orders['amount'].sum():,}원")

        # Seaborn을 사용한 주문 분포 시각화
        plt.figure(figsize=(12, 8))

        # 서브플롯 1: 주문 수 히스토그램
        plt.subplot(2, 2, 1)
        sns.histplot(aggregated['주문_수'], bins=20, kde=True)
        plt.title('H3 육각형별 주문 수 분포')
        plt.xlabel('주문 수')
        plt.ylabel('빈도')

        # 서브플롯 2: 평균 금액 히스토그램
        plt.subplot(2, 2, 2)
        sns.histplot(aggregated['평균_금액'], bins=20, kde=True, color='orange')
        plt.title('H3 육각형별 평균 주문 금액 분포')
        plt.xlabel('평균 금액 (원)')
        plt.ylabel('빈도')

        # 서브플롯 3: 주문 수 vs 평균 금액 산점도
        plt.subplot(2, 2, 3)
        sns.scatterplot(data=aggregated, x='주문_수', y='평균_금액', alpha=0.6)
        plt.title('주문 수 vs 평균 금액')
        plt.xlabel('주문 수')
        plt.ylabel('평균 금액 (원)')

        # 서브플롯 4: 상위 10개 지역 막대 그래프
        plt.subplot(2, 2, 4)
        top_10 = aggregated.head(10)
        sns.barplot(data=top_10.reset_index(), x='주문_수', y=range(len(top_10)), orient='h')
        plt.title('상위 10개 H3 지역 주문 수')
        plt.xlabel('주문 수')
        plt.ylabel('순위')

        plt.tight_layout()
        plt.savefig(os.path.join(self.result_dir, f'aggregation_analysis_{self.timestamp}.png'), dpi=300, bbox_inches='tight')
        plt.show()
        print(f"집계 분석 차트가 저장되었습니다: {os.path.join(self.result_dir, f'aggregation_analysis_{self.timestamp}.png')}")

        # Folium을 사용한 핫스팟 지도 시각화
        center_lat = df['lat'].mean()
        center_lng = df['lng'].mean()

        m = folium.Map(location=[center_lat, center_lng], zoom_start=10)

        # 핫스팟 영역의 모든 육각형을 지도에 표시
        for hex_id in hotspot_area:
            boundary = h3.h3_to_geo_boundary(hex_id)
            folium_coords = [[lat, lng] for lat, lng in boundary]

            # 해당 육각형의 주문 수에 따라 색상 조절
            if hex_id in aggregated.index:
                order_count = aggregated.loc[hex_id, '주문_수']
                # 주문 수에 비례한 색상 강도
                opacity = min(order_count / aggregated['주문_수'].max(), 1.0)
                color = 'red' if hex_id == top_hex else 'orange'
                popup_text = f"H3: {hex_id[:10]}...\n주문 수: {order_count}"
            else:
                order_count = 0
                opacity = 0.1
                color = 'blue'
                popup_text = f"H3: {hex_id[:10]}...\n주문 수: 0"

            folium.Polygon(
                locations=folium_coords,
                color=color,
                fill=True,
                fillOpacity=opacity,
                popup=popup_text
            ).add_to(m)

        hotspot_map_file = os.path.join(self.result_dir, f"hotspot_analysis_{self.timestamp}.html")
        m.save(hotspot_map_file)
        print(f"핫스팟 분석 지도가 저장되었습니다: {hotspot_map_file}")

        return df, aggregated, hotspot_area

    def step_8_grid_analysis(self):
        """8단계: 격자 분석 및 경계 처리"""
        print("\n=== 8단계: 격자 분석 및 경계 처리 ===")

        # 특정 영역의 모든 H3 육각형 구하기
        # 서울 강남구 대략적인 경계
        boundary_coords = [
            (37.4850, 127.0350),  # 남서쪽
            (37.4850, 127.0650),  # 남동쪽
            (37.5150, 127.0650),  # 북동쪽
            (37.5150, 127.0350),  # 북서쪽
        ]

        resolution = 9

        # 경계 내부의 모든 H3 육각형 찾기
        all_hexes = set()

        # 경계 상자 내의 모든 점을 샘플링하여 H3 인덱스 생성
        lat_min = min(coord[0] for coord in boundary_coords)
        lat_max = max(coord[0] for coord in boundary_coords)
        lng_min = min(coord[1] for coord in boundary_coords)
        lng_max = max(coord[1] for coord in boundary_coords)

        # 샘플링 간격
        step = 0.001
        lat_range = np.arange(lat_min, lat_max, step)
        lng_range = np.arange(lng_min, lng_max, step)

        for lat in lat_range:
            for lng in lng_range:
                hex_id = h3.geo_to_h3(lat, lng, resolution)
                # 육각형 중심점이 경계 내부에 있는지 확인
                center_lat, center_lng = h3.h3_to_geo(hex_id)
                if (lat_min <= center_lat <= lat_max and
                        lng_min <= center_lng <= lng_max):
                    all_hexes.add(hex_id)

        print(f"분석 영역 내 H3 육각형 개수: {len(all_hexes)}")

        # 육각형들의 연결성 분석
        connected_groups = []
        unvisited = set(all_hexes)

        while unvisited:
            # BFS로 연결된 육각형 그룹 찾기
            start_hex = next(iter(unvisited))
            group = set()
            queue = [start_hex]

            while queue:
                current_hex = queue.pop(0)
                if current_hex in unvisited:
                    group.add(current_hex)
                    unvisited.remove(current_hex)

                    # 인접한 육각형들 중 방문하지 않은 것들을 큐에 추가
                    neighbors = h3.k_ring(current_hex, 1)
                    for neighbor in neighbors:
                        if neighbor in unvisited:
                            queue.append(neighbor)

            if group:
                connected_groups.append(group)

        print(f"연결된 그룹 개수: {len(connected_groups)}")
        for i, group in enumerate(connected_groups):
            print(f"그룹 {i + 1}: {len(group)}개 육각형")

        # Folium을 사용한 격자 분석 시각화
        center_lat = (lat_min + lat_max) / 2
        center_lng = (lng_min + lng_max) / 2

        m = folium.Map(location=[center_lat, center_lng], zoom_start=12)

        # 각 연결 그룹을 다른 색상으로 표시
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']

        for group_idx, group in enumerate(connected_groups):
            color = colors[group_idx % len(colors)]

            for hex_id in group:
                boundary = h3.h3_to_geo_boundary(hex_id)
                folium_coords = [[lat, lng] for lat, lng in boundary]

                folium.Polygon(
                    locations=folium_coords,
                    color=color,
                    fill=True,
                    fillOpacity=0.4,
                    popup=f"그룹 {group_idx + 1}\nH3: {hex_id[:10]}..."
                ).add_to(m)

        # 분석 영역 경계 표시
        boundary_folium = [[lat, lng] for lat, lng in boundary_coords]
        boundary_folium.append(boundary_folium[0])  # 닫힌 폴리곤

        folium.Polygon(
            locations=boundary_folium,
            color='black',
            weight=3,
            fill=False,
            popup="분석 영역 경계"
        ).add_to(m)

        grid_map_file = os.path.join(self.result_dir, f"grid_analysis_{self.timestamp}.html")
        m.save(grid_map_file)
        print(f"격자 분석 지도가 저장되었습니다: {grid_map_file}")

        return all_hexes, connected_groups

    def step_9_hierarchical_analysis(self):
        """9단계: 계층적 분석"""
        print("\n=== 9단계: 계층적 분석 ===")

        # 서로 다른 해상도에서의 부모-자식 관계
        lat, lng = 37.5665, 126.9780

        hierarchy_data = []
        for resolution in range(3, 10):
            hex_id = h3.geo_to_h3(lat, lng, resolution)

            # 부모 육각형 (해상도 - 1)
            if resolution > 0:
                parent = h3.h3_to_parent(hex_id, resolution - 1)
            else:
                parent = None

            # 자식 육각형들 (해상도 + 1)
            if resolution < 15:
                children = h3.h3_to_children(hex_id, resolution + 1)
                child_count = len(children)
            else:
                children = []
                child_count = 0

            hierarchy_data.append({
                '해상도': resolution,
                'H3_인덱스': hex_id,
                '부모': parent,
                '자식_개수': child_count
            })

        df_hierarchy = pd.DataFrame(hierarchy_data)
        print("계층적 구조:")
        print(df_hierarchy.to_string(index=False))

        # 특정 해상도의 육각형을 더 높은 해상도로 세분화
        base_resolution = 6
        target_resolution = 8

        base_hex = h3.geo_to_h3(lat, lng, base_resolution)
        subdivided = h3.h3_to_children(base_hex, target_resolution)

        print(f"\n해상도 {base_resolution} 육각형 {base_hex}를")
        print(f"해상도 {target_resolution}로 세분화: {len(subdivided)}개 육각형")

        # Matplotlib을 사용한 계층적 구조 시각화
        plt.figure(figsize=(12, 6))

        # 해상도별 육각형 크기 그래프
        plt.subplot(1, 2, 1)
        resolutions = [item['해상도'] for item in hierarchy_data]
        areas = [h3.hex_area(res, unit='km^2') for res in resolutions]

        plt.semilogy(resolutions, areas, 'bo-', linewidth=2, markersize=8)
        plt.title('H3 해상도별 육각형 면적')
        plt.xlabel('해상도')
        plt.ylabel('면적 (km², 로그 스케일)')
        plt.grid(True, alpha=0.3)

        # 해상도별 자식 개수 그래프
        plt.subplot(1, 2, 2)
        child_counts = [item['자식_개수'] for item in hierarchy_data]

        plt.bar(resolutions, child_counts, color='lightblue', edgecolor='navy', alpha=0.7)
        plt.title('H3 해상도별 자식 육각형 개수')
        plt.xlabel('해상도')
        plt.ylabel('자식 개수')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.result_dir, f'hierarchical_analysis_{self.timestamp}.png'), dpi=300, bbox_inches='tight')
        plt.show()
        print(f"계층적 분석 차트가 저장되었습니다: {os.path.join(self.result_dir, f'hierarchical_analysis_{self.timestamp}.png')}")

        # Folium을 사용한 계층적 세분화 시각화
        m = folium.Map(location=[lat, lng], zoom_start=13)

        # 기본 해상도 육각형 (큰 육각형)
        base_boundary = h3.h3_to_geo_boundary(base_hex)
        folium_coords_base = [[lat, lng] for lat, lng in base_boundary]

        folium.Polygon(
            locations=folium_coords_base,
            color='red',
            weight=4,
            fill=False,
            popup=f"기본 해상도 {base_resolution}"
        ).add_to(m)

        # 세분화된 육각형들 (작은 육각형들)
        for i, sub_hex in enumerate(subdivided):
            sub_boundary = h3.h3_to_geo_boundary(sub_hex)
            folium_coords_sub = [[lat, lng] for lat, lng in sub_boundary]

            folium.Polygon(
                locations=folium_coords_sub,
                color='blue',
                weight=1,
                fill=True,
                fillOpacity=0.3,
                popup=f"세분화 {i + 1}/{len(subdivided)}"
            ).add_to(m)

        # 중심점 마커
        folium.Marker(
            location=[lat, lng],
            popup=f"중심점\n해상도 {base_resolution}: {base_hex[:10]}...\n해상도 {target_resolution}: {len(subdivided)}개로 세분화",
            icon=folium.Icon(color='green', icon='star')
        ).add_to(m)

        hierarchy_map_file = os.path.join(self.result_dir, f"hierarchical_analysis_{self.timestamp}.html")
        m.save(hierarchy_map_file)
        print(f"계층적 분석 지도가 저장되었습니다: {hierarchy_map_file}")

        return hierarchy_data, subdivided

    def step_10_performance_optimization(self):
        """10단계: 성능 최적화 기법"""
        print("\n=== 10단계: 성능 최적화 기법 ===")

        # 대량 데이터 처리 시뮬레이션
        import time

        # 100만 개의 좌표 생성
        n_points = 100000  # 실제로는 더 적은 수로 테스트
        np.random.seed(42)

        lats = np.random.uniform(37.4, 37.7, n_points)
        lngs = np.random.uniform(126.8, 127.2, n_points)

        print(f"{n_points:,}개 좌표에 대한 H3 변환 성능 테스트")

        # 방법 1: 개별 변환
        start_time = time.time()
        hex_indices_1 = []
        for lat, lng in zip(lats[:1000], lngs[:1000]):  # 샘플만 테스트
            hex_indices_1.append(h3.geo_to_h3(lat, lng, 7))
        time_1 = time.time() - start_time
        print(f"개별 변환 (1,000개): {time_1:.3f}초")

        # 방법 2: 벡터화된 처리 (pandas 활용)
        start_time = time.time()
        df = pd.DataFrame({'lat': lats[:1000], 'lng': lngs[:1000]})
        df['h3'] = df.apply(lambda row: h3.geo_to_h3(row['lat'], row['lng'], 7), axis=1)
        time_2 = time.time() - start_time
        print(f"Pandas apply (1,000개): {time_2:.3f}초")

        # 인덱스 캐싱 예제
        print("\n인덱스 캐싱 효과:")
        cache = {}

        def cached_geo_to_h3(lat, lng, resolution, precision=4):
            """소수점 자리수를 제한하여 캐시 효과 높이기"""
            key = (round(lat, precision), round(lng, precision), resolution)
            if key not in cache:
                cache[key] = h3.geo_to_h3(lat, lng, resolution)
            return cache[key]

        # 캐시 없이 (더 많은 중복 데이터로 테스트)
        start_time = time.time()
        for i in range(10000):
            lat, lng = lats[i % 10], lngs[i % 10]  # 10개 좌표만 반복 사용
            h3.geo_to_h3(lat, lng, 7)
        time_no_cache = time.time() - start_time

        # 캐시 사용 (같은 조건)
        start_time = time.time()
        for i in range(10000):
            lat, lng = lats[i % 10], lngs[i % 10]  # 10개 좌표만 반복 사용
            cached_geo_to_h3(lat, lng, 7)
        time_with_cache = time.time() - start_time

        print(f"캐시 없이: {time_no_cache:.3f}초")
        print(f"캐시 사용: {time_with_cache:.3f}초")
        print(f"성능 개선: {time_no_cache / time_with_cache:.1f}배")

        # Seaborn을 사용한 성능 비교 시각화
        plt.figure(figsize=(12, 8))

        # 성능 비교 데이터
        performance_data = {
            '방법': ['개별 변환', 'Pandas Apply', '캐시 없음', '캐시 사용'],
            '시간(초)': [time_1, time_2, time_no_cache, time_with_cache],
            '데이터크기': ['1,000개', '1,000개', '10,000개 (중복)', '10,000개 (중복)']
        }

        # 서브플롯 1: 성능 비교 막대 그래프
        plt.subplot(2, 2, 1)
        sns.barplot(data=performance_data, x='방법', y='시간(초)', palette='viridis')
        plt.title('H3 변환 방법별 성능 비교')
        plt.xticks(rotation=45)
        plt.ylabel('실행 시간 (초)')

        # 서브플롯 2: 캐시 효과 비교
        plt.subplot(2, 2, 2)
        cache_data = ['캐시 없음', '캐시 사용']
        cache_times = [time_no_cache, time_with_cache]
        colors = ['red', 'green']

        bars = plt.bar(cache_data, cache_times, color=colors, alpha=0.7)
        plt.title('캐시 사용 효과')
        plt.ylabel('실행 시간 (초)')

        # 막대 위에 값 표시
        for bar, time_val in zip(bars, cache_times):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                     f'{time_val:.3f}s', ha='center', va='bottom')

        # 서브플롯 3: 해상도별 변환 시간 시뮬레이션
        plt.subplot(2, 2, 3)
        resolutions = [6, 7, 8, 9, 10]
        conversion_times = []

        for res in resolutions:
            start_time = time.time()
            for i in range(100):  # 작은 샘플로 테스트
                h3.geo_to_h3(lats[i], lngs[i], res)
            conversion_times.append(time.time() - start_time)

        plt.plot(resolutions, conversion_times, 'bo-', linewidth=2, markersize=8)
        plt.title('해상도별 변환 시간')
        plt.xlabel('H3 해상도')
        plt.ylabel('실행 시간 (초, 100회)')
        plt.grid(True, alpha=0.3)

        # 서브플롯 4: 데이터 크기별 성능
        plt.subplot(2, 2, 4)
        data_sizes = [100, 500, 1000, 2000, 5000]
        processing_times = []

        for size in data_sizes:
            start_time = time.time()
            for i in range(min(size, len(lats))):
                h3.geo_to_h3(lats[i], lngs[i], 8)
            processing_times.append(time.time() - start_time)

        plt.plot(data_sizes, processing_times, 'ro-', linewidth=2, markersize=8)
        plt.title('데이터 크기별 처리 시간')
        plt.xlabel('데이터 크기')
        plt.ylabel('실행 시간 (초)')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.result_dir, f'performance_optimization_{self.timestamp}.png'), dpi=300, bbox_inches='tight')
        plt.show()
        print(f"성능 최적화 분석 차트가 저장되었습니다: {os.path.join(self.result_dir, f'performance_optimization_{self.timestamp}.png')}")

        return df, cache


def main():
    """메인 실행 함수"""
    print("🔥 H3 고급 학습 시작!")

    learner = H3AdvancedLearning()

    # 6단계: 공간 분석
    learner.step_6_spatial_analysis()

    # 7단계: 데이터 집계 분석
    learner.step_7_aggregation_analysis()

    # 8단계: 격자 분석
    learner.step_8_grid_analysis()

    # 9단계: 계층적 분석
    learner.step_9_hierarchical_analysis()

    # 10단계: 성능 최적화
    learner.step_10_performance_optimization()

    print("\n✅ H3 고급 학습이 완료되었습니다!")


if __name__ == "__main__":
    main()
