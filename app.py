import streamlit as st
import numpy as np

st.set_page_config(page_title="서울 대기질 CRI 분석기", layout="centered")

st.title("🌫️ 대기질 건강 위험도 분석 (CRI)")
st.markdown("미세먼지 + 기상 데이터를 기반으로 복합 위험지수(CRI)를 계산합니다.")

# ------------------------
# 사용자 입력
# ------------------------
st.sidebar.header("입력 변수")

pm25 = st.sidebar.slider("PM2.5 (μg/m³)", 0, 200, 50)
temp = st.sidebar.slider("기온 (°C)", -20, 40, 10)
humidity = st.sidebar.slider("습도 (%)", 0, 100, 50)

st.sidebar.markdown("---")

# 가중치 (기본값)
w1 = st.sidebar.slider("PM2.5 가중치", 0.0, 1.0, 0.5)
w2 = st.sidebar.slider("기온 가중치", 0.0, 1.0, 0.3)
w3 = st.sidebar.slider("습도 가중치", 0.0, 1.0, 0.2)

# ------------------------
# CRI 계산 함수
# ------------------------
def calculate_cri(pm25, temp, humidity, w1, w2, w3):
    temp = temp if temp != 0 else 0.1
    humidity = humidity if humidity != 0 else 0.1

    cri = (w1 * pm25) + (w2 * (1 / temp)) + (w3 * (1 / humidity))
    return cri

cri_value = calculate_cri(pm25, temp, humidity, w1, w2, w3)

# ------------------------
# 위험 등급 판단
# ------------------------
def classify_cri(cri):
    if cri < 30:
        return "🟢 낮음", "일상 활동 가능"
    elif cri < 70:
        return "🟡 보통", "민감군 주의 필요"
    elif cri < 120:
        return "🟠 높음", "외출 자제 권고"
    else:
        return "🔴 심각", "외출 금지 및 보호 필요"

level, message = classify_cri(cri_value)

# ------------------------
# 결과 출력
# ------------------------
st.subheader("📊 분석 결과")

st.metric("CRI 지수", round(cri_value, 2))
st.write(f"**위험 등급:** {level}")
st.write(f"**권고:** {message}")

# ------------------------
# 정책 대응 로직 (보고서 기반)
# ------------------------
st.subheader("🏙️ 정책 대응 시뮬레이션")

if "심각" in level:
    st.error("공공기관 실외 작업 중단 / 취약계층 보호 필요")
elif "높음" in level:
    st.warning("클린존 이용 및 외출 최소화 권장")
else:
    st.info("일반적인 환경 상태 유지")

# ------------------------
# 간단한 시각화
# ------------------------
st.subheader("📈 PM2.5 변화 시나리오")

pm_range = np.linspace(0, 150, 50)
cri_sim = [calculate_cri(p, temp, humidity, w1, w2, w3) for p in pm_range]

st.line_chart({"CRI": cri_sim})
