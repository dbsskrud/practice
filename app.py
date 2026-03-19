import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="서울 CRI 대기질 분석",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 글로벌 스타일 ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* 배경 */
.stApp {
    background: #0d0f14;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: #13161f;
    border-right: 1px solid #1e2130;
}
section[data-testid="stSidebar"] * {
    color: #c9d0e0 !important;
}
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stNumberInput label {
    font-size: 13px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #6b7592 !important;
}

/* 메인 텍스트 */
h1, h2, h3, h4 { color: #e8ecf4 !important; }
p, li { color: #9aa3b8; }

/* 메트릭 카드 커스텀 */
[data-testid="stMetric"] {
    background: #13161f;
    border: 1px solid #1e2130;
    border-radius: 12px;
    padding: 20px 24px;
}
[data-testid="stMetricLabel"] { color: #6b7592 !important; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
[data-testid="stMetricValue"] { color: #e8ecf4 !important; font-family: 'DM Mono', monospace; }
[data-testid="stMetricDelta"] svg { display: none; }

/* 구분선 */
hr { border-color: #1e2130; }

/* 탭 */
.stTabs [data-baseweb="tab-list"] { background: #13161f; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] { color: #6b7592; border-radius: 8px; }
.stTabs [aria-selected="true"] { background: #1e2130 !important; color: #e8ecf4 !important; }

/* 경고/성공 박스 */
.stAlert { border-radius: 10px; border: none; }

/* 헤더 배지 */
.cri-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.03em;
}
.badge-safe   { background: #0a2818; color: #4ade80; border: 1px solid #166534; }
.badge-mid    { background: #2a1e06; color: #fbbf24; border: 1px solid #92400e; }
.badge-high   { background: #2a1006; color: #fb923c; border: 1px solid #9a3412; }
.badge-crit   { background: #2a0808; color: #f87171; border: 1px solid #991b1b; }

.section-header {
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6b7592;
    margin-bottom: 12px;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Plotly 공통 레이아웃 ──────────────────────────────────────
PLOT_BG   = "#13161f"
PAPER_BG  = "#13161f"
GRID_CLR  = "#1e2130"
TEXT_CLR  = "#9aa3b8"
FONT      = "DM Sans"

BASE_LAYOUT = dict(
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=PLOT_BG,
    font=dict(family=FONT, color=TEXT_CLR, size=12),
    margin=dict(l=16, r=16, t=32, b=16),
    xaxis=dict(gridcolor=GRID_CLR, linecolor=GRID_CLR, tickfont=dict(size=11)),
    yaxis=dict(gridcolor=GRID_CLR, linecolor=GRID_CLR, tickfont=dict(size=11)),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=GRID_CLR,
        font=dict(size=12),
    ),
)

# ── CRI 계산 ──────────────────────────────────────────────────
def calc_cri(pm25, temp, humidity, w1=0.5, w2=0.3, w3=0.2):
    t = temp if temp != 0 else 0.1
    h = humidity if humidity != 0 else 0.1
    return (w1 * pm25) + (w2 * (1 / t)) + (w3 * (1 / h))

def cri_level(v):
    if v < 30:   return "낮음",  "#4ade80", "badge-safe"
    if v < 70:   return "보통",  "#fbbf24", "badge-mid"
    if v < 120:  return "높음",  "#fb923c", "badge-high"
    return           "심각",  "#f87171", "badge-crit"

def threshold_pm(target, temp, humidity):
    for p in range(0, 501):
        if calc_cri(p, temp, humidity) >= target:
            return p
    return None

# ── 사이드바 ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌫️ 입력 변수")
    st.markdown("---")
    st.markdown('<p class="section-header">환경 측정값</p>', unsafe_allow_html=True)
    pm25     = st.slider("PM2.5 (μg/m³)", 0.0, 200.0, 50.0, 1.0)
    temp     = st.slider("기온 (°C)",     -20.0, 45.0, 10.0, 0.5)
    humidity = st.slider("습도 (%)",       1.0, 100.0, 50.0, 1.0)

    st.markdown("---")
    st.markdown('<p class="section-header">가중치 설정</p>', unsafe_allow_html=True)
    w1 = st.slider("PM2.5 가중치", 0.0, 1.0, 0.5, 0.05)
    w2 = st.slider("기온 가중치",  0.0, 1.0, 0.3, 0.05)
    w3 = st.slider("습도 가중치",  0.0, 1.0, 0.2, 0.05)

# ── 계산 ──────────────────────────────────────────────────────
cri_val   = calc_cri(pm25, temp, humidity, w1, w2, w3)
level_txt, level_clr, badge_cls = cri_level(cri_val)
delta10   = calc_cri(pm25 + 10, temp, humidity, w1, w2, w3) - cri_val
t_safe    = threshold_pm(30,  temp, humidity)
t_mid     = threshold_pm(70,  temp, humidity)
t_high    = threshold_pm(120, temp, humidity)

# ── 헤더 ──────────────────────────────────────────────────────
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown("# 서울 대기질 건강 위험도")
    st.markdown('<p style="color:#6b7592;font-size:14px;margin-top:-8px;">복합 위험지수(CRI) · PM2.5 + 기상 데이터 기반 분석</p>', unsafe_allow_html=True)
with col_badge:
    st.markdown(f"""
    <div style="text-align:right;padding-top:20px;">
      <span style="font-family:'DM Mono',monospace;font-size:36px;font-weight:600;color:{level_clr};">{cri_val:.1f}</span>
      <br><span class="cri-badge {badge_cls}">{level_txt}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── 지표 카드 4개 ─────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
tv = temp if temp != 0 else 0.1
hv = humidity if humidity != 0 else 0.1
c1.metric("PM2.5 기여", f"{w1*pm25:.2f}", f"가중치 {w1}")
c2.metric("기온 기여",  f"{w2*(1/tv):.3f}", f"가중치 {w2}")
c3.metric("습도 기여",  f"{w3*(1/hv):.3f}", f"가중치 {w3}")
c4.metric("+10 μg/m³ 민감도", f"+{delta10:.2f}", "CRI 증가폭")

st.markdown("---")

# ── 탭 레이아웃 ────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈  시나리오 분석", "🏙️  자치구 비교", "🗺️  위험 지도"])

# ════════════════════════════════════════════════════════════
# TAB 1: 시나리오 + 민감도
# ════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([3, 2], gap="large")

    # ── 꺾은선 그래프 ──
    with col_left:
        st.markdown('<p class="section-header">PM2.5 변화에 따른 CRI 시나리오</p>', unsafe_allow_html=True)

        pm_arr  = np.linspace(0, 200, 400)
        cri_arr = [calc_cri(p, temp, humidity, w1, w2, w3) for p in pm_arr]

        fig_line = go.Figure()

        # 위험 단계 배경 영역
        zones = [(0,30,"#4ade80",0.05,"낮음"), (30,70,"#fbbf24",0.05,"보통"),
                 (70,120,"#fb923c",0.05,"높음"), (120,300,"#f87171",0.05,"심각")]
        for y0, y1, clr, alpha, name in zones:
            fig_line.add_hrect(y0=y0, y1=y1,
                fillcolor=clr, opacity=alpha, line_width=0,
                annotation_text=name, annotation_position="left",
                annotation_font=dict(color=clr, size=11))

        # 임계선
        for thr, clr, dash in [(30,"#4ade80","dot"),(70,"#fbbf24","dot"),(120,"#f87171","dot")]:
            fig_line.add_hline(y=thr, line_color=clr, line_dash=dash,
                               line_width=1, opacity=0.6)

        # 메인 라인
        fig_line.add_trace(go.Scatter(
            x=pm_arr, y=cri_arr, mode="lines",
            line=dict(color="#60a5fa", width=2.5),
            name="CRI", hovertemplate="PM2.5: %{x:.0f} μg/m³<br>CRI: %{y:.2f}<extra></extra>",
        ))

        # 현재 포인트
        fig_line.add_trace(go.Scatter(
            x=[pm25], y=[cri_val], mode="markers+text",
            marker=dict(size=12, color=level_clr, line=dict(color="#0d0f14", width=2)),
            text=[f"  현재 {cri_val:.1f}"], textposition="middle right",
            textfont=dict(color=level_clr, size=12, family="DM Mono"),
            name="현재",
            hovertemplate=f"PM2.5: {pm25} μg/m³<br>CRI: {cri_val:.2f}<extra></extra>",
        ))

        layout = dict(**BASE_LAYOUT)
        layout["xaxis"]["title"] = "PM2.5 (μg/m³)"
        layout["yaxis"]["title"] = "CRI"
        layout["height"] = 360
        fig_line.update_layout(**layout)
        st.plotly_chart(fig_line, use_container_width=True)

    # ── 도넛 + 임계점 ──
    with col_right:
        st.markdown('<p class="section-header">CRI 구성 요소</p>', unsafe_allow_html=True)

        comp_vals  = [w1*pm25, w2*(1/tv), w3*(1/hv)]
        comp_labels = ["PM2.5", "기온", "습도"]
        comp_colors = ["#60a5fa", "#f87171", "#34d399"]

        fig_donut = go.Figure(go.Pie(
            labels=comp_labels, values=comp_vals,
            hole=0.65,
            marker=dict(colors=comp_colors, line=dict(color=PLOT_BG, width=3)),
            textinfo="label+percent",
            textfont=dict(size=12, color="#e8ecf4"),
            hovertemplate="%{label}: %{value:.3f}<extra></extra>",
        ))
        fig_donut.add_annotation(
            text=f"<b>{cri_val:.1f}</b>",
            font=dict(size=22, color=level_clr, family="DM Mono"),
            showarrow=False,
        )
        donut_layout = dict(paper_bgcolor=PAPER_BG, font=dict(family=FONT, color=TEXT_CLR),
                            margin=dict(l=0,r=0,t=0,b=0), height=200, showlegend=False)
        fig_donut.update_layout(**donut_layout)
        st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown('<p class="section-header" style="margin-top:16px;">위험 단계 전환 PM2.5</p>', unsafe_allow_html=True)

        for label, val, clr in [
            ("🟢→🟡 낮음→보통", t_safe,  "#4ade80"),
            ("🟡→🟠 보통→높음", t_mid,   "#fbbf24"),
            ("🟠→🔴 높음→심각", t_high,  "#f87171"),
        ]:
            txt = f"{val} μg/m³" if val is not None else "범위 초과"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;margin-bottom:6px;
                        background:#13161f;border:1px solid #1e2130;border-radius:8px;">
              <span style="font-size:13px;color:#9aa3b8;">{label}</span>
              <span style="font-family:'DM Mono',monospace;font-size:14px;color:{clr};font-weight:500;">{txt}</span>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 2: 자치구 비교
# ════════════════════════════════════════════════════════════
with tab2:
    district_df = pd.DataFrame({
        "자치구": ["강북구", "중구", "서초구", "강서구", "송파구", "마포구"],
        "pm25":   [80, 75, 35, 30, 55, 62],
        "temp":   [0,  2,  5,  6,  3,  1],
        "humidity":[30, 35, 50, 55, 40, 38],
    })
    district_df["CRI"] = district_df.apply(
        lambda r: calc_cri(r["pm25"], r["temp"], r["humidity"], w1, w2, w3), axis=1
    )
    district_df["등급"] = district_df["CRI"].apply(lambda v: cri_level(v)[0])
    district_df["색상"] = district_df["CRI"].apply(lambda v: cri_level(v)[1])
    district_df = district_df.sort_values("CRI", ascending=True)

    col_bar, col_radar = st.columns([3, 2], gap="large")

    with col_bar:
        st.markdown('<p class="section-header">자치구별 CRI 수치 (현재 가중치 적용)</p>', unsafe_allow_html=True)

        fig_bar = go.Figure(go.Bar(
            x=district_df["CRI"].round(2),
            y=district_df["자치구"],
            orientation="h",
            marker=dict(
                color=district_df["색상"],
                line=dict(color="rgba(0,0,0,0)", width=0),
            ),
            text=district_df["CRI"].round(2),
            textposition="outside",
            textfont=dict(family="DM Mono", size=12, color="#9aa3b8"),
            hovertemplate="<b>%{y}</b><br>CRI: %{x:.2f}<extra></extra>",
        ))

        bar_layout = dict(**BASE_LAYOUT)
        bar_layout["height"] = 340
        bar_layout["xaxis"]["title"] = "CRI"
        bar_layout["xaxis"]["range"] = [0, district_df["CRI"].max() * 1.18]
        bar_layout["yaxis"]["title"] = ""
        bar_layout["yaxis"]["tickfont"] = dict(size=13)
        bar_layout["bargap"] = 0.35
        fig_bar.update_layout(**bar_layout)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_radar:
        st.markdown('<p class="section-header">구성 요소별 레이더 (상위 4개 자치구)</p>', unsafe_allow_html=True)

        top4 = district_df.tail(4)
        categories = ["PM2.5 기여", "기온 기여", "습도 기여"]

        fig_radar = go.Figure()
        colors_r = ["#60a5fa", "#f87171", "#34d399", "#fbbf24"]
        for i, (_, row) in enumerate(top4.iterrows()):
            tv_ = row["temp"] if row["temp"] != 0 else 0.1
            hv_ = row["humidity"] if row["humidity"] != 0 else 0.1
            vals = [w1*row["pm25"], w2*(1/tv_), w3*(1/hv_)]
            vals_c = vals + [vals[0]]
            cats_c = categories + [categories[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_c, theta=cats_c,
                fill="toself", opacity=0.25,
                line=dict(color=colors_r[i], width=2),
                name=row["자치구"],
                hovertemplate="%{theta}: %{r:.3f}<extra>" + row["자치구"] + "</extra>",
            ))

        fig_radar.update_layout(
            polar=dict(
                bgcolor=PLOT_BG,
                radialaxis=dict(visible=True, gridcolor=GRID_CLR, tickfont=dict(size=10)),
                angularaxis=dict(gridcolor=GRID_CLR, tickfont=dict(size=11, color=TEXT_CLR)),
            ),
            paper_bgcolor=PAPER_BG,
            font=dict(family=FONT, color=TEXT_CLR),
            legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=40, r=40, t=20, b=20),
            height=340,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # 데이터 테이블
    st.markdown('<p class="section-header" style="margin-top:8px;">상세 데이터</p>', unsafe_allow_html=True)
    show_df = district_df[["자치구","pm25","temp","humidity","CRI","등급"]].copy()
    show_df.columns = ["자치구","PM2.5","기온(°C)","습도(%)","CRI","등급"]
    show_df["CRI"] = show_df["CRI"].round(2)
    st.dataframe(show_df.set_index("자치구"), use_container_width=True)

# ════════════════════════════════════════════════════════════
# TAB 3: 지도
# ════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-header">자치구별 CRI 위험 지도</p>', unsafe_allow_html=True)

    map_df = pd.DataFrame({
        "자치구":  ["강북구","중구","서초구","강서구","송파구","마포구"],
        "lat":     [37.6396, 37.5636, 37.4837, 37.5509, 37.5145, 37.5540],
        "lon":     [127.0256, 126.9975, 127.0324, 126.8495, 127.1059, 126.9535],
        "pm25":    [80, 75, 35, 30, 55, 62],
        "temp":    [0,  2,  5,  6,  3,  1],
        "humidity":[30, 35, 50, 55, 40, 38],
    })
    map_df["CRI"] = map_df.apply(
        lambda r: calc_cri(r["pm25"], r["temp"], r["humidity"], w1, w2, w3), axis=1
    )

    def map_color(v):
        if v < 30:  return "#4ade80"
        if v < 70:  return "#fbbf24"
        if v < 120: return "#fb923c"
        return "#f87171"

    m = folium.Map(
        location=[37.5665, 126.9780], zoom_start=11,
        tiles="CartoDB dark_matter",
    )

    for _, row in map_df.iterrows():
        clr = map_color(row["CRI"])
        level = cri_level(row["CRI"])[0]
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=max(10, row["CRI"] / 5),
            color=clr, fill=True, fill_color=clr, fill_opacity=0.75,
            weight=2,
            popup=folium.Popup(f"""
            <div style="font-family:sans-serif;min-width:160px;">
              <b style="font-size:15px;">{row['자치구']}</b>
              <hr style="margin:6px 0;">
              <table style="width:100%;font-size:13px;">
                <tr><td>CRI</td><td style="text-align:right;color:{clr};font-weight:600;">{row['CRI']:.2f} ({level})</td></tr>
                <tr><td>PM2.5</td><td style="text-align:right;">{row['pm25']} μg/m³</td></tr>
                <tr><td>기온</td><td style="text-align:right;">{row['temp']}°C</td></tr>
                <tr><td>습도</td><td style="text-align:right;">{row['humidity']}%</td></tr>
              </table>
            </div>""", max_width=220),
            tooltip=f"{row['자치구']}  CRI {row['CRI']:.1f}",
        ).add_to(m)

    # 범례
    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                background:rgba(15,18,28,0.92);border:1px solid #1e2130;
                border-radius:10px;padding:14px 18px;font-family:sans-serif;font-size:13px;color:#c9d0e0;">
      <b style="display:block;margin-bottom:8px;font-size:14px;">CRI 위험 등급</b>
      <span style="color:#4ade80;">● </span> 낮음  (0–30)<br>
      <span style="color:#fbbf24;">● </span> 보통  (30–70)<br>
      <span style="color:#fb923c;">● </span> 높음  (70–120)<br>
      <span style="color:#f87171;">● </span> 심각  (120+)
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width="100%", height=520)

# ── 푸터 ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;font-size:12px;color:#3a3f52;">'
    '서울시 대기질 CRI 분석 대시보드 · 데이터는 예시 값입니다</p>',
    unsafe_allow_html=True,
)
