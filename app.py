import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# --- 페이지 설정 ---
st.set_page_config(page_title="서울 스타터 v3.0", layout="wide", page_icon="🗺️")

# --- 커스텀 CSS ---
st.markdown("""
<style>
    /* 전체 배경 흰색 */
    .stApp { background-color: #ffffff; }
    
    /* 메인 폰트 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Bebas+Neue&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

    /* 타이틀 */
    .main-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.8rem;
        color: #1a1a2e;
        letter-spacing: 3px;
        margin-bottom: 0;
    }
    .sub-title {
        color: #6c757d;
        font-size: 0.95rem;
        font-weight: 300;
        margin-top: 0;
    }

    /* 컨트롤 패널 */
    .control-panel {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 14px;
        padding: 22px 28px;
        margin-bottom: 20px;
    }
    .section-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #495057;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 10px;
    }

    /* 추천 카드 */
    .gu-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 24px;
        color: white;
        text-align: center;
        margin-bottom: 16px;
    }
    .gu-card h2 { margin: 0; font-size: 1.9rem; font-weight: 900; }
    .gu-card p  { margin: 10px 0 0; font-size: 0.9rem; color: #adb5bd; font-style: italic; line-height: 1.5; }

    /* 지표 카드 */
    .metric-card {
        border: 1.5px solid #e9ecef;
        border-radius: 12px;
        padding: 18px 14px;
        text-align: center;
        background: #fff;
        height: 100%;
    }
    .metric-label { color: #adb5bd; font-size: 0.78rem; font-weight: 500; margin-bottom: 6px; }
    .metric-value { font-size: 1.5rem; font-weight: 800; margin: 0; }

    /* 인프라 항목 */
    .infra-item {
        display: flex; align-items: center; gap: 10px;
        padding: 10px 14px;
        border-radius: 10px;
        background: #f8f9fa;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
    .infra-icon { font-size: 1.2rem; }
    .infra-text { color: #343a40; }
    .infra-val  { font-weight: 700; color: #1a1a2e; margin-left: auto; }

    /* 배지 */
    .rank-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }

    /* 순위 테이블 */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* 사이드 구분선 */
    hr { border-color: #e9ecef; }

    /* selectbox 스타일 정리 */
    .stSelectbox label { font-size: 0.78rem !important; color: #6c757d !important; font-weight: 500 !important; }
</style>
""", unsafe_allow_html=True)

# --- 데이터 로드 ---
@st.cache_data
def load_data():
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
            "트렌디한 인프라와 압도적 일자리, 비용만큼 확실한 가치.",
            "한강 공원과 저렴한 물가, 쾌적한 주거의 정석.",
            "자연과 정겨운 동네 풍경, 여유로운 삶이 가능합니다.",
            "서울 식물원과 마곡의 인프라, 녹지 부자 동네.",
            "청년들의 성지, 가장 활발한 자취 생태계와 가성비.",
            "대학가와 건대 상권, 활기찬 2030의 주거지.",
            "사통팔달의 교통 허브, 실속 있는 역세권 생활권.",
            "G밸리 직장인을 위한 가성비 끝판왕 자취 명당.",
            "깔끔한 아파트 단지와 치안, 공부와 휴식에 최적화.",
            "서울에서 가장 착한 월세, 조용하고 평화로운 동네.",
            "전통시장과 대학 상권의 완벽한 조화, 먹거리 천국.",
            "사당과 노량진 사이, 직장인들의 스테디셀러.",
            "연남, 망원 등 핫플레이스가 내 집 앞마당.",
            "신촌의 대학 문화와 연희동의 고즈넉함이 공존.",
            "강남의 편리함에 품격 있는 예술 인프라를 더함.",
            "서울의 브루클린, 성수동 카페거리를 내 집처럼.",
            "개성 넘치는 독립서점과 예술가들이 사랑하는 동네.",
            "석촌호수와 올림픽공원, 주말이 기다려지는 곳.",
            "정돈된 주거 환경과 높은 안전성, 깔끔한 생활권.",
            "여의도 직주근접과 쇼핑의 메카, 사통팔달 교통망.",
            "글로벌한 이색 문화와 남산 조망이 펼쳐지는 곳.",
            "은평 한옥마을의 고즈넉함과 자연의 여유.",
            "문화예술 1번지, 집 밖을 나서면 예술이 일상이 됨.",
            "서울의 심장부, 어디든 갈 수 있는 최고의 위치.",
            "중랑천의 여유와 가성비 좋은 생활 밀착형 주거지."
        ]
    }
    df = pd.DataFrame(data)
    avg_p = df['생활물가'].mean()
    df['물가비율'] = ((df['생활물가'] / avg_p) - 1) * 100

    for col, high_is_good in [('평균월세', False), ('생활물가', False), ('전체문화공간', True), ('공원수', True)]:
        mn, mx = df[col].min(), df[col].max()
        df[f'norm_{col}'] = (df[col] - mn) / (mx - mn) if high_is_good else (mx - df[col]) / (mx - mn)
    return df

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/juso/2015/json/seoul_municipalities_geo_simple.json"
    resp = requests.get(url, timeout=10)
    return resp.json()

