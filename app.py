import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import json

# ══════════════════════════════════════════════════════════════════════════
# 페이지 설정 및 테마 정의
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="서울 스타터 v4.0", layout="wide", page_icon="🏠")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Bebas+Neue&display=swap');

/* ── 메인 폰트 및 배경 ── */
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

/* ── 타이틀 스타일 ── */
h1 { 
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 3px;
    font-size: 2.8rem !important;
    background: linear-gradient(45deg, #3590f3, #c2bbf0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ── 헤더 카드 (가운데 정렬) ── */
.gu-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 20px;
    padding: 30px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

/* ── 메트릭 박스 ── */
.metric-card {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# 데이터 로드 및 전처리
# ══════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_app_data():
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
            "인프라와 일자리 중심, 비용만큼 확실한 가치.", "한강 공원과 저렴한 물가, 쾌적한 주거 환경.", "맑은 공기와 정겨운 분위기가 매력적입니다.",
            "마곡의 성장과 함께 떠오르는 녹지 부자 동네.", "자취 생태계 1위, 최고의 가성비를 자랑합니다.", "대학가와 한강 공원의 에너지가 넘치는 곳.",
            "교통의 요지, 실속 있는 역세권 생활권입니다.", "직장인을 위한 실속형 자취 명당.", "안전하고 조용한 주택 밀집 지역입니다.",
            "서울에서 가장 착한 월세, 평화로운 생활.", "전통시장과 대학 상권이 어우러진 맛집 천국.", "사당과 노량진 사이, 직장인 스테디셀러.",
            "핫플레이스가 마당인 트렌디한 동네.", "활기와 고즈넉함이 공존하는 대학가.", "편리함과 예술적 품격을 모두 갖춘 곳.",
            "카페거리를 내 집처럼, 숲과 강이 만나는 곳.", "독립서점과 예술가들의 감성 동네.", "석촌호수와 롯데타워, 완벽한 주말 여가.",
            "정돈된 거리와 높은 치안, 깔끔한 삶.", "여의도 직주근접과 교통 허브의 중심.", "글로벌 문화와 이색적인 풍경이 펼쳐집니다.",
            "자연의 여유를 담은 친환경 주거지.", "예술이 일상이 되는 문화예술 1번지.", "어디든 연결되는 서울의 심장부.", "중랑천의 여유와 가성비 좋은 생활권."
        ]
    }
    df = pd.DataFrame(data)
    df['기기타문화공간'] = df['전체문화공간'] - df['도서관수']
    
    # 평균치 계산
    means = df[['평균월세', '생활물가', '공원수', '도서관수', '기기타문화공간']].mean()
    
    # 정규화 점수 (0~1)
    for col, high_is_good in [('평균월세', False), ('생활물가', False), ('전체문화공간', True), ('공원수', True)]:
        mn, mx = df[col].min(), df[col].max()
        df[f'norm_{col}'] = (df[col] - mn) / (mx - mn) if high_is_good else (mx - df[col]) / (mx - mn)
    
    return df, means

@st.cache_data
def load_seoul_geo():
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/juso/2015/json/seoul_municipalities_geo_simple.json"
    return requests.get(url).json()

df, seoul_avg = load_app_data()
seoul_geo = load_seoul_geo()

# 세션 상태 초기화
if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '종로구'

# ══════════════════════════════════════════════════════════════════════════
# 메인 화면 및 탭 구성
# ══════════════════════════════════════════════════════════════════════════
st.title("🚀 SEOUL STARTER v4.0")

tab1, tab2 = st.tabs(["✨ 지역 큐레이션", "⚖️ 1:1 지역 비교"])

# ── 탭 1: 지역 큐레이션 및 명당 찾기 ──
with tab1:
    # 설정 영역
    with st.container(border=True):
        c_line, c_rank = st.columns([1, 2.5])
        with c_line:
            st.subheader("🚇 호선 선택")
            selected_line = st.selectbox("주요 이용 호선", ["전체"] + [str(i) for i in range(1, 10)])
        with c_rank:
            st.subheader("🔝 우선순위 설정")
            p_cols = st.columns(4)
            criteria = ["저렴한 월세", "낮은 물가", "문화 공간", "녹지 시설"]
            r1 = p_cols[0].selectbox("1순위 (4점)", criteria, index=0)
            r2 = p_cols[1].selectbox("2순위 (3점)", criteria, index=1)
            r3 = p_cols[2].selectbox("3순위 (2점)", criteria, index=2)
            r4 = p_cols[3].selectbox("4순위 (1점)", criteria, index=3)

    # 추천 로직
    weights = {r1: 4, r2: 3, r3: 2, r4: 1}
    df['total_score'] = (df['norm_평균월세'] * weights.get("저렴한 월세", 0) + 
                         df['norm_생활물가'] * weights.get("낮은 물가", 0) + 
                         df['norm_전체문화공간'] * weights.get("문화 공간", 0) + 
                         df['norm_공원수'] * weights.get("녹지 시설", 0))

    display_df = df.copy()
    if selected_line != "전체":
        display_df = display_df[display_df['지하철호선'].str.contains(selected_line)]

    top_3 = display_df.sort_values('total_score', ascending=False).head(3)['자치구'].tolist()
    display_df['recommendation'] = display_df['자치구'].apply(
        lambda x: f"{top_3.index(x)+1}위 추천" if x in top_3 else "기타 지역"
    )

    col_map, col_info = st.columns([1.5, 1])

    with col_map:
        st.subheader("🗺️ 서울시 추천 지역 맵")
        st.caption("지도 위의 자치구를 클릭하면 우측 상세 정보가 업데이트됩니다.")
        
        fig = go.Figure(go.Choroplethmapbox(
            geojson=seoul_geo,
            locations=display_df['자치구'],
            z=display_df['total_score'],
            featureidkey="properties.name",
            colorscale="Blues",
            marker_opacity=0.6,
            marker_line_width=1,
            text=display_df['자치구'],
            hoverinfo="text"
        ))
        
        # 상위 3위 강조
        for i, target_gu in enumerate(top_3):
            color = ["#FF4B4B", "#FFAA00", "#FFD700"][i]
            gu_geo = [f for f in seoul_geo['features'] if f['properties']['name'] == target_gu]
            if gu_geo:
                fig.add_trace(go.Choroplethmapbox(
                    geojson={'type': 'FeatureCollection', 'features': gu_geo},
                    locations=[target_gu], z=[1], featureidkey="properties.name",
                    colorscale=[[0, color], [1, color]], showscale=False,
                    text=f"⭐ {i+1}위: {target_gu}", hoverinfo="text"
                ))

        fig.update_layout(
            mapbox_style="carto-positron", mapbox_zoom=10,
            mapbox_center={"lat": 37.565, "lon": 126.985},
            margin={"r":0,"t":0,"l":0,"b":0}, height=600
        )
        fig.update_traces(selectedpoints=None)
        
        select_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
        if select_event and select_event.selection and select_event.selection.points:
            st.session_state.selected_gu = select_event.selection.points[0]['location']

    with col_info:
        gu = st.session_state.selected_gu
        row = df[df['자치구'] == gu].iloc[0]
        
        st.markdown(f"""
        <div class="gu-header">
            <h2 style="margin: 0; letter-spacing: 2px;">{gu}</h2>
            <p style="font-size: 1.1em; color: #ECF0F1; margin-top: 10px; font-style: italic;">「 {row['한줄평']} 」</p>
        </div>
        """, unsafe_allow_html=True)
        
        def calc_comp(val, avg, is_cost=False):
            diff = ((val - avg) / avg) * 100
            if is_cost: label = "저렴 🔹" if diff < 0 else "비쌈 🔺"
            else: label = "많음 🔺" if diff > 0 else "적음 🔹"
            return f"평균 대비 {abs(diff):.1f}% {label}"

        m_cols = st.columns(2)
        with m_cols[0]:
            st.markdown(f"""<div class="metric-card"><small>평균 월세</small><br><strong>{row['평균월세']}만원</strong><br>
                <small style="font-size:0.8em; color:#555;">{calc_comp(row['평균월세'], seoul_avg['평균월세'], True)}</small></div>""", unsafe_allow_html=True)
        with m_cols[1]:
            st.markdown(f"""<div class="metric-card"><small>공원 수</small><br><strong>{row['공원수']}개</strong><br>
                <small style="font-size:0.8em; color:#555;">{calc_comp(row['공원수'], seoul_avg['공원수'])}</small></div>""", unsafe_allow_html=True)

        st.write("")
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[row['norm_평균월세'], row['norm_생활물가'], row['norm_전체문화공간'], row['norm_공원수']],
            theta=['월세가성비', '물가가성비', '문화시설', '녹지시설'], fill='toself', line_color='#3590f3'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), height=300, margin=dict(t=30, b=20))
        st.plotly_chart(fig_radar, use_container_width=True)

