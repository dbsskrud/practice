import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import requests
import json
from sklearn.preprocessing import MinMaxScaler

# ══════════════════════════════════════════════════════════════════════════
# 0. 초기 설정 및 통합 데이터 로드
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="서울 스타터 통합본", layout="wide", page_icon="🏠")

@st.cache_data
def load_master_data():
    # 자치구 기본 데이터 세트 (융합용)
    data = {
        '자치구': ['강남구','강동구','강북구','강서구','관악구','광진구','구로구','금천구','노원구','도봉구',
                  '동대문구','동작구','마포구','서대문구','서초구','성동구','성북구','송파구','양천구','영등포구',
                  '용산구','은평구','종로구','중구','중랑구'],
        '지하철호선': ['2,3,7,9','5,8,9','4','5','2','2,5,7','2,7','7','4,6,7','4,7',
                    '1,2,5','2,4,7','2,5,6','2,3,5','2,3,4,7','2,3,5','4,6','2,3,5,8,9','2,5','2,5,7',
                    '4,6','3,6','1,3,4,5,6','1,2,3,4,5,6','6,7'],
        '평균월세': [95,72,62,68,60,78,63,58,60,55,68,75,85,70,92,80,65,88,70,75,82,63,75,78,60],
        '생활물가': [7361,5935,6424,6165,6629,7265,6021,6619,6837,6338,6384,6378,6705,6735,6680,6599,6973,7098,6593,6070,6978,6388,6702,6614,6687],
        '도서관수': [17,10,7,9,5,8,13,4,10,10,10,9,6,4,9,7,14,12,10,6,4,8,9,8,6],
        '공원수': [7,7,3,10,2,2,4,4,2,6,4,7,5,4,6,5,3,7,5,5,2,7,12,6,5],
        '전체문화공간': [115,24,23,25,21,33,40,20,33,33,39,32,53,36,62,33,62,62,27,27,66,33,250,83,19],
        '한줄평': [
            "인프라와 일자리 중심, 높은 비용만큼 확실한 가치.", "한강 인접 쾌적한 주거환경, 물가가 가장 저렴해요.", "맑은 공기와 정겨운 분위기가 매력적입니다.",
            "마곡지구의 성장과 함께 떠오르는 녹지 부자 동네.", "청년들의 성지, 최고의 가성비와 활발한 에너지.", "대학가와 한강 공원을 동시에 누리는 젊은 주거지.",
            "교통의 요지, 실속 있는 역세권 매물이 많습니다.", "G밸리 직장인을 위한 실속형 자취 명당.", "교육열만큼이나 안전하고 조용한 주택 밀집 지역.",
            "서울에서 가장 낮은 월세, 조용한 삶을 원하는 분께 추천.", "전통시장과 대학가가 어우러진 맛집 천국.", "사당과 노량진 사이, 직장인 선호 지역.",
            "트렌디한 카페와 핫플레이스가 집 앞마당인 곳.", "신촌의 활기와 연희동의 고즈넉함이 공존.", "강남의 편리함에 예술적 품격을 더한 곳.",
            "성수 카페거리와 서울숲이 만나는 트렌디한 지역.", "독립서점과 대학 문화가 살아있는 동네.", "석촌호수와 롯데타워, 완벽한 주말 보장.",
            "정돈된 거리와 높은 치안, 깔끔한 삶의 질.", "여의도 직주근접과 쇼핑의 메카, 교통의 허브.", "글로벌 문화와 이색적인 풍경이 펼쳐지는 곳.",
            "자연 친화적인 주거지와 고즈넉한 한옥마을.", "문화예술 1번지, 예술이 일상이 되는 곳.", "서울의 심장부, 어디든 갈 수 있는 최고의 위치.", "중랑천의 여유와 가성비 좋은 생활 밀착형 주거."
        ]
    }
    df = pd.DataFrame(data)
    df['기타문화공간'] = df['전체문화공간'] - df['도서관수']
    
    # 평균 계산
    means = df[['평균월세', '공원수', '도서관수', '기타문화공간']].mean()
    
    # 정규화 점수 (예다은 로직용)
    scaler = MinMaxScaler()
    df['norm_월세'] = 1 - scaler.fit_transform(df[['평균월세']])
    df['norm_물가'] = 1 - scaler.fit_transform(df[['생활물가']])
    df['norm_문화'] = scaler.fit_transform(df[['전체문화공간']])
    df['norm_공원'] = scaler.fit_transform(df[['공원수']])
    
    return df, means

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/juso/2015/json/seoul_municipalities_geo_simple.json"
    return requests.get(url).json()