df = load_data()
try:
    seoul_geojson = load_geojson()
    geojson_ok = True
except Exception:
    geojson_ok = False

if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '종로구'

# ===================== HEADER =====================
st.markdown('<p class="main-title">📍 서울 스타터 3.0</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">서울에서 처음 자취하는 2030을 위한 지역 추천 가이드</p>', unsafe_allow_html=True)

st.markdown("---")

# ===================== CONTROL PANEL =====================
st.markdown('<div class="control-panel">', unsafe_allow_html=True)

col_line, col_prio = st.columns([1, 3])

with col_line:
    st.markdown('<p class="section-label">🚇 지하철 호선으로 찾기</p>', unsafe_allow_html=True)
    all_lines = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    selected_line = st.selectbox(
        "주로 이용할 호선 선택",
        ["전체"] + all_lines,
        label_visibility="collapsed"
    )

with col_prio:
    st.markdown('<p class="section-label">🔝 주거 우선순위 설정 (드래그하듯 순서대로 선택)</p>', unsafe_allow_html=True)
    options = ["저렴한 월세", "생활 물가", "문화 공간", "녹지 시설"]
    p_cols = st.columns(4)
    labels = ["1순위 (4점)", "2순위 (3점)", "3순위 (2점)", "4순위 (1점)"]
    defaults = [0, 1, 2, 3]
    ranks = []
    for i, (pc, label, default) in enumerate(zip(p_cols, labels, defaults)):
        r = pc.selectbox(label, options, index=default, key=f"rank_{i}")
        ranks.append(r)
    rank1, rank2, rank3, rank4 = ranks

st.markdown('</div>', unsafe_allow_html=True)

# ===================== SCORING =====================
weight_map = {rank1: 4, rank2: 3, rank3: 2, rank4: 1}
# 중복 선택 처리: 같은 항목이 여러 순위에 있으면 최고 가중치 사용
final_weights = {}
for item, w in weight_map.items():
    final_weights[item] = max(final_weights.get(item, 0), w)

df['total_score'] = (
    df['norm_평균월세'] * final_weights.get("저렴한 월세", 1) +
    df['norm_생활물가'] * final_weights.get("생활 물가", 1) +
    df['norm_전체문화공간'] * final_weights.get("문화 공간", 1) +
    df['norm_공원수'] * final_weights.get("녹지 시설", 1)
)

filtered_df = df.copy()
if selected_line != "전체":
    filtered_df = filtered_df[filtered_df['지하철호선'].str.contains(selected_line)]

sorted_filtered = filtered_df.sort_values('total_score', ascending=False)
top_3_list = sorted_filtered.head(3)['자치구'].tolist()

rank_labels = {top_3_list[0]: "🥇 1위 추천", top_3_list[1]: "🥈 2위 추천", top_3_list[2]: "🥉 3위 추천"} if len(top_3_list) >= 3 else {}

def get_status(x):
    return rank_labels.get(x, "기타 지역")

filtered_df = filtered_df.copy()
filtered_df['status'] = filtered_df['자치구'].apply(get_status)

# ===================== MAIN LAYOUT =====================
col_map, col_info = st.columns([1.6, 1], gap="large")

# ---- 지도 ----
with col_map:
    st.markdown('<p class="section-label">🗺️ 서울시 자치구 추천 지도</p>', unsafe_allow_html=True)

    # 점수를 숫자로 매핑해서 색상 계층화
    filtered_df['색상순위'] = filtered_df['자치구'].apply(
        lambda x: 3 if x == top_3_list[0] else (2 if len(top_3_list)>1 and x == top_3_list[1] else (1 if len(top_3_list)>2 and x == top_3_list[2] else 0))
    )

    color_map = {
        "🥇 1위 추천": "#E63946",
        "🥈 2위 추천": "#F4A261",
        "🥉 3위 추천": "#2A9D8F",
        "기타 지역": "#CED4DA"
    }

    if geojson_ok:
        fig_map = px.choropleth_mapbox(
            filtered_df,
            geojson=seoul_geojson,
            locations='자치구',
            featureidkey="properties.name",
            color='status',
            color_discrete_map=color_map,
            mapbox_style="carto-positron",
            zoom=10,
            center={"lat": 37.563, "lon": 126.986},
            opacity=0.78,
            height=520,
            hover_data={'자치구': True, 'total_score': ':.2f', 'status': True}
        )
        fig_map.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            showlegend=True,
            legend=dict(
                title="추천 등급",
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#dee2e6",
                borderwidth=1,
                font=dict(size=12),
            ),
            paper_bgcolor="white",
            plot_bgcolor="white",
        )
        fig_map.update_traces(
            marker_line_color="white",
            marker_line_width=1.2,
        )
        select_event = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun")
        if select_event and select_event.selection and select_event.selection.points:
            clicked = select_event.selection.points[0].get('location') or select_event.selection.points[0].get('customdata', [None])[0]
            if clicked:
                st.session_state.selected_gu = clicked
    else:
        st.warning("GeoJSON 로드 실패. 네트워크 연결을 확인해 주세요.")

    # 지도 아래 TOP3 배지
    st.markdown("**현재 조건 기준 TOP 3 추천 지역구**")
    badge_cols = st.columns(3)
    badge_info = [
        ("🥇", top_3_list[0] if len(top_3_list) > 0 else "-", "#E63946"),
        ("🥈", top_3_list[1] if len(top_3_list) > 1 else "-", "#F4A261"),
        ("🥉", top_3_list[2] if len(top_3_list) > 2 else "-", "#2A9D8F"),
    ]
    for bc, (emoji, name, color) in zip(badge_cols, badge_info):
        bc.markdown(f"""
        <div style="text-align:center; padding:14px 8px; border-radius:12px; border: 2px solid {color}; background:#fff;">
            <div style="font-size:1.6rem;">{emoji}</div>
            <div style="font-size:1.1rem; font-weight:800; color:{color}; margin-top:4px;">{name}</div>
        </div>""", unsafe_allow_html=True)

