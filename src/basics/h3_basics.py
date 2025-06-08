# -*- coding: utf-8 -*-
"""
H3 기본 학습 모듈
Uber H3 라이브러리의 기본 기능들을 단계별로 학습합니다.
"""

import h3
import folium
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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


class H3BasicLearning:
    """H3 기본 기능 학습을 위한 클래스"""
    
    def __init__(self):
        """초기화"""
        print("🌐 H3 학습을 시작합니다!")
        
        # 프로젝트 루트 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))  # src/basics/ -> 프로젝트 루트
        self.result_dir = os.path.join(self.project_root, 'result')
        
        # result 디렉토리가 없으면 생성
        os.makedirs(self.result_dir, exist_ok=True)
        
    def step_1_basic_concepts(self):
        """1단계: H3 기본 개념 이해"""
        print("\n=== 1단계: H3 기본 개념 ===")
        
        # 위도, 경도 좌표
        lat, lng = 37.5665, 126.9780  # 서울 시청 좌표
        print(f"📍 대상 위치: 서울 시청 (위도: {lat}, 경도: {lng})")
        
        # 다양한 해상도로 H3 인덱스 생성
        for resolution in range(0, 8):
            h3_index = h3.geo_to_h3(lat, lng, resolution)
            print(f"해상도 {resolution}: {h3_index}")
            
        return lat, lng
    
    def step_2_resolution_analysis(self):
        """2단계: 해상도별 특성 분석"""
        print("\n=== 2단계: 해상도별 특성 분석 ===")
        
        lat, lng = 37.5665, 126.9780
        
        # 해상도별 육각형 크기 정보
        resolution_info = []
        for res in range(0, 11):
            area_km2 = h3.hex_area(res, unit='km^2')
            edge_length_km = h3.edge_length(res, unit='km')
            resolution_info.append({
                '해상도': res,
                '면적(km²)': round(area_km2, 4),
                '변의길이(km)': round(edge_length_km, 4)
            })
        
        df = pd.DataFrame(resolution_info)
        print(df.to_string(index=False))
        
        return df
    
    def step_3_neighbor_analysis(self):
        """3단계: 인근 육각형 분석"""
        print("\n=== 3단계: 인근 육각형 분석 ===")
        
        lat, lng = 37.5665, 126.9780
        resolution = 7
        
        # 중심 육각형
        center_hex = h3.geo_to_h3(lat, lng, resolution)
        print(f"중심 육각형: {center_hex}")
        
        # 1차 인근 육각형들
        neighbors = h3.k_ring(center_hex, 1)
        print(f"인근 육각형 개수 (k=1): {len(neighbors)}")
        
        # 2차 인근 육각형들
        neighbors_2 = h3.k_ring(center_hex, 2)
        print(f"인근 육각형 개수 (k=2): {len(neighbors_2)}")
        
        # 거리별 육각형 개수
        for k in range(1, 5):
            ring_hexes = h3.k_ring(center_hex, k)
            print(f"거리 {k}: {len(ring_hexes)}개 육각형")
            
        return center_hex, neighbors
    
    def step_4_coordinate_conversion(self):
        """4단계: 좌표 변환"""
        print("\n=== 4단계: 좌표 변환 ===")
        
        # H3 인덱스에서 중심점 좌표 구하기
        h3_index = h3.geo_to_h3(37.5665, 126.9780, 7)
        center_lat, center_lng = h3.h3_to_geo(h3_index)
        print(f"H3 중심점: ({center_lat:.6f}, {center_lng:.6f})")
        
        # 육각형 경계 좌표 구하기
        boundary = h3.h3_to_geo_boundary(h3_index)
        print(f"육각형 꼭짓점 개수: {len(boundary)}")
        print("꼭짓점 좌표:")
        for i, (lat, lng) in enumerate(boundary):
            print(f"  점 {i+1}: ({lat:.6f}, {lng:.6f})")
            
        return h3_index, center_lat, center_lng, boundary
    
    def step_5_visualization(self):
        """5단계: 시각화"""
        print("\n=== 5단계: H3 육각형 시각화 ===")
        
        lat, lng = 37.5665, 126.9780
        resolution = 8
        
        # 지도 생성
        m = folium.Map(location=[lat, lng], zoom_start=12)
        
        # 중심 육각형과 인근 육각형들
        center_hex = h3.geo_to_h3(lat, lng, resolution)
        hexes = h3.k_ring(center_hex, 2)
        
        # 각 육각형을 지도에 추가
        for hex_id in hexes:
            boundary = h3.h3_to_geo_boundary(hex_id)
            # folium 형식으로 좌표 변환 (lat, lng 순서)
            folium_coords = [[lat, lng] for lat, lng in boundary]
            
            # 중심 육각형은 빨간색, 나머지는 파란색
            color = 'red' if hex_id == center_hex else 'blue'
            
            folium.Polygon(
                locations=folium_coords,
                color=color,
                fill=True,
                fillOpacity=0.3,
                popup=f"H3: {hex_id}"
            ).add_to(m)
        
        # 지도 저장
        map_file = os.path.join(self.result_dir, "h3_visualization.html")
        m.save(map_file)
        print(f"지도가 저장되었습니다: {map_file}")
        
        return map_file


def main():
    """메인 실행 함수"""
    print("🚀 H3 단계별 학습 시작!")
    
    learner = H3BasicLearning()
    
    # 1단계: 기본 개념
    learner.step_1_basic_concepts()
    
    # 2단계: 해상도 분석
    learner.step_2_resolution_analysis()
    
    # 3단계: 인근 육각형 분석
    learner.step_3_neighbor_analysis()
    
    # 4단계: 좌표 변환
    learner.step_4_coordinate_conversion()
    
    # 5단계: 시각화
    learner.step_5_visualization()
    
    print("\n✅ H3 기본 학습이 완료되었습니다!")


if __name__ == "__main__":
    main()