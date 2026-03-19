import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("🏠 서울 자취 지역 선택 가이드")
st.write("원하는 자치구와 시설을 선택하세요")

# -------------------------
# 📊 샘플 데이터 (실제 데이터 대신)
# -------------------------

data = pd.DataFrame({
    "name": ["홍대입구역", "서울숲", "망원시장", "공공도서관"],
    "lat": [37.557, 37.544, 37.556, 37.55],
    "lon": [126.924, 127.037, 126.905, 126.92],
    "type": ["지하철", "공원", "시장", "편의시설"],
    "district": ["마포구", "성동구", "마포구", "마포구"]
})

# -------------------------
# 🎛️ 사이드바 UI
# -------------------------

st.sidebar.header("🔍 필터")

districts = data["district"].unique()
selected_district = st.sidebar.selectbox("자치구 선택", districts)

facility_types = ["지하철", "공원", "편의시설", "시장"]
selected_types = st.sidebar.multiselect(
    "시설 선택", facility_types, default=facility_types
)

# -------------------------
# 📍 데이터 필터링
# -------------------------

filtered = data[
    (data["district"] == selected_district) &
    (data["type"].isin(selected_types))
]

# -------------------------
# 🗺️ 지도 생성
# -------------------------

m = folium.Map(location=[37.55, 126.98], zoom_start=12)

for _, row in filtered.iterrows():
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=f"{row['name']} ({row['type']})"
    ).add_to(m)

st.subheader(f"📍 {selected_district} 시설 지도")

st_folium(m, width=800, height=500)

# -------------------------
# 📋 리스트 출력
# -------------------------

st.subheader("📋 선택된 시설 목록")
st.dataframe(filtered)
