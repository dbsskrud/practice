import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 페이지 설정 ---
st.set_page_config(page_title="서울 스타터 v2.0", layout="wide", page_icon="🏠")

# --- 데이터 준비 (기존 분석 데이터 및 상세 정보 통합) ---
@st.cache_data
def load_comprehensive_data():
    # 25개 자치구 기초 데이터
    data = {
        '자치구': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', 
                  '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', 
                  '용산구', '은평구', '종로구', '중구', '중랑구'],
        '지하철역_예시': ['강남역,역삼역', '천호역,강동역', '수유역,미아역', '발산역,화곡역', '서울대입구역,신림역', '건대입구역', '신도림역,구로역', '가산디지털단지역', '노원역,상계역', '창동역,도봉산역', 
                        '회기역,청량리역', '노량진역,사당역', '홍대입구역,망원역', '신촌역,연희역', '교대역,양재역', '왕십리역,성수역', '성신여대입구역', '잠실역,가락시장역', '목동역,오목교역', '여의도역,당산역', 
                        '이태원역,한남역', '연신내역,불광역', '혜화역,종로3가역', '명동역,을지로입구역', '상봉역,중랑역'],
        '생활물가': [7361, 5935, 6424, 6165, 6629, 7265, 6021, 6619, 6837, 6338, 6384, 6378, 6705, 6735, 6680, 6599, 6973, 7098, 6593, 6070, 6978, 6388, 6702, 6614, 6687],
        '전체문화공간': [115, 24, 23, 25, 21, 33, 40, 20, 33, 33, 39, 32, 53, 36, 62, 33, 62, 62, 27, 27, 66, 33, 250, 83, 19],
        '도서관수': [17, 10, 7, 9, 5, 8, 13, 4, 10, 10, 10, 9, 6, 4, 9, 7, 14, 12, 10, 6, 4, 8, 9, 8, 6],
        '공원수': [7, 7, 3, 10, 2, 2, 4, 4, 2, 6, 4, 7, 5, 4, 6, 5, 3, 7, 5, 5, 2, 7, 12, 6, 5],
        '평균월세': [95, 72, 62, 68, 60, 78, 63, 58, 60, 55, 68, 75, 85, 70, 92, 80, 65, 88, 70, 75, 82, 63, 75, 78, 60],
        '한줄평': [
            "화려한 도시 라이프의 중심, 높은 비용만큼 확실한 인프라.", "한강과 인접한 쾌적한 주거환경, 장보기 물가가 가장 저렴해요.", "북한산 자락의 맑은 공기, 정겨운 동네 분위기를 느낄 수 있습니다.",
            "마곡지구의 성장과 함께 떠오르는 녹지 부자 동네.", "청년들의 성지, 저렴한 물가와 활기찬 에너지가 가득합니다.", "대학가와 한강 공원을 동시에 누리는 젊은 주거지.",
            "사통팔달 교통의 요지, 가성비 좋은 역세권 매물이 많습니다.", "G밸리 직장인들을 위한 실속형 자취 명당.", "교육열만큼이나 안전하고 조용한 주택 밀집 지역.",
            "서울에서 가장 낮은 월세, 조용한 삶을 원하는 분께 추천.", "전통시장과 대학가가 어우러진 맛집 천국.", "노량진과 사당을 잇는 공무원·직장인 최선호 지역.",
            "트렌디한 카페와 핫플레이스가 집 앞마당인 곳.", "신촌의 활기와 연희동의 고즈넉함이 공존하는 동네.", "강남의 편리함에 예술적 품격을 더한 고급 주거지.",
            "성수동 카페거리를 내 집처럼, 숲과 강이 만나는 곳.", "개성 넘치는 독립서점과 대학 문화가 살아있는 동네.", "석촌호수와 롯데타워, 완벽한 주말 여가를 보장합니다.",
            "안전한 치안과 깔끔한 거리, 정돈된 삶을 꿈꾼다면.", "여의도 직주근접의 정석, 쇼핑과 교통의 허브.", "글로벌한 문화와 이색적인 풍경이 펼쳐지는 곳.",
            "은평한옥마을처럼 여유롭고 자연 친화적인 동네.", "문화예술 공간 밀집도 1위, 감성이 일상이 되는 곳.", "서울의 심장, 어디든 갈 수 있는 최고의 교통지.", "중랑천 산책로와 가성비 좋은 생활권이 강점입니다."
        ],
        'lat': [37.4959, 37.5492, 37.6469, 37.5658, 37.4654, 37.5481, 37.4954, 37.4601, 37.6544, 37.6659, 37.5838, 37.5029, 37.5623, 37.5820, 37.4769, 37.5506, 37.6061, 37.5048, 37.5271, 37.5206, 37.5311, 37.6176, 37.5991, 37.5579, 37.5954],
        'lon': [127.0664, 127.1465, 127.0147, 126.8223, 126.9436, 127.0857, 126.8581, 126.9002, 127.0772, 127.0318, 127.0507, 126.9427, 126.9088, 126.9356, 127.0122, 127.0409, 127.0232, 127.1145, 126.8565, 126.9139, 126.9811, 126.9227, 126.9861, 126.9942, 127.0922]
    }
    df = pd.DataFrame(data)
    # 물가 비율 계산 (서울 평균 대비)
    avg_price = df['생활물가'].mean()
    df['물가비율'] = ((df['생활물가'] / avg_price) - 1) * 100
    
    # 정규화 스코어링
    for col, high_is_good in [('평균월세', False), ('생활물가', False), ('전체문화공간', True), ('공원수', True)]:
        mn, mx = df[col].min(), df[col].max()
        df[f'norm_{col}'] = (df[col] - mn) / (mx - mn) if high_is_good else (mx - df[col]) / (mx - mn)
    
    return df

