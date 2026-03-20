import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import re

# --- 페이지 설정 ---
st.set_page_config(page_title="서울 스타터 v4.5", layout="wide", page_icon="🏙️")

# --- 데이터 전처리 및 통합 함수 ---
@st.cache_data
def load_and_process_data():
    # 1. 자치구 자동 매핑을 위한 기본 리스트
    districts = ['강남구','강동구','강북구','강서구','관악구','광진구','구로구','금천구','노원구','도봉구',
                 '동대문구','동작구','마포구','서대문구','서초구','성동구','성북구','송파구','양천구','영등포구',
                 '용산구','은평구','종로구','중구','중랑구']
    
    # 2. 개별 데이터 로드
    culture = pd.read_csv('서울시 문화공간 정보.csv')
    parks = pd.read_csv('서울시 주요 공원현황(2026 상반기).xlsx - 서울시 주요 공원현황.csv')
    prices = pd.read_csv('생필품 농수축산물 가격 정보(2024년).csv')
    subway = pd.read_csv('서울교통공사_역주소 및 전화번호.csv')
    library = pd.read_csv('서울시 공공도서관 현황정보.csv')

    # 3. 데이터 정제 및 집계 (물가 지수 산출 포함)
    # [생활물가] 자치구별 평균 가격 계산
    price_stats = prices.groupby('자치구 이름')['가격(원)'].mean().reindex(districts).fillna(method='ffill')
    
    # [문화공간] 자치구별 시설 수 집계
    culture_counts = culture.groupby('자치구').size().reindex(districts).fillna(0)
    
    # [공원] 자치구별 공원 수 집계
    park_counts = parks.groupby('지역').size().reindex(districts).fillna(0)
    
    # [도서관] 자치구별 도서관 수 집계
    lib_counts = library.groupby('구명').size().reindex(districts).fillna(0)
    
    # [교통] 주소에서 자치구 추출 및 호선 매핑
    def extract_gu(addr):
        match = re.search(r'\b(\w+구)\b', str(addr))
        return match.group(1) if match else None

    subway['자치구'] = subway['도로명주소'].apply(extract_gu)
    subway_lines = subway.groupby('자치구')['호선'].apply(lambda x: ','.join(sorted(set(x.astype(str))))).reindex(districts).fillna("-")

    # 4. 마스터 데이터프레임 통합
    master_df = pd.DataFrame({
        '자치구': districts,
        '지하철호선': subway_lines.values,
        '생활물가': price_stats.values,
        '전체문화공간': (culture_counts + lib_counts).values,
        '도서관수': lib_counts.values,
        '공원수': park_counts.values,
        '평균월세': [95,72,62,68,60,78,63,58,60,55,68,75,85,70,92,80,65,88,70,75,82,63,75,78,60] # 월세는 외부 API 연동 전까지 유지
    })
    
    master_df['기타문화공간'] = master_df['전체문화공간'] - master_df['도서관수']

    # 5. 점수 계산을 위한 정규화 (Min-Max)
    for col, high_is_good in [('평균월세', False), ('생활물가', False), ('전체문화공간', True), ('공원수', True)]:
        mn, mx = master_df[col].min(), master_df[col].max()
        master_df[f'norm_{col}'] = (master_df[col] - mn) / (mx - mn) if high_is_good else (mx - master_df[col]) / (mx - mn)
    
    return master_df, culture, library

# 데이터 로드
df, raw_culture, raw_library = load_and_process_data()

# --- (이후 UI 로직 및 시각화 코드는 기존과 동일하게 유지하되, df 변수를 활용) ---
# [상세 리포트 영역 예시]
# 좌표 기반 시각화를 위해 raw_culture, raw_library의 위도/경도 데이터를 맵에 추가할 수 있습니다.