# ── 탭 2: 1:1 지역 비교 모드 ──
with tab2:
    st.subheader("⚖️ 두 자치구의 정주 여건 비교")
    st.write("비교하고 싶은 두 지역을 선택하여 인프라 밸런스를 확인하세요.")
    
    c_sel1, c_sel2 = st.columns(2)
    gu_a = c_sel1.selectbox("지역 A 선택", df['자치구'], index=22) # 종로구 기본
    gu_b = c_sel2.selectbox("지역 B 선택", df['자치구'], index=0)  # 강남구 기본
    
    row_a = df[df['자치구'] == gu_a].iloc[0]
    row_b = df[df['자치구'] == gu_b].iloc[0]
    
    # 지표 비교 테이블
    comparison_data = {
        '지표': ['월세(만원)', '생활물가(원)', '공원 수', '도서관 수', '전체문화공간'],
        gu_a: [row_a['평균월세'], row_a['생활물가'], row_a['공원수'], row_a['도서관수'], row_a['전체문화공간']],
        gu_b: [row_b['평균월세'], row_b['생활물가'], row_b['공원수'], row_b['도서관수'], row_b['전체문화공간']]
    }
    st.table(pd.DataFrame(comparison_data).set_index('지표'))
    
    # 레이더 차트 비교
    col_radar, col_bar = st.columns([1, 1.2])
    
    with col_radar:
        st.write("🔍 **인프라 밸런스 비교**")
        fig_comp_radar = go.Figure()
        fig_comp_radar.add_trace(go.Scatterpolar(
            r=[row_a['norm_평균월세'], row_a['norm_생활물가'], row_a['norm_전체문화공간'], row_a['norm_공원수']],
            theta=['월세', '물가', '문화', '녹지'], fill='toself', name=gu_a, line_color='#3590f3'
        ))
        fig_comp_radar.add_trace(go.Scatterpolar(
            r=[row_b['norm_평균월세'], row_b['norm_생활물가'], row_b['norm_전체문화공간'], row_b['norm_공원수']],
            theta=['월세', '물가', '문화', '녹지'], fill='toself', name=gu_b, line_color='#FF4B4B'
        ))
        fig_comp_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), height=400)
        st.plotly_chart(fig_comp_radar, use_container_width=True)

    with col_bar:
        st.write("💰 **월세 및 물가 비교**")
        fig_bar = go.Figure(data=[
            go.Bar(name=gu_a, x=['월세', '생활물가'], y=[row_a['평균월세'], row_a['생활물가']/100], marker_color='#3590f3'),
            go.Bar(name=gu_b, x=['월세', '생활물가'], y=[row_b['평균월세'], row_b['생활물가']/100], marker_color='#FF4B4B')
        ])
        fig_bar.update_layout(barmode='group', height=400, yaxis_title="수치 (물가는 1/100 단위)")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.info(f"💡 **분석 결과:** {gu_a}는 {gu_b}에 비해 {'월세가 저렴함' if row_a['평균월세'] < row_b['평균월세'] else '인프라가 더 풍부함'} 등의 특징이 있습니다.")
