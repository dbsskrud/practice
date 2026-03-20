import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import requests
import json
import re
import os
from sklearn.preprocessing import MinMaxScaler

# ══════════════════════════════════════════════════════════════════════════
# 0. 초기 설정 및 데이터 엔진 (예다은 님의 로직 기반)
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="서울, 처음이니? 통합 마스터", layout="wide", page_icon="🏠")

# --- 공통 스타일 (예다은 님의 디자인 시스템 적용)  ---
st.markdown("""
<style>
    :root{ --navy:#253F52; --orange:#F9852D; --teal:#68A595; --line:#D8E2EB; }
    .hero{ background: linear-gradient(135deg, var(--navy) 0%, var(--orange) 100%); border-radius: 28px; padding: 30px; color: white; margin-bottom: 18px; text-align: center; }
    .hero h1{ font-size:2.2rem; font-weight:900; margin-bottom:10px; color: white; }
    .metric-card{ background: white; border:1px solid var(--line); border-radius:20px; padding:18px; box-shadow:0 6px 18px rgba(37,63,82,.06); height: 140px; text-align: center; }
    .gu-header { background: var(--navy); border-radius: 15px; padding: 20px; color: white; text-align: center; margin-bottom: 15px; }
    .top-card{ border-radius:22px; padding:18px; height:100%; border:1px solid var(--line); box-shadow:0 10px 26px rgba(15,23,42,.05); background:white; }
</style>
""", unsafe_allow_html=True)

# --- 예다은 님의 데이터 로드 함수들  ---
@st.cache_data
def load_unified_data():
    # 예다은 님의 상세 데이터셋 및 정규화 로직 적용
    districts = ["강남구","강동구","강북구","강서구","관악구","광진구","구로구","금천구","노원구","도봉구",
                 "동대문구","동작구","마포구","서대문구","서초구","성동구","성북구","송파구","양천구","영등포구",
                 "용산구","은평구","종로구","중구","중랑구"]
    
    # 기초 렌트 데이터 (Ye's Embedded Rent) 
    rent_data = {"강남구":95,"강동구":72,"강북구":62,"강서구":68,"관악구":60,"광진구":78,"구로구":63,"금천구":58,"노원구":60,
                 "도봉구":55,"동대문구":68,"동작구":75,"마포구":85,"서대문구":70,"서초구":92,"성동구":80,"성북구":65,"송파구":88,
                 "양천구":70,"영등포구":75,"용산구":82,"은평구":63,"종로구":75,"중구":78,"중랑구":60}
    
    df = pd.DataFrame({"자치구": districts, "평균월세": [rent_data[d] for d in districts]})
    
    # 생활물가 및 인프라 가상 데이터 (Yoon & Ye 통합 지표)
    df['생활물가'] = [7361,5935,6424,6165,6629,7265,6021,6619,6837,6338,6384,6378,6705,6735,6680,6599,6973,7098,6593,6070,6978,6388,6702,6614,6687]
    df['전체문화공간'] = [115,24,23,25,21,33,40,20,33,33,39,32,53,36,62,33,62,62,27,27,66,33,250,83,19]
    df['공원수'] = [7,7,3,10,2,2,4,4,2,6,4,7,5,4,6,5,3,7,5,5,2,7,12,6,5]
    df['지하철호선'] = ['2,3,7,9','5,8,9','4','5','2','2,5,7','2,7','7','4,6,7','4,7','1,2,5','2,4,7','2,5,6','2,3,5','2,3,4,7','2,3,5','4,6','2,3,5,8,9','2,5','2,5,7','4,6','3,6','1,3,4,5,6','1,2,3,4,5,6','6,7']
    
    # 정규화 (Min-Max) 
    scaler = MinMaxScaler()
    df['norm_월세'] = 1 - scaler.fit_transform(df[['평균월세']])
    df['norm_물가'] = 1 - scaler.fit_transform(df[['생활물가']])
    df['norm_문화'] = scaler.fit_transform(df[['전체문화공간']])
    df['norm_공원'] = scaler.fit_transform(df[['공원수']])
    
    return df

master_df = load_unified_data()

# 세션 상태 초기화
if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '종로구'

# ══════════════════════════════════════════════════════════════════════════
# 상단 HERO 섹션 (Ye's Style) 
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <h1>서울, 처음이니? 통합 마스터 대시보드</h1>
    <p>윤나경의 스마트 랭킹 시스템과 예다은의 프리미엄 분석 리포트를 한 번에 확인하세요.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 지역 큐레이션 (Yoon)", 
    "✨ 추천 리포트 (Ye)", 
    "🔍 지역 심층분석 (Ye)", 
    "⚖️ 비교 분석 (Ye)", 
    "✅ 체크리스트 (Ye)"
])

