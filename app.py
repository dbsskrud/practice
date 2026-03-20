import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import requests

# --- 페이지 설정 ---
st.set_page_config(page_title="서울 스타터 v3.0", layout="wide", page_icon="🗺️")

# --- 데이터 및 지도 GeoJSON 로드 ---
@st.cache_data
def load_data():
    # 25개 자치구 데이터 (기존 분석 결과 통합)
    data = {
        '자치구': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', 
                  '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', 
                  '용산구', '은평구', '종로구', '중구', '중랑구'],
        '지하철호선': ['2,3,7,9', '5,8,9', '4', '5', '2', '2,5,7', '2,7', '7', '4,6,7', '4,7', 
                    '1,2,5', '2,4,7', '2,5,6', '2,3,5', '2,3,4,7', '2,3,5', '4,6', '2,3,5,8,9', '2,5', '2,5,7', 
                    '4,6', '3,6', '1,3,4,5,6', '1,2,3,4,5,6', '6,7'],
        '생활물가': [7361, 5935, 6424, 6165, 6629, 7265, 6021, 6619, 6837, 6338, 6384, 6378, 6705, 6735, 6680, 6599, 6973, 7098, 6593, 6070, 6978, 6388, 6702, 6614, 6687],
        '전체문화공간': [115, 24, 23, 25, 21, 33, 40, 20, 33, 33, 39, 32, 53, 36, 62, 33, 62, 62, 27, 27, 66, 33, 250, 83, 19],
        '도서관수': [17, 10, 7, 9, 5, 8, 13, 4, 10, 10, 10, 9, 6, 4, 9, 7, 14, 12, 10, 6, 4, 8, 9, 8, 6],
        '공원수': [7, 7, 3, 10, 2, 2, 4, 4, 2, 6, 4, 7, 5, 4, 6, 5, 3, 7, 5, 5, 2, 7, 12, 6, 5],
        '평균월세': [95, 72, 62, 68, 60, 78, 63, 58, 60, 55, 68, 75, 85, 70, 92, 80, 65, 88, 70, 75, 82, 63, 75, 78, 60],
        '한줄평': [
            "트렌디한 인프라와 압도적 일자리, 비용만큼 확실한 가치.", "한강 공원과 저렴한 물가, 쾌적한 주거의 정석.", "자연과 정겨운 동네 풍경, 여유로운 삶이 가능합니다.",
            "서울 식물원과 마곡의 인프라, 녹지 부자 동네.", "청년들의 성지, 가장 활발한 자취 생태계와 가성비.", "대학가와 건대 상권, 활기찬 2030의 주거지.",
            "사통팔달의 교통 허브, 실속 있는 역세권 생활권.", "G밸리 직장인을 위한 가성비 끝판왕 자취 명당.", "깔끔한 아파트 단지와 치안, 공부와 휴식에 최적화.",
            "서울에서 가장 착한 월세, 조용하고 평화로운 동네.", "전통시장과 대학 상권의 완벽한 조화, 먹거리 천국.", "사당과 노량진 사이, 직장인들의 스테디셀러.",
            "연남, 망원 등 핫플레이스가 내 집 앞마당.", "신촌의 대학 문화와 연희동의 고즈넉함이 공존.", "강남의 편리함에 품격 있는 예술 인프라를 더함.",
            "서울의 브루클린, 성수동 카페거리를 내 집처럼.", "개성 넘치는 독립서점과 예술가들이 사랑하는 동네.", "석촌호수와 올림픽공원, 주말이 기다려지는 곳.",
            "정돈된 주거 환경과 높은 안전성, 깔끔한 생활권.", "여의도 직주근접과 쇼핑의 메카, 사통팔달 교통망.", "글로벌한 이색 문화와 남산 조망이 펼쳐지는 곳.",
            "은평 한옥마을의 고즈넉함과 자연의 여유.", "문화예술 1번지, 집 밖을 나서면 예술이 일상이 됨.", "서울의 심장부, 어디든 갈 수 있는 최고의 위치.", "중랑천의 여유와 가성비 좋은 생활 밀착형 주거지."
        ]
    }
    df = pd.DataFrame(data)
    
    # 평균 물가 대비 비율 계산
    avg_p = df['생활물가'].mean()
    df['물가비율'] = ((df['생활물가'] / avg_p) - 1) * 100
    
    # 정규화 점수 (0~1)
    for col, high_is_good in [('평균월세', False), ('생활물가', False), ('전체문화공간', True), ('공원수', True)]:
        mn, mx = df[col].min(), df[col].max()
        df[f'norm_{col}'] = (df[col] - mn) / (mx - mn) if high_is_good else (mx - df[col]) / (mx - mn)
    
    return df

@st.cache_data
def load_geojson():
    # 서울시 자치구 경계 GeoJSON (공공 데이터 활용)
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/juso/2015/json/seoul_municipalities_geo_simple.json"
    response = requests.get(url)
    return response.json()

df = load_data()
seoul_geojson = load_geojson()

# --- 세션 상태 ---
if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '종로구'

# --- 1. 상단 설정 창 (Control Panel) ---
st.title("📍 서울 스타터 v3.0: 랭킹 기반 지역 추천")

