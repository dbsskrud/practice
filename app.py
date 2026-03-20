import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import requests

# ══════════════════════════════════════════════════════════════════════════
# 페이지 설정
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="서울 스타터 v2.0", layout="wide", page_icon="🏠")

# ══════════════════════════════════════════════════════════════════════════
# 커스텀 CSS (기존 스타일 유지)
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Bebas+Neue&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
h1 { font-family: 'Bebas Neue', 'Noto Sans KR', sans-serif; letter-spacing: 2px; font-size: 2.5rem !important; }
.gu-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 16px; padding: 22px; color: white; margin-bottom: 12px; text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# 데이터 로드 및 전처리
# ══════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_all_data():
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
            "화려한 인프라와 일자리, 높은 비용만큼 확실한 가치.", "한강 공원과 저렴한 물가, 쾌적한 주거의 정석.", "북한산 자락의 맑은 공기, 정겨운 동네 풍경.",
            "서울 식물원과 마곡의 성장, 녹지 부자 동네.", "청년들의 성지, 활발한 자취 생태계와 높은 가성비.", "대학가와 건대 상권, 활기찬 2030의 주거지.",
            "사통팔달 교통의 허브, 실속 있는 역세권 생활권.", "G밸리 직장인을 위한 가성비 끝판왕 자취 명당.", "깔끔한 아파트 단지와 치안, 안전한 주거 환경.",
            "서울에서 가장 착한 월세, 조용한 삶을 위한 선택.", "전통시장과 대학 상권의 조화, 먹거리 천국.", "사당과 노량진 사이, 직장인들의 스테디셀러.",
            "연남, 망원 핫플레이스가 내 집 앞마당인 곳.", "신촌의 활기와 연희동의 고즈넉함이 공존.", "강남의 편리함에 예술적 품격을 더한 주거지.",
            "서울의 브루클린, 성수동 카페거리를 내 집처럼.", "독립서점과 예술가들이 사랑하는 감성 동네.", "석촌호수와 올림픽공원, 완벽한 주말 보장.",
            "정돈된 주거 환경과 높은 치안 수준, 깔끔한 생활.", "여의도 직주근접과 쇼핑 메카, 사통팔달 교통망.", "글로벌한 문화와 이색적인 풍경이 펼쳐지는 곳.",
            "은평 한옥마을의 여유와 자연 친화적 주거지.", "문화예술 1번지, 예술이 일상이 되는 감성지.", "서울의 심장부, 어디든 연결되는 최고의 위치.", "중랑천의 여유와 가성비 좋은 생활 밀착형 주거."
        ]
    }
    df = pd.DataFrame(data)
    df['기타문화공간수'] = df['전체문화공간'] - df['도서관수']
    
    # 서울시 전체 평균치
    means = df[['평균월세', '공원수', '도서관수', '기타문화공간수']].mean()
    
    # 정규화 (0~1)
    for col, high_is_good in [('평균월세', False), ('생활물가', False), ('전체문화공간', True), ('공원수', True)]:
        mn, mx = df[col].min(), df[col].max()
        df[f'norm_{col}'] = (df[col] - mn) / (mx - mn) if high_is_good else (mx - df[col]) / (mx - mn)
    
    return df, means

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/juso/2015/json/seoul_municipalities_geo_simple.json"
    return requests.get(url).json()

df, seoul_avg = load_all_data()
seoul_geo = load_geojson()

if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '종로구'

# ══════════════════════════════════════════════════════════════════════════
# 상단 설정 (호선 및 우선순위)
# ══════════════════════════════════════════════════════════════════════════
st.title("🚀 SEOUL STARTER v3.0")

with st.container(border=True):
    c1, c2 = st.columns([1, 2.5])
    with c1:
        st.subheader("🚇 호선 선택")
        selected_line = st.selectbox("주요 이용 호선을 선택하세요.", ["전체"] + [str(i) for i in range(1, 10)])
    with c2:
        st.subheader("🔝 우선순위 설정")
        p_cols = st.columns(4)
        criteria = ["저렴한 월세", "생활 물가", "문화 공간", "녹지 시설"]
        r1 = p_cols[0].selectbox("1순위 (4점)", criteria, index=0)
        r2 = p_cols[1].selectbox("2순위 (3점)", criteria, index=1)
        r3 = p_cols[2].selectbox("3순위 (2점)", criteria, index=2)
        r4 = p_cols[3].selectbox("4순위 (1점)", criteria, index=3)

# 추천 점수 계산
weights = {r1: 4, r2: 3, r3: 2, r4: 1}
df['total_score'] = (df['norm_평균월세'] * weights.get("저렴한 월세", 0) + 
                     df['norm_생활물가'] * weights.get("생활 물가", 0) + 
                     df['norm_전체문화공간'] * weights.get("문화 공간", 0) + 
                     df['norm_공원수'] * weights.get("녹지 시설", 0))

display_df = df.copy()
if selected_line != "전체":
    display_df = display_df[display_df['지하철호선'].str.contains(selected_line)]

# 상위 3개 자치구 선정
top_3 = display_df.sort_values('total_score', ascending=False).head(3)['자치구'].tolist()
display_df['recommendation'] = display_df['자치구'].apply(
    lambda x: f"{top_3.index(x)+1}위 추천" if x in top_3 else "기타 지역"
)

# ══════════════════════════════════════════════════════════════════════════
# 메인 대시보드 (지도 및 상세 리포트)
# ══════════════════════════════════════════════════════════════════════════
col_map, col_info = st.columns([1.5, 1])

with col_map:
    st.subheader("🗺️ 서울시 지역구별 추천 맵")
    st.caption("지도 위의 자치구를 클릭하여 상세 리포트를 확인하세요.")
    
    # ── 지도 생성 ──
    fig = go.Figure(go.Choroplethmapbox(
        geojson=seoul_geo,
        locations=display_df['자치구'],
        z=display_df['total_score'],
        featureidkey="properties.name",
        colorscale="Viridis",
        marker_opacity=0.7,
        marker_line_width=1,
        marker_line_color="white",
        text=display_df['자치구
