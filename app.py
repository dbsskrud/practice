import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

# ══════════════════════════════════════════════════════════════════════════
# 페이지 설정
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="서울 스타터: 서울시 자취 가이드", layout="wide", page_icon="🏠")

# ══════════════════════════════════════════════════════════════════════════
# 커스텀 CSS (Glassmorphism & Responsive Animations)
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css');

:root {
    --bg-main: #f0f4f8;
    --glass-bg: rgba(255, 255, 255, 0.75);
    --glass-border: rgba(255, 255, 255, 0.4);
    --col-main: #2979c8;
    --col-dark: #1a5499;
    --soft-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
    --accent-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.15);
}

/* 전역 폰트 설정 */
html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif !important;
    background: #ffffff !important;
}

.block-container { padding-top:2.5rem; max-width:1280px; }

/* ── 글래스모피즘 카드 공통 ── */
.glass-card {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border) !important;
    border-radius: 20px !important;
    box-shadow: var(--soft-shadow);
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--accent-shadow);
    border: 1px solid rgba(41, 121, 200, 0.3) !important;
}

/* ── 입력 컨테이너 ── */
.input-panel {
    background: #f8fafd;
    border-radius: 24px;
    padding: 28px;
    margin-bottom: 30px;
    border: 1px solid #eef2f7;
}

/* ── 메트릭 카드 특화 ── */
.metric-card {
    padding: 20px;
    text-align: center;
    border-top: 4px solid var(--col-main) !important;
}

/* ── 섹션 라벨 ── */
.section-label {
    font-size: 0.75rem; font-weight: 800; color: #8aadcc;
    letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 12px;
    display: flex; align-items: center; gap: 10px;
}
.section-label::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, #eef2f7, transparent);
}

/* ── 버튼 애니메이션 ── */
.stButton > button {
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: scale(1.02);
}

