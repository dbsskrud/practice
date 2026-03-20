import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import textwrap

st.set_page_config(page_title="서울 스타터 v3.0", layout="wide", page_icon="🏠")

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp { background: #0f1117; color: #f0f0f0; }
.info-panel {
    background: linear-gradient(145deg, #1a2035, #0f1525);
    border: 1px solid #2a3a5c;
    border-radius: 16px;
    overflow: hidden;
}
.info-header {
    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
    padding: 20px;
}
.info-body { padding: 20px; }
.quote-box {
    background: rgba(79,172,254,0.08);
    border-left: 4px solid #4facfe;
    padding: 10px;
    border-radius: 8px;
}
.stat-card {
    background: rgba(74,144,217,0.08);
    border: 1px solid rgba(74,144,217,0.2);
    border-radius: 10px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- 데이터 ----------------
@st.cache_data
def load_data():
    data = {
        '자치구': ['강남구','마포구','송파구','관악구','노원구'],
        '평균월세': [95,85,88,60,60],
        '생활물가': [7361,6705,7098,6629,6837],
        '공원수': [7,5,7,2,2],
        '문화': [115,53,62,21,33],
        '한줄평': [
            "비싸지만 최고의 인프라",
            "핫플의 중심",
            "주거 안정 + 인프라",
            "청년 성지",
            "조용한 주거지역"
        ],
        'lat':[37.49,37.56,37.50,37.46,37.65],
        'lon':[127.06,126.90,127.11,126.94,127.07]
    }
    return pd.DataFrame(data)

df = load_data()

# ---------------- 추천 로직 ----------------
df['score'] = (100 - df['평균월세']) + df['공원수']*5 + df['문화']
df = df.sort_values('score', ascending=False)

top3 = df.head(3)['자치구'].tolist()

# ---------------- 지도 ----------------
st.subheader("📍 서울 추천 지도")

fig = go.Figure()

for i, row in df.iterrows():
    color = "gold" if row['자치구']==top3[0] else "silver" if row['자치구']==top3[1] else "brown" if row['자치구']==top3[2] else "gray"

    fig.add_trace(go.Scattermapbox(
        lat=[row['lat']],
        lon=[row['lon']],
        mode='markers+text',
        text=row['자치구'],
        marker=dict(size=12, color=color),
    ))

fig.update_layout(
    mapbox=dict(style="carto-darkmatter", zoom=10, center={"lat":37.55,"lon":126.98}),
    margin=dict(l=0,r=0,t=0,b=0),
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- 상세 패널 ----------------
st.subheader("📊 상세 정보")

selected = st.selectbox("지역 선택", df['자치구'])

row = df[df['자치구']==selected].iloc[0]

html = textwrap.dedent(f"""
<div class="info-panel">
  <div class="info-header">
    <h2>{selected}</h2>
    <div class="quote-box">{row['한줄평']}</div>
  </div>

  <div class="info-body">
    <div class="stat-card">💰 월세: {row['평균월세']}만원</div>
    <div class="stat-card">🛒 물가: {row['생활물가']}</div>
    <div class="stat-card">🌳 공원: {row['공원수']}</div>
    <div class="stat-card">🏛 문화시설: {row['문화']}</div>
  </div>
</div>
""")

st.markdown(html, unsafe_allow_html=True)

# ---------------- TOP 5 ----------------
st.subheader("🏆 TOP 추천")

cols = st.columns(5)

for i, (_, r) in enumerate(df.head(5).iterrows()):
    with cols[i]:
        st.markdown(f"""
        **{i+1}위**  
        {r['자치구']}  
        💰 {r['평균월세']}만원  
        ⭐ {round(r['score'],1)}
        """)