with st.container(border=True):
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.subheader("🚇 원하는 호선 선택")
        all_lines = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        selected_line = st.selectbox("주로 이용할 지하철 호선을 골라주세요.", ["전체"] + all_lines)

    with c2:
        st.subheader("🔝 항목별 우선순위 설정")
        p_cols = st.columns(4)
        options = ["저렴한 월세", "생활 물가", "문화 공간", "녹지 시설"]
        
        rank1 = p_cols[0].selectbox("1순위 (4점)", options, index=0)
        rank2 = p_cols[1].selectbox("2순위 (3점)", options, index=1)
        rank3 = p_cols[2].selectbox("3순위 (2점)", options, index=2)
        rank4 = p_cols[3].selectbox("4순위 (1점)", options, index=3)

# --- 추천 알고리즘 ---
# 순위에 따른 가중치 맵핑
weight_map = {rank1: 4, rank2: 3, rank3: 2, rank4: 1}
df['total_score'] = (df['norm_평균월세'] * weight_map["저렴한 월세"] + 
                     df['norm_생활물가'] * weight_map["생활 물가"] + 
                     df['norm_전체문화공간'] * weight_map["문화 공간"] + 
                     df['norm_공원수'] * weight_map["녹지 시설"])

# 호선 필터링
filtered_df = df.copy()
if selected_line != "전체":
    filtered_df = filtered_df[filtered_df['지하철호선'].str.contains(selected_line)]

# 상위 3개 지역구 마킹
top_3_list = filtered_df.sort_values('total_score', ascending=False).head(3)['자치구'].tolist()
filtered_df['status'] = filtered_df['자치구'].apply(lambda x: f"{top_3_list.index(x)+1}위 추천" if x in top_3_list else "기타 지역")

# --- 2. 메인 대시보드 (지도 & 상세 설명) ---
col_map, col_info = st.columns([1.5, 1])

with col_map:
    st.subheader("🗺️ 서울시 지역구별 추천 맵")
    # Choropleth 지도로 행정구역 구분 및 상위 3개 색칠
    fig = px.choropleth_mapbox(
        filtered_df, geojson=seoul_geojson, locations='자치구', featureidkey="properties.name",
        color='status',
        color_discrete_map={
            "1위 추천": "#E74C3C", # 강렬한 빨강
            "2위 추천": "#F39C12", # 주황
            "3위 추천": "#F1C40F", # 노랑
            "기타 지역": "#D5DBDB"  # 회색
        },
        mapbox_style="carto-positron",
        zoom=10, center={"lat": 37.563, "lon": 126.986},
        opacity=0.7, height=600,
        hover_data={'자치구': True, 'total_score': ':.2f', 'status': False}
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, showlegend=True)
    
    # 클릭 이벤트
    select_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    if select_event and select_event.selection and select_event.selection.points:
        st.session_state.selected_gu = select_event.selection.points[0]['location']

with col_info:
    # 5. 우측 설명란 시각적 배치 강화
    gu = st.session_state.selected_gu
    row = df[df['자치구'] == gu].iloc[0]
    
    # 타이틀 섹션
    st.markdown(f"""
    <div style="background-color: #2C3E50; padding: 20px; border-radius: 10px; color: white; text-align: center;">
        <h2 style="margin: 0;">{gu}</h2>
        <p style="font-size: 1.1em; font-style: italic; margin-top: 10px; color: #BDC3C7;">"{row['한줄평']}"</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("") # 간격
    
    # 주요 지표 섹션 (Card 형태)
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.markdown(f"""
        <div style="border: 1px solid #D5DBDB; padding: 15px; border-radius: 8px; text-align: center;">
            <p style="color: gray; margin-bottom: 5px;">평균 월세</p>
            <h3 style="margin: 0; color: #E67E22;">{row['평균월세']}만원</h3>
        </div>
        """, unsafe_allow_html=True)
    with c_m2:
        price_color = "#E74C3C" if row['물가비율'] > 0 else "#27AE60"
        price_text = "평균 대비 높음" if row['물가비율'] > 0 else "평균 대비 낮음"
        st.markdown(f"""
        <div style="border: 1px solid #D5DBDB; padding: 15px; border-radius: 8px; text-align: center;">
            <p style="color: gray; margin-bottom: 5px;">생활 물가</p>
            <h3 style="margin: 0; color: {price_color};">{abs(row['물가비율']):.1f}%</h3>
            <p style="font-size: 0.8em; color: {price_color};">{price_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()
    
    # 인프라 상세 정보
    st.subheader("🏗️ 인프라 리포트")
    st.write(f"📚 **공공도서관:** `{row['도서관수']}개` (총 {row['전체문화공간']}개의 문화공간)")
    st.write(f"🌳 **녹지 시설:** `{row['공원수']}개의 주요 공원` 보유")
    st.write(f"🚇 **운행 호선:** `{row['지하철호선']}호선` 운영 중")
    
    # 방사형 비교 차트
    categories = ['월세가성비', '물가가성비', '문화시설', '녹지시설']
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[row['norm_평균월세'], row['norm_생활물가'], row['norm_전체문화공간'], row['norm_공원수']],
        theta=categories, fill='toself', name=gu, line_color='#2C3E50'
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), height=300, margin=dict(t=20, b=20))
    st.plotly_chart(fig_radar, use_container_width=True)

# --- 하단 랭킹 테이블 ---
st.subheader("🏆 조건별 추천 순위")
st.dataframe(filtered_df[['자치구', 'status', '평균월세', '지하철호선', 'total_score']].sort_values('total_score', ascending=False), 
             use_container_width=True, hide_index=True)
