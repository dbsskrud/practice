import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json

# --- 페이지 설정 ---
st.set_page_config(page_title="서울 스타터 v3.0", layout="wide", page_icon="🗺️")

# --- 데이터 및 지도 GeoJSON 로드 ---
@st.cache_data
def load_data():
    # 25개 자치구 분석 통합 데이터
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
            "화려한 도시 라이프의 중심, 높은 비용만큼 확실한 인프라.", "한강 인접 쾌적한 주거환경, 장보기 물가가 가장 저렴해요.", "북한산 자락의 맑은 공기, 정겨운 동네 분위기가 특징입니다.",
            "마곡지구의 성장과 함께 떠오르는 녹지 부자 동네.", "청년들의 성지, 저렴한 물가와 활기찬 에너지가 가득합니다.", "대학가와 한강 공원을 동시에 누리는 젊은 주거지.",
            "사통팔달 교통의 요지, 가성비 좋은 역세권 매물이 많습니다.", "G밸리 직장인들을 위한 실속형 자취 명당.", "교육열만큼이나 안전하고 조용한 주택 밀집 지역.",
            "서울에서 가장 낮은 월세, 조용한 삶을 원하는 분께 추천.", "전통시장과 대학가가 어우러진 맛집 천국.", "노량진과 사당을 잇는 직장인 최선호 지역.",
            "트렌디한 카페와 핫플레이스가 집 앞마당인 곳.", "신촌의 활기와 연희동의 고즈넉함이 공존하는 동네.", "강남의 편리함에 예술적 품격을 더한 고급 주거지.",
            "성수동 카페거리를 내 집처럼, 숲과 강이 만나는 곳.", "개성 넘치는 독립서점과 대학 문화가 살아있는 동네.", "석촌호수와 롯데타워, 완벽한 주말 여가를 보장합니다.",
            "안전한 치안과 깔끔한 거리, 정돈된 삶을 꿈꾼다면.", "여의도 직주근접의 정석, 쇼핑과 교통의 허브.", "글로벌한 문화와 이색적인 풍경이 펼쳐지는 곳.",
            "은평 한옥마을처럼 여유롭고 자연 친화적인 동네.", "문화예술 공간 밀집도 1위, 감성이 일상이 되는 곳.", "서울의 심장, 어디든 갈 수 있는 최고의 교통지.", "중랑천 산책로와 가성비 좋은 생활권이 강점입니다."
        ]
    }
    df = pd.DataFrame(data)
    
    # 평균 물가 대비 비율 계산
    avg_price = df['생활물가'].mean()
    df['물가비율'] = ((df['생활물가'] / avg_price) - 1) * 100
    
    # 정규화 점수 (0~1)
    for col, high_is_good in [('평균월세', False), ('생활물가', False), ('전체문화공간', True), ('공원수', True)]:
        mn, mx = df[col].min(), df[col].max()
        df[f'norm_{col}'] = (df[col] - mn) / (mx - mn) if high_is_good else (mx - df[col]) / (mx - mn)
    
    return df

@st.cache_data
def load_geojson():
    # 서울시 행정구역 GeoJSON 로드
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/juso/2015/json/seoul_municipalities_geo_simple.json"
    return requests.get(url).json()

df = load_data()
seoul_geo = load_geojson()

# --- 세션 상태 ---
if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '종로구'

# --- 1. 상단 설정 창 (Control Panel) ---
st.title("🚀 서울 스타터 v3.0: 랭킹 기반 지역 추천")

with st.container(border=True):
    c1, c2 = st.columns([1, 2.5])
    
    with c1:
        st.subheader("🚇 호선 선택")
        all_lines = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        selected_line = st.selectbox("주요 이용 호선을 선택하세요.", ["전체"] + all_lines)

    with c2:
        st.subheader("🔝 우선순위 설정")
        p_cols = st.columns(4)
        criteria = ["저렴한 월세", "낮은 물가", "문화 공간", "녹지 시설"]
        
        # 순위 선택 (중복 선택은 사용자 주의 사항으로 처리)
        rank1 = p_cols[0].selectbox("1순위 (4점)", criteria, index=0)
        rank2 = p_cols[1].selectbox("2순위 (3점)", criteria, index=1)
        rank3 = p_cols[2].selectbox("3순위 (2점)", criteria, index=2)
        rank4 = p_cols[3].selectbox("4순위 (1점)", criteria, index=3)

