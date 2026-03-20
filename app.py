import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from sklearn.preprocessing import MinMaxScaler

# ══════════════════════════════════════════════════════════════════════════
# 1. 페이지 설정 및 커스텀 스타일 (예다은 스타일 적용)
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="서울 스타터 v5.0", layout="wide", page_icon="🏠")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
:root { --navy:#253F52; --orange:#F9852D; --teal:#68A595; }
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.hero {
    background: linear-gradient(135deg, #253F52 0%, #F9852D 100%);
    border-radius: 20px; padding: 30px; color: white; margin-bottom: 20px; text-align: center;
}
.gu-header {
    background: #253F52; border-radius: 15px; padding: 20px; color: white; 
    text-align: center; margin-bottom: 15px;
}
.metric-box {
    border: 1px solid #ddd; padding: 15px; border-radius: 12px; 
    text-align: center; background-color: white; height: 120px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# 2. 데이터 엔진 (통합 데이터 로직)
# ══════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_integrated_data():
    # 자치구 기본 데이터 
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
        '한줄평': ["일자리 중심, 높은 비용만큼 확실한 인프라.", "한강 인근, 물가가 저렴한 주거 안정지.", "맑은 공기와 정겨운 분위기가 특징.", "마곡지구 성장과 녹지 부자 동네.", "최고의 가성비와 활발한 자취 생태계.", "대학가와 한강 공원을 동시에 향유.", "교통 요지, 실속 역세권 매물 다수.", "가산 직장인을 위한 실속 자취 명당.", "안전하고 조용한 주택 밀집 지역.", "가장 낮은 월세, 조용한 삶에 최적.", "교통 중심, 전통시장과 대학가의 조화.", "노량진-사당 직장인 선호 지역.", "트렌디한 카페와 핫플이 가득한 곳.", "신촌의 활기와 연희의 고즈넉함 공존.", "강남의 편리함에 예술적 품격 더함.", "성수 카페거리와 서울숲 인접 지역.", "독립서점과 대학 문화가 살아있는 곳.", "석촌호수와 롯데타워, 완벽한 여가.", "안전하고 정돈된 깔끔한 생활권.", "여의도 직주근접과 쇼핑의 허브.", "글로벌 문화와 남산 조망의 이색 풍경.", "여유로운 자연 친화적 주거 환경.", "문화예술 1번지, 예술이 일상이 됨.", "서울의 심장부, 어디든 연결되는 위치.", "가성비 생활권과 중랑천의 여유."]
    }
    df = pd.DataFrame(data)
    df['기타문화공간'] = df['전체문화공간'] - df['도서관수']
    
    # 서울 평균 계산
    means = df[['평균월세', '공원수', '도서관수', '기타문화공간', '생활물가']].mean()
    
    # 정규화 스코어링
    scaler = MinMaxScaler()
    cols_to_norm = ['평균월세', '생활물가', '전체문화공간', '공원수']
    norm_data = scaler.fit_transform(df[cols_to_norm])
    df['norm_월세'] = 1 - norm_data[:, 0]
    df['norm_물가'] = 1 - norm_data[:, 1]
    df['norm_문화'] = norm_data[:, 2]
    df['norm_공원'] = norm_data[:, 3]
    
    return df, means

@st.cache_data
def load_seoul_geojson():
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/juso/2015/json/seoul_municipalities_geo_simple.json"
    return requests.get(url).json()

df, seoul_avg = load_integrated_data()
seoul_geo = load_seoul_geojson()

# 세션 상태 초기화
if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '종로구'

# ══════════════════════════════════════════════════════════════════════════
# 3. 메인 레이아웃 (Hero Section & Tabs)
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <h1>서울, 처음이니? 통합 가이드</h1>
    <p>데이터로 찾고, 1:1로 비교하며, 체크리스트로 완성하는 스마트한 첫 자취 프로젝트</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📊 지역 큐레이션", "🔍 자치구 심층 분석", "⚖️ 1:1 지역 비교", "📝 자취 체크리스트"])

# ── Tab 1: 지역 큐레이션 (윤나경 랭킹 로직 적용) ── 
with tab1:
    with st.container(border=True):
        c_line, c_rank = st.columns([1, 2.5])
        with c_line:
            st.subheader("🚇 호선 선택")
            selected_line = st.selectbox("이동이 잦은 호선을 고르세요.", ["전체"] + [str(i) for i in range(1, 10)])
        with c_rank:
            st.subheader("🔝 우선순위 설정")
            p_cols = st.columns(4)
            options = ["저렴한 월세", "생활 물가", "문화 공간", "녹지 시설"]
            r1 = p_cols[0].selectbox("1순위 (4점)", options, index=0)
            r2 = p_cols[1].selectbox("2순위 (3점)", options, index=1)
            r3 = p_cols[2].selectbox("3순위 (2점)", options, index=2)
            r4 = p_cols[3].selectbox("4순위 (1점)", options, index=3)

    # 랭킹 점수 계산 
    w = {r1: 4, r2: 3, r3: 2, r4: 1}
    df['total_score'] = (df['norm_월세'] * w.get("저렴한 월세", 0) + 
                         df['norm_물가'] * w.get("생활 물가", 0) + 
                         df['norm_문화'] * w.get("문화 공간", 0) + 
                         df['norm_공원'] * w.get("녹지 시설", 0))

    filtered_df = df.copy()
    if selected_line != "전체":
        filtered_df = filtered_df[filtered_df['지하철호선'].str.contains(selected_line)]

    top_3 = filtered_df.sort_values('total_score', ascending=False).head(3)['자치구'].tolist()
    filtered_df['rank_label'] = filtered_df['자치구'].apply(lambda x: f"{top_3.index(x)+1}위" if x in top_3 else "기타")

    col_map, col_top = st.columns([1.5, 1])
    with col_map:
        st.subheader("🗺️ 추천 지역 맵")
        fig = px.choropleth_mapbox(
            filtered_df, geojson=seoul_geo, locations='자치구', featureidkey="properties.name",
            color='rank_label',
            color_discrete_map={"1위": "#FF4B4B", "2위": "#FFAA00", "3위": "#FFD700", "기타": "#E0E0E0"},
            mapbox_style="carto-positron", zoom=10, center={"lat": 37.563, "lon": 126.986}, opacity=0.7, height=500
        )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_traces(selectedpoints=None)
        
        select_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
        if select_event and select_event.selection and select_event.selection.points:
            st.session_state.selected_gu = select_event.selection.points[0]['location']

    with col_top:
        st.subheader("🏆 TOP 3 추천")
        for i, gu_name in enumerate(top_3):
            gu_row = df[df['자치구'] == gu_name].iloc[0]
            st.info(f"**{i+1}위: {gu_name}** \n월세 {gu_row['평균월세']}만원 | {gu_row['한줄평']}")

# ── Tab 2: 자치구 심층 분석 (예다은 수치 분석 적용) ──
with tab2:
    gu = st.session_state.selected_gu
    row = df[df['자치구'] == gu].iloc[0]
    
    st.markdown(f'<div class="gu-header"><h2>{gu} 심층 리포트</h2><p>「 {row["한줄평"]} 」</p></div>', unsafe_allow_html=True)
    
    def get_diff(val, avg, is_cost=True):
        diff = ((val - avg) / avg) * 100
        label = "저렴 🔹" if diff < 0 else "비쌈 🔺"
        if not is_cost: label = "많음 🔺" if diff > 0 else "적음 🔹"
        return f"평균 대비 {abs(diff):.1f}% {label}"

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(f'<div class="metric-box"><small>평균 월세</small><br><strong>{row["평균월세"]}만원</strong><br><small>{get_diff(row["평균월세"], seoul_avg["평균월세"])}</small></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-box"><small>공원 수</small><br><strong>{row["공원수"]}개</strong><br><small>{get_diff(row["공원수"], seoul_avg["공원수"], False)}</small></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-box"><small>도서관 수</small><br><strong>{row["도서관수"]}개</strong><br><small>{get_diff(row["도서관수"], seoul_avg["도서관수"], False)}</small></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-box"><small>문화공간</small><br><strong>{int(row["기타문화공간"])}개</strong><br><small>{get_diff(row["기타문화공간"], seoul_avg["기타문화공간"], False)}</small></div>', unsafe_allow_html=True)

    st.write("")
    radar_col, line_col = st.columns([1, 1])
    with radar_col:
        st.write("📊 인프라 밸런스")
        fig_radar = go.Figure(go.Scatterpolar(
            r=[row['norm_월세'], row['norm_물가'], row['norm_문화'], row['norm_공원']],
            theta=['월세가성비', '물가가성비', '문화시설', '녹지시설'], fill='toself', line_color='#253F52'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), height=350)
        st.plotly_chart(fig_radar, use_container_width=True)
    with line_col:
        st.write("🚇 이용 가능 호선")
        lines = row['지하철호선'].split(',')
        for l in lines:
            st.button(f"{l}호선", key=f"btn_{l}", disabled=True)
        st.success(f"현재 선택된 {gu}는 이사를 고려하기에 **{'안정적인' if row['total_score'] > 10 else '무난한'}** 선택지입니다.")

# ── Tab 3: 1:1 지역 비교 (윤나경 비교 시스템) ── 
with tab3:
    st.subheader("⚖️ 비교하고 싶은 두 지역을 고르세요")
    c_sel1, c_sel2 = st.columns(2)
    gu_a = c_sel1.selectbox("지역 A", df['자치구'], index=22)
    gu_b = c_sel2.selectbox("지역 B", df['자치구'], index=0)
    
    r_a, r_b = df[df['자치구'] == gu_a].iloc[0], df[df['자치구'] == gu_b].iloc[0]
    
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Scatterpolar(r=[r_a['norm_월세'], r_a['norm_물가'], r_a['norm_문화'], r_a['norm_공원']],
                                       theta=['월세','물가','문화','녹지'], fill='toself', name=gu_a))
    fig_comp.add_trace(go.Scatterpolar(r=[r_b['norm_월세'], r_b['norm_물가'], r_b['norm_문화'], r_b['norm_공원']],
                                       theta=['월세','물가','문화','녹지'], fill='toself', name=gu_b))
    st.plotly_chart(fig_comp, use_container_width=True)
    
    st.table(pd.DataFrame({
        "항목": ["평균 월세", "생활 물가", "전체 문화공간", "공원 수"],
        gu_a: [f"{r_a['평균월세']}만원", f"{r_a['생활물가']:,}원", f"{r_a['전체문화공간']}개", f"{r_a['공원수']}개"],
        gu_b: [f"{r_b['평균월세']}만원", f"{r_b['생활물가']:,}원", f"{r_b['전체문화공간']}개", f"{r_b['공원수']}개"]
    }))

# ── Tab 4: 자취 체크리스트 (예다은 유틸리티 적용) ──
with tab4:
    st.subheader("✅ 방 보러 가기 전 필수 체크!")
    checklist = [
        "등본 확인 (전입 가능 여부)", "곰팡이 및 결로 흔적", "수압 및 배수 상태",
        "밤길 가로등 및 치안", "관리비 포함 항목", "옵션 가전 상태"
    ]
    selected = []
    for item in checklist:
        if st.checkbox(item): selected.append(item)
    
    if st.button("체크리스트 결과 저장"):
        st.write("선택된 항목:", ", ".join(selected))
        st.download_button("결과 파일 다운로드", data="\n".join(selected), file_name="checklist.txt")