df = load_comprehensive_data()

# --- 세션 상태 ---
if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '종로구'

# --- 1. 상단 선택 및 설정 창 (Top Header Section) ---
st.title("🚀 서울 스타터 v2.0: 당신의 첫 자취 명당 찾기")
with st.container(border=True):
    col_input1, col_input2 = st.columns([1, 2])
    
    with col_input1:
        st.subheader("🚉 지하철역으로 찾기")
        # 모든 지하철역 리스트업 (데이터 기반)
        all_stations = sorted(list(set([s.strip() for sublist in df['지하철역_예시'].str.split(',') for s in sublist])))
        selected_station = st.selectbox("가까이 살고 싶은 지하철역을 선택하세요.", ["선택 안 함"] + all_stations)
        
        if selected_station != "선택 안 함":
            # 역이 속한 구를 찾아 세션 업데이트
            st.session_state.selected_gu = df[df['지하철역_예시'].str.contains(selected_station)]['자치구'].values[0]

    with col_input2:
        st.subheader("⚖️ 주거 우선순위 설정")
        col_w1, col_w2, col_w3, col_w4 = st.columns(4)
        w_rent = col_w1.select_slider("월세 저렴", options=range(1, 6), value=5)
        w_price = col_w2.select_slider("물가 저렴", options=range(1, 6), value=3)
        w_culture = col_w3.select_slider("문화시설", options=range(1, 6), value=4)
        w_park = col_w4.select_slider("녹지/공원", options=range(1, 6), value=2)

# --- 추천 로직 적용 ---
df['total_score'] = (df['norm_평균월세'] * w_rent + df['norm_생활물가'] * w_price + 
                     df['norm_전체문화공간'] * w_culture + df['norm_공원수'] * w_park)
recommended_df = df.sort_values('total_score', ascending=False)

# --- 2. 메인 대시보드 (지도 & 상세 정보) ---
col_map, col_info = st.columns([1.5, 1])

with col_map:
    st.subheader("📍 서울 정주 여건 지도")
    fig = px.scatter_mapbox(df, lat="lat", lon="lon", text="자치구", hover_name="자치구",
                            color="total_score", size="total_score",
                            color_continuous_scale="Viridis", size_max=18,
                            zoom=10.2, center={"lat": 37.56, "lon": 126.98},
                            mapbox_style="carto-positron", height=550)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    # 지도 클릭 시 rerun
    select_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    if select_event and select_event.selection and select_event.selection.points:
        st.session_state.selected_gu = select_event.selection.points[0]['hovertext']

with col_info:
    # 4. 자치구별 한 줄 평 및 상세 데이터
    gu = st.session_state.selected_gu
    row = df[df['자치구'] == gu].iloc[0]
    
    st.header(f"🔍 {gu}")
    st.markdown(f"**「 {row['한줄평']} 」**") # 한 줄 평 노출
    
    # 3. 생활물가 비율 표시
    price_status = "높음 📈" if row['물가비율'] > 0 else "낮음 📉"
    st.metric("💸 생활물가 수준", f"서울 평균 대비 {abs(row['물가비율']):.1f}% {price_status}")
    
    st.divider()
    
    # 2. 문화공간 상세 정보
    st.subheader("🎨 문화 인프라 분석")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.write(f"📚 **공공도서관:** {row['도서관수']}개")
    with col_c2:
        # 영화관/공연장/미술관 등은 전체에서 도서관을 뺀 수치로 예시
        st.write(f"🎬 **기타 문화공간:** {int(row['전체문화공간'] - row['도서관수'])}개")
    st.caption("(기타: 영화관, 공연장, 전시관, 예술회관 포함)")
    
    st.divider()
    
    # 기타 정보
    st.write(f"🏠 **평균 월세:** {row['평균월세']}만원")
    st.write(f"🌳 **주요 공원:** {row['공원수']}개소")
    st.write(f"🚉 **주변 주요역:** {row['지하철역_예시']}")

# --- 3. 하단 추천 리스트 ---
st.subheader("🌟 설정하신 우선순위에 따른 추천 지역 Top 5")
top_5 = recommended_df.head(5)
cols_top = st.columns(5)
for i, (idx, r) in enumerate(top_5.iterrows()):
    with cols_top[i]:
        st.info(f"**{i+1}위: {r['자치구']}**")
        st.write(f"💰 월세 {r['평균월세']}만")
        st.write(f"✨ 추천점수: {r['total_score']:.1f}")