# ---- 상세 정보 패널 ----
with col_info:
    gu = st.session_state.selected_gu
    if gu not in df['자치구'].values:
        gu = df['자치구'].iloc[0]
    row = df[df['자치구'] == gu].iloc[0]

    # 헤더 카드
    rank_text = rank_labels.get(gu, "")
    rank_badge_color = {"🥇 1위 추천": "#E63946", "🥈 2위 추천": "#F4A261", "🥉 3위 추천": "#2A9D8F"}.get(rank_text, "#6c757d")

    st.markdown(f"""
    <div class="gu-card">
        {'<span style="font-size:0.8rem; background:' + rank_badge_color + '; padding:4px 14px; border-radius:20px; font-weight:700;">' + rank_text + '</span>' if rank_text else ''}
        <h2 style="margin-top:12px;">{gu}</h2>
        <p>"{row['한줄평']}"</p>
    </div>
    """, unsafe_allow_html=True)

    # 핵심 지표 2개
    mc1, mc2 = st.columns(2)
    price_color = "#E63946" if row['물가비율'] > 0 else "#2A9D8F"
    price_text = "평균보다 높음 ↑" if row['물가비율'] > 0 else "평균보다 낮음 ↓"

    mc1.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💸 평균 월세</div>
        <div class="metric-value" style="color:#F4A261;">{row['평균월세']}만원</div>
    </div>""", unsafe_allow_html=True)

    mc2.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🛒 생활 물가</div>
        <div class="metric-value" style="color:{price_color};">{abs(row['물가비율']):.1f}%</div>
        <div style="font-size:0.75rem; color:{price_color}; margin-top:4px;">{price_text}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)

    # 인프라 리포트
    st.markdown('<p class="section-label">🏗️ 인프라 리포트</p>', unsafe_allow_html=True)
    infra_items = [
        ("📚", "공공 도서관", f"{row['도서관수']}개"),
        ("🎨", "전체 문화 공간", f"{row['전체문화공간']}개"),
        ("🌳", "주요 공원", f"{row['공원수']}개"),
        ("🚇", "운행 지하철 호선", f"{row['지하철호선']}호선"),
    ]
    for icon, label, val in infra_items:
        st.markdown(f"""
        <div class="infra-item">
            <span class="infra-icon">{icon}</span>
            <span class="infra-text">{label}</span>
            <span class="infra-val">{val}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)

    # 방사형 차트
    st.markdown('<p class="section-label">📊 종합 역량 분석</p>', unsafe_allow_html=True)
    categories = ['월세 가성비', '물가 가성비', '문화 시설', '녹지 시설']
    values = [row['norm_평균월세'], row['norm_생활물가'], row['norm_전체문화공간'], row['norm_공원수']]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(26,26,46,0.15)',
        line=dict(color='#1a1a2e', width=2.5),
        name=gu,
        marker=dict(size=7, color='#1a1a2e')
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor='#f8f9fa',
            radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=9), gridcolor='#dee2e6'),
            angularaxis=dict(tickfont=dict(size=11, color='#343a40'))
        ),
        height=270,
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white',
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ===================== 하단 랭킹 테이블 =====================
st.markdown("---")
st.markdown('<p class="section-label">🏆 조건별 전체 추천 순위</p>', unsafe_allow_html=True)

display_df = filtered_df[['자치구', 'status', '평균월세', '지하철호선', '생활물가', 'total_score']].sort_values('total_score', ascending=False).copy()
display_df.columns = ['자치구', '추천 등급', '평균월세(만원)', '지하철 호선', '생활물가(원)', '종합점수']
display_df['종합점수'] = display_df['종합점수'].round(3)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=340,
    column_config={
        "추천 등급": st.column_config.TextColumn("추천 등급", width="medium"),
        "종합점수": st.column_config.ProgressColumn("종합점수", min_value=0, max_value=display_df['종합점수'].max(), format="%.3f"),
    }
)

st.markdown("""
<div style="text-align:center; padding:24px 0 8px; color:#adb5bd; font-size:0.8rem;">
    서울 스타터 v3.0 · 데이터 기반 자취 지역 추천 · Made for Seoul's 2030
</div>
""", unsafe_allow_html=True)
