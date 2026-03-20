import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

# ══════════════════════════════════════════════════════════════════════════
# 페이지 설정
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="서울 스타터", layout="wide", page_icon="🏠")

# ══════════════════════════════════════════════════════════════════════════
# 커스텀 CSS — 미니멀 / 모노크롬 테마
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Playfair+Display:wght@700;900&display=swap');

:root {
    --bg:       #F8F7F4;
    --surface:  #FFFFFF;
    --border:   #E5E2DA;
    --accent:   #1A1A1A;
    --accent2:  #4A4A4A;
    --muted:    #9A9590;
    --highlight:#2563EB;
    --hl2:      #60A5FA;
    --hl3:      #BFDBFE;
    --green:    #059669;
    --red:      #DC2626;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: var(--bg) !important;
    color: var(--accent);
}

/* Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
.block-container {
    padding: 1.8rem 2.5rem 3rem;
    max-width: 1200px;
}

/* ── 헤더 배너 ── */
.banner {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    border-bottom: 2px solid var(--accent);
    padding-bottom: 1rem;
    margin-bottom: 1.8rem;
}
.banner-left h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.6rem !important;
    font-weight: 900 !important;
    color: var(--accent) !important;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin: 0 !important;
}
.banner-left p {
    font-size: 0.82rem;
    color: var(--muted);
    margin: 0.35rem 0 0;
    font-weight: 400;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.banner-right {
    font-size: 0.75rem;
    color: var(--muted);
    text-align: right;
    line-height: 1.7;
}

/* ── 컨트롤 패널 ── */
.ctrl-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.5rem;
}
.ctrl-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.6rem;
}

/* ── 지도 힌트 ── */
.map-hint {
    font-size: 0.78rem;
    color: var(--muted);
    padding: 0.5rem 0.8rem;
    border-left: 2px solid var(--highlight);
    background: #EFF6FF;
    border-radius: 0 6px 6px 0;
    margin-bottom: 0.8rem;
}

/* ── 상세 카드 헤더 ── */
.gu-header {
    background: var(--accent);
    color: #fff;
    border-radius: 12px;
    padding: 1.5rem 1.6rem 1.3rem;
    margin-bottom: 1rem;
}
.gu-rank-tag {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--hl2);
    margin-bottom: 0.4rem;
}
.gu-header h2 {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 900;
    color: #fff;
    margin: 0 0 0.4rem;
    line-height: 1.1;
}
.gu-tagline {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.65);
    font-style: italic;
    line-height: 1.5;
}

/* ── 물가 배지 ── */
.price-badge {
    display: inline-block;
    padding: 0.3rem 0.9rem;
    border-radius: 4px;
    font-size: 0.77rem;
    font-weight: 600;
    margin-bottom: 1rem;
    letter-spacing: 0.01em;
}
.price-badge.high { background: #FEF2F2; color: var(--red); border: 1px solid #FECACA; }
.price-badge.low  { background: #ECFDF5; color: var(--green); border: 1px solid #A7F3D0; }

/* ── 메트릭 그리드 ── */
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; }
.metric-card {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1rem;
}
.metric-card .mlabel {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.3rem;
}
.metric-card .mvalue {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1.2;
}
.metric-card .msub {
    font-size: 0.65rem;
    color: var(--muted);
    margin-top: 0.25rem;
    line-height: 1.5;
}
.mcomp {
    display: inline-block;
    margin-top: 0.4rem;
    padding: 0.15rem 0.55rem;
    border-radius: 3px;
    font-size: 0.65rem;
    font-weight: 700;
}
.mcomp.better  { background: #ECFDF5; color: var(--green); }
.mcomp.worse   { background: #FEF2F2; color: var(--red); }
.mcomp.neutral { background: var(--border); color: var(--muted); }

/* ── 점수 바 ── */
.score-bar-wrap {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1rem;
    margin-bottom: 10px;
}
.score-bar-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
}
.score-bar-bg { background: var(--border); border-radius: 3px; height: 8px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 3px; }
.score-bar-val {
    text-align: right;
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--accent);
    margin-top: 0.35rem;
}

/* ── 역 태그 ── */
.station-tags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 0.5rem; }
.station-tag {
    background: var(--accent);
    color: #fff;
    padding: 0.2rem 0.65rem;
    border-radius: 3px;
    font-size: 0.68rem;
    font-weight: 500;
}

/* ── TOP5 카드 ── */
.top5-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 0.8rem;
    text-align: center;
    transition: box-shadow 0.2s;
}
.top5-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.top5-card.active { border-color: var(--highlight); border-width: 2px; }

/* ── 우선순위 힌트 ── */
.priority-hint {
    font-size: 0.75rem;
    color: var(--muted);
    margin-bottom: 0.7rem;
    padding: 0.4rem 0.7rem;
    background: var(--bg);
    border-radius: 6px;
    border: 1px solid var(--border);
}