/* 스크롤바 커스텀 */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e0; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# 데이터 로드 및 초기화 (기존 로직 유지)
# ══════════════════════════════════════════════════════════════════════════
@st.cache_data
def build_geojson():
    features = [
      {"type":"Feature","id":"강남구","properties":{"name":"강남구"},"geometry":{"type":"Polygon","coordinates":[[[127.0635,37.5172],[127.0531,37.4938],[127.0531,37.4792],[127.0707,37.4679],[127.0865,37.4679],[127.1054,37.4877],[127.1054,37.5023],[127.0865,37.5172],[127.0635,37.5172]]]}},
      {"type":"Feature","id":"강동구","properties":{"name":"강동구"},"geometry":{"type":"Polygon","coordinates":[[[127.1054,37.5023],[127.1054,37.4877],[127.1243,37.4795],[127.1710,37.4959],[127.1710,37.5413],[127.1243,37.5413],[127.1054,37.5310],[127.1054,37.5023]]]}},
      {"type":"Feature","id":"강북구","properties":{"name":"강북구"},"geometry":{"type":"Polygon","coordinates":[[[126.9882,37.6376],[126.9882,37.6225],[127.0071,37.6151],[127.0260,37.6151],[127.0449,37.6225],[127.0449,37.6526],[127.0260,37.6676],[126.9882,37.6676],[126.9882,37.6376]]]}},
      {"type":"Feature","id":"강서구","properties":{"name":"강서구"},"geometry":{"type":"Polygon","coordinates":[[[126.7930,37.5413],[126.7930,37.5188],[126.8308,37.5038],[126.8686,37.5038],[126.8875,37.5188],[126.8875,37.5863],[126.8497,37.5863],[126.8119,37.5713],[126.7930,37.5413]]]}},
      {"type":"Feature","id":"관악구","properties":{"name":"관악구"},"geometry":{"type":"Polygon","coordinates":[[[126.9005,37.4942],[126.9005,37.4642],[126.9383,37.4567],[126.9572,37.4567],[126.9761,37.4642],[126.9761,37.4942],[126.9383,37.5017],[126.9005,37.4942]]]}},
      {"type":"Feature","id":"광진구","properties":{"name":"광진구"},"geometry":{"type":"Polygon","coordinates":[[[127.0543,37.5685],[127.0543,37.5310],[127.0732,37.5310],[127.1054,37.5310],[127.1054,37.5610],[127.0732,37.5685],[127.0543,37.5685]]]}},
      {"type":"Feature","id":"구로구","properties":{"name":"구로구"},"geometry":{"type":"Polygon","coordinates":[[[126.8308,37.5263],[126.8308,37.4888],[126.8686,37.4738],[126.9005,37.4738],[126.9005,37.5038],[126.8686,37.5188],[126.8497,37.5263],[126.8308,37.5263]]]}},
      {"type":"Feature","id":"금천구","properties":{"name":"금천구"},"geometry":{"type":"Polygon","coordinates":[[[126.8686,37.4738],[126.8686,37.4413],[126.9005,37.4338],[126.9194,37.4338],[126.9194,37.4738],[126.9005,37.4888],[126.8686,37.4738]]]}},
      {"type":"Feature","id":"노원구","properties":{"name":"노원구"},"geometry":{"type":"Polygon","coordinates":[[[127.0449,37.6226],[127.0449,37.6376],[127.0638,37.6376],[127.0827,37.6526],[127.0827,37.6676],[127.0638,37.6751],[127.0260,37.6676],[127.0071,37.6526],[127.0260,37.6301],[127.0449,37.6226]]]}},
      {"type":"Feature","id":"도봉구","properties":{"name":"도봉구"},"geometry":{"type":"Polygon","coordinates":[[[127.0071,37.6376],[127.0071,37.6526],[127.0260,37.6676],[127.0449,37.6676],[127.0449,37.6826],[127.0260,37.6901],[126.9882,37.6826],[126.9882,37.6676],[127.0071,37.6376]]]}},
      {"type":"Feature","id":"동대문구","properties":{"name":"동대문구"},"geometry":{"type":"Polygon","coordinates":[[[127.0260,37.5760],[127.0260,37.5610],[127.0449,37.5535],[127.0638,37.5535],[127.0827,37.5610],[127.0827,37.5910],[127.0449,37.5985],[127.0260,37.5760]]]}},
      {"type":"Feature","id":"동작구","properties":{"name":"동작구"},"geometry":{"type":"Polygon","coordinates":[[[126.9194,37.5263],[126.9194,37.4888],[126.9572,37.4888],[126.9761,37.5038],[126.9761,37.5263],[126.9383,37.5338],[126.9194,37.5263]]]}},
      {"type":"Feature","id":"마포구","properties":{"name":"마포구"},"geometry":{"type":"Polygon","coordinates":[[[126.8875,37.5788],[126.8875,37.5413],[126.9194,37.5338],[126.9572,37.5338],[126.9572,37.5638],[126.9383,37.5863],[126.9005,37.5863],[126.8875,37.5788]]]}},
      {"type":"Feature","id":"서대문구","properties":{"name":"서대문구"},"geometry":{"type":"Polygon","coordinates":[[[126.9194,37.5788],[126.9194,37.5638],[126.9383,37.5563],[126.9572,37.5563],[126.9761,37.5638],[126.9761,37.5938],[126.9572,37.6013],[126.9194,37.5938],[126.9194,37.5788]]]}},
      {"type":"Feature","id":"서초구","properties":{"name":"서초구"},"geometry":{"type":"Polygon","coordinates":[[[127.0071,37.5172],[127.0071,37.4792],[127.0260,37.4642],[127.0449,37.4642],[127.0638,37.4792],[127.0638,37.5172],[127.0260,37.5247],[127.0071,37.5172]]]}},
      {"type":"Feature","id":"성동구","properties":{"name":"성동구"},"geometry":{"type":"Polygon","coordinates":[[[127.0260,37.5685],[127.0260,37.5460],[127.0449,37.5385],[127.0638,37.5385],[127.0827,37.5460],[127.0827,37.5685],[127.0638,37.5760],[127.0260,37.5685]]]}},
      {"type":"Feature","id":"성북구","properties":{"name":"성북구"},"geometry":{"type":"Polygon","coordinates":[[[126.9761,37.6076],[126.9761,37.5863],[126.9950,37.5788],[127.0260,37.5788],[127.0449,37.5938],[127.0449,37.6226],[127.0260,37.6226],[126.9950,37.6076],[126.9761,37.6076]]]}},
      {"type":"Feature","id":"송파구","properties":{"name":"송파구"},"geometry":{"type":"Polygon","coordinates":[[[127.0827,37.5310],[127.0827,37.4885],[127.1054,37.4795],[127.1243,37.4795],[127.1243,37.5310],[127.1054,37.5310],[127.0827,37.5310]]]}},
      {"type":"Feature","id":"양천구","properties":{"name":"양천구"},"geometry":{"type":"Polygon","coordinates":[[[126.8308,37.5413],[126.8308,37.5113],[126.8497,37.5038],[126.8686,37.5038],[126.8875,37.5188],[126.8875,37.5413],[126.8686,37.5563],[126.8308,37.5413]]]}},
      {"type":"Feature","id":"영등포구","properties":{"name":"영등포구"},"geometry":{"type":"Polygon","coordinates":[[[126.9005,37.5338],[126.9005,37.5038],[126.9194,37.4963],[126.9383,37.4963],[126.9572,37.5038],[126.9572,37.5338],[126.9194,37.5488],[126.9005,37.5338]]]}},
      {"type":"Feature","id":"용산구","properties":{"name":"용산구"},"geometry":{"type":"Polygon","coordinates":[[[126.9572,37.5563],[126.9572,37.5188],[126.9761,37.5113],[126.9950,37.5113],[127.0071,37.5263],[127.0071,37.5488],[126.9950,37.5638],[126.9572,37.5638],[126.9572,37.5563]]]}},
      {"type":"Feature","id":"은평구","properties":{"name":"은평구"},"geometry":{"type":"Polygon","coordinates":[[[126.9005,37.6376],[126.9005,37.5938],[126.9194,37.5863],[126.9572,37.5863],[126.9761,37.6076],[126.9761,37.6376],[126.9572,37.6526],[126.9194,37.6451],[126.9005,37.6376]]]}},
      {"type":"Feature","id":"종로구","properties":{"name":"종로구"},"geometry":{"type":"Polygon","coordinates":[[[126.9572,37.6151],[126.9572,37.5788],[126.9761,37.5713],[126.9950,37.5713],[127.0071,37.5863],[127.0071,37.6151],[126.9950,37.6301],[126.9572,37.6226],[126.9572,37.6151]]]}},
      {"type":"Feature","id":"중구","properties":{"name":"중구"},"geometry":{"type":"Polygon","coordinates":[[[126.9761,37.5713],[126.9761,37.5488],[126.9950,37.5413],[127.0071,37.5488],[127.0071,37.5713],[126.9950,37.5788],[126.9761,37.5713]]]}},
      {"type":"Feature","id":"중랑구","properties":{"name":"중랑구"},"geometry":{"type":"Polygon","coordinates":[[[127.0827,37.5985],[127.0827,37.5685],[127.1016,37.5610],[127.1205,37.5610],[127.1205,37.5985],[127.1016,37.6226],[127.0827,37.6226],[127.0827,37.5985]]]}}
    ]
    return {"type": "FeatureCollection", "features": features}

