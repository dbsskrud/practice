import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

# ------------------------
# 기본 설정
# ------------------------
st.set_page_config(page_title="서울 대기질 CRI 분석기", layout="centered")

st.title("🌫️ 대기질 건강 위험도 분석 (CRI)")
st.markdown("미세먼지 + 기상 데이터를 기반으로 복합 위험지수(CRI)를 계산합니다.")

# ------------------------
# 사용자 입력
# ------------------------
st.sidebar.header("입력 변수")

pm25 = st.sidebar.number_input(
    "PM2.5 (μg/m³)", min_value=0.0, max_value=500.0, value=50.0, step=1.0
)

temp = st.sidebar.number_input(
    "기온 (°C)", min_value=-30.0, max_value=50.0, value=10.0, step=0.5
)

humidity = st.sidebar.number_input(
    "습도 (%)", min_value=0.1, max_value=100.0, value=50.0, step=1.0
)

st.sidebar.markdown("---")

w1 = st.sidebar.number_input("PM2.5 가중치", 0.0, 1.0, 0.5, step=0.05)
w2 = st.sidebar.number_input("기온 가중치", 0.0, 1.0, 0.3, step=0.05)
w3 = st.sidebar.number_input("습도 가중치", 0.0, 1.0, 0.2, step=0.05)

# ------------------------
# CRI 계산 함수
# ------------------------
def calculate_cri(pm25, temp, humidity, w1, w2, w3):
    temp = temp if temp != 0 else 0.1
    humidity = humidity if humidity != 0 else 0.1
    return (w1 * pm25) + (w2 * (1 / temp)) + (w3 * (1 / humidity))

cri_value = calculate_cri(pm25, temp, humidity, w1, w2, w3)

# ------------------------
# 결과 출력 (강화 UI)
# ------------------------
st.subheader("📊 분석 결과")

max_cri = 150
progress_value = min(cri_value / max_cri, 1.0)

st.metric("CRI 지수", round(cri_value, 2))
st.progress(progress_value)

# 위험 등급 표시
if cri_value < 30:
    st.success("🟢 낮음: 일상 활동 가능")
    st.info("현재 대기 환경은 안정적인 상태입니다.")

elif cri_value < 70:
    st.warning("🟡 보통: 민감군 주의 필요")
    st.info("호흡기 질환자 및 노약자는 장시간 외출을 피하세요.")

elif cri_value < 120:
    st.error("🟠 높음: 외출 자제 권고")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ⚠️ 권장 행동")
        st.write("- 외출 최소화")
        st.write("- KF 마스크 착용")
        st.write("- 실내 공기질 관리")

    with col2:
        st.markdown("### 🏙️ 정책 대응")
        st.write("- 클린존 이용 권장")
        st.write("- 취약계층 보호 필요")

else:
    st.error("🔴 심각: 즉각 대응 필요")
    
    st.markdown("## 🚨 긴급 경보")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 👤 시민 행동 지침")
        st.write("- 외출 금지")
        st.write("- 실내 대기")
        st.write("- 공기청정기 가동")

    with col2:
        st.markdown("### 🏛️ 행정 조치")
        st.write("- 실외 작업 중단")
        st.write("- 대피소(클린존) 개방")
        st.write("- 취약계층 보호 조치")

# ------------------------
# 시각화 (PM 변화)
# ------------------------
st.subheader("📈 PM2.5 변화 시나리오")

pm_range = np.linspace(0, 150, 50)
cri_sim = [calculate_cri(p, temp, humidity, w1, w2, w3) for p in pm_range]

st.line_chart({"CRI": cri_sim})

# ------------------------
# 지도 시각화
# ------------------------
st.subheader("🗺️ 자치구별 CRI 위험 지도")

data = pd.DataFrame({
    "district": ["강북구", "중구", "서초구", "강서구"],
    "lat": [37.6396, 37.5636, 37.4837, 37.5509],
    "lon": [127.0256, 126.9975, 127.0324, 126.8495],
    "pm25": [80, 75, 35, 30],
    "temp": [0, 2, 5, 6],
    "humidity": [30, 35, 50, 55]
})

data["CRI"] = data.apply(
    lambda row: calculate_cri(row["pm25"], row["temp"], row["humidity"], w1, w2, w3),
    axis=1
)

def get_color(cri):
    if cri < 30:
        return "green"
    elif cri < 70:
        return "yellow"
    elif cri < 120:
        return "orange"
    else:
        return "red"

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

st_folium(m, width=700, height=500)
