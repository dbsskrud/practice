import matplotlib.pyplot as plt

st.subheader("📈 PM2.5 변화 시나리오 (정책 분석 포함)")

# ------------------------
# 시뮬레이션 데이터 생성
# ------------------------
pm_range = np.linspace(0, 150, 200)
cri_sim = [calculate_cri(p, temp, humidity, w1, w2, w3) for p in pm_range]

current_cri = calculate_cri(pm25, temp, humidity, w1, w2, w3)

# ------------------------
# 그래프 생성
# ------------------------
fig, ax = plt.subplots()

# 기본 선
ax.plot(pm_range, cri_sim)

# 현재 위치
ax.scatter([pm25], [current_cri])
ax.annotate(f"현재\n({pm25}, {current_cri:.1f})",
            (pm25, current_cri),
            textcoords="offset points",
            xytext=(10,10))

# 임계선
thresholds = [30, 70, 120]
labels = ["낮음", "보통", "높음"]

for t, label in zip(thresholds, labels):
    ax.axhline(t)
    ax.text(0, t, label)

# 축 라벨
ax.set_xlabel("PM2.5 (μg/m³)")
ax.set_ylabel("CRI")

st.pyplot(fig)

# ------------------------
# ΔCRI 분석
# ------------------------
st.subheader("📊 민감도 분석")

delta = 10
future_cri = calculate_cri(pm25 + delta, temp, humidity, w1, w2, w3)
delta_cri = future_cri - current_cri

st.write(f"👉 PM2.5가 **+{delta} 증가**하면 CRI는 **{delta_cri:.2f} 증가**합니다.")

# ------------------------
# 위험 전환 지점 계산
# ------------------------
st.subheader("🚨 위험 단계 전환 지점")

def find_threshold_crossing(target_cri):
    for p in range(0, 201):
        c = calculate_cri(p, temp, humidity, w1, w2, w3)
        if c >= target_cri:
            return p
    return None

cross_30 = find_threshold_crossing(30)
cross_70 = find_threshold_crossing(70)
cross_120 = find_threshold_crossing(120)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🟢→🟡 전환", f"{cross_30} μg/m³" if cross_30 else "없음")

with col2:
    st.metric("🟡→🟠 전환", f"{cross_70} μg/m³" if cross_70 else "없음")

with col3:
    st.metric("🟠→🔴 전환", f"{cross_120} μg/m³" if cross_120 else "없음")