@st.cache_data
def load_data():
    data = {
        '자치구': [
            '강남구','강동구','강북구','강서구','관악구','광진구','구로구','금천구',
            '노원구','도봉구','동대문구','동작구','마포구','서대문구','서초구','성동구',
            '성북구','송파구','양천구','영등포구','용산구','은평구','종로구','중구','중랑구'
        ],
        '도서관수':       [17,10, 7, 9, 5, 8,13, 4,10,10,10, 9, 6, 4, 9, 7,14,12,10, 6, 4, 8, 9, 8, 6],
        '기타문화공간수': [80, 7,11,13,13,18,15,11,17,15,18,12,42,29,48,23,38,38,12,17,57,18,229,73, 8],
        '공원수':         [ 7, 7, 3,10, 2, 2, 4, 4, 2, 6, 4, 7, 5, 4, 6, 5, 3, 7, 5, 5, 2, 7,12, 6, 5],
        '평균물가':       [4979,4124,5138,5124,4791,6413,4645,5259,5022,5038,4208,4515,5330,5761,4685,5775,5120,6027,5401,4031,5010,4312,4995,5421,6218],
        '평균월세': [95,72,62,68,60,78,63,58,60,55,68,75,85,70,92,80,65,88,70,75,82,63,75,78,60],
        '지하철역_예시': [
            '삼성, 선릉, 역삼, 강남', '천호, 강동, 강동구청, 길동', '수유, 미아, 미아사거리', '방화, 발산, 마곡, 김포공항',
            '낙성대, 서울대입구, 봉천, 신림', '건대입구, 구의, 강변, 군자', '구로디지털단지, 신도림, 대림, 남구로', '가산디지털단지',
            '노원, 상계, 중계, 석계', '창동, 쌍문, 도봉산', '신설동, 청량리, 제기동, 동대문', '사당, 동작, 총신대입구, 이수',
            '합정, 홍대입구, 신촌, 공덕', '충정로, 홍제, 독립문, 서대문', '교대, 서초, 방배, 양재', '왕십리, 성수, 뚝섬, 한양대',
            '길음, 성신여대입구, 보문', '잠실, 잠실나루, 종합운동장, 석촌', '목동, 오목교, 양천구청', '문래, 당산, 영등포구청, 여의도',
            '삼각지, 신용산, 이태원, 한강진', '연신내, 불광, 구파발, 응암', '종각, 종로3가, 혜화, 안국', '시청, 을지로입구, 명동, 충무로', '봉화산, 신내, 중화, 상봉'
        ],
        '한줄평': [
            "화려한 도시 라이프의 중심.", "한강과 인접한 쾌적한 주거환경.", "북한산 자락의 정겨운 동네.", "마곡지구의 성장과 녹지 부자.",
            "청년들의 성지, 가성비 주거지.", "대학가와 한강을 동시에.", "사통팔달 교통의 요지.", "G밸리 직장인 명당.",
            "조용하고 안전한 주택 밀집 지역.", "서울 최저 월세, 실속파 추천.", "전통시장과 대학가 맛집 천국.", "공무원·직장인 최선호 지역.",
            "트렌디한 카페와 핫플이 집 앞.", "신촌의 활기와 고즈넉함의 공존.", "강남의 인프라와 예술적 품격.", "성수동 카페거리와 서울숲.",
            "독립서점과 대학 문화의 산실.", "석촌호수와 롯데타워의 여유.", "깔끔한 거리와 높은 치안.", "여의도 직주근접의 정석.",
            "글로벌 문화와 이색 풍경.", "여유롭고 자연 친화적인 동네.", "문화예술 공간 밀집도 1위.", "서울의 심장, 최강의 교통.", "가성비 생활권과 산책로."
        ],
        'lat': [37.4959,37.5492,37.6469,37.5658,37.4654,37.5481,37.4954,37.4601,37.6544,37.6659,37.5838,37.5029,37.5623,37.5820,37.4769,37.5506,37.6061,37.5048,37.5271,37.5206,37.5311,37.6176,37.5991,37.5579,37.5954],
        'lon': [127.0664,127.1465,127.0147,126.8223,126.9436,127.0857,126.8581,126.9002,127.0772,127.0318,127.0507,126.9427,126.9088,126.9356,127.0122,127.0409,127.0232,127.1145,126.8565,126.9139,126.9811,126.9227,126.9861,126.9942,127.0922],
    }
    df = pd.DataFrame(data)
    df['물가비율'] = ((df['평균물가'] / df['평균물가'].mean()) - 1) * 100
    for col, hi in [('평균월세', False), ('평균물가', False), ('기타문화공간수', True), ('공원수', True)]:
        mn, mx = df[col].min(), df[col].max()
        df[f'norm_{col}'] = (df[col]-mn)/(mx-mn) if hi else (mx-df[col])/(mx-mn)
    return df

