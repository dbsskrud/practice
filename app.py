import streamlit as st
import pandas as pd

# -------------------------
# 🎨 페이지 설정
# -------------------------
st.set_page_config(
    page_title="서울 자취 지역 추천",
    layout="wide"
)

# -------------------------
# 🎨 스타일 (CSS)
# -------------------------
st.markdown("""
<style>
.main-title {
    font-size:40px;
    font-weight:700;
}
.card {
    padding:20px;
    border-radius:15px;
    background-color:#f7f7f7;
    text-align:center;
}
.small-text {
    color:gray;
    font-size:14px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 🏠 타이틀
# -------------------------
st.markdown('<div class="main-title">🏠 서울 자취 지역 선택 가이드</div>', unsafe_allow_html=True)
st.write("원하는 조건을 선택하면 나에게 맞는 지역을 추천해드립니다.")

# -------------------------
# 📊 샘플 데이터
# -------------------------
data = pd.DataFrame({
    "district": ["마포구","마포구","마포구","강남구","강남구","관악구","성동구"],
    "type": ["지하철","공원","시장","지하철","편의시설","시장","공원"],
    "name": ["홍대입구역","망원공원","망원시장","강남역","코엑스","신림시장","서울숲"]
})

# -------------------------
# 🎛️ 사이드바
# -------------------------
st.sidebar.header("🔍 조건 선택")

selected_types = st.sidebar.multiselect(
    "시설 선택",
    ["지하철", "공원", "편의시설", "시장"],
    default=["지하철", "공원"]
)

# -------------------------
# 🟢 자치구 선택 버튼 UI
# -------------------------
st.subheader("📍 자치구 선택")

districts = data["district"].unique()
cols = st.columns(len(districts))

selected_district = st.session_state.get("district", districts[0])

for i, d in enumerate(districts):
    if cols[i].button(d):
        st.session_state["district"] = d
        selected_district = d

# -------------------------
# 📊 데이터 필터링
# -------------------------
filtered = data[
    (data["district"] == selected_district) &
    (data["type"].isin(selected_types))
]

# -------------------------
# 📈 점수 계산
# -------------------------
score_dict = {
    "지하철": 0,
    "공원": 0,
    "편의시설": 0,
    "시장": 0
}

for t in filtered["type"]:
    score_dict[t] += 1

# -------------------------
# 🎯 결과 영역
# -------------------------
st.markdown("---")
st.subheader(f"✨ {selected_district} 분석 결과")

# 카드 UI
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f'<div class="card">🚇<br><b>지하철</b><br>{score_dict["지하철"]}</div>', unsafe_allow_html=True)
col2.markdown(f'<div class="card">🌿<br><b>공원</b><br>{score_dict["공원"]}</div>', unsafe_allow_html=True)
col3.markdown(f'<div class="card">🏪<br><b>편의시설</b><br>{score_dict["편의시설"]}</div>', unsafe_allow_html=True)
col4.markdown(f'<div class="card">🛒<br><b>시장</b><br>{score_dict["시장"]}</div>', unsafe_allow_html=True)

# -------------------------
# 📊 차트
# -------------------------
st.markdown("### 📊 시설 분포")
chart_df = pd.DataFrame.from_dict(score_dict, orient="index", columns=["개수"])
st.bar_chart(chart_df)

# -------------------------
# 📋 리스트
# -------------------------
st.markdown("### 📋 시설 목록")
st.dataframe(filtered, use_container_width=True)

# -------------------------
# 💡 추천 메시지
# -------------------------
if score_dict["지하철"] >= 2:
    st.success("🚇 교통이 매우 편리한 지역입니다!")
elif score_dict["공원"] >= 2:
    st.success("🌿 자연환경이 좋은 지역입니다!")
elif score_dict["시장"] >= 2:
    st.success("🛒 생활비 절약에 유리한 지역입니다!")
else:
    st.info("📍 균형 잡힌 생활이 가능한 지역입니다.")
