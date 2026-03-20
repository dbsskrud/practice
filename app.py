import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# --- 페이지 설정 ---
st.set_page_config(page_title="서울 스타터", layout="wide", page_icon="🏠")

# --- 데이터 로드 ---
@st.cache_data
def load_data():
    # 자치구 기본 데이터
    data = {
        '자치구': ['강남구','강동구','강북구','강서구','관악구','광진구','구로구','금천구','노원구','도봉구',
                  '동대문구','동작구','마포구','서대문구','서초구','성동구','성북구','송파구','양천구','영등포구',
                  '용산구','은평구','종로구','중구','중랑구'],
        '지하철호선': ['2,3,7,9','5,8,9','4','5','2','2,5,7','2,7','7','4,6,7','4,7',
                    '1,2,5','2,4,7','2,5,6','2,3,5','2,3,4,7','2,3,5','4,6','2,3,5,8,9','2,5','2,5,7',
                    '4,6','3,6','1,3,4,5,6','1,2,3,4,5,6','6,7'],
        '생활물가': [7361,5935,6424,6165,6629,7265,6021,6619,6837,6338,6384,6378,6705,6735,6680,6599,6973,7098,6593,6070,6978,6388,6702,6614,6687],
        '전체문화공간': [115,24,23,25,21,33,40,20,33,33,39,32,53,36,62,33,62,62,27,27,66,33,250,83,19],
        '도서관수': [17,10,7,9,5,8,13,4,10,10,10,9,6,4,9,7,14,12,10,6,4,8,9,8,6],
        '공원수': [7,7,3,10,2,2,4,4,2,6,4,7,5,4,6,5,3,7,5,5,2,7,12,6,5],
        '평균월세': [95,72,62,68,60,78,63,58,60,55,68,75,85,70,92,80,65,88,70,75,82,63,75,78,60]
    }
    df = pd.DataFrame(data)
    df['기타문화공간'] = df['전체문화공간'] - df['도서관수']
    
    # 정규화 (0~1)
    for col, high_is_good in [('평균월세', False), ('생활물가', False), ('전체문화공간', True), ('공원수', True)]:
        mn, mx = df[col].min(), df[col].max()
        df[f'norm_{col}'] = (df[col] - mn) / (mx - mn) if high_is_good else (mx - df[col]) / (mx - mn)
    
    return df

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/juso/2015/json/seoul_municipalities_geo_simple.json"
    return requests.get(url).json()

df = load_data()
seoul_geo = load_geojson()

if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '종로구'

# 1. 타이틀 변경
st.title("서울 스타터:서울시 자취 가이드")

# 2. 웹페이지 설명 문구 추가
st.markdown("""
서울에서 처음 자취를 시작하는 분들을 위한 맞춤형 지역 가이드입니다. 
본인이 중요하게 생각하는 주거 조건(월세, 물가, 문화 인프라 등)의 우선순위를 설정하고, 
자신에게 가장 적합한 서울 자치구를 찾아보세요.
""")

# --- 사이드바 설정 ---
st.sidebar.header("⚙️ 검색 조건 설정")

# 3. 지하철 호선 최대 3개 선택 가능하도록 수정
subway_lines = [str(i) for i in range(1, 10)]
selected_lines = st.sidebar.multiselect(
    "🚉 선호하는 지하철 호선 (최대 3개)", 
    subway_lines, 
    default=["2"], 
    max_selections=3
)

w_rent = st.sidebar.slider("💰 저렴한 월세 중요도", 0, 10, 8)
w_price = st.sidebar.slider("🛒 저렴한 생활물가 중요도", 0, 10, 5)
w_culture = st.sidebar.slider("🎨 문화 공간 중요도", 0, 10, 6)
w_park = st.sidebar.slider("🌳 공원 수 중요도", 0, 10, 4)

# 점수 계산
df['total_score'] = (df['norm_평균월세'] * w_rent + df['norm_생활물가'] * w_price + 
                     df['norm_전체문화공간'] * w_culture + df['norm_공원수'] * w_park)

# 필터링 및 추천 순위 산출
display_df = df.copy()
if selected_lines:
    display_df = display_df[display_df['지하철호선'].apply(lambda x: any(line in x for line in selected_lines))]

top_3 = display_df.sort_values('total_score', ascending=False).head(3)['자치구'].tolist()
display_df['추천순위'] = display_df['자치구'].apply(
    lambda x: f"{top_3.index(x)+1}위" if x in top_3 else "기타"
)

# --- 메인 레이아웃 ---
col_map, col_info = st.columns([1.5, 1])

with col_map:
    # 4. 자치구 추천 지도 색상 설정 (1~3순위 눈에 띄게)
    st.subheader("📍 서울 자치구 추천 지도")
    fig_map = px.choropleth_mapbox(
        display_df, geojson=seoul_geo, locations='자치구', featureidkey="properties.name",
        color='추천순위',
        color_discrete_map={
            "1위": "#FF4B4B", # 강렬한 빨강
            "2위": "#FFAA00", # 주황
            "3위": "#FFD700", # 노랑
            "기타": "#E0E0E0"  # 회색
        },
        mapbox_style="carto-positron", zoom=10, center={"lat": 37.565, "lon": 126.985},
        opacity=0.7, height=600
    )
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    # 지도 클릭 시 자치구 선택 기능
    select_event = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun")
    if select_event and select_event.selection and select_event.selection.points:
        st.session_state.selected_gu = select_event.selection.points[0]['location']

with col_info:
    gu = st.session_state.selected_gu
    row = df[df['자치구'] == gu].iloc[0]
    
    # 5. 자치구명 및 지표 텍스트 가운데 정렬
    st.markdown(f"<h2 style='text-align: center;'>🔍 {gu} 상세 정보</h2>", unsafe_allow_html=True)
    
    # 6. 종합 추천점수 반원 도넛형 그래프 및 숫자 표시
    max_score = w_rent + w_price + w_culture + w_park
    score_percentage = (row['total_score'] / max_score) * 100 if max_score > 0 else 0
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score_percentage,
        number = {'suffix': "점", 'font': {'size': 40}},
        title = {'text': "종합 추천 점수", 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#253F52"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#FFD700'},
                {'range': [50, 80], 'color': '#FFAA00'},
                {'range': [80, 100], 'color': '#FF4B4B'}]
        }
    ))
    fig_gauge.update_layout(height=300, margin=dict(l=30, r=30, t=50, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # 5. 주요 지표 가운데 정렬
    st.markdown(f"""
    <div style="text-align: center; border: 1px solid #ddd; padding: 20px; border-radius: 10px; background-color: #f9f9f9;">
        <p style="margin: 10px 0;">💰 <b>평균 월세:</b> {row['평균월세']}만원</p>
        <p style="margin: 10px 0;">🌳 <b>공원 수:</b> {row['공원수']}개</p>
        <p style="margin: 10px 0;">📚 <b>공공도서관:</b> {row['도서관수']}개</p>
        <p style="margin: 10px 0;">🎨 <b>기타 문화공간:</b> {int(row['기타문화공간'])}개</p>
        <hr>
        <p style="margin: 10px 0;">🚇 <b>지나가는 호선:</b> {row['지하철호선']}호선</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.caption("※ 본 데이터는 서울시 공공데이터를 기반으로 한 분석 결과입니다.")
