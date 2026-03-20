import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# --- 페이지 설정 ---
st.set_page_config(page_title="서울 스타터 v3.0", layout="wide", page_icon="🏠")

# --- 커스텀 CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700;900&display=swap');

* { font-family: 'Noto Sans KR', sans-serif !important; }

.stApp { background: #0f1117; color: #f0f0f0; }

.top-header {
    background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #2a3a5c;
    border-radius: 16px;
    padding: 20px 28px;
    margin-bottom: 16px;
}

.rank-card {
    background: linear-gradient(145deg, #1e2535, #16213e);
    border: 1px solid #2a3a5c;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    transition: transform 0.2s, border-color 0.2s;
    cursor: pointer;
}
.rank-card:hover { transform: translateY(-3px); border-color: #4a90d9; }

.rank-badge-1 { color: #FFD700; font-size: 1.4rem; font-weight: 900; }
.rank-badge-2 { color: #C0C0C0; font-size: 1.3rem; font-weight: 900; }
.rank-badge-3 { color: #CD7F32; font-size: 1.2rem; font-weight: 900; }

.info-panel {
    background: linear-gradient(145deg, #1a2035, #0f1525);
    border: 1px solid #2a3a5c;
    border-radius: 16px;
    padding: 0;
    overflow: hidden;
}

.info-header {
    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
    padding: 20px 24px;
    border-bottom: 1px solid #2a3a5c;
}

.info-body { padding: 20px 24px; }

.stat-card {
    background: rgba(74, 144, 217, 0.08);
    border: 1px solid rgba(74, 144, 217, 0.2);
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}

.stat-label {
    font-size: 0.72rem;
    color: #7a8fa8;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.stat-value {
    font-size: 1.4rem;
    font-weight: 800;
    color: #e8f4ff;
    line-height: 1.2;
}

.stat-sub {
    font-size: 0.75rem;
    color: #7a8fa8;
    margin-top: 2px;
}

.quote-box {
    background: linear-gradient(135deg, rgba(79, 172, 254, 0.08), rgba(0, 242, 254, 0.05));
    border-left: 4px solid #4facfe;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 14px 0;
    font-size: 0.88rem;
    color: #b8d4f0;
    line-height: 1.6;
    font-style: italic;
}

.metro-tag {
    display: inline-block;
    background: rgba(74, 144, 217, 0.15);
    border: 1px solid rgba(74, 144, 217, 0.3);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.73rem;
    color: #7eb8e8;
    margin: 2px;
}

.section-title {
    font-size: 0.72rem;
    color: #5a7fa0;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.section-title::before {
    content: '';
    display: inline-block;
    width: 18px;
    height: 2px;
    background: #4a90d9;
}

.priority-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}

.priority-num {
    background: linear-gradient(135deg, #4a90d9, #7b68ee);
    color: white;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 800;
    flex-shrink: 0;
}

.top5-container {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-top: 8px;
}

.top5-card {
    background: linear-gradient(145deg, #1e2535, #16213e);
    border: 1px solid #2a3a5c;
    border-radius: 14px;
    padding: 16px 12px;
    text-align: center;
}
.top5-card.gold { border-color: rgba(255, 215, 0, 0.4); background: linear-gradient(145deg, #2a2510, #1e1c0a); }
.top5-card.silver { border-color: rgba(192,192,192,0.35); background: linear-gradient(145deg, #222325, #181a1c); }
.top5-card.bronze { border-color: rgba(205,127,50,0.4); background: linear-gradient(145deg, #261d10, #1c150a); }

h1 { color: #e8f4ff !important; }

div[data-testid="stSelectbox"] label,
div[data-testid="stSlider"] label,
.stMarkdown p { color: #c0d8f0 !important; }

.stSelectbox select, div[data-baseweb="select"] {
    background: #1a2035 !important;
    border-color: #2a3a5c !important;
    color: #e0ecff !important;
}

div[data-testid="metric-container"] {
    background: rgba(74,144,217,0.08);
    border-radius: 10px;
    padding: 10px !important;
    border: 1px solid rgba(74,144,217,0.2);
}
</style>
""", unsafe_allow_html=True)

# --- 서울 GeoJSON (구별 경계) ---
@st.cache_data
def load_geojson():
    import urllib.request
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return json.loads(response.read().decode())
    except:
        return None

# --- 데이터 ---
@st.cache_data
def load_data():
    data = {
        '자치구': ['강남구','강동구','강북구','강서구','관악구','광진구','구로구','금천구','노원구','도봉구',
                  '동대문구','동작구','마포구','서대문구','서초구','성동구','성북구','송파구','양천구','영등포구',
                  '용산구','은평구','종로구','중구','중랑구'],
        '호선': [
            '2,3,7,9', '5,8', '4', '5,9', '2', '2,5,7', '1,2,7', '1,7', '4,6,7', '1,7',
            '1,2,5', '1,2,4,9', '2,5,6', '2,3', '2,3', '2,5', '4,6', '2,8,9', '5,9', '2,5,9',
            '1,4,6', '3,6', '1,3,5', '2,4', '5,7'
        ],
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
        '대표역': [
            '강남·역삼', '천호·강동', '수유·미아', '발산·화곡', '서울대입구·신림', '건대입구·강변',
            '신도림·구로', '가산디지털단지', '노원·상계', '창동·도봉산',
            '회기·청량리', '노량진·사당', '홍대입구·망원', '신촌·이대', '교대·양재', '왕십리·성수',
            '성신여대입구·한성대', '잠실·석촌', '목동·오목교', '여의도·당산',
            '이태원·한남', '연신내·불광', '혜화·종로3가', '명동·을지로', '상봉·중랑'
        ],
        'lat': [37.4959,37.5492,37.6469,37.5658,37.4654,37.5481,37.4954,37.4601,37.6544,37.6659,
                37.5838,37.5029,37.5623,37.5820,37.4769,37.5506,37.6061,37.5048,37.5271,37.5206,
                37.5311,37.6176,37.5991,37.5579,37.5954],
        'lon': [127.0664,127.1465,127.0147,126.8223,126.9436,127.0857,126.8581,126.9002,127.0772,127.0318,
                127.0507,126.9427,126.9088,126.9356,127.0122,127.0409,127.0232,127.1145,126.8565,126.9139,
                126.9811,126.9227,126.9861,126.9942,127.0922]
    }
    df = pd.DataFrame(data)
    avg_price = df['생활물가'].mean()
    df['물가비율'] = ((df['생활물가'] / avg_price) - 1) * 100
    for col, hig in [('평균월세', False), ('생활물가', False), ('전체문화공간', True), ('공원수', True)]:
        mn, mx = df[col].min(), df[col].max()
        df[f'norm_{col}'] = (df[col] - mn) / (mx - mn) if hig else (mx - df[col]) / (mx - mn)
    return df

df = load_data()

LINE_COLORS = {
    '1': '#0052A4', '2': '#009246', '3': '#EF7C1C', '4': '#00A4E3',
    '5': '#996CAC', '6': '#CD7C2F', '7': '#747F00', '8': '#E6186C', '9': '#BDB092'
}
LINE_NAMES = {
    '1': '1호선', '2': '2호선', '3': '3호선', '4': '4호선',
    '5': '5호선', '6': '6호선', '7': '7호선', '8': '8호선', '9': '9호선'
}

# --- 세션 상태 ---
if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '마포구'

# ============================================================
# 상단 헤더
# ============================================================
st.markdown("""
<div style="margin-bottom:20px;">
  <h1 style="font-size:2rem; font-weight:900; margin:0; 
    background: linear-gradient(90deg, #4facfe, #00f2fe);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
    🚀 서울 스타터 v3.0
  </h1>
  <p style="color:#7a8fa8; margin:4px 0 0; font-size:0.85rem; letter-spacing:0.05em;">
    20-30대를 위한 서울 첫 자취 지역 추천 가이드
  </p>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    col_input1, col_input2 = st.columns([1, 1.8])

    # ── 1. 호선 선택 ──────────────────────────────────────────
    with col_input1:
        st.markdown("##### 🚇 호선으로 찾기")
        line_options = ['선택 안 함'] + [f'{k}호선' for k in sorted(LINE_COLORS.keys())]
        selected_line = st.selectbox("자주 이용할 지하철 호선을 선택하세요.", line_options)

        if selected_line != '선택 안 함':
            line_num = selected_line.replace('호선', '')
            mask = df['호선'].str.split(',').apply(lambda lst: line_num in lst)
            matched = df[mask]['자치구'].tolist()
            if matched:
                st.caption(f"🔍 {selected_line} 경유 구: **{'  |  '.join(matched)}**")
            else:
                matched = df['자치구'].tolist()
        else:
            matched = df['자치구'].tolist()

    # ── 2. 우선순위 설정 ──────────────────────────────────────
    with col_input2:
        st.markdown("##### ⚖️ 주거 우선순위 설정")
        priority_options = ['월세 저렴', '생활물가 저렴', '문화시설 풍부', '녹지/공원 풍부']
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)

        with col_p1:
            st.caption("🥇 1순위")
            p1 = st.selectbox("1순위", priority_options, index=0, label_visibility="collapsed")
        remaining2 = [x for x in priority_options if x != p1]
        with col_p2:
            st.caption("🥈 2순위")
            p2 = st.selectbox("2순위", remaining2, index=0, label_visibility="collapsed")
        remaining3 = [x for x in remaining2 if x != p2]
        with col_p3:
            st.caption("🥉 3순위")
            p3 = st.selectbox("3순위", remaining3, index=0, label_visibility="collapsed")
        remaining4 = [x for x in remaining3 if x != p3]
        with col_p4:
            st.caption("4️⃣ 4순위")
            p4 = st.selectbox("4순위", remaining4, index=0, label_visibility="collapsed")

# 우선순위 → 가중치 (4:3:2:1)
priority_weight_map = {
    '월세 저렴': 'norm_평균월세',
    '생활물가 저렴': 'norm_생활물가',
    '문화시설 풍부': 'norm_전체문화공간',
    '녹지/공원 풍부': 'norm_공원수',
}
weights = {priority_weight_map[p1]: 4, priority_weight_map[p2]: 3,
           priority_weight_map[p3]: 2, priority_weight_map[p4]: 1}

df['total_score'] = sum(df[col] * w for col, w in weights.items())

# 호선 필터 적용 후 추천
filtered_df = df[df['자치구'].isin(matched)].copy()
recommended_df = filtered_df.sort_values('total_score', ascending=False)
top3_gu = recommended_df.head(3)['자치구'].tolist()
top5_df = recommended_df.head(5)

# ============================================================
# 메인: 지도 + 상세정보
# ============================================================
col_map, col_info = st.columns([1.5, 1])

with col_map:
    st.markdown("##### 📍 서울 자치구 지도")

    geojson = load_geojson()

    # 점수 레이어 (choropleth 스타일)
    # top3 강조 색상
    def get_color_score(row):
        if row['자치구'] in top3_gu:
            rank = top3_gu.index(row['자치구'])
            return [4, 3, 2][rank]
        return 0

    df['map_highlight'] = df.apply(get_color_score, axis=1)
    df['map_label'] = df['자치구'].apply(
        lambda x: f"🥇 {x}" if x == top3_gu[0] else (f"🥈 {x}" if x == top3_gu[1] else (f"🥉 {x}" if x == top3_gu[2] else x))
    )

    # GeoJSON choropleth
    if geojson:
        fig = go.Figure()

        # 전체 구 경계 + 음영
        for feature in geojson['features']:
            gu_name = feature['properties'].get('name', '')
            if gu_name in top3_gu:
                rank = top3_gu.index(gu_name)
                fill_colors = ['rgba(255,215,0,0.30)', 'rgba(192,192,192,0.22)', 'rgba(205,127,50,0.22)']
                line_colors = ['rgba(255,215,0,0.9)', 'rgba(200,200,200,0.8)', 'rgba(205,127,50,0.8)']
                fill_color = fill_colors[rank]
                line_color = line_colors[rank]
                line_width = 2.5
            else:
                fill_color = 'rgba(42,58,92,0.25)'
                line_color = 'rgba(74,144,217,0.35)'
                line_width = 0.8

            geom = feature['geometry']
            polys = geom['coordinates'] if geom['type'] == 'Polygon' else [c for c in geom['coordinates']]
            if geom['type'] == 'Polygon':
                polys = [geom['coordinates']]
            else:
                polys = geom['coordinates']

            for poly in polys:
                ring = poly[0]
                lons = [p[0] for p in ring]
                lats = [p[1] for p in ring]
                fig.add_trace(go.Scattermapbox(
                    lon=lons + [lons[0]],
                    lat=lats + [lats[0]],
                    mode='lines',
                    fill='toself',
                    fillcolor=fill_color,
                    line=dict(color=line_color, width=line_width),
                    hoverinfo='skip',
                    showlegend=False
                ))

        # 구 이름 마커
        row_data = df[df['자치구'].isin(top3_gu)]
        row_other = df[~df['자치구'].isin(top3_gu)]

        fig.add_trace(go.Scattermapbox(
            lat=row_other['lat'], lon=row_other['lon'],
            text=row_other['자치구'],
            mode='text',
            textfont=dict(size=9, color='rgba(180,200,230,0.75)'),
            hoverinfo='skip', showlegend=False
        ))

        medals = ['🥇', '🥈', '🥉']
        medal_colors = ['#FFD700', '#C0C0C0', '#CD7F32']
        for i, (_, r) in enumerate(top3_gu_df := df[df['자치구'].isin(top3_gu)].set_index('자치구').loc[top3_gu].reset_index().iterrows()):
            fig.add_trace(go.Scattermapbox(
                lat=[r['lat']], lon=[r['lon']],
                text=[f"{medals[i]} {r['자치구']}"],
                mode='markers+text',
                marker=dict(size=14, color=medal_colors[i], opacity=0.85),
                textfont=dict(size=11, color=medal_colors[i]),
                textposition='top center',
                hovertemplate=f"<b>{r['자치구']}</b><br>추천점수: {r['total_score']:.2f}<br>월세: {r['평균월세']}만원<extra></extra>",
                showlegend=False
            ))

        fig.update_layout(
            mapbox=dict(
                style="carto-darkmatter",
                zoom=10.0,
                center={"lat": 37.555, "lon": 126.985}
            ),
            margin=dict(r=0, t=0, l=0, b=0),
            height=520,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
    else:
        # fallback: scatter
        df['marker_size'] = df['자치구'].apply(lambda x: 18 if x in top3_gu else 8)
        df['marker_color'] = df['자치구'].apply(
            lambda x: '#FFD700' if x == top3_gu[0] else ('#C0C0C0' if x == top3_gu[1] else ('#CD7F32' if x == top3_gu[2] else '#2a4870'))
        )
        fig = go.Figure()
        fig.add_trace(go.Scattermapbox(
            lat=df['lat'], lon=df['lon'], text=df['자치구'],
            mode='markers+text',
            marker=dict(size=df['marker_size'], color=df['marker_color']),
            textfont=dict(size=9, color='#b8cce0'),
            textposition='top center',
            hovertemplate='<b>%{text}</b><extra></extra>',
        ))
        fig.update_layout(
            mapbox=dict(style="carto-darkmatter", zoom=10.0, center={"lat": 37.555, "lon": 126.985}),
            margin=dict(r=0, t=0, l=0, b=0), height=520,
            paper_bgcolor='rgba(0,0,0,0)',
        )

    select_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    if select_event and select_event.selection and select_event.selection.points:
        pt = select_event.selection.points[0]
        hover = pt.get('hovertext') or pt.get('text', '')
        for gu_name in df['자치구'].tolist():
            if gu_name in hover:
                st.session_state.selected_gu = gu_name
                break

    # 지도 범례
    st.markdown("""
    <div style="display:flex; gap:16px; margin-top:6px; font-size:0.78rem; color:#7a8fa8;">
      <span>🥇 1순위 추천</span>
      <span>🥈 2순위 추천</span>
      <span>🥉 3순위 추천</span>
      <span style="color:#4a90d9">· 경계선: 자치구 구분</span>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 우측 상세 정보 패널
# ============================================================
with col_info:
    gu = st.session_state.selected_gu
    if gu not in df['자치구'].values:
        gu = '마포구'
    row = df[df['자치구'] == gu].iloc[0]

    rank_label = ""
    if gu in top3_gu:
        rank_label = ["🥇 1순위 추천", "🥈 2순위 추천", "🥉 3순위 추천"][top3_gu.index(gu)]

    price_icon = "📈" if row['물가비율'] > 0 else "📉"
    price_text = f"평균 대비 {abs(row['물가비율']):.1f}% {'높음' if row['물가비율'] > 0 else '낮음'}"

    # 호선 태그
    lines = row['호선'].split(',')
    line_tags = ''.join([
        f'<span style="display:inline-block; background:{LINE_COLORS.get(l, "#333")}; '
        f'color:white; border-radius:20px; padding:2px 10px; font-size:0.7rem; '
        f'font-weight:700; margin:2px;">{l}호선</span>'
        for l in lines
    ])

    # 점수 프로그레스바 계산
    score_max = df['total_score'].max()
    score_pct = int(row['total_score'] / score_max * 100)

    rank_badge_html = ""
    if rank_label:
        rank_badge_html = f"<div style='background:rgba(255,215,0,0.15);border:1px solid rgba(255,215,0,0.4);border-radius:8px;padding:6px 12px;font-size:0.8rem;font-weight:700;color:#FFD700;text-align:center;'>{rank_label}</div>"

    st.markdown(f"""
    <div class="info-panel">
      <div class="info-header">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <div style="font-size:0.72rem; color:#4facfe; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:4px;">
              선택 지역
            </div>
            <div style="font-size:1.8rem; font-weight:900; color:#e8f4ff; line-height:1.1;">
              {gu}
            </div>
          </div>
          {rank_badge_html}
        </div>
        <div class="quote-box" style="margin-top:14px; margin-bottom:0;">
          {row['한줄평']}
        </div>
      </div>

      <div class="info-body">
        <div class="section-title">핵심 지표</div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px;">
          <div class="stat-card">
            <div class="stat-label">💰 평균 월세</div>
            <div class="stat-value">{row['평균월세']}<span style="font-size:1rem;color:#7a8fa8;">만원</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">🛒 생활물가 {price_icon}</div>
            <div class="stat-value" style="font-size:1.05rem;">{price_text}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">🏛 문화공간</div>
            <div class="stat-value">{row['전체문화공간']}<span style="font-size:0.85rem;color:#7a8fa8;">개소</span></div>
            <div class="stat-sub">도서관 {row['도서관수']}개 포함</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">🌳 공원 / 녹지</div>
            <div class="stat-value">{row['공원수']}<span style="font-size:0.85rem;color:#7a8fa8;">개소</span></div>
          </div>
        </div>

        <div class="section-title">지하철 노선</div>
        <div style="margin-bottom:14px;">{line_tags}</div>

        <div class="section-title">대표 역세권</div>
        <div style="font-size:0.85rem; color:#b8d4f0; margin-bottom:14px;">
          🚉 {row['대표역']}
        </div>

        <div class="section-title">추천 점수</div>
        <div style="background:rgba(74,144,217,0.08); border-radius:10px; padding:10px 14px; border:1px solid rgba(74,144,217,0.2);">
          <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:#7a8fa8; margin-bottom:5px;">
            <span>종합 추천 점수</span>
            <span style="color:#4facfe; font-weight:700;">{row['total_score']:.2f}점</span>
          </div>
          <div style="background:#1a2a3a; border-radius:6px; height:8px; overflow:hidden;">
            <div style="width:{score_pct}%; height:100%; background:linear-gradient(90deg,#4facfe,#00f2fe); border-radius:6px;"></div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 구 선택
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    all_gu = sorted(df['자치구'].tolist())
    selected_gu_box = st.selectbox("🔍 다른 지역구 보기", all_gu,
                                    index=all_gu.index(gu), key='gu_select_box')
    if selected_gu_box != gu:
        st.session_state.selected_gu = selected_gu_box
        st.rerun()

# ============================================================
# 하단 Top 5 추천
# ============================================================
st.markdown("---")
st.markdown("##### 🌟 우선순위 기반 추천 지역 Top 5")

priority_summary = f"**{p1}** → **{p2}** → **{p3}** → **{p4}**"
st.caption(f"현재 우선순위: {priority_summary}" + (f"  |  🚇 {selected_line} 경유 지역 기준" if selected_line != '선택 안 함' else "  |  전체 지역 기준"))

medal_styles = ['gold', 'silver', 'bronze', '', '']
medal_emojis = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
cols_top = st.columns(5)

for i, (_, r) in enumerate(top5_df.iterrows()):
    with cols_top[i]:
        is_top3 = i < 3
        border_color = ['rgba(255,215,0,0.5)', 'rgba(192,192,192,0.45)', 'rgba(205,127,50,0.5)', 'rgba(74,144,217,0.25)', 'rgba(74,144,217,0.2)'][i]
        bg = ['linear-gradient(145deg,#2a2510,#1e1c0a)', 'linear-gradient(145deg,#232325,#181a1c)',
              'linear-gradient(145deg,#261d10,#1c150a)', 'linear-gradient(145deg,#1e2535,#16213e)',
              'linear-gradient(145deg,#1c2230,#141b2a)'][i]
        name_color = ['#FFD700', '#C0C0C0', '#CD7F32', '#b8d4f0', '#9ab8d0'][i]

        # 이 구가 현재 선택된 구인지 확인
        is_selected = r['자치구'] == st.session_state.selected_gu
        shadow_style = "box-shadow:0 0 12px rgba(79,172,254,0.25);" if is_selected else ""

        st.markdown(f"""
        <div style="
            background:{bg};
            border:1px solid {border_color};
            border-radius:14px;
            padding:16px 12px;
            text-align:center;
            {shadow_style}
        ">
          <div style="font-size:1.5rem; margin-bottom:4px;">{medal_emojis[i]}</div>
          <div style="font-size:1.05rem; font-weight:800; color:{name_color}; margin-bottom:8px;">{r['자치구']}</div>
          <div style="font-size:0.75rem; color:#7a8fa8; margin-bottom:4px;">월세</div>
          <div style="font-size:1.1rem; font-weight:700; color:#e8f4ff;">{r['평균월세']}<span style="font-size:0.75rem;color:#7a8fa8;">만</span></div>
          <div style="margin-top:8px; background:rgba(255,255,255,0.05); border-radius:6px; padding:4px 8px;">
            <span style="font-size:0.72rem; color:#4facfe; font-weight:700;">점수 {r['total_score']:.1f}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"상세보기", key=f"top5_btn_{i}", use_container_width=True):
            st.session_state.selected_gu = r['자치구']
            st.rerun()
