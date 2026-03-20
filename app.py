import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# --- 페이지 설정 ---
st.set_page_config(page_title="서울 스타터 v2.0", layout="wide", page_icon="🏠")

# --- 커스텀 CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Bebas+Neue&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 전체 배경색 유지 (Streamlit 기본) */
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* 상단 타이틀 */
h1 { 
    font-family: 'Bebas Neue', 'Noto Sans KR', sans-serif;
    letter-spacing: 2px;
    font-size: 2.6rem !important;
}

/* 지역 상세 카드 스타일 */
.gu-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 16px;
    padding: 20px 24px 16px;
    color: white;
    margin-bottom: 12px;
    border: 1px solid rgba(255,255,255,0.08);
}
.gu-header h2 {
    font-size: 2rem;
    font-weight: 900;
    margin: 0 0 6px 0;
    color: #fff;
}
.gu-tagline {
    font-size: 0.9rem;
    color: #aac4e0;
    line-height: 1.5;
    font-style: italic;
}

/* 메트릭 카드 */
.metric-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 12px;
}
.metric-card {
    background: linear-gradient(135deg, #e8f4fd, #d1ecf9);
    border-radius: 12px;
    padding: 14px 16px;
    border-left: 4px solid #2196F3;
}
.metric-card.green { background: linear-gradient(135deg, #e8f8f0, #c8efd8); border-left-color: #4CAF50; }
.metric-card.orange { background: linear-gradient(135deg, #fff3e0, #ffe0b2); border-left-color: #FF9800; }
.metric-card.purple { background: linear-gradient(135deg, #f3e5f5, #e1bee7); border-left-color: #9C27B0; }
.metric-card .label { font-size: 0.72rem; color: #555; font-weight: 500; margin-bottom: 3px; }
.metric-card .value { font-size: 1.35rem; font-weight: 700; color: #1a1a2e; }
.metric-card .sub { font-size: 0.7rem; color: #777; margin-top: 2px; }

/* 지하철 태그 */
.station-tags {
    display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px;
}
.station-tag {
    background: #1a1a2e;
    color: #aac4e0;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 500;
    border: 1px solid rgba(170,196,224,0.3);
}

/* 물가 배지 */
.price-badge {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    margin-bottom: 12px;
}
.price-badge.high { background: #fde8e8; color: #c0392b; border: 1px solid #e74c3c40; }
.price-badge.low  { background: #e8fde8; color: #1e8449; border: 1px solid #27ae6040; }

/* TOP 5 카드 */
.rank-card {
    border-radius: 14px;
    padding: 16px 14px;
    text-align: center;
    border: 2px solid transparent;
    transition: all 0.2s;
    cursor: pointer;
    height: 100%;
}
.rank-card.rank-1 { background: linear-gradient(135deg, #fff8e1, #ffe082); border-color: #ffc107; }
.rank-card.rank-2 { background: linear-gradient(135deg, #f5f5f5, #e0e0e0); border-color: #9e9e9e; }
.rank-card.rank-3 { background: linear-gradient(135deg, #fbe9e7, #ffccbc); border-color: #ff7043; }
.rank-card.rank-4, .rank-card.rank-5 { background: linear-gradient(135deg, #e8f4fd, #bbdefb); border-color: #64b5f6; }
.rank-num { font-size: 1.8rem; font-weight: 900; }
.rank-name { font-size: 1.1rem; font-weight: 700; margin: 4px 0; }
.rank-detail { font-size: 0.75rem; color: #555; line-height: 1.5; }
.rank-score { font-size: 0.7rem; background: rgba(0,0,0,0.08); border-radius: 8px; padding: 2px 8px; display: inline-block; margin-top: 6px; }

/* 우선순위 선택 안내 */
.priority-hint {
    background: linear-gradient(90deg, #e3f0ff, #f0e3ff);
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 0.8rem;
    color: #444;
    margin-top: 6px;
    border-left: 3px solid #6a85b6;
}
</style>
""", unsafe_allow_html=True)


# ── 지하철 호선별 역 데이터 ──────────────────────────────────────────────
LINE_STATIONS = {
    "1호선": ["서울역","시청","종각","종로3가","종로5가","동대문","신설동","청량리","회기","외대앞","광운대","석계","신이문","제기동","가산디지털단지","금천구청","독산","구일","구로","영등포","신도림","도림천","도봉산","방학","창동","녹천","월계","성북","노원","상계"],
    "2호선": ["강남","역삼","선릉","삼성","종합운동장","잠실","잠실나루","강변","구의","건대입구","뚝섬","성수","왕십리","상왕십리","신당","동대문역사문화공원","을지로4가","을지로3가","을지로입구","시청","충정로","아현","이대","신촌","홍대입구","합정","당산","영등포구청","대림","신도림","구로디지털단지","신림","서울대입구","낙성대","사당","방배","서초","교대","강남"],
    "3호선": ["지축","구파발","연신내","불광","녹번","홍제","무악재","독립문","경복궁","안국","종로3가","을지로3가","충무로","동대입구","약수","금호","옥수","압구정","신사","잠원","고속터미널","교대","남부터미널","양재","매봉","도곡","대치","학여울","대청","일원","수서","가락시장","경찰병원","오금"],
    "4호선": ["창동","쌍문","수유","미아","미아사거리","길음","성신여대입구","한성대입구","혜화","동대문","동대문역사문화공원","충무로","명동","회현","서울역","숙대입구","삼각지","신용산","이촌","동작","총신대입구","사당","남태령"],
    "5호선": ["방화","개화산","김포공항","송정","마곡","발산","우장산","화곡","까치산","신정","목동","오목교","양평","영등포구청","영등포시장","신길","여의도","여의나루","마포","공덕","애오개","충정로","서대문","광화문","종로3가","을지로4가","동대문역사문화공원","청구","신금호","행당","왕십리","마장","답십리","장한평","군자","아차산","광나루","천호","강동","길동","굽은다리","명일","고덕","상일동"],
    "6호선": ["응암","역촌","불광","독바위","연신내","구산","새절","증산","디지털미디어시티","월드컵경기장","마포구청","망원","합정","상수","광흥창","대흥","공덕","효창공원앞","삼각지","녹사평","이태원","한강진","버티고개","약수","청구","신당","동묘앞","창신","보문","안암","고려대","월곡","상월곡","돌곶이","석계","태릉입구","화랑대","봉화산","신내"],
    "7호선": ["장암","도봉산","수락산","마들","노원","중계","하계","공릉","태릉입구","먹골","중화","상봉","면목","사가정","용마산","중곡","군자","어린이대공원","건대입구","뚝섬유원지","청담","강남구청","학동","논현","반포","고속터미널","내방","이수","남성","숭실대입구","상도","장승배기","신대방삼거리","보라매","신풍","대림","가산디지털단지","철산","광명사거리","온수"],
    "8호선": ["암사","천호","강동구청","몽촌토성","잠실","석촌","송파","가락시장","문정","장지","복정","산성","남한산성입구","단대오거리","신흥","수진","모란"],
    "9호선": ["개화","김포공항","공항시장","신방화","마곡나루","양천향교","가양","증미","등촌","염창","신목동","선유도","당산","국회의사당","여의도","샛강","노량진","노들","흑석","동작","구반포","신반포","고속터미널","사평","신논현","언주","선정릉","삼성중앙","봉은사","종합운동장","삼전","석촌고분","석촌","송파나루","한성백제","올림픽공원","둔촌오륜","중앙보훈병원"],
}

# 역 → 구 매핑 (기존 데이터의 지하철역_예시 기반)
STATION_TO_GU = {
    "강남": "강남구", "역삼": "강남구", "선릉": "강남구", "삼성": "강남구",
    "천호": "강동구", "강동": "강동구", "강동구청": "강동구",
    "수유": "강북구", "미아": "강북구", "미아사거리": "강북구",
    "발산": "강서구", "화곡": "강서구", "마곡": "강서구", "마곡나루": "강서구", "까치산": "강서구", "우장산": "강서구",
    "서울대입구": "관악구", "신림": "관악구", "낙성대": "관악구",
    "건대입구": "광진구", "구의": "광진구", "강변": "광진구", "뚝섬유원지": "광진구", "광나루": "광진구", "아차산": "광진구",
    "신도림": "구로구", "구로": "구로구", "구로디지털단지": "구로구", "도림천": "구로구",
    "가산디지털단지": "금천구", "금천구청": "금천구",
    "노원": "노원구", "상계": "노원구", "중계": "노원구", "하계": "노원구",
    "창동": "도봉구", "방학": "도봉구", "도봉산": "도봉구",
    "회기": "동대문구", "청량리": "동대문구", "외대앞": "동대문구", "답십리": "동대문구", "장한평": "동대문구",
    "노량진": "동작구", "사당": "동작구", "동작": "동작구", "흑석": "동작구", "상도": "동작구",
    "홍대입구": "마포구", "망원": "마포구", "합정": "마포구", "마포": "마포구", "공덕": "마포구", "상수": "마포구",
    "신촌": "서대문구", "이대": "서대문구", "연희": "서대문구", "홍제": "서대문구", "녹번": "서대문구",
    "교대": "서초구", "양재": "서초구", "서초": "서초구", "방배": "서초구", "사평": "서초구",
    "성수": "성동구", "왕십리": "성동구", "옥수": "성동구", "금호": "성동구", "행당": "성동구",
    "성신여대입구": "성북구", "길음": "성북구", "한성대입구": "성북구", "안암": "성북구", "보문": "성북구",
    "잠실": "송파구", "가락시장": "송파구", "석촌": "송파구", "문정": "송파구", "송파": "송파구",
    "목동": "양천구", "오목교": "양천구", "신목동": "양천구",
    "여의도": "영등포구", "당산": "영등포구", "영등포": "영등포구", "대림": "영등포구", "신길": "영등포구",
    "이태원": "용산구", "한강진": "용산구", "삼각지": "용산구", "신용산": "용산구", "이촌": "용산구",
    "연신내": "은평구", "불광": "은평구", "구산": "은평구", "응암": "은평구",
    "혜화": "종로구", "종로3가": "종로구", "경복궁": "종로구", "안국": "종로구", "종각": "종로구",
    "명동": "중구", "을지로입구": "중구", "시청": "중구", "동대문": "중구", "충무로": "중구",
    "상봉": "중랑구", "중화": "중랑구", "망우": "중랑구",
}

# ── 데이터 ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    data = {
        '자치구': ['강남구','강동구','강북구','강서구','관악구','광진구','구로구','금천구','노원구','도봉구',
                  '동대문구','동작구','마포구','서대문구','서초구','성동구','성북구','송파구','양천구','영등포구',
                  '용산구','은평구','종로구','중구','중랑구'],
        '지하철역_예시': ['강남역,역삼역','천호역,강동역','수유역,미아역','발산역,화곡역','서울대입구역,신림역','건대입구역','신도림역,구로역','가산디지털단지역','노원역,상계역','창동역,도봉산역',
                        '회기역,청량리역','노량진역,사당역','홍대입구역,망원역','신촌역,연희역','교대역,양재역','왕십리역,성수역','성신여대입구역','잠실역,가락시장역','목동역,오목교역','여의도역,당산역',
                        '이태원역,한남역','연신내역,불광역','혜화역,종로3가역','명동역,을지로입구역','상봉역,중랑역'],
        '생활물가': [7361,5935,6424,6165,6629,7265,6021,6619,6837,6338,6384,6378,6705,6735,6680,6599,6973,7098,6593,6070,6978,6388,6702,6614,6687],
        '전체문화공간': [115,24,23,25,21,33,40,20,33,33,39,32,53,36,62,33,62,62,27,27,66,33,250,83,19],
        '도서관수': [17,10,7,9,5,8,13,4,10,10,10,9,6,4,9,7,14,12,10,6,4,8,9,8,6],
        '공원수': [7,7,3,10,2,2,4,4,2,6,4,7,5,4,6,5,3,7,5,5,2,7,12,6,5],
        '평균월세': [95,72,62,68,60,78,63,58,60,55,68,75,85,70,92,80,65,88,70,75,82,63,75,78,60],
        '한줄평': [
            "화려한 도시 라이프의 중심, 높은 비용만큼 확실한 인프라.",
            "한강과 인접한 쾌적한 주거환경, 장보기 물가가 가장 저렴해요.",
            "북한산 자락의 맑은 공기, 정겨운 동네 분위기를 느낄 수 있습니다.",
            "마곡지구의 성장과 함께 떠오르는 녹지 부자 동네.",
            "청년들의 성지, 저렴한 물가와 활기찬 에너지가 가득합니다.",
            "대학가와 한강 공원을 동시에 누리는 젊은 주거지.",
            "사통팔달 교통의 요지, 가성비 좋은 역세권 매물이 많습니다.",
            "G밸리 직장인들을 위한 실속형 자취 명당.",
            "교육열만큼이나 안전하고 조용한 주택 밀집 지역.",
            "서울에서 가장 낮은 월세, 조용한 삶을 원하는 분께 추천.",
            "전통시장과 대학가가 어우러진 맛집 천국.",
            "노량진과 사당을 잇는 공무원·직장인 최선호 지역.",
            "트렌디한 카페와 핫플레이스가 집 앞마당인 곳.",
            "신촌의 활기와 연희동의 고즈넉함이 공존하는 동네.",
            "강남의 편리함에 예술적 품격을 더한 고급 주거지.",
            "성수동 카페거리를 내 집처럼, 숲과 강이 만나는 곳.",
            "개성 넘치는 독립서점과 대학 문화가 살아있는 동네.",
            "석촌호수와 롯데타워, 완벽한 주말 여가를 보장합니다.",
            "안전한 치안과 깔끔한 거리, 정돈된 삶을 꿈꾼다면.",
            "여의도 직주근접의 정석, 쇼핑과 교통의 허브.",
            "글로벌한 문화와 이색적인 풍경이 펼쳐지는 곳.",
            "은평한옥마을처럼 여유롭고 자연 친화적인 동네.",
            "문화예술 공간 밀집도 1위, 감성이 일상이 되는 곳.",
            "서울의 심장, 어디든 갈 수 있는 최고의 교통지.",
            "중랑천 산책로와 가성비 좋은 생활권이 강점입니다."
        ],
        'lat': [37.4959,37.5492,37.6469,37.5658,37.4654,37.5481,37.4954,37.4601,37.6544,37.6659,37.5838,37.5029,37.5623,37.5820,37.4769,37.5506,37.6061,37.5048,37.5271,37.5206,37.5311,37.6176,37.5991,37.5579,37.5954],
        'lon': [127.0664,127.1465,127.0147,126.8223,126.9436,127.0857,126.8581,126.9002,127.0772,127.0318,127.0507,126.9427,126.9088,126.9356,127.0122,127.0409,127.0232,127.1145,126.8565,126.9139,126.9811,126.9227,126.9861,126.9942,127.0922]
    }
    df = pd.DataFrame(data)
    avg_price = df['생활물가'].mean()
    df['물가비율'] = ((df['생활물가'] / avg_price) - 1) * 100
    for col, high_is_good in [('평균월세', False), ('생활물가', False), ('전체문화공간', True), ('공원수', True)]:
        mn, mx = df[col].min(), df[col].max()
        df[f'norm_{col}'] = (df[col] - mn)/(mx-mn) if high_is_good else (mx-df[col])/(mx-mn)
    return df

df = load_data()

# ── 세션 상태 ─────────────────────────────────────────────────────────────
if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '마포구'

# ── 우선순위 항목 ─────────────────────────────────────────────────────────
PRIORITY_ITEMS = {
    "💰 월세 저렴": "norm_평균월세",
    "🛒 물가 저렴": "norm_생활물가",
    "🎨 문화시설": "norm_전체문화공간",
    "🌳 녹지/공원": "norm_공원수",
}

# ─────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────
st.title("🚀 서울 스타터 v2.0 : 당신의 첫 자취 명당 찾기")
st.caption("20~30대를 위한 서울 자취 지역 추천 가이드")

# ─────────────────────────────────────────────────────────────────────────
# TOP CONTROL PANEL
# ─────────────────────────────────────────────────────────────────────────
with st.container(border=True):
    col_left, col_right = st.columns([1, 1.6])

    # ── 호선 선택 ──
    with col_left:
        st.subheader("🚉 지하철 호선으로 찾기")
        line_options = ["선택 안 함"] + list(LINE_STATIONS.keys())
        selected_line = st.selectbox("호선을 선택하세요", line_options, key="line_select")

        if selected_line != "선택 안 함":
            stations_in_line = LINE_STATIONS[selected_line]
            selected_station = st.selectbox("역을 선택하세요", ["선택 안 함"] + stations_in_line, key="station_select")
            if selected_station != "선택 안 함":
                if selected_station in STATION_TO_GU:
                    st.session_state.selected_gu = STATION_TO_GU[selected_station]
                    st.success(f"📍 {selected_station}역 → **{st.session_state.selected_gu}** 로 이동!")
                else:
                    st.info("해당 역의 자치구 정보를 찾는 중...")

    # ── 우선순위 설정 ──
    with col_right:
        st.subheader("⚖️ 주거 우선순위 설정 (1순위 ~ 4순위)")
        st.markdown('<div class="priority-hint">💡 가장 중요한 것을 1순위로 놓으세요. 순위에 따라 추천 지역이 달라집니다.</div>', unsafe_allow_html=True)

        priority_keys = list(PRIORITY_ITEMS.keys())
        p_cols = st.columns(4)
        used = []
        priority_order = []
        valid = True

        for rank in range(1, 5):
            with p_cols[rank - 1]:
                st.markdown(f"**{rank}순위**")
                remaining = [k for k in priority_keys if k not in used]
                choice = st.selectbox(
                    f"#{rank}",
                    options=["선택"] + remaining,
                    key=f"prio_{rank}",
                    label_visibility="collapsed"
                )
                if choice != "선택":
                    used.append(choice)
                    priority_order.append(choice)
                else:
                    valid = False

# ── 점수 계산 ────────────────────────────────────────────────────────────
weights = {4: 4, 3: 3, 2: 2, 1: 1}  # 1순위=4점, 4순위=1점
if len(priority_order) == 4:
    df['total_score'] = sum(
        df[PRIORITY_ITEMS[item]] * weights[4 - idx]
        for idx, item in enumerate(priority_order)
    )
else:
    # 기본: 균등 가중치
    df['total_score'] = sum(df[v] for v in PRIORITY_ITEMS.values()) / 4

recommended_df = df.sort_values('total_score', ascending=False).reset_index(drop=True)
top3_gu = recommended_df.head(3)['자치구'].tolist()

# ─────────────────────────────────────────────────────────────────────────
# MAIN: 지도 + 상세 정보
# ─────────────────────────────────────────────────────────────────────────
col_map, col_info = st.columns([1.6, 1])

with col_map:
    st.subheader("📍 서울 자치구 추천 지도")

    # 색상 레이블 지정
    def get_color_label(gu):
        if gu == top3_gu[0]: return "🥇 1위 추천"
        elif gu == top3_gu[1]: return "🥈 2위 추천"
        elif gu == top3_gu[2]: return "🥉 3위 추천"
        else: return "일반"

    df['추천등급'] = df['자치구'].apply(get_color_label)

    # 마커 크기: 상위 3개 강조
    df['marker_size'] = df['자치구'].apply(
        lambda g: 28 if g == top3_gu[0] else (22 if g == top3_gu[1] else (18 if g == top3_gu[2] else 10))
    )

    color_map = {
        "🥇 1위 추천": "#FF4136",
        "🥈 2위 추천": "#FF851B",
        "🥉 3위 추천": "#FFDC00",
        "일반": "#AAAAAA"
    }

    # ── GeoJSON 서울 자치구 경계 ──
    # 간략화된 서울 25개 자치구 GeoJSON 로드
    import urllib.request

    GEOJSON_URL = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json"

    @st.cache_data
    def load_geojson():
        try:
            with urllib.request.urlopen(GEOJSON_URL, timeout=5) as r:
                return json.loads(r.read().decode())
        except Exception:
            return None

    geojson = load_geojson()

    fig = go.Figure()

    # 1) 자치구 경계 Choropleth (GeoJSON 로드 성공 시)
    if geojson:
        # 점수 매핑
        score_map = dict(zip(df['자치구'], df['total_score']))
        top3_map = {top3_gu[0]: 3, top3_gu[1]: 2, top3_gu[2]: 1}

        # features의 name 키 확인 후 매핑
        for feat in geojson['features']:
            name = feat['properties'].get('name', feat['properties'].get('SIG_KOR_NM', ''))
            feat['properties']['name'] = name

        df['지도이름'] = df['자치구'].str.replace('구', '')  # GeoJSON key 맞춤용 (필요 시)

        fig.add_trace(go.Choroplethmapbox(
            geojson=geojson,
            locations=df['자치구'],
            z=df['total_score'],
            featureidkey="properties.name",
            colorscale=[
                [0.0, "rgba(200,220,255,0.3)"],
                [0.5, "rgba(100,160,255,0.5)"],
                [1.0, "rgba(30,90,200,0.7)"]
            ],
            showscale=False,
            marker_line_width=1.2,
            marker_line_color="rgba(80,80,80,0.6)",
            hovertemplate="<b>%{location}</b><br>추천점수: %{z:.2f}<extra></extra>",
        ))

        # 상위 3개 하이라이트 오버레이
        highlight_colors = {top3_gu[0]: "rgba(255,65,54,0.55)", top3_gu[1]: "rgba(255,133,27,0.5)", top3_gu[2]: "rgba(255,220,0,0.45)"}
        for gu_h, color_h in highlight_colors.items():
            df_h = df[df['자치구'] == gu_h]
            fig.add_trace(go.Choroplethmapbox(
                geojson=geojson,
                locations=df_h['자치구'],
                z=[1],
                featureidkey="properties.name",
                colorscale=[[0, color_h], [1, color_h]],
                showscale=False,
                marker_line_width=2.5,
                marker_line_color="rgba(255,255,255,0.9)",
                hoverinfo="skip",
            ))
    else:
        # GeoJSON 실패 시 scatter 대체
        st.info("지도 경계 데이터를 불러오는 중입니다. 마커 지도로 표시합니다.")

    # 2) 산점도 마커 (모든 구 레이블)
    for _, row_d in df.iterrows():
        gu_name = row_d['자치구']
        is_top = gu_name in top3_gu
        rank_icon = "🥇" if gu_name == top3_gu[0] else ("🥈" if gu_name == top3_gu[1] else ("🥉" if gu_name == top3_gu[2] else ""))
        fig.add_trace(go.Scattermapbox(
            lat=[row_d['lat']],
            lon=[row_d['lon']],
            mode="markers+text",
            marker=dict(
                size=row_d['marker_size'],
                color=color_map[row_d['추천등급']],
                opacity=0.92 if is_top else 0.55,
            ),
            text=[f"{rank_icon}{gu_name}" if is_top else gu_name],
            textposition="top center",
            textfont=dict(size=11 if is_top else 9, color="black" if is_top else "#555"),
            hovertemplate=f"<b>{gu_name}</b><br>추천점수: {row_d['total_score']:.2f}<br>평균월세: {row_d['평균월세']}만원<extra></extra>",
            showlegend=False,
            customdata=[gu_name],
        ))

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center={"lat": 37.5665, "lon": 126.978},
            zoom=10.3,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=530,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    select_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    if select_event and select_event.selection and select_event.selection.points:
        pt = select_event.selection.points[0]
        hover = pt.get('hovertext') or pt.get('text') or ''
        for gu_name in df['자치구'].tolist():
            if gu_name in hover:
                st.session_state.selected_gu = gu_name
                break

    # 범례 설명
    st.markdown("""
    <div style='display:flex;gap:18px;padding:6px 4px;font-size:0.8rem;color:#555;'>
        <span>🔴 1위 추천 &nbsp;&nbsp;</span>
        <span>🟠 2위 추천 &nbsp;&nbsp;</span>
        <span>🟡 3위 추천 &nbsp;&nbsp;</span>
        <span>⚫ 그 외 자치구</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────
# 우측: 자치구 상세 정보 (시각적으로 강조)
# ─────────────────────────────────────────────────────────────────────────
with col_info:
    gu = st.session_state.selected_gu
    row = df[df['자치구'] == gu].iloc[0]
    rank_in_top = top3_gu.index(gu) + 1 if gu in top3_gu else None
    rank_badge = {1: "🥇 1위 추천", 2: "🥈 2위 추천", 3: "🥉 3위 추천"}.get(rank_in_top, "")

    # ── 헤더 카드 ──
    st.markdown(f"""
    <div class="gu-header">
        <div style="font-size:0.8rem;color:#7eb8e0;margin-bottom:4px;">{rank_badge}</div>
        <h2>{gu}</h2>
        <div class="gu-tagline">「 {row['한줄평']} 」</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 물가 배지 ──
    if row['물가비율'] > 0:
        st.markdown(f'<div class="price-badge high">💸 생활물가 서울 평균 대비 +{abs(row["물가비율"]):.1f}% 높음 📈</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="price-badge low">💸 생활물가 서울 평균 대비 -{abs(row["물가비율"]):.1f}% 낮음 📉</div>', unsafe_allow_html=True)

    # ── 메트릭 그리드 ──
    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card blue">
            <div class="label">🏠 평균 월세</div>
            <div class="value">{row['평균월세']}만원</div>
            <div class="sub">원룸 기준 추정</div>
        </div>
        <div class="metric-card green">
            <div class="label">🌳 공원 수</div>
            <div class="value">{row['공원수']}개소</div>
            <div class="sub">도시공원 기준</div>
        </div>
        <div class="metric-card orange">
            <div class="label">📚 공공도서관</div>
            <div class="value">{row['도서관수']}개</div>
            <div class="sub">구립·시립 포함</div>
        </div>
        <div class="metric-card purple">
            <div class="label">🎨 기타 문화공간</div>
            <div class="value">{int(row['전체문화공간'] - row['도서관수'])}개</div>
            <div class="sub">영화관·공연장·전시관</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 추천 점수 바 ──
    score = row['total_score']
    max_score = df['total_score'].max()
    score_pct = int(score / max_score * 100)
    bar_color = "#e74c3c" if rank_in_top == 1 else ("#e67e22" if rank_in_top == 2 else ("#f1c40f" if rank_in_top == 3 else "#3498db"))
    st.markdown(f"""
    <div style="background:#f0f4f8;border-radius:12px;padding:14px 16px;margin-bottom:12px;">
        <div style="font-size:0.78rem;color:#666;margin-bottom:6px;font-weight:600;">✨ 종합 추천 점수</div>
        <div style="background:#ddd;border-radius:6px;height:12px;overflow:hidden;">
            <div style="width:{score_pct}%;background:{bar_color};height:100%;border-radius:6px;transition:width 0.5s;"></div>
        </div>
        <div style="text-align:right;font-size:0.8rem;color:#333;font-weight:700;margin-top:4px;">{score:.2f} / {max_score:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 주변 주요 역 ──
    st.markdown("**🚉 주변 주요역**")
    stations_html = "".join([f'<span class="station-tag">{s.strip()}</span>' for s in row['지하철역_예시'].split(',')])
    st.markdown(f'<div class="station-tags">{stations_html}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 다른 구 선택 버튼 ──
    st.markdown("**🗺️ 다른 자치구 바로 보기**")
    gu_list = df['자치구'].tolist()
    sel = st.selectbox("자치구 선택", gu_list, index=gu_list.index(gu), key="gu_direct", label_visibility="collapsed")
    if sel != gu:
        st.session_state.selected_gu = sel
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────
# 하단: 상위 5 추천
# ─────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🌟 우선순위 기반 추천 지역 TOP 5")

top5 = recommended_df.head(5)
rank_styles = ["rank-1","rank-2","rank-3","rank-4","rank-5"]
rank_emojis = ["🥇","🥈","🥉","4️⃣","5️⃣"]
rank_bg_colors = ["#fff8e1","#f5f5f5","#fbe9e7","#e8f4fd","#e8f4fd"]
rank_border_colors = ["#ffc107","#9e9e9e","#ff7043","#64b5f6","#64b5f6"]

cols_top = st.columns(5)
for i, (_, r) in enumerate(top5.iterrows()):
    with cols_top[i]:
        is_cur = r['자치구'] == st.session_state.selected_gu
        border_style = f"3px solid {rank_border_colors[i]}"
        box_shadow = "0 4px 16px rgba(0,0,0,0.12)" if is_cur else "none"
        st.markdown(f"""
        <div style="
            background:{rank_bg_colors[i]};
            border:{border_style};
            border-radius:14px;padding:16px 12px;text-align:center;
            box-shadow:{box_shadow};min-height:160px;">
            <div style="font-size:2rem;">{rank_emojis[i]}</div>
            <div style="font-size:1.05rem;font-weight:800;margin:5px 0 4px;">{r['자치구']}</div>
            <div style="font-size:0.78rem;color:#555;line-height:1.5;">
                💰 월세 {r['평균월세']}만원<br>
                🏆 추천점수 {r['total_score']:.2f}<br>
                🌳 공원 {r['공원수']}개·📚 도서관 {r['도서관수']}개
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"자세히 보기", key=f"btn_top_{i}", use_container_width=True):
            st.session_state.selected_gu = r['자치구']
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
st.caption("※ 본 데이터는 참고용 추정치입니다. 실제 월세 및 물가는 시기에 따라 다를 수 있습니다.")