# --- 추천 로직 ---
# 선택한 순위에 따른 가중치 부여
weights = {rank1: 4, rank2: 3, rank3: 2, rank4: 1}
df['total_score'] = (df['norm_평균월세'] * weights.get("저렴한 월세", 0) + 
                     df['norm_생활물가'] * weights.get("낮은 물가", 0) + 
                     df['norm_전체문화공간'] * weights.get("문화 공간", 0) + 
                     df['norm_공원수'] * weights.get("녹지 시설", 0))

# 호선 필터링
display_df = df.copy()
if selected_line != "전체":
    display_df = display_df[display_df['지하철호선'].str.contains(selected_line)]

# 상위 3개 지역 마킹
top_3 = display_df.sort_values('total_score', ascending=False).head(3)['자치구'].tolist()
display_df['recommendation'] = display_df['자치구'].apply(
    lambda x: f"{top_3.index(x)+1}위 추천" if x in top_3 else "기타 지역"
)

# --- 2. 메인 대시보드 (지도 & 상세 설명) ---
col_map, col_info = st.columns([1.4, 1])

with col_map:
    st.subheader("🗺️ 서울시 추천 지역 맵")
    # Choropleth Map을 사용하여 지역구 분리 및 상위 3개 색상 강조
    fig = px.choropleth_mapbox(
        display_df, geojson=seoul_geo, locations='자치구', featureidkey="properties.name",
        color='recommendation',
        color_discrete_map={
            "1위 추천": "#FF4B4B", # 메인 강조색
            "2위 추천": "#FFAA00",
            "3위 추천": "#FFD700",
            "기타 지역": "#E0E0E0"
        },
        mapbox_style="carto-positron",
        zoom=10, center={"lat": 37.565, "lon": 126.985},
        opacity=0.7, height=600
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, showlegend=True)
    
    # 클릭 이벤트 처리
    select_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    if select_event and select_event.selection and select_event.selection.points:
        st.session_state.selected_gu = select_event.selection.points[0]['location']

with col_info:
    # 5. 시각적 배치를 강화한 우측 설명란
    gu = st.session_state.selected_gu
    row = df[df['자치구'] == gu].iloc[0]
    
    # 상단 카드형 배너
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #FF4B4B;">
        <h2 style="margin: 0; color: #1c1c1c;">{gu}</h2>
        <p style="font-size: 1.1em; color: #555; margin-top: 5px;">「 {row['한줄평']} 」</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("") 
    
    # 주요 지표 (Metric 카드)
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
            <small>평균 월세</small><br>
            <strong style="font-size: 1.5em; color: #FF4B4B;">{row['평균월세']}만원</strong>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        price_color = "#e74c3c" if row['물가비율'] > 0 else "#27ae60"
        st.markdown(f"""
        <div style="text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
            <small>물가 지수</small><br>
            <strong style="font-size: 1.5em; color: {price_color};">{abs(row['물가비율']):.1f}%</strong>
            <br><small style="color: {price_color};">평균 대비 {'높음' if row['물가비율'] > 0 else '낮음'}</small>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    
    # 인프라 상세 리포트
    st.subheader("🏗️ 인프라 리포트")
    st.write(f"📚 **도서관:** `{row['도서관수']}개` (전체 문화공간: {row['전체문화공간']}개)")
    st.write(f"🌳 **녹지:** `{row['공원수']}개` 주요 공원 인접")
    st.write(f"🚇 **교통:** `{row['지하철호선']}호선` 이용 가능")

    # 방사형 차트 (밸런스 시각화)
    categories = ['월세', '물가', '문화', '녹지']
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[row['norm_평균월세'], row['norm_생활물가'], row['norm_전체문화공간'], row['norm_공원수']],
        theta=categories, fill='toself', name=gu, line_color='#FF4B4B'
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), height=300, margin=dict(t=30, b=20))
    st.plotly_chart(fig_radar, use_container_width=True)

# --- 하단 랭킹 리스트 ---
st.subheader("🏆 추천 랭킹 TOP 5")
st.dataframe(display_df.sort_values('total_score', ascending=False).head(5)[['자치구', 'recommendation', '평균월세', '지하철호선']], 
             use_container_width=True, hide_index=True)