df = load_data()
geojson = build_geojson()

# ────────────────────────────────────────────────────────
# ⚙️ 필터 옵션 및 사전 정의
# ────────────────────────────────────────────────────────
UNI_TO_GU = {"선택 안 함": [], "서울대학교": ["관악구","동작구"], "연세대학교": ["서대문구","마포구"], "고려대학교": ["성북구","동대문구"]}
WORK_TO_GU = {"선택 안 함": [], "강남역/테헤란로": ["강남구","서초구"], "여의도": ["영등포구","동작구"]}
RENT_BAND = {"상관없음": (0, 999), "60만원대 이하": (0, 69), "70-80만원대": (70, 89), "90만원대 이상": (90, 999)}
PRIORITY_ITEMS = {"💰 월세 저렴": "norm_평균월세", "🛒 물가 저렴": "norm_평균물가", "🎨 문화시설": "norm_기타문화공간수", "🌳 녹지/공원": "norm_공원수"}
LINE_STATIONS = {"1호선":['서울','시청','종각'], "2호선":['강남','역삼','선릉','잠실','홍대입구'], "9호선":['여의도','고속터미널']}

if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = "관악구"

# ══════════════════════════════════════════════════════════════════════════
# ① 타이틀 섹션
# ══════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div style="background:var(--main-gradient); border-radius:24px; padding:40px; margin-bottom:30px; color:white; box-shadow:var(--accent-shadow);">'
    '<div style="background:rgba(255,255,255,0.2); display:inline-block; padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:700; margin-bottom:15px;">PUBLIC DATA DASHBOARD v2.0</div>'
    '<h1 style="margin:0; font-size:2.8rem; font-weight:800; letter-spacing:-1.5px;">🏠 서울 스타터</h1>'
    '<p style="opacity:0.85; font-size:1.1rem; margin-top:10px;">처음 자취를 시작하는 당신을 위한 최적의 서울 자치구 큐레이션</p>'
    '</div>',
    unsafe_allow_html=True
)