df, seoul_means = load_master_data()
seoul_geo = load_geojson()

if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '종로구'

# ══════════════════════════════════════════════════════════════════════════
# 1. 예다은 스타일 커스텀 CSS
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
:root { --navy:#253F52; --orange:#F9852D; --teal:#68A595; }
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.hero {
    background: linear-gradient(135deg, var(--navy) 0%, var(--orange) 100%);
    border-radius: 20px; padding: 30px; color: white; margin-bottom: 20px; text-align: center;
}
.metric-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 15px; padding: 15px;
    text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 130px;
}
.gu-header { background: var(--navy); border-radius: 15px; padding: 20px; color: white; text-align: center; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# 공통 레이아웃 - HERO SECTION
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <h1>서울, 처음이니? : 통합 주거 가이드</h1>
    <p>윤나경의 랭킹 시스템과 예다은의 심층 분석이 만난 첫 자취생 필독 대시보드</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📊 지역 큐레이션 (Yoon)", "✨ 추천 리포트 (Ye)", "🔍 심층 분석 (Ye)", "📝 체크리스트 (Ye)"])

# ══════════════════════════════════════════════════════════════════════════
# TAB 1: 윤나경의 랭킹 대시보드 (기존 윤나경 코드 유지)
# ══════════════════════════════════════════════════════════════════════════
with tab1:
    with st.container(border=True):
        c1, c2 = st.columns([1, 2.5])
        with c1:
            st.subheader("🚇 호선 선택")
            selected_line = st.selectbox("이용 호선", ["전체"] + [str(i) for i in range(1, 10)])
        with c2:
            st.subheader("🔝 우선순위 설정")
            p_cols = st.columns(4)
            options = ["저렴한 월세", "생활 물가", "문화 공간", "녹지 시설"]
            r1 = p_cols[0].selectbox("1순위", options, index=0)
            r2 = p_cols[1].selectbox("2순위", options, index=1)
            r3 = p_cols[2].selectbox("3순위", options, index=2)
            r4 = p_cols[3].selectbox("4순위", options, index=3)

    # 윤나경 추천 로직
    w = {r1: 4, r2: 3, r3: 2, r4: 1}
    df['total_score'] = (df['norm_월세'] * w.get("저렴한 월세", 0) + 
                         df['norm_물가'] * w.get("생활 물가", 0) + 
                         df['norm_문화'] * w.get("문화 공간", 0) + 
                         df['norm_공원'] * w.get("녹지 시설", 0))

    filtered_df = df.copy()
    if selected_line != "전체":
        filtered_df = filtered_df[filtered_df['지하철호선'].str.contains(selected_line)]

    top_3 = filtered_df.sort_values('total_score', ascending=False).head(3)['자치구'].tolist()
    filtered_df['rank_label'] = filtered_df['자치구'].apply(lambda x: f"{top_3.index(x)+1}위 추천" if x in top_3 else "기타")

    col_map, col_info = st.columns([1.5, 1])
    with col_map:
        fig = px.choropleth_mapbox(
            filtered_df, geojson=seoul_geo, locations='자치구', featureidkey="properties.name",
            color='rank_label', color_discrete_map={"1위 추천": "#FF4B4B", "2위 추천": "#FFAA00", "3위 추천": "#FFD700", "기타": "#E0E0E0"},
            mapbox_style="carto-positron", zoom=10, center={"lat": 37.56, "lon": 126.98}, opacity=0.7, height=600
        )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_traces(selectedpoints=None)
        select_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
        if select_event and select_event.selection and select_event.selection.points:
            st.session_state.selected_gu = select_event.selection.points[0]['location']

    with col_info:
        gu = st.session_state.selected_gu
        row = df[df['자치구'] == gu].iloc[0]
        st.markdown(f'<div class="gu-header"><h2>{gu}</h2><p>「 {row["한줄평"]} 」</p></div>', unsafe_allow_html=True)
        # 윤나경 스타일 메트릭
        def get_diff_txt(val, avg, is_cost=True):
            diff = ((val - avg) / avg) * 100
            label = "저렴 🔹" if diff < 0 else "비쌈 🔺"
            if not is_cost: label = "많음 🔺" if diff > 0 else "적음 🔹"
            return f"평균 대비 {abs(diff):.1f}% {label}"

        m1, m2 = st.columns(2)
        m1.markdown(f'<div class="metric-card"><small>월세</small><br><strong>{row["평균월세"]}만원</strong><br><small>{get_diff_txt(row["평균월세"], seoul_means["평균월세"])}</small></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><small>공원수</small><br><strong>{row["공원수"]}개</strong><br><small>{get_diff_txt(row["공원수"], seoul_means["공원수"], False)}</small></div>', unsafe_allow_html=True)
        st.write("")
        fig_radar = go.Figure(go.Scatterpolar(r=[row['norm_월세'], row['norm_물가'], row['norm_문화'], row['norm_공원']],
                                           theta=['월세','물가','문화','녹지'], fill='toself', line_color='#253F52'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), height=300, margin=dict(t=20, b=20))
        st.plotly_chart(fig_radar, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 2~4: 예다은의 코드 스타일 및 로직 적용
# ══════════════════════════════════════════════════════════════════════════
with tab2: # 추천 리포트 (Ye's Card UI)
    st.markdown("### ✨ 조건별 추천 지역 TOP 5")
    top_5_df = filtered_df.sort_values('total_score', ascending=False).head(5)
    cols = st.columns(5)
    for i, (idx, r) in enumerate(top_5_df.iterrows()):
        with cols[i]:
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:15px; border-radius:15px; background:white; height:200px; border-top: 5px solid {['#FF4B4B','#FFAA00','#FFD700','#22C55E','#3B82F6'][i]}">
                <small>TOP {i+1}</small>
                <h4 style="margin:0;">{r['자치구']}</h4>
                <p style="font-size:0.85em; color:gray;">월세: {r['평균월세']}만<br>노선: {r['지하철호선']}<br>점수: {r['total_score']:.1f}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{r['자치구']} 분석하기", key=f"btn_{idx}"):
                st.session_state.selected_gu = r['자치구']
                st.rerun()

with tab3: # 심층 분석 (Ye's Deep Dive)
    gu_d = st.session_state.selected_gu
    row_d = df[df['자치구'] == gu_d].iloc[0]
    st.subheader(f"📍 {gu_d} 심층 분석 리포트")
    
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.info(f"**💬 한 줄 평:** {row_d['한줄평']}")
        st.write(f"🚇 **주요 노선:** {row_d['지하철호선']}호선")
        st.write(f"🎭 **문화 시설:** 총 {int(row_d['전체문화공간'])}개소 (도서관 {int(row_d['도서관수'])}개 포함)")
        st.write(f"🌳 **녹지 환경:** 주요 공원 {int(row_d['공원수'])}개소 인접")
    with col_b:
        fig_bar = px.bar(x=['월세 점수', '물가 점수', '문화 점수', '공원 점수'], 
                         y=[row_d['norm_월세'], row_d['norm_물가'], row_d['norm_문화'], row_d['norm_공원']],
                         labels={'x': '지표', 'y': '점수(0~1)'}, title=f"{gu_d} 인프라 지수")
        st.plotly_chart(fig_bar, use_container_width=True)

with tab4: # 체크리스트 (Ye's Checklist)
    st.subheader("📝 자취방 구하기 체크리스트")
    items = ["등기부등본 확인", "수압 및 배수 상태", "결로/곰팡이 흔적", "치안(CCTV/가로등)", "관리비 포함 항목"]
    selected = [st.checkbox(item) for item in items]
    if st.button("내 체크리스트 저장"):
        st.success("체크리스트가 세션에 저장되었습니다!")
