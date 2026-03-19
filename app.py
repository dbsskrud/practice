import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="서울 자취 지역 추천", layout="wide")

# -------------------------
# 🎨 스타일
# -------------------------
st.markdown("""
<style>
.main-title {
    font-size:38px;
    font-weight:700;
}
.card {
    padding:18px;
    border-radius:15px;
    background-color:#f5f5f5;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏠 서울 자취 지역 선택 가이드</div>', unsafe_allow_html=True)
st.write("자치구와 원하는 시설을 선택하면 지도와 함께 보여드립니다.")

# -------------------------
# 📊 서울 전체 자치구 리스트
# -------------------------
districts = [
    "강남구","강동구","강북구","강서구","관악구","광진구","구로구",
    "금천구","노원구","도봉구","동대문구","동작구","마포구",
    "서대문구","서초구","성동구","성북구","송파구","양천구",
    "영등포구","용산구","은평구","종로구","중구","중랑구"
]

# -------------------------
# 📊 샘플 좌표 데이터 (간단 버전)
# -------------------------
data = pd.DataFrame({
    "district": ["마포구","마포구","강남구","관악구","성동구","송파구"],
    "name": ["홍대입구역","망원공원","강남역","신림시장","서울숲","올림픽공원"],
    "lat": [37.557,37.556,37.497,37.484,37.544,37.516],
    "lon": [126.924,126.905,127.027,126.929,127.037,127.121],
    "type": ["지하철","공원","지하철","시장","공원","공원"]
})

# -------------------------
# 🎛️ 사이드바
# -------------------------
st.sidebar.header("🔍 조건 선택")

selected_district = st.sidebar.selectbox("자치구 선택", districts)

selected_types = st.sidebar.multiselect(
    "시설 선택",
    ["지하철","공원","편의시설","시장"],
    default=["지하철","공원"]
)

# -------------------------
# 📊 필터링
# -------------------------
filtered = data[
    (data["district"] == selected_district) &
    (data["type"].isin(selected_types))
]

# -------------------------
# 🎨 지도 생성
# -------------------------
st.subheader("🗺️ 지도")

m = folium.Map(location=[37.55, 126.98], zoom_start=11)

color_dict = {
    "지하철": "blue",
    "공원": "green",
    "시장": "red",
    "편의시설": "purple"
}

for _, row in filtered.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=8,
        popup=f"{row['name']} ({row['type']})",
        color=color_dict.get(row["type"], "gray"),
        fill=True
    ).add_to(m)

st_folium(m, width=900, height=500)

# -------------------------
# 📈 점수 계산
# -------------------------
score_dict = {"지하철":0,"공원":0,"편의시설":0,"시장":0}

for t in filtered["type"]:
    score_dict[t] += 1

# -------------------------
# 🎯 카드 UI
# -------------------------
st.subheader(f"✨ {selected_district} 분석")

col1, col2, col3, col4 = st.columns(4)

col1.markdown(f'<div class="card">🚇<br>{score_dict["지하철"]}</div>', unsafe_allow_html=True)
col2.markdown(f'<div class="card">🌿<br>{score_dict["공원"]}</div>', unsafe_allow_html=True)
col3.markdown(f'<div class="card">🏪<br>{score_dict["편의시설"]}</div>', unsafe_allow_html=True)
col4.markdown(f'<div class="card">🛒<br>{score_dict["시장"]}</div>', unsafe_allow_html=True)

# -------------------------
# 📊 차트
# -------------------------
st.bar_chart(pd.DataFrame.from_dict(score_dict, orient="index"))

# -------------------------
# 📋 리스트
# -------------------------
st.subheader("📋 시설 목록")
st.dataframe(filtered, use_container_width=True)

# -------------------------
# 💡 추천 메시지
# -------------------------
if score_dict["지하철"] >= 2:
    st.success("🚇 교통이 매우 좋은 지역입니다")
elif score_dict["공원"] >= 2:
    st.success("🌿 자연환경이 좋은 지역입니다")
elif score_dict["시장"] >= 1:
    st.success("🛒 생활비 절약에 유리한 지역입니다")
else:
    st.info("📍 기본적인 생활 인프라가 갖춰진 지역입니다")