# ══════════════════════════════════════════════════════════════════════════
# ② 컨트롤 패널 — 글래스모피즘 입력창
# ══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-label">⚙️ 검색 조건 설정</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1.2])
    
    with c1:
        st.markdown("##### 📍 목적지")
        university = st.selectbox("학교", list(UNI_TO_GU.keys()))
        work_place = st.selectbox("주요 업무지구", list(WORK_TO_GU.keys()))

    with c2:
        st.markdown("##### 💸 예산 및 교통")
        rent_band = st.selectbox("희망 월세", list(RENT_BAND.keys()))
        selected_lines = st.multiselect("선호 지하철", list(LINE_STATIONS.keys()))

    with c3:
        st.markdown("##### 🌟 주거 우선순위")
        prio_1 = st.selectbox("1순위 가치", list(PRIORITY_ITEMS.keys()), index=0)
        prio_2 = st.selectbox("2순위 가치", [k for k in PRIORITY_ITEMS.keys() if k != prio_1], index=0)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ── 점수 계산 (기존 로직) ──
df['total_score'] = df[PRIORITY_ITEMS[prio_1]] * 0.7 + df[PRIORITY_ITEMS[prio_2]] * 0.3
rec_df = df.sort_values('total_score', ascending=False).reset_index(drop=True)
top5_gu = rec_df.head(5)['자치구'].tolist()

# ══════════════════════════════════════════════════════════════════════════
# ③ 메인 대시보드 (지도 + 상세정보)
# ══════════════════════════════════════════════════════════════════════════
col_map, col_info = st.columns([1.6, 1])

with col_map:
    st.markdown('<div class="section-label">🗺️ 지역별 추천 분포</div>', unsafe_allow_html=True)
    
    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson,
        locations=df['자치구'],
        z=df['total_score'],
        featureidkey="properties.name",
        colorscale="Blues",
        marker_opacity=0.6,
        marker_line_width=1,
        hovertemplate="<b>%{location}</b><br>추천도: %{z:.2f}<extra></extra>"
    ))
    fig.update_layout(
        mapbox=dict(style="carto-positron", center={"lat": 37.5635, "lon": 126.987}, zoom=10),
        margin={"r":0,"t":0,"l":0,"b":0}, height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # 자치구 선택 버튼 (TOP 5)
    cols = st.columns(5)
    for i, g in enumerate(top5_gu):
        if cols[i].button(f"{i+1}위 {g}", use_container_width=True):
            st.session_state.selected_gu = g
            st.rerun()

with col_info:
    gu = st.session_state.selected_gu
    row = df[df['자치구'] == gu].iloc[0]
    
    st.markdown(f"""
    <div class="glass-card" style="padding:25px; border-top:6px solid var(--col-main) !important;">
        <div style="font-size:0.8rem; color:var(--col-main); font-weight:800; margin-bottom:5px;">SELECTED DISTRICT</div>
        <h2 style="margin:0; font-size:2rem; font-weight:800;">{gu}</h2>
        <p style="color:#666; font-style:italic; margin-bottom:20px;">"{row['한줄평']}"</p>
        <hr style="border:0; border-top:1px solid #eee; margin:20px 0;">
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
            <div class="metric-card glass-card">
                <div style="font-size:0.7rem; color:#888;">평균 월세</div>
                <div style="font-size:1.4rem; font-weight:800;">{row['평균월세']}만</div>
            </div>
            <div class="metric-card glass-card" style="border-top-color:#4a9de0 !important;">
                <div style="font-size:0.7rem; color:#888;">공원 수</div>
                <div style="font-size:1.4rem; font-weight:800;">{row['공원수']}개</div>
            </div>
        </div>
        <div style="margin-top:20px; background:rgba(41,121,200,0.05); padding:15px; border-radius:15px;">
            <div style="font-size:0.75rem; font-weight:700; color:var(--col-dark); margin-bottom:8px;">🚉 인근 주요역</div>
            <div style="font-size:0.85rem; color:#4a6d96;">{row['지하철역_예시']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# ④ 푸터: 데이터 출처
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="margin-top:50px; text-align:center; padding:20px; color:#aaa; font-size:0.75rem;">
    서울시 공공데이터 기반 (2024-2026) | 전월세 실거래가 및 문화공간 현황 반영<br>
    Designed with Glassmorphism UI
</div>
""", unsafe_allow_html=True)
