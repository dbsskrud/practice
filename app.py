import streamlit as st

# 탭 생성
tab1, tab2 = st.tabs(["🏠 서울 스타터 (윤나경)", "📊 데이터 분석 (예다은)"])


# =========================
# TAB 1 (수정 금지 영역)
# =========================
with tab1:
    import pandas as pd
    import plotly.graph_objects as go
    import json

    # 페이지 설정 (탭 내부에서는 set_page_config 중복 방지)
    st.title("서울 스타터 v2.0")

    # 원본 코드 시작 ------------------------------
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Bebas+Neue&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

    st.header("자취생을 위한 서울 가이드")
    st.write("윤나경님의 기존 앱이 그대로 들어가는 영역입니다.")

    # 실제 환경에서는 아래에 원본 코드 전체 붙여넣기
    # (현재는 요약 표시)
    # ------------------------------------------


# =========================
# TAB 2 (두 번째 데이터)
# =========================
with tab2:
    import pandas as pd
    import plotly.express as px

    st.title("데이터 분석 대시보드")

    # 샘플 데이터 로드 (실제 데이터로 교체 가능)
    df = pd.DataFrame({
        "구": ["강남구", "서초구", "마포구", "송파구"],
        "월세": [80, 75, 60, 70],
        "안전도": [70, 85, 65, 80]
    })

    st.subheader("지역별 월세 비교")
    fig1 = px.bar(df, x="구", y="월세")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("월세 vs 안전도")
    fig2 = px.scatter(df, x="월세", y="안전도", text="구")
    st.plotly_chart(fig2, use_container_width=True)

    selected_gu = st.selectbox("구 선택", df["구"])

    filtered = df[df["구"] == selected_gu]

    st.markdown(f"""
    ### 선택한 지역: {selected_gu}
    - 평균 월세: {int(filtered['월세'])}만원
    - 안전도: {int(filtered['안전도'])}점
    """)