# ══════════════════════════════════════════════════════════════════════════
# TAB 1: 윤나경의 지역 큐레이션 (Yoon's Logic)
# ══════════════════════════════════════════════════════════════════════════
with tab1:
    with st.container(border=True):
        c1, c2 = st.columns([1, 2.5])
        with c1:
            st.subheader("🚇 호선 선택")
            sel_line = st.selectbox("주요 이용 호선", ["전체"] + [str(i) for i in range(1, 10)], key="y_line")
        with c2:
            st.subheader("🔝 우선순위 설정")
            p_cols = st.columns(4)
            opts = ["저렴한 월세", "생활 물가", "문화 공간", "녹지 시설"]
            r1 = p_cols[0].selectbox("1순위", opts, index=0, key="y_r1")
            r2 = p_cols[1].selectbox("2순위", opts, index=1, key="y_r2")
            r3 = p_cols[2].selectbox("3순위", opts, index=2, key="y_r3")
            r4 = p_cols[3].selectbox("4순위", opts, index=3, key="y_r4")

    # 윤나경 추천 가중치 계산
    w = {r1: 4, r2: 3, r3: 2, r4: 1}
    master_df['total_score'] = (master_df['norm_월세'] * w.get("저렴한 월세", 0) + 
                                master_df['norm_물가'] * w.get("생활 물가", 0) + 
                                master_df['norm_문화'] * w.get("문화 공간", 0) + 
                                master_df['norm_공원'] * w.get("녹지 시설", 0))

    y_filtered = master_df.copy()
    if sel_line != "전체":
        y_filtered = y_filtered[y_filtered['지하철호선'].str.contains(sel_line)]

    top_3_names = y_filtered.sort_values('total_score', ascending=False).head(3)['자치구'].tolist()
    
    col_map, col_list = st.columns([1.5, 1])
    with col_map:
        # 윤나경 스타일 Plotly Map
        fig = px.choropleth_mapbox(
            y_filtered, geojson="https://raw.githubusercontent.com/southkorea/seoul-maps/master/juso/2015/json/seoul_municipalities_geo_simple.json",
            locations='자치구', featureidkey="properties.name", color='total_score',
            color_continuous_scale="Viridis", mapbox_style="carto-positron",
            zoom=10, center={"lat": 37.56, "lon": 126.98}, opacity=0.7, height=550
        )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

    with col_list:
        st.subheader("🏆 실시간 추천 TOP 3")
        for i, gu in enumerate(top_3_names):
            st.success(f"**{i+1}위: {gu}**")
        st.info("💡 지도의 자치구를 확인하고 다음 탭에서 상세 리포트를 확인하세요.")

# ══════════════════════════════════════════════════════════════════════════
# TAB 2~5: 예다은의 고도화 분석 (Ye's Logic & UI) 
# ══════════════════════════════════════════════════════════════════════════
with tab2: # 추천 리포트 (Ye's Card UI)
    st.markdown("### ✨ 자취 초보를 위한 맞춤 추천 리포트")
    cols = st.columns(3)
    for i, gu in enumerate(top_3_names):
        row = master_df[master_df['자치구'] == gu].iloc[0]
        with cols[i]:
            st.markdown(f"""
            <div class="top-card" style="border-top:8px solid {['#ef4444','#f97316','#eab308'][i]};">
                <div style="font-weight:800; font-size:0.8rem; color:#64748b;">TOP {i+1}</div>
                <div style="font-size:1.4rem; font-weight:900; margin-bottom:10px;">{gu}</div>
                <div style="font-size:0.95rem; line-height:1.6;">
                    💰 월세: <b>{row['평균월세']}만원</b><br>
                    🚇 주요 노선: {row['지하철호선']}<br>
                    🌳 공원 수: {int(row['공원수'])}개
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{gu} 분석하기", key=f"ye_btn_{i}"):
                st.session_state.selected_gu = gu

with tab3: # 지역 심층분석 (Ye's Deep Dive)
    active_gu = st.session_state.selected_gu
    r = master_df[master_df['자치구'] == active_gu].iloc[0]
    st.markdown(f"<div class='gu-header'><h2>{active_gu} 심층 분석</h2></div>", unsafe_allow_html=True)
    
    # 예다은 스타일 메트릭 섹션 
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"<div class='metric-card'><small>평균 월세</small><br><span style='font-size:1.7rem; font-weight:800;'>{r['평균월세']}만</span></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-card'><small>문화시설</small><br><span style='font-size:1.7rem; font-weight:800;'>{int(r['전체문화공간'])}개</span></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-card'><small>공원 수</small><br><span style='font-size:1.7rem; font-weight:800;'>{int(r['공원수'])}개</span></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='metric-card'><small>물가 점수</small><br><span style='font-size:1.7rem; font-weight:800;'>{int(r['norm_물가']*100)}점</span></div>", unsafe_allow_html=True)

    # 방사형 인프라 차트 
    st.write("")
    fig_radar = go.Figure(go.Scatterpolar(
        r=[r['norm_월세'], r['norm_물가'], r['norm_문화'], r['norm_공원']],
        theta=['월세 가성비', '물가 가성비', '문화 인프라', '녹지 환경'], fill='toself', line_color='#68A595'
    ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), height=400)
    st.plotly_chart(fig_radar, use_container_width=True)

with tab4: # 비교 분석 (Ye's Comparison)
    st.markdown("### 🆚 자치구 비교 분석")
    comp_list = st.multiselect("비교할 지역을 선택하세요 (최대 3개)", master_df['자치구'].tolist(), default=top_3_names[:2])
    if comp_list:
        comp_df = master_df[master_df['자치구'].isin(comp_list)]
        st.table(comp_df[['자치구', '평균월세', '지하철호선', '전체문화공간', '공원수']].set_index('자치구'))

with tab5: # 체크리스트 (Ye's Utility) 
    st.markdown("### ✅ 자취방 계약 전 필수 체크리스트")
    items = ["등기부등본 확인 (전입 가능 여부)", "수압 및 배수 상태", "결로/곰팡이 흔적", "치안(CCTV/가로등)", "관리비 포함 항목"]
    for item in items:
        st.checkbox(item)
    st.button("체크리스트 파일로 저장")
