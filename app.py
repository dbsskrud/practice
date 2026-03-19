import folium
from streamlit_folium import st_folium
import pandas as pd

st.subheader("🗺️ 자치구별 CRI 위험 지도")

# ------------------------
# 샘플 데이터 (추후 실제 데이터로 교체 가능)
# ------------------------
data = pd.DataFrame({
    "district": ["강북구", "중구", "서초구", "강서구"],
    "lat": [37.6396, 37.5636, 37.4837, 37.5509],
    "lon": [127.0256, 126.9975, 127.0324, 126.8495],
    "pm25": [80, 75, 35, 30],
    "temp": [0, 2, 5, 6],
    "humidity": [30, 35, 50, 55]
})

# ------------------------
# CRI 계산 적용
# ------------------------
data["CRI"] = data.apply(
    lambda row: calculate_cri(row["pm25"], row["temp"], row["humidity"], w1, w2, w3),
    axis=1
)

# ------------------------
# 색상 매핑 함수
# ------------------------
def get_color(cri):
    if cri < 30:
        return "green"
    elif cri < 70:
        return "yellow"
    elif cri < 120:
        return "orange"
    else:
        return "red"

# ------------------------
# 지도 생성
# ------------------------
m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)

for _, row in data.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=10,
        color=get_color(row["CRI"]),
        fill=True,
        fill_opacity=0.7,
        popup=f"""
        <b>{row['district']}</b><br>
        CRI: {row['CRI']:.2f}<br>
        PM2.5: {row['pm25']}<br>
        Temp: {row['temp']}°C<br>
        Humidity: {row['humidity']}%
        """
    ).add_to(m)

# ------------------------
# 지도 출력
# ------------------------
st_folium(m, width=700, height=500)