/* ── Streamlit overrides ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1.5px solid var(--border);
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--muted);
    padding: 0.5rem 1.1rem;
    background: transparent;
    border: none;
    border-radius: 0;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    background: transparent !important;
    border-bottom: 2px solid var(--accent) !important;
    font-weight: 700 !important;
}
div[data-testid="stHorizontalBlock"] > div { padding: 0 0.3rem; }
.stButton > button {
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--accent);
    padding: 0.4rem 0.6rem;
    transition: all 0.15s;
}
.stButton > button:hover {
    background: var(--accent);
    color: #fff;
    border-color: var(--accent);
}
.stSelectbox label, .stExpander summary { font-size: 0.82rem; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# 헤더
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="banner">
  <div class="banner-left">
    <h1>서울 스타터</h1>
    <p>첫 자취를 위한 서울 자치구 추천 가이드 · 실측 공공데이터 기반</p>
  </div>
  <div class="banner-right">
    도서관 215개 · 문화공간 862개<br>
    공원 130개 · 지하철 289역<br>
    물가 98,053건 (2024)
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# GeoJSON (내장)
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


# ══════════════════════════════════════════════════════════════════════════
# 실측 데이터
# ══════════════════════════════════════════════════════════════════════════
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
        '평균물가':       [
            4979,4124,5138,5124,4791,6413,4645,5259,5022,5038,
            4208,4515,5330,5761,4685,5775,5120,6027,5401,4031,
            5010,4312,4995,5421,6218
        ],
        '평균월세': [95,72,62,68,60,78,63,58,60,55,68,75,85,70,92,80,65,88,70,75,82,63,75,78,60],
        '지하철역_예시': [
            '삼성(2호선), 선릉(2호선), 역삼(2호선), 강남(2호선)',
            '천호(5호선), 강동(5호선), 강동구청(8호선), 길동(5호선)',
            '수유(4호선), 미아(4호선), 미아사거리(4호선)',
            '방화(5호선), 발산(5호선), 마곡(5호선), 김포공항(5호선)',
            '낙성대(2호선), 서울대입구(2호선), 봉천(2호선), 신림(2호선)',
            '건대입구(2호선), 구의(2호선), 강변(2호선), 군자(5호선)',
            '구로디지털단지(2호선), 신도림(2호선), 대림(2호선), 남구로(7호선)',
            '가산디지털단지(7호선)',
            '노원(4호선), 상계(4호선), 중계(7호선), 석계(6호선)',
            '창동(4호선), 쌍문(4호선), 도봉산(7호선)',
            '신설동(1호선), 청량리(1호선), 제기동(1호선), 동대문(4호선)',
            '사당(2호선), 동작(4호선), 총신대입구(4호선), 이수(7호선)',
            '합정(2호선), 홍대입구(2호선), 신촌(2호선), 공덕(5호선)',
            '충정로(2호선), 홍제(3호선), 독립문(3호선), 서대문(5호선)',
            '교대(2호선), 서초(2호선), 방배(2호선), 양재(3호선)',
            '왕십리(2호선), 성수(2호선), 뚝섬(2호선), 한양대(2호선)',
            '길음(4호선), 성신여대입구(4호선), 한성대입구(4호선), 보문(6호선)',
            '잠실(2호선), 잠실나루(2호선), 종합운동장(2호선), 석촌(8호선)',
            '목동(5호선), 오목교(5호선), 양천구청(2호선), 신정네거리(2호선)',
            '문래(2호선), 당산(2호선), 영등포구청(2호선), 여의도(5호선)',
            '삼각지(4호선), 신용산(4호선), 이태원(6호선), 한강진(6호선)',
            '연신내(3호선), 불광(3호선), 구파발(3호선), 응암(6호선)',
            '종각(1호선), 종로3가(1호선), 혜화(4호선), 안국(3호선)',
            '시청(1호선), 을지로입구(2호선), 명동(4호선), 충무로(4호선)',
            '봉화산(6호선), 신내(6호선), 중화(7호선), 상봉(7호선)',
        ],
        '한줄평': [
            "화려한 도시 라이프의 중심, 높은 비용만큼 확실한 인프라.",
            "한강과 인접한 쾌적한 주거환경, 서울에서 물가가 가장 저렴한 편.",
            "북한산 자락의 맑은 공기, 정겨운 동네 분위기를 느낄 수 있습니다.",
            "마곡지구의 성장과 함께 떠오르는 녹지 부자 동네.",
            "청년들의 성지, 저렴한 월세와 활기찬 에너지가 가득합니다.",
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
            "중랑천 산책로와 가성비 좋은 생활권이 강점입니다.",
        ],
        'lat': [
            37.4959,37.5492,37.6469,37.5658,37.4654,37.5481,37.4954,37.4601,
            37.6544,37.6659,37.5838,37.5029,37.5623,37.5820,37.4769,37.5506,
            37.6061,37.5048,37.5271,37.5206,37.5311,37.6176,37.5991,37.5579,37.5954
        ],
        'lon': [
            127.0664,127.1465,127.0147,126.8223,126.9436,127.0857,126.8581,126.9002,
            127.0772,127.0318,127.0507,126.9427,126.9088,126.9356,127.0122,127.0409,
            127.0232,127.1145,126.8565,126.9139,126.9811,126.9227,126.9861,126.9942,127.0922
        ],
    }
    df = pd.DataFrame(data)
    df['물가비율'] = ((df['평균물가'] / df['평균물가'].mean()) - 1) * 100
    for col, hi in [('평균월세', False), ('평균물가', False),
                    ('기타문화공간수', True), ('공원수', True)]:
        mn, mx = df[col].min(), df[col].max()
        df[f'norm_{col}'] = (df[col]-mn)/(mx-mn) if hi else (mx-df[col])/(mx-mn)
    return df


df      = load_data()
geojson = build_geojson()

AVG_RENT    = df['평균월세'].mean()
AVG_PARK    = df['공원수'].mean()
AVG_LIB     = df['도서관수'].mean()
AVG_CULTURE = df['기타문화공간수'].mean()


# ══════════════════════════════════════════════════════════════════════════
# 호선 / 역 데이터
# ══════════════════════════════════════════════════════════════════════════
LINE_STATIONS = {
    "1호선": ['서울','시청','종각','종로3가','종로5가','동대문','신설동','제기동','청량리','동묘앞'],
    "2호선": ['시청','을지로입구','을지로3가','을지로4가','동대문역사문화공원','신당','상왕십리','왕십리',
              '한양대','뚝섬','성수','건대입구','구의','강변','잠실나루','잠실','잠실새내','종합운동장',
              '삼성','선릉','역삼','강남','교대','서초','방배','사당','낙성대','서울대입구','봉천','신림',
              '신대방','구로디지털단지','대림','신도림','문래','영등포구청','당산','합정','홍대입구',
              '신촌','이대','아현','충정로','용답','신답','도림천','양천구청','신정네거리','용두'],
    "3호선": ['구파발','연신내','불광','녹번','홍제','무악재','독립문','경복궁','안국','종로3가',
              '을지로3가','충무로','동대입구','약수','금호','옥수','압구정','신사','잠원','고속터미널',
              '교대','남부터미널','양재','매봉','도곡','대치','학여울','대청','일원','수서',
              '가락시장','경찰병원','오금'],
    "4호선": ['불암산','상계','노원','창동','쌍문','수유','미아','미아사거리','길음',
              '성신여대입구','한성대입구','혜화','동대문','동대문역사문화공원','충무로',
              '명동','회현','서울','숙대입구','삼각지','신용산','이촌','동작','총신대입구',
              '사당','남태령'],
    "5호선": ['방화','개화산','김포공항','송정','마곡','발산','우장산','화곡','까치산','신정',
              '목동','오목교','양평','영등포구청','영등포시장','신길','여의도','여의나루',
              '마포','공덕','애오개','충정로','서대문','광화문','종로3가','을지로4가',
              '동대문역사문화공원','청구','신금호','행당','왕십리','마장','답십리','장한평',
              '군자','아차산','광나루','천호','강동','길동','굽은다리','명일','고덕','상일동',
              '둔촌동','올림픽공원','방이','개롱','거여','마천','강일'],
    "6호선": ['응암','역촌','독바위','구산','새절','증산','디지털미디어시티','월드컵경기장',
              '마포구청','망원','상수','광흥창','대흥','효창공원앞','녹사평','이태원','한강진',
              '버티고개','창신','보문','안암','고려대','월곡','상월곡','돌곶이','석계','태릉입구',
              '화랑대','봉화산','신내'],
    "7호선": ['도봉산','수락산','마들','중계','하계','공릉','먹골','중화','상봉','면목',
              '사가정','용마산','중곡','어린이대공원','자양','청담','강남구청','학동','논현',
              '반포','내방','이수','남성','숭실대입구','상도','장승배기','신대방삼거리',
              '보라매','신풍','남구로','가산디지털단지','천왕','온수'],
    "8호선": ['암사','암사역사공원역','강동구청','몽촌토성','석촌','송파','문정','장지','복정'],
    "9호선": ['언주','선정릉','삼성중앙','봉은사','삼전','석촌고분','송파나루','한성백제',
              '둔촌오륜','중앙보훈병원'],
}

STATION_TO_GU = {
    '서울':'중구','시청':'중구','종각':'종로구','종로3가':'종로구','종로5가':'종로구',
    '동대문':'동대문구','신설동':'동대문구','제기동':'동대문구','청량리':'동대문구','동묘앞':'종로구',
    '을지로입구':'중구','을지로3가':'중구','을지로4가':'중구',
    '동대문역사문화공원':'중구','신당':'중구','상왕십리':'성동구','왕십리':'성동구',
    '한양대':'성동구','뚝섬':'성동구','성수':'성동구','건대입구':'광진구','구의':'광진구','강변':'광진구',
    '잠실나루':'송파구','잠실':'송파구','잠실새내':'송파구','종합운동장':'송파구',
    '삼성':'강남구','선릉':'강남구','역삼':'강남구','강남':'강남구','교대':'서초구',
    '서초':'서초구','방배':'서초구','사당':'동작구','낙성대':'관악구','서울대입구':'관악구',
    '봉천':'관악구','신림':'관악구','신대방':'동작구','구로디지털단지':'구로구','대림':'구로구',
    '신도림':'구로구','문래':'영등포구','영등포구청':'영등포구','당산':'영등포구',
    '합정':'마포구','홍대입구':'마포구','신촌':'마포구','이대':'마포구','아현':'마포구',
    '충정로':'서대문구','용답':'성동구','신답':'성동구','도림천':'구로구',
    '양천구청':'양천구','신정네거리':'양천구','용두':'동대문구',
    '구파발':'은평구','연신내':'은평구','불광':'은평구','녹번':'은평구','홍제':'서대문구',
    '무악재':'서대문구','독립문':'서대문구','경복궁':'종로구','안국':'종로구',
    '충무로':'중구','동대입구':'중구','약수':'중구','금호':'성동구','옥수':'성동구',
    '압구정':'강남구','신사':'강남구','잠원':'서초구','고속터미널':'서초구',
    '남부터미널':'서초구','양재':'서초구','매봉':'강남구','도곡':'강남구','대치':'강남구',
    '학여울':'강남구','대청':'강남구','일원':'강남구','수서':'강남구',
    '가락시장':'송파구','경찰병원':'송파구','오금':'송파구',
    '불암산':'노원구','상계':'노원구','노원':'노원구','창동':'도봉구','쌍문':'도봉구',
    '수유':'강북구','미아':'강북구','미아사거리':'강북구','길음':'성북구',
    '성신여대입구':'성북구','한성대입구':'성북구','혜화':'종로구',
    '명동':'중구','회현':'중구','숙대입구':'용산구','삼각지':'용산구',
    '신용산':'용산구','이촌':'용산구','동작':'동작구','총신대입구':'동작구','남태령':'동작구',
    '방화':'강서구','개화산':'강서구','김포공항':'강서구','송정':'강서구','마곡':'강서구',
    '발산':'강서구','우장산':'강서구','화곡':'강서구','까치산':'강서구','신정':'양천구',
    '목동':'양천구','오목교':'양천구','양평':'영등포구','영등포시장':'영등포구',
    '신길':'영등포구','여의도':'영등포구','여의나루':'영등포구','마포':'마포구','공덕':'마포구',
    '애오개':'마포구','서대문':'서대문구','광화문':'종로구','청구':'성동구','신금호':'성동구',
    '행당':'성동구','마장':'성동구','답십리':'동대문구','장한평':'동대문구',
    '군자':'광진구','아차산':'광진구','광나루':'광진구','천호':'강동구','강동':'강동구',
    '길동':'강동구','굽은다리':'강동구','명일':'강동구','고덕':'강동구','상일동':'강동구',
    '둔촌동':'강동구','올림픽공원':'강동구','방이':'강동구','개롱':'강동구',
    '거여':'강동구','마천':'강동구','강일':'강동구',
    '응암':'은평구','역촌':'은평구','독바위':'은평구','구산':'은평구','새절':'은평구',
    '증산':'은평구','디지털미디어시티':'마포구','월드컵경기장':'마포구','마포구청':'마포구',
    '망원':'마포구','상수':'마포구','광흥창':'마포구','대흥':'마포구',
    '효창공원앞':'용산구','녹사평':'용산구','이태원':'용산구','한강진':'용산구',
    '버티고개':'용산구','창신':'종로구','보문':'성북구','안암':'성북구','고려대':'성북구',
    '월곡':'성북구','상월곡':'성북구','돌곶이':'성북구','석계':'노원구',
    '태릉입구':'노원구','화랑대':'노원구','봉화산':'중랑구','신내':'중랑구',
    '도봉산':'도봉구','수락산':'노원구','마들':'노원구','중계':'노원구','하계':'노원구',
    '공릉':'노원구','먹골':'중랑구','중화':'중랑구','상봉':'중랑구','면목':'중랑구',
    '사가정':'중랑구','용마산':'중랑구','중곡':'광진구','어린이대공원':'광진구',
    '자양':'광진구','청담':'강남구','강남구청':'강남구','학동':'강남구','논현':'강남구',
    '반포':'서초구','내방':'서초구','이수':'동작구','남성':'동작구',
    '숭실대입구':'동작구','상도':'동작구','장승배기':'동작구','신대방삼거리':'동작구',
    '보라매':'동작구','신풍':'영등포구','남구로':'구로구','가산디지털단지':'금천구',
    '천왕':'구로구','온수':'구로구',
    '암사':'강동구','암사역사공원역':'강동구','강동구청':'강동구','몽촌토성':'송파구',
    '석촌':'송파구','송파':'송파구','문정':'송파구','장지':'송파구','복정':'송파구',
    '언주':'강남구','선정릉':'강남구','삼성중앙':'강남구','봉은사':'강남구',
    '삼전':'송파구','석촌고분':'송파구','송파나루':'송파구','한성백제':'송파구',
    '둔촌오륜':'강동구','중앙보훈병원':'강동구',
}

PRIORITY_ITEMS = {
    "💰 월세 저렴":  "norm_평균월세",
    "🛒 물가 저렴":  "norm_평균물가",
    "🎨 문화시설":   "norm_기타문화공간수",
    "🌳 녹지/공원":  "norm_공원수",
}

if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = None


# ══════════════════════════════════════════════════════════════════════════
# 컨트롤 패널
# ══════════════════════════════════════════════════════════════════════════
with st.container():
    col_left, col_right = st.columns([1, 1.7])

    with col_left:
        st.markdown('<div class="ctrl-label">🚉 지하철 호선으로 찾기</div>', unsafe_allow_html=True)
        selected_line = st.selectbox(
            "호선 선택",
            ["선택 안 함"] + list(LINE_STATIONS.keys()),
            key="line_select",
            label_visibility="collapsed"
        )
        if selected_line != "선택 안 함":
            st.info(f"**{selected_line}** 경유 자치구를 우선 반영합니다")
        else:
            st.caption("호선을 선택하면 경유 자치구를 우선 추천합니다")

    with col_right:
        st.markdown('<div class="ctrl-label">⚖️ 주거 우선순위 설정 (1순위 → 4순위)</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="priority-hint">💡 1순위에 가장 중요한 항목을 선택하세요. 중복 선택 불가.</div>',
            unsafe_allow_html=True
        )
        p_cols = st.columns(4)
        priority_keys = list(PRIORITY_ITEMS.keys())
        used, priority_order = [], []
        for rank in range(1, 5):
            with p_cols[rank - 1]:
                st.markdown(f"**{rank}순위**")
                remaining = [k for k in priority_keys if k not in used]
                choice = st.selectbox(
                    f"#{rank}", options=["선택"] + remaining,
                    key=f"prio_{rank}", label_visibility="collapsed"
                )
                if choice != "선택":
                    used.append(choice)
                    priority_order.append(choice)

st.markdown("<hr style='border:none;border-top:1px solid #E5E2DA;margin:0.5rem 0 1.2rem'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# 점수 계산
# ══════════════════════════════════════════════════════════════════════════
if len(priority_order) == 4:
    w = {0: 4, 1: 3, 2: 2, 3: 1}
    df['total_score'] = sum(
        df[PRIORITY_ITEMS[item]] * w[i] for i, item in enumerate(priority_order)
    )
else:
    df['total_score'] = sum(df[v] for v in PRIORITY_ITEMS.values()) / 4.0

if selected_line != "선택 안 함":
    line_stations = LINE_STATIONS.get(selected_line, [])
    line_gu_set = set()
    for st_name in line_stations:
        if st_name in STATION_TO_GU:
            line_gu_set.add(STATION_TO_GU[st_name])
    bonus = df['total_score'].max() * 0.3
    df['total_score'] = df.apply(
        lambda r: r['total_score'] + bonus if r['자치구'] in line_gu_set else r['total_score'],
        axis=1
    )

rec_df  = df.sort_values('total_score', ascending=False).reset_index(drop=True)
top3_gu = rec_df.head(3)['자치구'].tolist()
top5_df = rec_df.head(5)

SCORE_MAX = df['total_score'].max()
SCORE_MIN = df['total_score'].min()

def to_100(score):
    if SCORE_MAX > SCORE_MIN:
        return (score - SCORE_MIN) / (SCORE_MAX - SCORE_MIN) * 100
    return 100.0

if st.session_state.selected_gu is None:
    st.session_state.selected_gu = top3_gu[0]

RANK_COLOR = {top3_gu[0]: "#1A1A1A", top3_gu[1]: "#4A4A4A", top3_gu[2]: "#8A8A8A"}
RANK_ICON  = {top3_gu[0]: "🥇", top3_gu[1]: "🥈", top3_gu[2]: "🥉"}
RANK_LABEL = {top3_gu[0]: "추천 1위", top3_gu[1]: "추천 2위", top3_gu[2]: "추천 3위"}


# ══════════════════════════════════════════════════════════════════════════
# 메인 레이아웃
# ══════════════════════════════════════════════════════════════════════════
col_map, col_info = st.columns([1.6, 1])


# ─────────────────────────── 지도 ────────────────────────────────────────
with col_map:
    hint_line = f" · {selected_line} 경유 우선 반영" if selected_line != "선택 안 함" else ""
    st.markdown(
        f'<div class="map-hint">추천 자치구가 지도에 강조 표시됩니다{hint_line}. 아래 버튼으로 상세 정보를 확인하세요.</div>',
        unsafe_allow_html=True
    )

    score_map = dict(zip(df['자치구'], df['total_score']))

    @st.cache_data(show_spinner=False)
    def load_precise_geojson():
        import urllib.request
        URLS = [
            "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json",
        ]
        for url in URLS:
            try:
                with urllib.request.urlopen(url, timeout=5) as r:
                    gj = json.loads(r.read().decode())
                gu_names = set(df['자치구'].tolist())
                filtered = []
                for f in gj.get('features', []):
                    props = f.get('properties', {})
                    name = (props.get('name') or props.get('SIG_KOR_NM') or '')
                    if name in gu_names:
                        f['properties']['name'] = name
                        f['id'] = name
                        filtered.append(f)
                if len(filtered) >= 20:
                    return {"type": "FeatureCollection", "features": filtered}
            except Exception:
                continue
        return None

    precise = load_precise_geojson()
    active_geojson = precise if precise else geojson

    fig = go.Figure()

    # Choropleth layer
    fig.add_trace(go.Choroplethmapbox(
        geojson=active_geojson,
        locations=df['자치구'],
        z=df['total_score'],
        featureidkey="properties.name",
        colorscale=[
            [0.00, "rgba(229,226,218,0.5)"],
            [0.50, "rgba(147,197,253,0.6)"],
            [1.00, "rgba(37,99,235,0.75)"],
        ],
        showscale=False,
        marker_line_width=1.2,
        marker_line_color="rgba(100,100,100,0.4)",
        hovertemplate="<b>%{location}</b><br>추천점수: %{z:.2f}<extra></extra>",
        name="전체구",
    ))

    # TOP3 강조
    for rgu in top3_gu:
        sub = df[df['자치구'] == rgu][['자치구','total_score']]
        alpha = {"rgba(37,99,235,0.5)": top3_gu[0], "rgba(96,165,250,0.45)": top3_gu[1], "rgba(191,219,254,0.4)": top3_gu[2]}
        fill_map = {top3_gu[0]: "rgba(37,99,235,0.5)", top3_gu[1]: "rgba(96,165,250,0.45)", top3_gu[2]: "rgba(191,219,254,0.4)"}
        fig.add_trace(go.Choroplethmapbox(
            geojson=active_geojson,
            locations=sub['자치구'],
            z=sub['total_score'],
            featureidkey="properties.name",
            colorscale=[[0, fill_map[rgu]], [1, fill_map[rgu]]],
            showscale=False,
            marker_line_width=2.5,
            marker_line_color="rgba(255,255,255,0.9)",
            hoverinfo="skip",
            name=RANK_LABEL[rgu],
        ))

    # TOP3 마커
    for rgu in top3_gu:
        row_d = df[df['자치구'] == rgu].iloc[0]
        rank_n = top3_gu.index(rgu)
        sizes = [28, 22, 18]
        fig.add_trace(go.Scattermapbox(
            lat=[row_d['lat']], lon=[row_d['lon']],
            mode="markers+text",
            marker=dict(size=sizes[rank_n], color=RANK_COLOR[rgu], opacity=1.0, allowoverlap=True),
            text=[f"{RANK_ICON[rgu]} {rgu}"],
            textposition="top center",
            textfont=dict(size=12, color="#111111", family="Noto Sans KR"),
            hovertemplate=(
                f"<b>{RANK_ICON[rgu]} {rgu}</b><br>"
                f"추천점수: {row_d['total_score']:.2f}<br>"
                f"월세: {int(row_d['평균월세'])}만원<br>"
                f"공원: {int(row_d['공원수'])}개 · 도서관: {int(row_d['도서관수'])}개<extra></extra>"
            ),
            customdata=[[rgu]],
            showlegend=False, name=rgu,
        ))

    # 나머지 구 마커
    for _, row_d in df[~df['자치구'].isin(top3_gu)].iterrows():
        gn = row_d['자치구']
        fig.add_trace(go.Scattermapbox(
            lat=[row_d['lat']], lon=[row_d['lon']],
            mode="markers+text",
            marker=dict(size=8, color="#9A9590", opacity=0.55, allowoverlap=True),
            text=[gn],
            textposition="top center",
            textfont=dict(size=7.5, color="#555555", family="Noto Sans KR"),
            customdata=[[gn]],
            hovertemplate=f"<b>{gn}</b><br>월세: {int(row_d['평균월세'])}만원<extra></extra>",
            showlegend=False, name=gn,
        ))

    fig.update_layout(
        mapbox=dict(style="carto-positron", center={"lat": 37.5635, "lon": 126.987}, zoom=10.3),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=470,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True, key="main_map")

    # ── 자치구 선택 버튼 ──────────────────────────────────────────────────────
    sel_gu = st.session_state.selected_gu

    st.markdown(
        "<div style='font-size:0.75rem;color:#9A9590;margin:2px 0 8px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;'>자치구를 선택하면 우측 상세정보가 변경됩니다</div>",
        unsafe_allow_html=True
    )

    # TOP3 버튼
    cols3 = st.columns(3)
    for i, rgu in enumerate(top3_gu):
        with cols3[i]:
            is_active = (sel_gu == rgu)
            label = f"{RANK_ICON[rgu]} {rgu}"
            if is_active:
                st.markdown(
                    f'<div style="background:#1A1A1A;color:#fff;border-radius:6px;'
                    f'padding:8px 4px;text-align:center;font-size:0.82rem;font-weight:700;">{label} ✓</div>',
                    unsafe_allow_html=True
                )
            else:
                if st.button(label, key=f"sel_top_{i}", use_container_width=True):
                    st.session_state.selected_gu = rgu
                    st.rerun()

    # 나머지 구
    others_gu = [g for g in df['자치구'].tolist() if g not in top3_gu]
    with st.expander("다른 자치구 보기", expanded=False):
        n_cols = 5
        rows_list = [others_gu[k:k+n_cols] for k in range(0, len(others_gu), n_cols)]
        for row_items in rows_list:
            cols_o = st.columns(n_cols)
            for j, g in enumerate(row_items):
                with cols_o[j]:
                    is_active = (sel_gu == g)
                    if is_active:
                        st.markdown(
                            f'<div style="background:#1A1A1A;color:#fff;border-radius:5px;'
                            f'padding:5px 2px;text-align:center;font-size:0.72rem;font-weight:700;">{g} ✓</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        if st.button(g, key=f"sel_other_{g}", use_container_width=True):
                            st.session_state.selected_gu = g
                            st.rerun()

    # 범례
    st.markdown(
        f"<div style='font-size:0.74rem;color:#9A9590;margin-top:6px;'>"
        f"<b style='color:#1A1A1A;'>추천순위</b>&ensp;"
        f"🥇 <b>{top3_gu[0]}</b>&ensp;"
        f"🥈 <b>{top3_gu[1]}</b>&ensp;"
        f"🥉 <b>{top3_gu[2]}</b></div>",
        unsafe_allow_html=True
    )


# ─────────────────────────── 우측 상세 ──────────────────────────────────
with col_info:
    gu      = st.session_state.selected_gu
    row     = df[df['자치구'] == gu].iloc[0]
    rank_pos = top3_gu.index(gu) + 1 if gu in top3_gu else None

    rl = RANK_LABEL.get(gu, "")
    st.markdown(f"""
    <div class="gu-header">
        <div class="gu-rank-tag">{rl}</div>
        <h2>{gu}</h2>
        <div class="gu-tagline">「 {row['한줄평']} 」</div>
    </div>
    """, unsafe_allow_html=True)

    # 물가 배지
    pr = row['물가비율']
    if pr > 0:
        st.markdown(f'<div class="price-badge high">생활물가 평균 대비 +{abs(pr):.1f}% 높음</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="price-badge low">생활물가 평균 대비 -{abs(pr):.1f}% 낮음</div>', unsafe_allow_html=True)

    def _pct(val, avg):
        return (val - avg) / avg * 100 if avg != 0 else 0

    rent_pct    = _pct(row['평균월세'], AVG_RENT)
    park_pct    = _pct(row['공원수'], AVG_PARK)
    lib_pct     = _pct(row['도서관수'], AVG_LIB)
    culture_pct = _pct(row['기타문화공간수'], AVG_CULTURE)

    def _badge_rent(pct):
        if pct < -2:   return "better", f"평균보다 {abs(pct):.0f}% 저렴"
        elif pct > 2:  return "worse",  f"평균보다 +{pct:.0f}% 비쌈"
        else:          return "neutral", "서울 평균과 비슷"

    def _badge_more(pct):
        if pct > 2:    return "better", f"평균보다 +{pct:.0f}% 많음"
        elif pct < -2: return "worse",  f"평균보다 {pct:.0f}% 적음"
        else:          return "neutral", "서울 평균과 비슷"

    rc, rt   = _badge_rent(rent_pct)
    pc, pt_t = _badge_more(park_pct)
    lc, lt   = _badge_more(lib_pct)
    cc, ct   = _badge_more(culture_pct)

    # 메트릭 그리드
    metric_html = (
        '<div class="metric-grid">'
        f'<div class="metric-card"><div class="mlabel">🏠 평균 월세</div>'
        f'<div class="mvalue">{int(row["평균월세"])}만원</div>'
        f'<div class="msub">원룸 기준 추정<br>서울 평균 <b>{AVG_RENT:.0f}만원</b></div>'
        f'<span class="mcomp {rc}">{rt}</span></div>'

        f'<div class="metric-card"><div class="mlabel">🌳 공원 수</div>'
        f'<div class="mvalue">{int(row["공원수"])}개소</div>'
        f'<div class="msub">서울시 주요공원 기준<br>서울 평균 <b>{AVG_PARK:.1f}개</b></div>'
        f'<span class="mcomp {pc}">{pt_t}</span></div>'

        f'<div class="metric-card"><div class="mlabel">📚 공공도서관</div>'
        f'<div class="mvalue">{int(row["도서관수"])}개</div>'
        f'<div class="msub">구립·시립 포함<br>서울 평균 <b>{AVG_LIB:.1f}개</b></div>'
        f'<span class="mcomp {lc}">{lt}</span></div>'

        f'<div class="metric-card"><div class="mlabel">🎨 문화공간</div>'
        f'<div class="mvalue">{int(row["기타문화공간수"])}개</div>'
        f'<div class="msub">미술관·공연장 등<br>서울 평균 <b>{AVG_CULTURE:.1f}개</b></div>'
        f'<span class="mcomp {cc}">{ct}</span></div>'
        '</div>'
    )
    st.markdown(metric_html, unsafe_allow_html=True)

    # 점수 바
    score     = row['total_score']
    score_100 = to_100(score)
    bar_col   = "#2563EB" if rank_pos == 1 else "#60A5FA" if rank_pos == 2 else "#BFDBFE" if rank_pos == 3 else "#9A9590"
    st.markdown(f"""
    <div class="score-bar-wrap">
        <div class="score-bar-label">종합 추천 점수</div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{score_100:.0f}%;background:{bar_col};"></div>
        </div>
        <div class="score-bar-val">{score_100:.0f}점</div>
    </div>
    """, unsafe_allow_html=True)

    # 역 태그
    st.markdown("<div style='font-size:0.75rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#9A9590;margin-top:0.8rem;margin-bottom:0.4rem;'>🚉 주변 주요역</div>", unsafe_allow_html=True)
    tags_html = "".join(
        f'<span class="station-tag">{s.strip()}</span>'
        for s in row['지하철역_예시'].split(',')
    )
    st.markdown(f'<div class="station-tags">{tags_html}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# TOP 5 카드
# ══════════════════════════════════════════════════════════════════════════
st.markdown("<hr style='border:none;border-top:1px solid #E5E2DA;margin:0.5rem 0 1.2rem'>", unsafe_allow_html=True)
st.markdown(
    "<div style='font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;"
    "color:#9A9590;margin-bottom:0.8rem;'>우선순위 기반 추천 지역 TOP 5</div>",
    unsafe_allow_html=True
)

CARD_EMOJI = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
cols_top = st.columns(5)

for i, (_, r) in enumerate(top5_df.iterrows()):
    with cols_top[i]:
        is_sel  = r['자치구'] == st.session_state.selected_gu
        rd      = r['평균월세'] - AVG_RENT
        rs, rc  = ("▲", "#DC2626") if rd > 0 else ("▼", "#059669")
        p_diff  = r['공원수'] - AVG_PARK
        l_diff  = r['도서관수'] - AVG_LIB
        s100    = to_100(r['total_score'])
        border  = "2px solid #1A1A1A" if is_sel else "1px solid #E5E2DA"
        bg      = "#F0F0F0" if is_sel else "#FFFFFF"

        st.markdown(f"""
        <div style="background:{bg};border:{border};border-radius:10px;
                    padding:14px 8px;text-align:center;min-height:170px;">
            <div style="font-size:1.7rem;">{CARD_EMOJI[i]}</div>
            <div style="font-size:1rem;font-weight:700;margin:6px 0 5px;">{r['자치구']}</div>
            <div style="font-size:0.71rem;color:#4A4A4A;line-height:1.8;">
                🏠 월세 <b>{int(r['평균월세'])}만원</b>
                <span style="color:{rc};font-size:0.65rem;">({rs}{abs(rd):.0f}만)</span><br>
                🌳 공원 {int(r['공원수'])}개
                <span style="color:{'#059669' if p_diff>=0 else '#DC2626'};font-size:0.63rem;">
                ({'+'if p_diff>=0 else ''}{p_diff:.1f})</span>
                &nbsp;📚 {int(r['도서관수'])}개
                <span style="color:{'#059669' if l_diff>=0 else '#DC2626'};font-size:0.63rem;">
                ({'+'if l_diff>=0 else ''}{l_diff:.1f})</span><br>
                🎨 문화공간 {int(r['기타문화공간수'])}개
            </div>
            <div style="font-size:0.67rem;background:#1A1A1A;color:#fff;border-radius:4px;
                        padding:3px 10px;display:inline-block;margin-top:7px;font-weight:700;">
                {s100:.0f}점
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption(
    "※ 도서관: 서울시 공공도서관 현황(2024, 215개) · "
    "문화공간: 서울시 문화공간 정보(862개) · "
    "공원: 서울시 주요공원현황(2026 상반기, 130개) · "
    "생활물가: 생필품·농수축산물 가격정보(2024, 98,053건) · "
    "지하철: 서울교통공사 역주소(289개)"
)
