"""
서울 자취 추천 앱 — 융합 버전
  코딩(예다은): 사이드바 복합 필터 / 4페이지 구조 / 교통 점수 보정 / folium 지도 클릭 / 체크리스트 저장
  바이브(윤나경): 메트릭 그리드 대시보드 / 100점 환산 / 서울 평균 % 배지 / TOP5 카드 / 호선 보너스
"""

import json
import os
import re
from typing import Dict, List, Tuple

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from streamlit_folium import st_folium

# ════════════════════════════════════════════════════════════════════════
# 페이지 설정
# ════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="서울, 처음이니? : 어디서 자취할까?",
    page_icon="🏠",
    layout="wide",
)

# ════════════════════════════════════════════════════════════════════════
# 스타일 (코딩 앱 기본 + 바이브 앱 카드/배지 병합)
# ════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
:root{
    --navy:#253F52;
    --orange:#F9852D;
    --mustard:#F2C84B;
    --sage:#9CBA7B;
    --teal:#68A595;
    --cream:#F8FAFC;
    --ink:#0F172A;
    --muted:#5B6776;
    --line:#D8E2EB;
    --soft:#EEF3F6;
}
.block-container {padding-top: 1rem; padding-bottom: 2rem; max-width: 1350px;}
html, body, [class*="css"]  {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Pretendard", sans-serif;
    color: var(--ink);
}
h1,h2,h3{letter-spacing:-0.02em;}
.hero{
    background: linear-gradient(135deg, var(--navy) 0%, var(--orange) 38%, var(--mustard) 68%, var(--teal) 100%);
    border-radius: 28px; padding: 28px 30px; color: white;
    margin-bottom: 18px; box-shadow: 0 18px 40px rgba(37,63,82,.18);
}
.hero h1{margin:0 0 8px 0; font-size:2rem; font-weight:900; color:white;}
.hero p{margin:0; line-height:1.65; font-size:1rem; color:rgba(255,255,255,.96);}
.badge{
    display:inline-block; margin-top:12px; margin-right:8px; padding:6px 12px;
    border-radius:999px; background:rgba(255,255,255,.18); border:1px solid rgba(255,255,255,.25);
    font-size:.82rem; font-weight:700; color:white;
}
.panel{
    background:white; border:1px solid var(--line); border-radius:22px; padding:18px;
    box-shadow: 0 8px 24px rgba(15,23,42,.05);
}
/* 코딩 앱 메트릭 카드 */
.metric-card-old{
    background: linear-gradient(180deg,#fff 0%, #f9fbfd 100%);
    border:1px solid var(--line);
    border-radius:20px; padding:18px; min-height:132px; box-shadow:0 6px 18px rgba(37,63,82,.06);
}
.metric-kicker{font-size:.84rem; color:var(--muted); font-weight:700; margin-bottom:8px;}
.metric-value{font-size:1.9rem; font-weight:900; color:var(--ink); line-height:1.1;}
.metric-desc{font-size:.88rem; color:var(--muted); line-height:1.55; margin-top:8px;}
/* 바이브 앱 메트릭 그리드 */
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; margin-bottom: 11px; }
.metric-card {
    border-radius: 12px; padding: 13px 15px;
    border-left: 4px solid #2196F3;
    background: linear-gradient(135deg, #e8f4fd, #d1ecf9);
}
.metric-card.green  { background: linear-gradient(135deg,#e8f8f0,#c8efd8); border-left-color:#4CAF50; }
.metric-card.orange { background: linear-gradient(135deg,#fff3e0,#ffe0b2); border-left-color:#FF9800; }
.metric-card.purple { background: linear-gradient(135deg,#f3e5f5,#e1bee7); border-left-color:#9C27B0; }
.metric-card .mlabel { font-size:.70rem; color:#555; font-weight:700; margin-bottom:3px; }
.metric-card .mvalue { font-size:1.25rem; font-weight:900; color:#1a1a2e; line-height:1.2; }
.metric-card .msub   { font-size:.66rem; color:#777; margin-top:3px; line-height:1.45; }
/* 비교 배지 */
.mcomp { display:inline-block; margin-top:5px; padding:2px 8px; border-radius:8px; font-size:.67rem; font-weight:700; }
.mcomp.better  { background:#d4edda; color:#155724; }
.mcomp.worse   { background:#f8d7da; color:#721c24; }
.mcomp.neutral { background:#e2e3e5; color:#383d41; }
/* 점수 바 */
.score-bar-wrap { background:#f0f4f8; border-radius:12px; padding:13px 15px; margin-bottom:11px; }
.score-bar-label { font-size:.76rem; color:#666; font-weight:700; margin-bottom:6px; }
.score-bar-bg { background:#ddd; border-radius:6px; height:11px; overflow:hidden; }
.score-bar-fill { height:100%; border-radius:6px; transition: width 0.4s ease; }
.score-bar-val { text-align:right; font-size:.78rem; color:#333; font-weight:700; margin-top:3px; }
/* 역 태그 */
.station-tags { display:flex; flex-wrap:wrap; gap:5px; margin-top:6px; }
.station-tag { background:#1a1a2e; color:#aac4e0; padding:3px 10px; border-radius:20px; font-size:.69rem; font-weight:500; }
/* 코딩 앱 기타 */
.top-card{
    border-radius:22px; padding:18px; height:100%;
    border:1px solid var(--line); box-shadow:0 10px 26px rgba(15,23,42,.05); background:white;
}
.top-rank{font-size:.82rem; font-weight:800; margin-bottom:8px;}
.top-name{font-size:1.35rem; font-weight:900; color:var(--ink); margin-bottom:10px;}
.top-meta{font-size:.92rem; line-height:1.65; color:#334155;}
.rank-1{border-top:8px solid #ef4444;} .rank-2{border-top:8px solid #f97316;}
.rank-3{border-top:8px solid #eab308;} .rank-4{border-top:8px solid #22c55e;} .rank-5{border-top:8px solid #3b82f6;}
.chip{display:inline-block; border-radius:999px; padding:5px 10px; margin:0 6px 6px 0;
    background:#eff6ff; color:#1d4ed8; font-size:.8rem; font-weight:700; border:1px solid #dbeafe;}
.chip-dark{background:#eef6f3; color:#0f766e; border:1px solid #cce8e0;}
.soft-box{background:#f8fafc; border:1px solid #e2e8f0; border-radius:18px; padding:16px; line-height:1.65;}
.warn-box{background:#fff7ed; border:1px solid #fed7aa; border-left:5px solid var(--orange);
    border-radius:18px; padding:16px; color:#9a3412; line-height:1.65;}
.good-box{background:#ecfdf5; border:1px solid #bbf7d0; border-left:5px solid var(--teal);
    border-radius:18px; padding:16px; color:#065f46; line-height:1.65;}
.compare-card{background:#fff; border:1px solid var(--line); border-radius:18px; padding:16px; min-height:190px;}
.section-title{font-size:1.15rem; font-weight:900; color:var(--ink); margin-bottom:10px;}
.small{font-size:.84rem; color:var(--muted);}
.footer-note{font-size:.82rem; color:#64748b; line-height:1.7;}
.stTabs [data-baseweb="tab-list"] {gap: 8px;}
.stTabs [data-baseweb="tab"] {height:44px; border-radius:999px; border:1px solid var(--line); background:#fff; padding-left:16px; padding-right:16px;}
.stTabs [aria-selected="true"] {background: #f8fafc;}
/* 힌트 */
.priority-hint{background:linear-gradient(90deg,#e3f0ff,#f0e3ff); border-radius:10px; padding:7px 13px; font-size:.78rem; color:#444; margin-top:5px; border-left:3px solid #6a85b6;}
.map-hint{background:#fffbe6; border-radius:8px; padding:6px 12px; font-size:.76rem; color:#7a6000; border-left:3px solid #f0c040; margin-bottom:6px;}
/* 헤더 카드 (바이브) */
.gu-header{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%); border-radius:16px; padding:18px 22px 16px; color:white; margin-bottom:12px; border:1px solid rgba(255,255,255,.08); text-align:center;}
.gu-header h2{font-size:1.8rem; font-weight:900; margin:0 0 6px 0; color:#fff; text-align:center;}
.gu-tagline{font-size:.86rem; color:#aac4e0; line-height:1.5; font-style:italic; text-align:center;}
.rank-badge-text{font-size:.82rem; color:#7eb8e0; margin-bottom:6px; text-align:center; font-weight:600;}
.price-badge{display:inline-block; padding:5px 14px; border-radius:20px; font-weight:700; font-size:.82rem; margin-bottom:10px;}
.price-badge.high{background:#fde8e8; color:#c0392b; border:1px solid #e74c3c40;}
.price-badge.low {background:#e8fde8; color:#1e8449; border:1px solid #27ae6040;}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
# 상수 (코딩 앱)
# ════════════════════════════════════════════════════════════════════════
DISTRICTS = [
    "강남구","강동구","강북구","강서구","관악구","광진구","구로구","금천구","노원구","도봉구",
    "동대문구","동작구","마포구","서대문구","서초구","성동구","성북구","송파구","양천구","영등포구",
    "용산구","은평구","종로구","중구","중랑구"
]
DISTRICT_CENTERS = {
    "강남구":[37.5172,127.0473],"강동구":[37.5301,127.1238],"강북구":[37.6397,127.0257],"강서구":[37.5509,126.8495],
    "관악구":[37.4784,126.9516],"광진구":[37.5385,127.0822],"구로구":[37.4954,126.8874],"금천구":[37.4602,126.9006],
    "노원구":[37.6542,127.0568],"도봉구":[37.6688,127.0471],"동대문구":[37.5744,127.0395],"동작구":[37.5124,126.9393],
    "마포구":[37.5663,126.9014],"서대문구":[37.5791,126.9368],"서초구":[37.4837,127.0324],"성동구":[37.5634,127.0366],
    "성북구":[37.5894,127.0167],"송파구":[37.5145,127.1059],"양천구":[37.5169,126.8664],"영등포구":[37.5264,126.8962],
    "용산구":[37.5326,126.9900],"은평구":[37.6027,126.9291],"종로구":[37.5735,126.9788],"중구":[37.5640,126.9970],
    "중랑구":[37.6063,127.0927]
}
EMBEDDED_RENT = {
    "강남구":95,"강동구":72,"강북구":62,"강서구":68,"관악구":60,"광진구":78,"구로구":63,"금천구":58,"노원구":60,
    "도봉구":55,"동대문구":68,"동작구":75,"마포구":85,"서대문구":70,"서초구":92,"성동구":80,"성북구":65,"송파구":88,
    "양천구":70,"영등포구":75,"용산구":82,"은평구":63,"종로구":75,"중구":78,"중랑구":60
}
DISTRICT_REVIEWS = {
    "강남구":"직주근접은 최고지만 월세와 관리비 압박이 커요. 역세권 신축은 편하지만 예산 여유가 있어야 안정적으로 버틸 수 있어요.",
    "강동구":"조용하고 안정적인 생활권이 강점이에요. 다만 번화가 감성보다 주거 안정감을 우선하는 사람에게 더 잘 맞아요.",
    "강북구":"상대적으로 예산 친화적이지만 역세권과 언덕 차이가 커요. 집 주변 도보 동선을 꼭 직접 체크하는 편이 좋아요.",
    "강서구":"마곡·발산 접근이 좋아 직장인 수요가 있어요. 대신 생활권에 따라 체감 이동시간 편차가 커요.",
    "관악구":"가성비 자취의 대표 지역이에요. 경사와 노후 원룸 편차, 골목 소음은 꼭 직접 확인해야 해요.",
    "광진구":"건대·성수 접근성이 좋아 재미와 편의가 강점이에요. 반면 상권 근처는 밤에 꽤 활기차요.",
    "구로구":"구디 생활권이라면 매우 현실적인 선택지예요. 역과 얼마나 가까운지가 만족도를 크게 좌우해요.",
    "금천구":"예산 대비 무난하지만 문화 상권은 단조롭게 느껴질 수 있어요. 회사와 가까우면 체감 만족도가 높아져요.",
    "노원구":"조용하고 공부하기 좋은 분위기가 있어요. 대신 도심 출퇴근·통학은 길게 느껴질 수 있어요.",
    "도봉구":"월세는 낮지만 핵심 업무지구까지 이동시간이 길 수 있어요. 차분한 거주감과 비용 절감이 장점이에요.",
    "동대문구":"회기·청량리 축은 교통이 매우 좋지만 동네별 분위기 차이가 커요. 밤 동선과 건물 노후도 확인이 중요해요.",
    "동작구":"통학·통근·거주의 균형형이에요. 흑석·사당·노량진은 성격이 달라 생활 취향에 맞춰 골라야 해요.",
    "마포구":"문화생활 만족도는 높지만 월세와 생활비가 같이 올라요. 놀기 좋은 동네와 살기 편한 골목은 다를 수 있어요.",
    "서대문구":"신촌 인근은 대학가 에너지가 강하고, 연희·북가좌는 비교적 차분해요. 통학 중심이면 여전히 강한 후보예요.",
    "서초구":"교통과 인프라는 훌륭하지만 예산 부담이 커요. 생활권별 가격 차도 큰 편이에요.",
    "성동구":"성수·왕십리 접근성 덕분에 트렌디하고 이동이 편해요. 최근 월세 상승 속도가 빨라 가성비 매물은 빨리 빠져요.",
    "성북구":"대학가·주거지 분위기가 좋아 공부 환경이 안정적이에요. 다만 오르막과 겨울 체감 이동은 생각해야 해요.",
    "송파구":"공원과 생활 인프라가 좋고 안정감 있어요. 잠실권은 예산이 높고 외곽은 체감 이동시간이 달라져요.",
    "양천구":"주거 안정감은 높지만 문화 상권은 상대적으로 약할 수 있어요. 목동권과 신월·신정권의 분위기가 달라요.",
    "영등포구":"여의도 접근성과 상권은 강하지만 유동인구가 많아요. 밤 분위기 편차가 있는 지역은 직접 걸어보는 게 좋아요.",
    "용산구":"서울 중심 접근성은 뛰어나지만 가격도 강해요. 생활권을 잘 고르면 편한데 예산 여유가 필요해요.",
    "은평구":"주거 안정감이 좋고 비교적 차분해요. 다만 도심·강남 이동은 환승 동선에 따라 피로감이 달라져요.",
    "종로구":"문화 인프라는 최상급이지만 주택 노후도와 소음 체감이 큽니다. 취향을 꽤 타는 생활권이에요.",
    "중구":"도심 접근성은 매우 뛰어나지만 주거 선택지가 제한될 수 있어요. 생활비도 같이 올라갈 가능성이 큽니다.",
    "중랑구":"예산 친화적이고 실거주 안정감은 무난해요. 대신 핵심 업무지구 접근은 노선 선택이 중요해요.",
}
DISTRICT_TAGLINES = {
    "강남구":"화려한 도시 라이프의 중심, 높은 비용만큼 확실한 인프라.",
    "강동구":"한강과 인접한 쾌적한 주거환경, 서울에서 물가가 가장 저렴한 편.",
    "강북구":"북한산 자락의 맑은 공기, 정겨운 동네 분위기를 느낄 수 있습니다.",
    "강서구":"마곡지구의 성장과 함께 떠오르는 녹지 부자 동네.",
    "관악구":"청년들의 성지, 저렴한 월세와 활기찬 에너지가 가득합니다.",
    "광진구":"대학가와 한강 공원을 동시에 누리는 젊은 주거지.",
    "구로구":"사통팔달 교통의 요지, 가성비 좋은 역세권 매물이 많습니다.",
    "금천구":"G밸리 직장인들을 위한 실속형 자취 명당.",
    "노원구":"교육열만큼이나 안전하고 조용한 주택 밀집 지역.",
    "도봉구":"서울에서 가장 낮은 월세, 조용한 삶을 원하는 분께 추천.",
    "동대문구":"전통시장과 대학가가 어우러진 맛집 천국.",
    "동작구":"노량진과 사당을 잇는 공무원·직장인 최선호 지역.",
    "마포구":"트렌디한 카페와 핫플레이스가 집 앞마당인 곳.",
    "서대문구":"신촌의 활기와 연희동의 고즈넉함이 공존하는 동네.",
    "서초구":"강남의 편리함에 예술적 품격을 더한 고급 주거지.",
    "성동구":"성수동 카페거리를 내 집처럼, 숲과 강이 만나는 곳.",
    "성북구":"개성 넘치는 독립서점과 대학 문화가 살아있는 동네.",
    "송파구":"석촌호수와 롯데타워, 완벽한 주말 여가를 보장합니다.",
    "양천구":"안전한 치안과 깔끔한 거리, 정돈된 삶을 꿈꾼다면.",
    "영등포구":"여의도 직주근접의 정석, 쇼핑과 교통의 허브.",
    "용산구":"글로벌한 문화와 이색적인 풍경이 펼쳐지는 곳.",
    "은평구":"은평한옥마을처럼 여유롭고 자연 친화적인 동네.",
    "종로구":"문화예술 공간 밀집도 1위, 감성이 일상이 되는 곳.",
    "중구":"서울의 심장, 어디든 갈 수 있는 최고의 교통지.",
    "중랑구":"중랑천 산책로와 가성비 좋은 생활권이 강점입니다.",
}
# 바이브 앱 실측 데이터
VIBE_DATA = {
    '도서관수':       [17,10,7,9,5,8,13,4,10,10,10,9,6,4,9,7,14,12,10,6,4,8,9,8,6],
    '기타문화공간수': [80,7,11,13,13,18,15,11,17,15,18,12,42,29,48,23,38,38,12,17,57,18,229,73,8],
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
}
LOW_BUDGET_WARNINGS = {
    "도봉구":"강남·여의도처럼 핵심 업무지구 접근은 길게 느껴질 수 있어요.",
    "금천구":"문화 상권이 단조롭게 느껴질 수 있어 생활 만족도가 취향을 타요.",
    "관악구":"가성비는 좋지만 노후 원룸과 경사, 골목 소음 편차가 커요.",
    "중랑구":"핵심 업무지구 접근은 노선 선택에 따라 피로감 차이가 커요.",
    "강북구":"역세권과 언덕 차이 때문에 체감 이동 난이도가 높을 수 있어요.",
}
CHECKLIST_ITEMS = [
    "등기부등본 / 전입 가능 여부 확인","관리비에 포함된 항목 확인",
    "밤 10시 이후 골목 동선 직접 확인","곰팡이·결로·환기 상태 확인",
    "세탁기·냉장고·에어컨 옵션 실물 확인","편의점·약국·마트·버스정류장 거리 확인",
    "휴대폰 수신 상태와 인터넷 품질 확인","역까지 도보 소요시간 직접 재보기",
]
THEME_COLORS = ["#ef4444","#f97316","#eab308","#22c55e","#3b82f6"]
PRIORITY_OPTIONS = ["월세","생활물가","교통","문화생활"]
PRICE_BAND_HELP = {
    "50만원대 이하":"월세 부담은 낮지만, 역세권 편차·노후 원룸·문화 상권 부족을 꼭 함께 보세요.",
    "60만원대":"가성비형 선택지가 많이 보이는 구간이에요. 역세권 여부에 따라 만족도가 크게 갈립니다.",
    "70만원대":"서울 자취 초보가 가장 많이 체감 비교하는 구간이에요. 교통/생활권 균형을 보기 좋아요.",
    "80만원대":"신축/핵심 생활권 선택지가 늘어나요. 대신 관리비까지 합산해 비교하는 게 좋아요.",
    "90만원대 이상":"교통과 생활권 프리미엄이 붙는 경우가 많아요. 월세 대비 실제 효용을 꼭 따져보세요.",
}
DEFAULT_UNI_TO_DISTRICTS = {
    "선택 안 함":[],"서울대학교":["관악구","동작구","금천구"],"연세대학교":["서대문구","마포구","은평구"],
    "이화여자대학교":["서대문구","마포구","은평구"],"서강대학교":["마포구","서대문구","영등포구"],
    "홍익대학교":["마포구","서대문구","영등포구"],"건국대학교":["광진구","성동구","송파구"],
    "세종대학교":["광진구","성동구","중랑구"],"경희대학교":["동대문구","성북구","중랑구"],
    "한국외국어대학교":["동대문구","성북구","중랑구"],"서울시립대학교":["동대문구","성동구","중랑구"],
    "고려대학교":["성북구","동대문구","종로구"],"성신여자대학교":["성북구","강북구","종로구"],
    "한양대학교":["성동구","동대문구","광진구"],"중앙대학교":["동작구","관악구","영등포구"],
    "숭실대학교":["동작구","관악구","영등포구"],"숙명여자대학교":["용산구","마포구","중구"],
    "성균관대학교(인문)":["종로구","성북구","중구"],"국민대학교":["성북구","강북구","종로구"],
    "덕성여자대학교":["강북구","노원구","성북구"],"서울과학기술대학교":["노원구","중랑구","도봉구"],
}
WORK_TO_DISTRICTS = {
    "선택 안 함":[],"강남역/테헤란로":["강남구","서초구","송파구","동작구","광진구"],
    "여의도":["영등포구","동작구","마포구","관악구","구로구"],
    "광화문/종로":["종로구","중구","서대문구","용산구","성북구"],
    "성수/서울숲":["성동구","광진구","송파구","동대문구"],
    "상암DMC":["마포구","은평구","서대문구","강서구"],
    "구로디지털단지":["구로구","금천구","관악구","영등포구"],
    "마곡":["강서구","양천구","영등포구","구로구"],
    "판교/분당":["서초구","강남구","송파구"],
    "수원/광교":["금천구","구로구","강남구"],
}
LINE_PREFS = {
    "1호선","2호선","3호선","4호선","5호선","6호선","7호선","8호선","9호선",
    "경의중앙선","공항철도","경춘선","수인분당선","신분당선","우이신설선","신림선","서해선"
}
EXTENDED_LINES = {
    "강남구":["2호선","3호선","7호선","9호선","수인분당선","신분당선"],
    "강동구":["5호선","8호선","9호선"],"강북구":["4호선","우이신설선"],
    "강서구":["5호선","9호선","공항철도"],"관악구":["2호선","신림선"],
    "광진구":["2호선","5호선","7호선"],"구로구":["1호선","2호선","7호선","서해선"],
    "금천구":["1호선","7호선"],"노원구":["4호선","6호선","7호선","경춘선"],
    "도봉구":["1호선","4호선","7호선"],
    "동대문구":["1호선","2호선","5호선","경의중앙선","경춘선","수인분당선"],
    "동작구":["1호선","2호선","4호선","7호선","9호선","신림선"],
    "마포구":["2호선","5호선","6호선","경의중앙선","공항철도"],
    "서대문구":["2호선","3호선","5호선","경의중앙선"],
    "서초구":["2호선","3호선","4호선","7호선","9호선","신분당선"],
    "성동구":["2호선","3호선","5호선","수인분당선","경의중앙선"],
    "성북구":["4호선","6호선","우이신설선"],
    "송파구":["2호선","3호선","5호선","8호선","9호선","수인분당선"],
    "양천구":["2호선","5호선"],"영등포구":["1호선","2호선","5호선","7호선","9호선"],
    "용산구":["1호선","4호선","6호선","경의중앙선","공항철도"],
    "은평구":["3호선","6호선","경의중앙선","공항철도"],
    "종로구":["1호선","3호선","4호선","5호선","6호선","경의중앙선"],
    "중구":["1호선","2호선","3호선","4호선","5호선","6호선","공항철도"],
    "중랑구":["6호선","7호선","경춘선"],
}
LINE_CONGESTION = {
    "1호선":0.70,"2호선":0.95,"3호선":0.80,"4호선":0.82,"5호선":0.72,"6호선":0.60,
    "7호선":0.88,"8호선":0.62,"9호선":0.98,"경의중앙선":0.84,"공항철도":0.56,
    "경춘선":0.48,"수인분당선":0.86,"신분당선":0.78,"우이신설선":0.42,"신림선":0.83,"서해선":0.50
}
# 바이브 앱 호선→역 매핑
LINE_STATIONS_VIBE = {
    "1호선":['서울','시청','종각','종로3가','종로5가','동대문','신설동','제기동','청량리','동묘앞'],
    "2호선":['시청','을지로입구','을지로3가','을지로4가','동대문역사문화공원','신당','상왕십리','왕십리',
             '한양대','뚝섬','성수','건대입구','구의','강변','잠실나루','잠실','잠실새내','종합운동장',
             '삼성','선릉','역삼','강남','교대','서초','방배','사당','낙성대','서울대입구','봉천','신림',
             '신대방','구로디지털단지','대림','신도림','문래','영등포구청','당산','합정','홍대입구',
             '신촌','이대','아현','충정로','용답','신답','도림천','양천구청','신정네거리','용두'],
    "3호선":['구파발','연신내','불광','녹번','홍제','무악재','독립문','경복궁','안국','종로3가',
             '을지로3가','충무로','동대입구','약수','금호','옥수','압구정','신사','잠원','고속터미널',
             '교대','남부터미널','양재','매봉','도곡','대치','학여울','대청','일원','수서','가락시장','경찰병원','오금'],
    "4호선":['불암산','상계','노원','창동','쌍문','수유','미아','미아사거리','길음',
             '성신여대입구','한성대입구','혜화','동대문','동대문역사문화공원','충무로',
             '명동','회현','서울','숙대입구','삼각지','신용산','이촌','동작','총신대입구','사당','남태령'],
    "5호선":['방화','개화산','김포공항','송정','마곡','발산','우장산','화곡','까치산','신정',
             '목동','오목교','양평','영등포구청','영등포시장','신길','여의도','여의나루',
             '마포','공덕','애오개','충정로','서대문','광화문','종로3가','을지로4가',
             '동대문역사문화공원','청구','신금호','행당','왕십리','마장','답십리','장한평',
             '군자','아차산','광나루','천호','강동','길동','굽은다리','명일','고덕','상일동',
             '둔촌동','올림픽공원','방이','오금','개롱','거여','마천','강일'],
    "6호선":['응암','역촌','불광','독바위','연신내','구산','새절','증산','디지털미디어시티',
             '월드컵경기장','마포구청','망원','합정','상수','광흥창','대흥','공덕',
             '효창공원앞','삼각지','녹사평','이태원','한강진','버티고개','약수','청구',
             '신당','동묘앞','창신','보문','안암','고려대','월곡','상월곡','돌곶이',
             '석계','태릉입구','화랑대','봉화산','신내'],
    "7호선":['도봉산','수락산','마들','노원','중계','하계','공릉','태릉입구','먹골','중화',
             '상봉','면목','사가정','용마산','중곡','군자','어린이대공원','건대입구','자양',
             '청담','강남구청','학동','논현','반포','고속터미널','내방','이수','남성',
             '숭실대입구','상도','장승배기','신대방삼거리','보라매','신풍','대림','남구로','가산디지털단지','천왕','온수'],
    "8호선":['암사','암사역사공원역','천호','강동구청','몽촌토성','잠실','석촌','송파','가락시장','문정','장지','복정'],
    "9호선":['언주','선정릉','삼성중앙','봉은사','종합운동장','삼전','석촌고분','석촌','송파나루','한성백제','올림픽공원','둔촌오륜','중앙보훈병원'],
}
STATION_TO_GU_VIBE = {
    '서울':'중구','시청':'중구','종각':'종로구','종로3가':'종로구','종로5가':'종로구',
    '동대문':'종로구','신설동':'동대문구','제기동':'동대문구','청량리':'동대문구','동묘앞':'종로구',
    '을지로입구':'중구','을지로3가':'중구','을지로4가':'중구','동대문역사문화공원':'중구',
    '신당':'중구','상왕십리':'성동구','왕십리':'성동구','한양대':'성동구','뚝섬':'성동구',
    '성수':'성동구','건대입구':'광진구','구의':'광진구','강변':'광진구',
    '잠실나루':'송파구','잠실':'송파구','잠실새내':'송파구','종합운동장':'송파구',
    '삼성':'강남구','선릉':'강남구','역삼':'강남구','강남':'강남구','교대':'서초구',
    '서초':'서초구','방배':'서초구','사당':'동작구','낙성대':'관악구','서울대입구':'관악구',
    '봉천':'관악구','신림':'관악구','신대방':'동작구','구로디지털단지':'구로구','대림':'구로구',
    '신도림':'구로구','문래':'영등포구','영등포구청':'영등포구','당산':'영등포구',
    '합정':'마포구','홍대입구':'마포구','신촌':'마포구','이대':'마포구','아현':'마포구',
    '충정로':'서대문구','용답':'성동구','신답':'성동구','도림천':'구로구','양천구청':'양천구','신정네거리':'양천구','용두':'동대문구',
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
    '둔촌동':'강동구','올림픽공원':'강동구','방이':'강동구','개롱':'강동구','거여':'강동구','마천':'강동구','강일':'강동구',
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
    '보라매':'동작구','신풍':'영등포구','남구로':'구로구','가산디지털단지':'금천구','천왕':'구로구','온수':'구로구',
    '암사':'강동구','암사역사공원역':'강동구','강동구청':'강동구','몽촌토성':'송파구',
    '석촌':'송파구','송파':'송파구','문정':'송파구','장지':'송파구','복정':'송파구',
    '언주':'강남구','선정릉':'강남구','삼성중앙':'강남구','봉은사':'강남구',
    '삼전':'송파구','석촌고분':'송파구','송파나루':'송파구','한성백제':'송파구',
    '둔촌오륜':'강동구','중앙보훈병원':'강동구',
}

# ════════════════════════════════════════════════════════════════════════
# 유틸
# ════════════════════════════════════════════════════════════════════════
def read_csv_safely(path: str) -> pd.DataFrame:
    for enc in ["utf-8-sig","utf-8","cp949","euc-kr"]:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue
    return pd.read_csv(path, engine="python", encoding_errors="ignore")

def extract_district(text):
    if pd.isna(text): return None
    m = re.search(r"([가-힣]+구)", str(text))
    return m.group(1) if m else None

def format_lines(lines: List[str]) -> str:
    uniq = list(dict.fromkeys(lines))
    return ", ".join(uniq[:8]) if uniq else "-"

def chip_html(items: List[str], dark: bool=False) -> str:
    klass = "chip chip-dark" if dark else "chip"
    return "".join([f"<span class='{klass}'>{x}</span>" for x in items if x])

def normalize_type(name: str) -> str:
    s = str(name).strip()
    if "미술" in s or "갤러리" in s: return "미술관/갤러리"
    if "박물" in s or "기념관" in s: return "박물관/기념관"
    if "공연" in s: return "공연장"
    if "도서관" in s: return "도서관"
    if "문화원" in s or "문화센터" in s: return "문화원/센터"
    if "문화예술회관" in s or "아트홀" in s or "아트센터" in s: return "문화예술회관/아트홀"
    return "복합문화공간/기타"

def priority_weights(order: List[str]) -> Dict[str, float]:
    points = [4,3,2,1]
    raw = {"월세":0,"생활물가":0,"교통":0,"문화생활":0}
    for i, item in enumerate(order): raw[item] = points[i]
    total = sum(raw.values())
    return {k: v/total for k,v in raw.items()}

def rent_band_filter(band: str) -> Tuple[int,int]:
    return {"상관없음":(0,999),"50만원대 이하":(0,59),"60만원대":(60,69),"70만원대":(70,79),"80만원대":(80,89),"90만원대 이상":(90,999)}[band]

def current_destination_bucket(district: str, destination: str) -> Tuple[str,str]:
    gbd_fast = {"강남구","서초구","송파구","동작구","성동구","광진구"}
    ybd_fast = {"영등포구","동작구","마포구","강서구","구로구","관악구"}
    cbd_fast = {"종로구","중구","서대문구","용산구","성북구","동대문구"}
    slow = {"도봉구","강북구","은평구","중랑구","노원구","금천구"}
    if destination == "강남":
        if district in gbd_fast: return "20분 안팎","환승 부담이 비교적 적고 출근 동선이 안정적이에요."
        if district in slow: return "45분+","강남권까지 이동시간이 길고 1회 이상 환승 피로가 누적되기 쉬워요."
        return "30~40분","무난하지만 출퇴근 시간대에는 혼잡도가 체감될 수 있어요."
    if destination == "여의도":
        if district in ybd_fast: return "20분 안팎","업무지구 접근성이 좋아 통근 스트레스가 낮은 편이에요."
        if district in slow: return "40분+","한 번에 연결되는 노선이 적어 환승 부담이 생길 수 있어요."
        return "25~35분","실사용은 가능하지만 출퇴근 시간대 혼잡도 체크가 필요해요."
    if district in cbd_fast: return "20분 안팎","도심 접근성이 좋아 이동 동선이 단순한 편이에요."
    if district in slow: return "40분+","도심권 이동은 가능하지만 왕복 피로도가 커질 수 있어요."
    return "25~35분","중심 업무지구 접근은 무난한 편이에요."

def transport_mismatch_reason(district, university, work_place, selected_lines, district_lines):
    reasons = []
    lines = set(district_lines.get(district,[]))
    if university != "선택 안 함" and district not in DEFAULT_UNI_TO_DISTRICTS.get(university,[]):
        reasons.append("재학 중인 대학교 기준 핵심 통학권이 아니어서 통학 시간이 길어질 수 있어요.")
    if work_place != "선택 안 함" and district not in WORK_TO_DISTRICTS.get(work_place,[]):
        reasons.append("선택한 근무지와의 직결성이 약해 1회 이상 환승 가능성이 높아요.")
    if selected_lines and len(lines.intersection(selected_lines)) == 0:
        reasons.append("희망 지하철 노선이 직접 지나지 않아 실제 체감 이동이 번거로울 수 있어요.")
    congestion_vals = [LINE_CONGESTION.get(line,0.6) for line in lines]
    if congestion_vals and np.mean(congestion_vals) >= 0.82:
        reasons.append("주요 이용 노선 혼잡도가 높은 편이라 출퇴근 시간 피로감이 클 수 있어요.")
    if not reasons:
        reasons.append("교통 자체가 나쁜 지역은 아니지만, 현재 설정한 조건과는 완벽히 맞지 않아요.")
    return " ".join(reasons[:2])

def estimate_monthly_pressure(row): return int(round(row["월세"]*10000+row["생활물가평균"]*4.2,-3))

# ════════════════════════════════════════════════════════════════════════
# 데이터 로드
# ════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_base_data():
    culture  = read_csv_safely("서울시 문화공간 정보.csv")
    library  = read_csv_safely("서울시 공공도서관 현황정보.csv")
    subway   = read_csv_safely("서울교통공사_역주소 및 전화번호.csv")
    prices   = read_csv_safely("생필품 농수축산물 가격 정보(2024년).csv")
    parks    = pd.read_excel("서울시 주요 공원현황(2026 상반기).xlsx")

    culture["자치구"] = culture["자치구"].astype(str).str.strip()
    culture = culture[culture["자치구"].isin(DISTRICTS)].copy()
    culture["문화유형"] = culture["주제분류"].apply(normalize_type)
    culture["위도"] = pd.to_numeric(culture["위도"], errors="coerce")
    culture["경도"] = pd.to_numeric(culture["경도"], errors="coerce")

    library["구명"] = library["구명"].astype(str).str.strip()
    library = library[library["구명"].isin(DISTRICTS)].copy()

    subway["자치구"] = subway["도로명주소"].apply(extract_district).fillna(subway["구주소"].apply(extract_district))
    subway["자치구"] = subway["자치구"].astype(str).str.strip()
    subway = subway[subway["자치구"].isin(DISTRICTS)].copy()

    prices["자치구 이름"] = prices["자치구 이름"].astype(str).str.strip()
    prices["가격(원)"] = pd.to_numeric(prices["가격(원)"], errors="coerce")
    prices = prices[prices["자치구 이름"].isin(DISTRICTS)].copy()
    price_month = pd.to_datetime(prices["년도-월"], format="%b-%y", errors="coerce")
    latest_month = price_month.max()
    if pd.notna(latest_month):
        prices = prices[price_month == latest_month].copy()

    parks["지역"] = parks["지역"].astype(str).str.strip()
    parks = parks[parks["지역"].isin(DISTRICTS)].copy()

    return culture, library, subway, prices, parks

@st.cache_data(show_spinner=False)
def load_rent_summary():
    seoul_avg = round(np.mean(list(EMBEDDED_RENT.values())),1)
    rent_df = pd.DataFrame({"자치구":list(EMBEDDED_RENT.keys()),"월세":list(EMBEDDED_RENT.values())})
    using_rent_csv = False
    if os.path.exists("서울특별시_전월세가_2025.csv"):
        try:
            raw = read_csv_safely("서울특별시_전월세가_2025.csv")
            if "전월세구분" in raw.columns:
                raw = raw[raw["전월세구분"].astype(str).str.contains("월세",na=False)].copy()
            rent_col = next((c for c in ["임대료(만원)","월세금액","월세금액(만원)"] if c in raw.columns), None)
            district_col = next((c for c in ["자치구명","구명","자치구"] if c in raw.columns), None)
            if rent_col and district_col:
                raw[rent_col] = pd.to_numeric(raw[rent_col], errors="coerce")
                raw[district_col] = raw[district_col].astype(str).str.strip()
                raw = raw[raw[district_col].isin(DISTRICTS)].copy()
                if not raw.empty:
                    summary = raw.groupby(district_col)[rent_col].median().reindex(DISTRICTS)
                    summary = summary.fillna(pd.Series(EMBEDDED_RENT)).round(0)
                    rent_df = pd.DataFrame({"자치구":summary.index,"월세":summary.values})
                    seoul_avg = float(raw[rent_col].median())
                    using_rent_csv = True
        except Exception: pass
    return rent_df, seoul_avg, using_rent_csv

@st.cache_data(show_spinner=False)
def build_district_dataframe():
    culture, library, subway, prices, parks = load_base_data()
    rent_df, seoul_rent_avg, using_rent_csv = load_rent_summary()

    base = pd.DataFrame(index=DISTRICTS)
    base["문화시설수"]   = culture.groupby("자치구").size().reindex(DISTRICTS).fillna(0)
    base["도서관수"]     = library.groupby("구명").size().reindex(DISTRICTS).fillna(0)
    base["공원수"]       = parks.groupby("지역").size().reindex(DISTRICTS).fillna(0)
    base["지하철역수"]   = subway.groupby("자치구").size().reindex(DISTRICTS).fillna(0)
    base["생활물가평균"] = prices.groupby("자치구 이름")["가격(원)"].mean().reindex(DISTRICTS).fillna(prices["가격(원)"].mean())
    base["월세"]         = rent_df.set_index("자치구")["월세"].reindex(DISTRICTS).fillna(pd.Series(EMBEDDED_RENT))

    # 바이브 앱 기타문화공간 수 병합 (도서관 제외 실측값)
    vibe_etc = dict(zip(DISTRICTS, VIBE_DATA["기타문화공간수"]))
    base["기타문화공간수"] = pd.Series(vibe_etc)

    district_lines = {}
    for d in DISTRICTS:
        lines = EXTENDED_LINES.get(d,[]).copy()
        if d in subway["자치구"].values:
            extra = subway[subway["자치구"]==d]["호선"].astype(str).str.strip().tolist()
            for line in extra:
                if line not in lines: lines.append(line)
        district_lines[d] = lines

    base["노선수"]   = [len(district_lines[d]) for d in DISTRICTS]
    base["대표노선"] = [format_lines(district_lines[d]) for d in DISTRICTS]

    scaler = MinMaxScaler()
    norm_df = pd.DataFrame(
        scaler.fit_transform(base[["월세","생활물가평균","지하철역수","노선수","문화시설수","공원수","도서관수"]]),
        columns=["월세_norm","생활물가_norm","지하철역_norm","노선_norm","문화_norm","공원_norm","도서관_norm"],
        index=base.index,
    )
    base["월세점수"]        = 1 - norm_df["월세_norm"]
    base["생활물가점수"]    = 1 - norm_df["생활물가_norm"]
    base["교통점수_base"]   = (norm_df["지하철역_norm"]*0.6 + norm_df["노선_norm"]*0.4).clip(0,1)
    base["문화점수_base"]   = (norm_df["문화_norm"]*0.5 + norm_df["공원_norm"]*0.22 + norm_df["도서관_norm"]*0.28).clip(0,1)
    base["안심점수"]        = (base["도서관수"].rank(pct=True)*0.45 + base["공원수"].rank(pct=True)*0.35 + (1-norm_df["월세_norm"])*0.20).clip(0.30,0.95)
    base["가성비지수"]      = ((base["교통점수_base"]*0.35 + base["문화점수_base"]*0.35 + base["월세점수"]*0.30)*100).round(0)

    crowding = []
    for d in DISTRICTS:
        vals = [LINE_CONGESTION.get(l,0.60) for l in district_lines[d]]
        crowding.append(float(np.mean(vals)) if vals else 0.60)
    base["혼잡도"]     = crowding
    base["혼잡도설명"] = base["혼잡도"].apply(lambda x: "높음" if x>=0.83 else ("보통" if x>=0.64 else "낮음"))

    # 바이브 앱 물가 비율
    base["물가비율"] = ((base["생활물가평균"] / base["생활물가평균"].mean()) - 1) * 100

    culture_type_top = (
        culture.groupby(["자치구","문화유형"]).size().rename("개수").reset_index()
        .sort_values(["자치구","개수"], ascending=[True,False])
    )

    base = base.reset_index().rename(columns={"index":"자치구"})
    return base, culture, library, subway, prices, parks, culture_type_top, district_lines, seoul_rent_avg, using_rent_csv

# ════════════════════════════════════════════════════════════════════════
# 추천 엔진
# ════════════════════════════════════════════════════════════════════════
def transport_match_score(district, university, work_place, selected_lines, district_lines):
    score = 0.0
    if university != "선택 안 함":
        ranked = DEFAULT_UNI_TO_DISTRICTS.get(university,[])
        if district in ranked: score += 0.60 - ranked.index(district)*0.14
    if work_place != "선택 안 함":
        ranked = WORK_TO_DISTRICTS.get(work_place,[])
        if district in ranked: score += 0.55 - ranked.index(district)*0.11
    if selected_lines:
        overlap = len(set(district_lines.get(district,[])).intersection(selected_lines))
        score += min(overlap/max(len(selected_lines),1),1.0)*0.50
    return min(score, 1.25)

def score_recommendations(df, university, work_place, selected_lines, order, district_lines, selected_line_vibe="선택 안 함"):
    work = df.copy()
    weights = priority_weights(order)
    work["교통보정"] = [transport_match_score(d,university,work_place,selected_lines,district_lines) for d in work["자치구"]]
    work["교통점수"] = (work["교통점수_base"]*0.74 + work["교통보정"]*0.26).clip(0,1.1)
    work["추천점수"] = (
        work["월세점수"]*weights["월세"] + work["생활물가점수"]*weights["생활물가"] +
        work["교통점수"]*weights["교통"] + work["문화점수_base"]*weights["문화생활"]
    ) * 100
    work["총평점"] = (work["추천점수"]*0.84 + work["안심점수"]*100*0.08 + work["가성비지수"]*0.08).round(1)
    work["월체감부담"] = work.apply(estimate_monthly_pressure, axis=1)

    # 바이브 앱 호선 보너스 (코딩 앱 교통 보정과 결합)
    if selected_line_vibe != "선택 안 함":
        line_stations = LINE_STATIONS_VIBE.get(selected_line_vibe,[])
        line_gu_set = set(STATION_TO_GU_VIBE.get(s,"") for s in line_stations) - {""}
        bonus = work["총평점"].max() * 0.15  # 15% 보너스 (코딩 교통 보정과 중복 방지)
        work["총평점"] = work.apply(lambda r: r["총평점"]+bonus if r["자치구"] in line_gu_set else r["총평점"], axis=1)

    return work.sort_values(["총평점","추천점수"], ascending=False).reset_index(drop=True)

def build_reason(row, seoul_avg_rent, university, work_place, selected_lines, district_lines):
    reasons = []
    if row["월세"] <= seoul_avg_rent: reasons.append(f"서울 평균 월세({round(seoul_avg_rent)}만 원)보다 부담이 적어요")
    if row["가성비지수"] >= 70: reasons.append("인프라 대비 가격 균형이 좋아요")
    if row["안심점수"] >= 0.75: reasons.append("밤길·정주 안정감이 비교적 좋아요")
    if university != "선택 안 함" and row["자치구"] in DEFAULT_UNI_TO_DISTRICTS.get(university,[]):
        reasons.append(f"{university} 통학권으로 무난해요")
    if work_place != "선택 안 함" and row["자치구"] in WORK_TO_DISTRICTS.get(work_place,[]):
        reasons.append(f"{work_place} 출퇴근 동선이 편한 편이에요")
    overlap = set(district_lines.get(row["자치구"],[])).intersection(selected_lines)
    if overlap: reasons.append("희망 노선 "+", ".join(sorted(list(overlap))[:3])+" 이용이 가능해요")
    return reasons[:3] if reasons else ["월세·교통·문화생활의 균형이 무난해요"]

# ════════════════════════════════════════════════════════════════════════
# 지도
# ════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_geojson():
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json"
    try: return requests.get(url, timeout=8).json()
    except Exception: return None

def make_rank_map(filtered_df, top5_names, rank_color_map, selected_district=None):
    fmap = folium.Map(location=[37.55,126.98], zoom_start=11, tiles="cartodbpositron")
    geojson = load_geojson()
    muted = "#CBD5E1"
    if geojson:
        def style_fn(feature):
            name = feature["properties"].get("name")
            fill = rank_color_map.get(name, muted if name in filtered_df["자치구"].values else "#E5E7EB")
            opacity = 0.88 if name in top5_names else 0.45
            weight  = 3.5 if name == selected_district else (2.2 if name in top5_names else 1.0)
            return {"fillColor":fill,"color":"#334155","weight":weight,"fillOpacity":opacity}
        gj = folium.GeoJson(geojson, name="서울 자치구", style_function=style_fn,
            highlight_function=lambda f:{"weight":3,"color":"#111827","fillOpacity":0.95},
            tooltip=folium.GeoJsonTooltip(fields=["name"],aliases=["자치구"],sticky=False),
            popup=folium.GeoJsonPopup(fields=["name"],aliases=["자치구"],labels=False))
        gj.add_to(fmap)
    for _, row in filtered_df.iterrows():
        color = rank_color_map.get(row["자치구"],"#64748B")
        is_selected = row["자치구"] == selected_district
        folium.CircleMarker(
            location=DISTRICT_CENTERS[row["자치구"]],
            radius=12 if is_selected else (9 if row["자치구"] in top5_names else 5),
            color="#FFD700" if is_selected else color,
            fill=True, fill_color="#FFD700" if is_selected else color, fill_opacity=0.98,
            popup=folium.Popup(
                f"<b>{row['자치구']}</b><br>총평점 {row['총평점']:.1f}<br>월세 {int(round(row['월세']))}만 원<br>대표 노선 {row['대표노선']}",
                max_width=280),
            tooltip=row["자치구"],
        ).add_to(fmap)
    return fmap

# ════════════════════════════════════════════════════════════════════════
# 100점 환산 (바이브 앱)
# ════════════════════════════════════════════════════════════════════════
def to_100(score, score_min, score_max):
    if score_max > score_min:
        return (score - score_min) / (score_max - score_min) * 100
    return 100.0

def pct_badge(val, avg, higher_is_better=True):
    if avg == 0: return ""
    pct = (val - avg) / avg * 100
    if higher_is_better:
        if pct > 2:   return f'<span class="mcomp better">평균보다 +{pct:.0f}% 많음 ▲</span>'
        elif pct < -2: return f'<span class="mcomp worse">평균보다 {pct:.0f}% 적음 ▼</span>'
    else:
        if pct < -2:  return f'<span class="mcomp better">평균보다 {abs(pct):.0f}% 저렴 ▼</span>'
        elif pct > 2: return f'<span class="mcomp worse">평균보다 +{pct:.0f}% 비쌈 ▲</span>'
    return '<span class="mcomp neutral">평균과 비슷</span>'

# ════════════════════════════════════════════════════════════════════════
# 초기 상태
# ════════════════════════════════════════════════════════════════════════
if "active_page" not in st.session_state:   st.session_state.active_page = "추천 결과"
if "detail_district" not in st.session_state: st.session_state.detail_district = "관악구"

# ════════════════════════════════════════════════════════════════════════
# 데이터 준비
# ════════════════════════════════════════════════════════════════════════
base_df, culture_df, library_df, subway_df, prices_df, parks_df, culture_type_top_df, district_lines_map, seoul_avg_rent, using_rent_csv = build_district_dataframe()
seoul_market_avg = int(round(prices_df["가격(원)"].mean(), 0))

# 서울 전체 평균 (바이브 앱 비교 배지용)
AVG_RENT    = base_df["월세"].mean()
AVG_PARK    = base_df["공원수"].mean()
AVG_LIB     = base_df["도서관수"].mean()
AVG_CULTURE = base_df["기타문화공간수"].mean()

# ════════════════════════════════════════════════════════════════════════
# 헤더
# ════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <h1>서울, 처음이니? : 어디서 자취할까?</h1>
    <p>
        서울에 처음 올라온 2030 자취생을 위해 만든 지역 추천 서비스예요.<br>
        <b>월세 · 생활물가 · 교통 · 문화생활</b>을 한 화면에서 비교하고,
        지도를 클릭해 지역 상세 대시보드를 바로 확인할 수 있어요.
    </p>
    <span class="badge">🏠 자취 초보용</span>
    <span class="badge">🚇 통학·통근·호선 추천</span>
    <span class="badge">🎭 문화생활 상세 제공</span>
    <span class="badge">🛡️ 밤길 안심 대리지표</span>
    <span class="badge">📊 100점 환산 추천 점수</span>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
# 사이드바
# ════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("⚙️ 추천 조건 설정")
    st.caption("1순위일수록 추천 점수에 더 크게 반영돼요. 1순위 40% · 2순위 30% · 3순위 20% · 4순위 10%")

    p1 = st.selectbox("1순위", PRIORITY_OPTIONS, index=0)
    remain = [x for x in PRIORITY_OPTIONS if x!=p1]
    p2 = st.selectbox("2순위", remain, index=0)
    remain = [x for x in remain if x!=p2]
    p3 = st.selectbox("3순위", remain, index=0)
    remain = [x for x in remain if x!=p3]
    p4 = st.selectbox("4순위", remain, index=0)
    order = [p1, p2, p3, p4]

    st.markdown("---")
    st.subheader("💸 희망 월세 가격대")
    rent_band = st.selectbox("월세 선택",
        ["상관없음","50만원대 이하","60만원대","70만원대","80만원대","90만원대 이상"], index=2)
    st.caption(PRICE_BAND_HELP[rent_band] if rent_band!="상관없음" else "가격대를 넓게 열면 추천 후보가 더 다양하게 보여요.")

    st.markdown("---")
    st.subheader("🚇 교통 조건")
    university   = st.selectbox("재학 중인 대학교", list(DEFAULT_UNI_TO_DISTRICTS.keys()), index=0)
    work_place   = st.selectbox("근무지 / 자주 가는 업무지구", list(WORK_TO_DISTRICTS.keys()), index=0)
    preferred_lines = st.multiselect("희망 지하철 노선 (복수 선택)", sorted(LINE_PREFS))

    st.markdown("---")
    st.subheader("🚉 호선으로 우선 추천 (바이브)")
    selected_line_vibe = st.selectbox("호선 선택", ["선택 안 함"]+list(LINE_STATIONS_VIBE.keys()), key="vibe_line")
    if selected_line_vibe != "선택 안 함":
        st.info(f"🚇 **{selected_line_vibe}** 경유 자치구에 추가 보너스 점수가 부여됩니다")

    st.markdown("---")
    st.subheader("✅ 자취 체크리스트")
    selected_checklist = [item for item in CHECKLIST_ITEMS if st.checkbox(item, value=item in CHECKLIST_ITEMS[:3])]

# ════════════════════════════════════════════════════════════════════════
# 추천 계산
# ════════════════════════════════════════════════════════════════════════
work_df = score_recommendations(base_df, university, work_place, preferred_lines, order, district_lines_map, selected_line_vibe)
lo, hi = rent_band_filter(rent_band)
if rent_band != "상관없음":
    work_df = work_df[(work_df["월세"]>=lo) & (work_df["월세"]<=hi)].reset_index(drop=True)
if work_df.empty:
    st.error("지금 조건을 동시에 만족하는 자치구가 없어요. 월세 가격대나 희망 노선을 조금 완화해 보세요.")
    st.stop()

top5 = work_df.head(5).copy()
top5_names = top5["자치구"].tolist()
rank_color_map = {name: THEME_COLORS[i] for i,name in enumerate(top5_names)}
SCORE_MAX = work_df["총평점"].max()
SCORE_MIN = work_df["총평점"].min()

# ════════════════════════════════════════════════════════════════════════
# 핵심 카드 (코딩 앱 스타일)
# ════════════════════════════════════════════════════════════════════════
m1,m2,m3,m4 = st.columns(4)
with m1:
    st.markdown(f"""<div class="metric-card-old"><div class="metric-kicker">🏙️ 서울 평균 월세</div>
    <div class="metric-value">{round(seoul_avg_rent)}만 원</div>
    <div class="metric-desc">{"업로드된 전월세 CSV 기준" if using_rent_csv else "보고서 기반 요약값 기준"}으로 계산한 서울 전체 월세 중앙값이에요.</div></div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""<div class="metric-card-old"><div class="metric-kicker">🛒 서울 생활물가 평균</div>
    <div class="metric-value">{seoul_market_avg:,}원</div>
    <div class="metric-desc">업로드한 생필품 가격 파일 기준 서울 자치구의 주요 생필품 평균 판매가예요.</div></div>""", unsafe_allow_html=True)
with m3:
    top_pick = top5.iloc[0]
    s100_top = to_100(top_pick["총평점"], SCORE_MIN, SCORE_MAX)
    st.markdown(f"""<div class="metric-card-old"><div class="metric-kicker">🥇 이번 조건의 1위 추천</div>
    <div class="metric-value">{top_pick['자치구']}</div>
    <div class="metric-desc">추천점수 <b>{s100_top:.0f}점</b> · 월세 {int(round(top_pick['월세']))}만 원</div></div>""", unsafe_allow_html=True)
with m4:
    safest = work_df.sort_values("안심점수", ascending=False).iloc[0]
    st.markdown(f"""<div class="metric-card-old"><div class="metric-kicker">🛡️ 밤길 안심 상위</div>
    <div class="metric-value">{safest['자치구']}</div>
    <div class="metric-desc">도서관·공원·거주비 부담을 함께 본 대리지표 기준이에요.</div></div>""", unsafe_allow_html=True)

if rent_band in {"50만원대 이하","60만원대"}:
    warns = [f"• <b>{d}</b> — {LOW_BUDGET_WARNINGS[d]}" for d in top5_names if d in LOW_BUDGET_WARNINGS][:3]
    if warns:
        st.markdown(f"<div class='warn-box'><b>💡 저예산 자취 팁</b><br>{'<br>'.join(warns)}</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
# 내비게이션
# ════════════════════════════════════════════════════════════════════════
nav_options = ["추천 결과","지역 상세","비교 분석","체크리스트 저장"]
active_page = st.radio("페이지", nav_options, horizontal=True, label_visibility="collapsed",
                       index=nav_options.index(st.session_state.active_page))
st.session_state.active_page = active_page

# ════════════════════════════════════════════════════════════════════════
# 페이지 1: 추천 결과
# ════════════════════════════════════════════════════════════════════════
if st.session_state.active_page == "추천 결과":
    st.markdown("### ✨ 지금 조건에 맞는 추천 지역 TOP 5")
    st.caption("지역명을 누르지 않아도 아래 카드와 지도만 보면 핵심 차이를 빠르게 파악할 수 있도록 구성했어요.")

    # TOP5 카드 (코딩 앱 스타일 + 바이브 앱 100점 점수)
    cols = st.columns(5)
    CARD_BG     = ["#fff8e1","#f5f5f5","#fbe9e7","#e8f4fd","#e8f4fd"]
    CARD_BORDER = ["#ffc107","#9e9e9e","#ff7043","#64b5f6","#64b5f6"]
    for i, (_, row) in enumerate(top5.iterrows(), start=1):
        reasons = build_reason(row, seoul_avg_rent, university, work_place, preferred_lines, district_lines_map)
        rent_delta = int(round(row["월세"] - seoul_avg_rent))
        s100 = to_100(row["총평점"], SCORE_MIN, SCORE_MAX)
        p_diff = row["공원수"] - AVG_PARK
        l_diff = row["도서관수"] - AVG_LIB
        with cols[i-1]:
            is_sel = row["자치구"] == st.session_state.detail_district
            shadow = "0 4px 20px rgba(0,0,0,0.16)" if is_sel else "0 10px 26px rgba(15,23,42,.05)"
            st.markdown(f"""
            <div class="top-card rank-{i}" style="box-shadow:{shadow};">
                <div class="top-rank">TOP {i} &nbsp; <b style="font-size:1.1rem;">{s100:.0f}점</b></div>
                <div class="top-name">{row['자치구']}</div>
                <div class="top-meta">
                    <b>월세</b> {int(round(row['월세']))}만 원
                    <span class="small">({rent_delta:+d}만 원 vs 서울 평균)</span><br>
                    <b>생활물가</b> {int(round(row['생활물가평균'])):,}원<br>
                    <b>대표 노선</b> {row['대표노선']}<br>
                    <b>공원</b> {int(row['공원수'])}개
                    <span class="small">({'+'if p_diff>=0 else ''}{p_diff:.1f})</span>
                    &nbsp;<b>도서관</b> {int(row['도서관수'])}개
                    <span class="small">({'+'if l_diff>=0 else ''}{l_diff:.1f})</span><br>
                    <b>문화공간</b> {int(row['기타문화공간수'])}개
                </div>
            </div>""", unsafe_allow_html=True)
            st.markdown(chip_html(reasons), unsafe_allow_html=True)
            if st.button(f"📊 {row['자치구']} 상세보기", key=f"card_detail_{i}", use_container_width=True):
                st.session_state.detail_district = row["자치구"]
                st.session_state.active_page = "지역 상세"
                st.rerun()

    theme1,theme2,theme3 = st.columns(3)
    with theme1: st.markdown(f"<div class='good-box'><b>💰 가성비 추천</b><br><b>{work_df.sort_values('가성비지수',ascending=False).iloc[0]['자치구']}</b> — 인프라 대비 월세 밸런스가 좋아요.</div>", unsafe_allow_html=True)
    with theme2: st.markdown(f"<div class='good-box'><b>🎭 문화생활 추천</b><br><b>{work_df.sort_values('문화점수_base',ascending=False).iloc[0]['자치구']}</b> — 문화시설·공원·도서관이 풍부해요.</div>", unsafe_allow_html=True)
    with theme3: st.markdown(f"<div class='good-box'><b>🌙 안정감 추천</b><br><b>{work_df.sort_values('안심점수',ascending=False).iloc[0]['자치구']}</b> — 밤길·정주 여건이 비교적 안정적이에요.</div>", unsafe_allow_html=True)

    st.markdown("### 🗺️ 서울 자치구 지도")
    st.markdown('<div class="map-hint">📍 지도에서 자치구를 클릭하면 <b>지역 상세</b> 탭으로 이동해 대시보드를 확인할 수 있어요</div>', unsafe_allow_html=True)
    fmap = make_rank_map(work_df, top5_names, rank_color_map, st.session_state.detail_district)
    map_data = st_folium(fmap, width=None, height=620, returned_objects=["last_object_clicked_tooltip"])
    if map_data and map_data.get("last_object_clicked_tooltip") in DISTRICTS:
        clicked_name = map_data["last_object_clicked_tooltip"]
        st.session_state.detail_district = clicked_name
        st.session_state.active_page = "지역 상세"
        st.rerun()

    # 바이브 앱 스타일 Plotly 점수 바 차트
    bar_df = top5[["자치구","총평점"]].copy()
    bar_df["100점"] = bar_df["총평점"].apply(lambda s: to_100(s, SCORE_MIN, SCORE_MAX))
    fig = px.bar(bar_df, x="자치구", y="100점", color="자치구",
                 color_discrete_map=rank_color_map, text="100점", title="상위 5개 지역 추천 점수 (100점 만점)")
    fig.update_traces(texttemplate="%{text:.0f}점", textposition="outside")
    fig.update_layout(height=360, showlegend=False, margin=dict(l=10,r=10,t=60,b=10), yaxis_range=[0,115])
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# 페이지 2: 지역 상세 (코딩 앱 + 바이브 앱 대시보드 결합)
# ════════════════════════════════════════════════════════════════════════
elif st.session_state.active_page == "지역 상세":
    default_idx = work_df.index[work_df["자치구"]==st.session_state.detail_district].tolist()
    idx = default_idx[0] if default_idx else 0
    detail_district = st.selectbox("🔎 심층 분석할 자치구", work_df["자치구"].tolist(), index=idx)
    st.session_state.detail_district = detail_district
    row = base_df.set_index("자치구").loc[detail_district]
    work_row = work_df.set_index("자치구").loc[detail_district] if detail_district in work_df["자치구"].values else row

    st.markdown(f"### 📍 {detail_district} 심층 분석")

    # ── 바이브 앱 헤더 카드 ──
    tagline = DISTRICT_TAGLINES.get(detail_district,"")
    rank_in_top = top5_names.index(detail_district)+1 if detail_district in top5_names else None
    rank_label  = {1:"🥇 추천 1위",2:"🥈 추천 2위",3:"🥉 추천 3위"}.get(rank_in_top,"")
    s100 = to_100(work_row["총평점"] if "총평점" in work_row else row.get("총평점",0), SCORE_MIN, SCORE_MAX)
    score_color = THEME_COLORS[rank_in_top-1] if rank_in_top and rank_in_top<=5 else "#3498db"
    st.markdown(f"""
    <div class="gu-header">
        <div class="rank-badge-text">{rank_label}</div>
        <h2>{detail_district}</h2>
        <div class="gu-tagline">「 {tagline} 」</div>
    </div>""", unsafe_allow_html=True)

    pr = row.get("물가비율", 0)
    if pr > 0:
        st.markdown(f'<div class="price-badge high">💸 생활물가 서울 평균 대비 +{abs(pr):.1f}% 높음 📈</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="price-badge low">💸 생활물가 서울 평균 대비 -{abs(pr):.1f}% 낮음 📉</div>', unsafe_allow_html=True)

    # ── 바이브 앱 메트릭 그리드 ──
    rb = pct_badge(row["월세"], AVG_RENT, higher_is_better=False)
    pb = pct_badge(row["공원수"], AVG_PARK)
    lb = pct_badge(row["도서관수"], AVG_LIB)
    cb = pct_badge(row.get("기타문화공간수", row["문화시설수"]), AVG_CULTURE)

    metric_html = (
        '<div class="metric-grid">'
        f'<div class="metric-card"><div class="mlabel">🏠 평균 월세</div>'
        f'<div class="mvalue">{int(round(row["월세"]))}만원</div>'
        f'<div class="msub">원룸 기준 추정<br>서울 평균 <b>{AVG_RENT:.0f}만원</b></div>{rb}</div>'
        f'<div class="metric-card green"><div class="mlabel">🌳 공원 수</div>'
        f'<div class="mvalue">{int(row["공원수"])}개소</div>'
        f'<div class="msub">서울시 주요공원 기준<br>서울 평균 <b>{AVG_PARK:.1f}개</b></div>{pb}</div>'
        f'<div class="metric-card orange"><div class="mlabel">📚 공공도서관</div>'
        f'<div class="mvalue">{int(row["도서관수"])}개</div>'
        f'<div class="msub">구립·시립 포함<br>서울 평균 <b>{AVG_LIB:.1f}개</b></div>{lb}</div>'
        f'<div class="metric-card purple"><div class="mlabel">🎨 기타 문화공간</div>'
        f'<div class="mvalue">{int(row.get("기타문화공간수", row["문화시설수"]))}개</div>'
        f'<div class="msub">미술관·공연장·박물관 등<br>서울 평균 <b>{AVG_CULTURE:.1f}개</b></div>{cb}</div>'
        '</div>'
    )
    st.markdown(metric_html, unsafe_allow_html=True)

    # ── 추천 점수 바 (바이브 앱) ──
    bar_col_score = THEME_COLORS[rank_in_top-1] if rank_in_top and rank_in_top<=5 else "#3498db"
    st.markdown(f"""
    <div class="score-bar-wrap">
        <div class="score-bar-label">✨ 종합 추천 점수</div>
        <div class="score-bar-bg"><div class="score-bar-fill" style="width:{s100:.0f}%;background:{bar_col_score};"></div></div>
        <div class="score-bar-val">{s100:.0f}점</div>
    </div>""", unsafe_allow_html=True)

    # ── 역 태그 (바이브 앱) ──
    station_list = VIBE_DATA["지하철역_예시"][DISTRICTS.index(detail_district)]
    st.markdown("**🚉 주변 주요역**")
    tags_html = "".join(f'<span class="station-tag">{s.strip()}</span>' for s in station_list.split(","))
    st.markdown(f'<div class="station-tags">{tags_html}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── 코딩 앱 상세 분석 ──
    a,b,c,d = st.columns(4)
    a.metric("예상 월세", f"{int(round(row['월세']))}만 원", f"{int(round(row['월세']-seoul_avg_rent)):+d}만 원 vs 서울 평균")
    b.metric("생활물가 평균", f"{int(round(row['생활물가평균'])):,}원")
    c.metric("가성비 지수", f"{int(round(row['가성비지수']))}")
    d.metric("밤길 안심 점수", f"{int(round(row['안심점수']*100))}점")

    left, right = st.columns([1.05, 1])
    with left:
        st.markdown(f"<div class='soft-box'><b>💬 자취생 한 줄 평</b><br>{DISTRICT_REVIEWS.get(detail_district,'')}</div>", unsafe_allow_html=True)
        st.markdown("#### 🚇 현재 교통 관점에서 보면")
        gbd,_ = current_destination_bucket(detail_district,"강남")
        ybd,_ = current_destination_bucket(detail_district,"여의도")
        cbd,_ = current_destination_bucket(detail_district,"종로")
        c1,c2,c3 = st.columns(3)
        c1.metric("강남권",gbd); c2.metric("여의도권",ybd); c3.metric("종로·시청권",cbd)
        transport_text = transport_mismatch_reason(detail_district,university,work_place,preferred_lines,district_lines_map)
        st.markdown(f"<div class='warn-box'><b>🚦 교통 비추천 포인트도 같이 보기</b><br>{transport_text}</div>", unsafe_allow_html=True)
        st.markdown("**지하철 노선**")
        st.markdown(chip_html(district_lines_map.get(detail_district,[]), dark=True), unsafe_allow_html=True)
        st.write(f"지하철역 수: **{int(row['지하철역수'])}개** &nbsp;|&nbsp; 혼잡도: **{row['혼잡도설명']}**")
        stations = subway_df[subway_df["자치구"]==detail_district][["호선","역명"]].drop_duplicates().sort_values(["호선","역명"])
        if not stations.empty:
            st.markdown("**대표 역**")
            st.dataframe(stations.head(12), use_container_width=True, hide_index=True)
    with right:
        st.markdown("#### 🎭 이 동네 문화생활은 어떤 편일까?")
        district_culture = culture_type_top_df[culture_type_top_df["자치구"]==detail_district][["문화유형","개수"]].head(6)
        if not district_culture.empty:
            fig = px.bar(district_culture, x="문화유형", y="개수", color="문화유형",
                         title="많이 분포한 문화생활 종류",
                         color_discrete_sequence=["#253F52","#F9852D","#F2C84B","#9CBA7B","#68A595","#94A3B8"])
            fig.update_layout(height=320, showlegend=False, margin=dict(l=10,r=10,t=55,b=10))
            st.plotly_chart(fig, use_container_width=True)
        culture_ex = culture_df[culture_df["자치구"]==detail_district][["문화유형","문화시설명","주소"]].dropna().head(8)
        if not culture_ex.empty:
            st.markdown("**대표 시설과 위치**")
            st.dataframe(culture_ex, use_container_width=True, hide_index=True)
        parks_ex = parks_df[parks_df["지역"]==detail_district][["공원명","공원주소"]].head(5)
        libs_ex  = library_df[library_df["구명"]==detail_district][["도서관명","주소"]].head(5)
        if not parks_ex.empty:
            st.markdown("**대표 공원 / 산책 포인트**")
            st.dataframe(parks_ex, use_container_width=True, hide_index=True)
        if not libs_ex.empty:
            st.markdown("**대표 도서관 / 공부환경**")
            st.dataframe(libs_ex, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════
# 페이지 3: 비교 분석
# ════════════════════════════════════════════════════════════════════════
elif st.session_state.active_page == "비교 분석":
    st.markdown("### 🆚 자치구 비교 분석")
    st.caption("최대 3곳까지 비교할 수 있어요. 그래프 대신 실제 의사결정에 도움 되는 요약으로 구성했어요.")
    compare_choices = st.multiselect("비교할 자치구 선택 (최대 3개)", work_df["자치구"].tolist(),
                                     default=work_df["자치구"].tolist()[:2], max_selections=3)
    if compare_choices:
        comp = base_df[base_df["자치구"].isin(compare_choices)].copy()
        comp_scored = score_recommendations(comp, university, work_place, preferred_lines, order, district_lines_map, selected_line_vibe)
        comp_s_max = comp_scored["총평점"].max(); comp_s_min = comp_scored["총평점"].min()

        st.markdown("#### 1) 한눈에 보는 선택 포인트")
        compare_cols = st.columns(len(compare_choices))
        for idx, district in enumerate(compare_choices):
            r = comp_scored.set_index("자치구").loc[district]
            s100 = to_100(r["총평점"], comp_s_min, comp_s_max)
            uni_match = "통학 추천권" if university!="선택 안 함" and district in DEFAULT_UNI_TO_DISTRICTS.get(university,[]) else "통학 일반권"
            work_match = "출퇴근 추천권" if work_place!="선택 안 함" and district in WORK_TO_DISTRICTS.get(work_place,[]) else "출퇴근 일반권"
            overlap = sorted(list(set(district_lines_map.get(district,[])).intersection(preferred_lines)))
            overlap_text = ", ".join(overlap[:3]) if overlap else "직결 노선 적음"
            compare_cols[idx].markdown(f"""
            <div class="compare-card">
                <div class="section-title">{district} <span style="color:#3b82f6;font-size:1rem;">{s100:.0f}점</span></div>
                <b>월세</b> {int(round(r['월세']))}만 원<br>
                <b>생활물가</b> {int(round(r['생활물가평균'])):,}원<br>
                <b>지하철 노선</b> {format_lines(district_lines_map.get(district,[]))}<br>
                <b>학교 기준</b> {uni_match}<br><b>근무지 기준</b> {work_match}<br>
                <b>희망 노선 일치</b> {overlap_text}<br>
                <b>밤길 안심</b> {int(round(r['안심점수']*100))}점
            </div>""", unsafe_allow_html=True)

        st.markdown("#### 2) 추천 점수 비교")
        bar_data = pd.DataFrame({"자치구":compare_choices,
            "100점":[to_100(comp_scored.set_index("자치구").loc[d,"총평점"],comp_s_min,comp_s_max) for d in compare_choices]})
        fig = px.bar(bar_data, x="자치구", y="100점", text="100점", color="자치구",
                     color_discrete_sequence=THEME_COLORS)
        fig.update_traces(texttemplate="%{text:.0f}점", textposition="outside")
        fig.update_layout(height=320, showlegend=False, yaxis_range=[0,120], margin=dict(l=10,r=10,t=30,b=10))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 3) 어디가 더 가까운가?")
        commute_rows = []
        for district in compare_choices:
            gbd,_ = current_destination_bucket(district,"강남")
            ybd,_ = current_destination_bucket(district,"여의도")
            cbd,_ = current_destination_bucket(district,"종로")
            commute_rows.append({"자치구":district,
                "학교 추천권":"O" if university!="선택 안 함" and district in DEFAULT_UNI_TO_DISTRICTS.get(university,[]) else "-",
                "근무지 추천권":"O" if work_place!="선택 안 함" and district in WORK_TO_DISTRICTS.get(work_place,[]) else "-",
                "강남권 체감 이동":gbd,"여의도권 체감 이동":ybd,"종로권 체감 이동":cbd,
                "교통 비추천 이유":transport_mismatch_reason(district,university,work_place,preferred_lines,district_lines_map)})
        st.dataframe(pd.DataFrame(commute_rows), use_container_width=True, hide_index=True)

        st.markdown("#### 4) 자취 선배들의 생활 팁")
        tip_rows = []
        for district in compare_choices:
            type_df = culture_type_top_df[culture_type_top_df["자치구"]==district][["문화유형","개수"]].head(2)
            culture_summary = ", ".join(type_df["문화유형"].tolist()) if not type_df.empty else "문화시설 정보 적음"
            tip_rows.append({"자치구":district,"주요 문화생활":culture_summary,"한 줄 팁":DISTRICT_REVIEWS.get(district,"")})
        st.dataframe(pd.DataFrame(tip_rows), use_container_width=True, hide_index=True)
    else:
        st.info("비교할 자치구를 1곳 이상 선택해 주세요.")

# ════════════════════════════════════════════════════════════════════════
# 페이지 4: 체크리스트 저장
# ════════════════════════════════════════════════════════════════════════
else:
    st.markdown("### ✅ 초보 자취생 체크리스트 저장")
    st.caption("방 보러 갈 때 필요한 항목과 현재 추천 결과를 함께 저장해 둘 수 있어요.")
    if selected_checklist:
        st.markdown("\n".join([f"- {x}" for x in selected_checklist]))
    else:
        st.info("왼쪽 체크리스트에서 항목을 선택해 보세요.")
    summary_text = (
        f"[서울, 처음이니? : 어디서 자취할까?]\n"
        f"- 우선순위: {' > '.join(order)}\n"
        f"- 희망 월세: {rent_band}\n"
        f"- 재학 중인 대학교: {university}\n"
        f"- 근무지: {work_place}\n"
        f"- 희망 노선: {', '.join(preferred_lines) if preferred_lines else '없음'}\n"
        f"- 호선 우선 추천: {selected_line_vibe}\n"
        f"- 추천 TOP5: {', '.join(top5_names)}\n"
        f"- 체크리스트:\n  • " + "\n  • ".join(selected_checklist if selected_checklist else ["선택 항목 없음"])
    )
    summary_payload = {
        "site":"서울, 처음이니? : 어디서 자취할까?",
        "priority_order":order,"rent_band":rent_band,
        "university":university,"work_place":work_place,
        "preferred_lines":preferred_lines,"vibe_line":selected_line_vibe,
        "top_recommendations":top5_names,"selected_checklist":selected_checklist,
    }
    st.download_button("TXT로 저장", data=summary_text, file_name="seoul_starter_checklist.txt", mime="text/plain", use_container_width=True)
    st.download_button("JSON으로 저장", data=json.dumps(summary_payload,ensure_ascii=False,indent=2), file_name="seoul_starter_settings.json", mime="application/json", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# 푸터
# ════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer-note">
※ 서울 생활물가 평균은 업로드된 생필품 가격 데이터의 최신 월 기준 자치구 평균을 다시 평균낸 참고값이에요.<br>
※ 밤길 안심 점수는 공원·도서관·거주비 부담을 함께 본 대리지표이며, 실제 범죄 통계와 동일하지 않아요.<br>
※ 교통 평가는 현재 노선망과 혼잡도 대리지표를 바탕으로 했고, 미래 가치 가산점은 반영하지 않았어요.<br>
※ 추천 점수는 100점 만점으로 환산한 상대 점수예요. 평균 월세는 추정치이며 전월세 실거래 데이터 미반영.
</div>
""", unsafe_allow_html=True)
