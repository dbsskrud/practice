import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import textwrap  # ✅ 추가

# --- 페이지 설정 ---
st.set_page_config(page_title="서울 스타터 v3.0", layout="wide", page_icon="🏠")

# --- 커스텀 CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;600;700;900&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; }
.stApp { background: #0f1117; color: #f0f0f0; }
.info-panel { background: linear-gradient(145deg, #1a2035, #0f1525); border: 1px solid #2a3a5c; border-radius: 16px; overflow: hidden; }
.info-header { background: linear-gradient(135deg, #0f3460 0%, #16213e 100%); padding: 20px 24px; }
.info-body { padding: 20px 24px; }
.stat-card { background: rgba(74, 144, 217, 0.08); border: 1px solid rgba(74, 144, 217, 0.2); border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; }
.stat-label { font-size: 0.72rem; color: #7a8fa8; font-weight: 600; }
.stat-value { font-size: 1.4rem; font-weight: 800; color: #e8f4ff; }
.quote-box { background: rgba(79, 172, 254, 0.08); border-left: 4px solid #4facfe; padding: 14px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 데이터 ---
@st.cache_data
def load_data():
    data = {
        '자치구': ['강남구','마포구','송파구'],
        '평균월세': [95,85,88],
        '생활물가': [7361,6705,7098],
        '공원수': [7,5,7],
        '전체문화공간': [115,53,62],
        '도서관수': [17,6,12],
        '대표역': ['강남','홍대','잠실'],
        '한줄평': ["비싸지만 최고","핫플 중심","주거 안정"]
    }
    return pd.DataFrame(data)

df = load_data()

if 'selected_gu' not in st.session_state:
    st.session_state.selected_gu = '마포구'

st.title("서울 스타터")

gu = st.session_state.selected_gu
row = df[df['자치구'] == gu].iloc[0]

score_pct = 80
rank_badge_html = ""

# ✅ 여기만 수정됨 (dedent 적용)
st.markdown(textwrap.dedent(f"""
<div class="info-panel">
  <div class="info-header">
    <div>{gu}</div>
    {rank_badge_html}
    <div class="quote-box">{row['한줄평']}</div>
  </div>

  <div class="info-body">
    <div class="stat-card">
      <div class="stat-label">월세</div>
      <div class="stat-value">{row['평균월세']}만원</div>
    </div>

    <div class="stat-card">
      <div class="stat-label">생활물가</div>
      <div class="stat-value">{row['생활물가']}</div>
    </div>

    <div class="stat-card">
      <div class="stat-label">문화시설</div>
      <div class="stat-value">{row['전체문화공간']}</div>
    </div>

    <div class="stat-card">
      <div class="stat-label">공원</div>
      <div class="stat-value">{row['공원수']}</div>
    </div>

    <div class="stat-card">
      <div class="stat-label">대표역</div>
      <div class="stat-value">{row['대표역']}</div>
    </div>

    <div class="stat-card">
      <div class="stat-label">점수</div>
      <div style="background:#1a2a3a; border-radius:6px; height:8px;">
        <div style="width:{score_pct}%; height:100%; background:#4facfe;"></div>
      </div>
    </div>
  </div>
</div>
"""), unsafe_allow_html=True)

selected = st.selectbox("지역 선택", df['자치구'])
if selected != gu:
    st.session_state.selected_gu = selected
    st.rerun()
