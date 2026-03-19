import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="서울 CRI 대기질 분석",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 글로벌 스타일 (화이트 테마) ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }

.stApp { background: #f8f9fc; }

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e8eaf0;
}

h1, h2, h3, h4 { color: #111827 !important; }
p, li { color: #4b5563; }
hr { border-color: #e8eaf0; }

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 12px;
    padding: 18px 22px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
[data-testid="stMetricLabel"] {
    color: #6b7280 !important;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    color: #111827 !important;
    font-family: 'DM Mono', monospace;
}
[data-testid="stMetricDelta"] svg { display: none; }

.stTabs [data-baseweb="tab-list"] {
    background: #f1f3f8;
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] { color: #6b7280; border-radius: 8px; }
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #111827 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.cri-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.02em;
}
.badge-safe { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.badge-mid  { background: #fef9c3; color: #854d0e; border: 1px solid #fde68a; }
.badge-high { background: #ffedd5; color: #9a3412; border: 1px solid #fed7aa; }
.badge-crit { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

.section-header {
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 10px;
    margin-top: 6px;
    font-weight: 500;
}
.card {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Plotly 공통 레이아웃 (화이트) ─────────────────────────────
PLOT_BG  = "#ffffff"
PAPER_BG = "#ffffff"
GRID_CLR = "#f0f1f5"
TEXT_CLR = "#6b7280"
FONT     = "Pretendard"

BASE_LAYOUT = dict(
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=PLOT_BG,
    font=dict(family=FONT, color=TEXT_CLR, size=12),
    margin=dict(l=16, r=16, t=36, b=16),
    xaxis=dict(gridcolor=GRID_CLR, linecolor="#e8eaf0", tickfont=dict(size=11), zeroline=False),
    yaxis=dict(gridcolor=GRID_CLR, linecolor="#e8eaf0", tickfont=dict(size=11), zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRID_CLR, font=dict(size=12)),
)

# ── CRI 계산 ──────────────────────────────────────────────────
def calc_cri(pm25, temp, humidity, w1=0.5, w2=0.3, w3=0.2):
    t = temp if temp != 0 else 0.1
    h = humidity if humidity != 0 else 0.1
    return (w1 * pm25) + (w2 * (1 / t)) + (w3 * (1 / h))

def cri_level(v):
    if v < 30:  return "낮음",  "#16a34a", "badge-safe"
    if v < 70:  return "보통",  "#d97706", "badge-mid"
    if v < 120: return "높음",  "#ea580c", "badge-high"
    return          "심각",  "#dc2626", "badge-crit"

def threshold_pm(target, temp, humidity, w1, w2, w3):
    for p in range(0, 501):
        if calc_cri(p, temp, humidity, w1, w2, w3) >= target:
            return p
    return None

# ── 자치구 기본 데이터 ────────────────────────────────────────
DISTRICTS = pd.DataFrame({
    "자치구":   ["강북구","도봉구","노원구","중랑구","성북구","동대문구",
                "중구","종로구","용산구","마포구","서대문구","은평구",
                "강서구","양천구","구로구","금천구","영등포구","동작구",
                "관악구","서초구","강남구","송파구","강동구","광진구"],
    "lat":     [37.6396,37.6688,37.6542,37.5953,37.5894,37.5744,
                37.5636,37.5730,37.5321,37.5540,37.5791,37.6027,
                37.5509,37.5170,37.4954,37.4570,37.5264,37.5124,
                37.4784,37.4837,37.5172,37.5145,37.5301,37.5384],
    "lon":     [127.0256,127.0472,127.0568,127.0930,127.0167,127.0407,
                126.9975,126.9790,126.9904,126.9535,126.9368,126.9277,
                126.8495,126.8667,126.8876,126.9019,126.8963,126.9395,
                126.9515,127.0324,127.0473,127.1059,127.1238,127.0820],
    "pm25":    [80,78,75,73,68,70,75,65,58,62,60,66,
                30,35,40,45,50,48,55,35,38,55,52,60],
    "temp":    [0, 0, 1, 1, 2, 2, 2, 3, 4, 1, 2, 1,
                6, 5, 5, 5, 4, 4, 4, 5, 5, 3, 3, 3],
    "humidity":[30,32,33,35,36,35,35,38,40,38,37,34,
                55,52,48,46,44,45,43,50,49,40,42,41],
})

# ── 월별 시계열 데이터 (시뮬레이션) ──────────────────────────
MONTHS = ["1월","2월","3월","4월","5월","6월","7월","8월","9월","10월","11월","12월"]
MONTHLY_PM = {
    "강북구": [88,82,75,60,55,50,48,52,60,70,80,85],
    "중구":   [82,76,70,55,50,46,44,48,55,65,74,80],
    "서초구": [40,38,32,25,22,20,19,21,26,32,38,42],
    "강서구": [35,33,28,22,18,16,15,17,22,28,32,37],
    "송파구": [62,58,52,42,38,34,33,36,42,50,58,64],
    "마포구": [70,65,58,48,43,39,37,41,48,56,65,72],
}
MONTHLY_TEMP = {
    "강북구": [-3,-1,5,12,18,23,27,26,20,13,5,-1],
    "중구":   [-2, 0,6,13,19,24,28,27,21,14,6, 0],
    "서초구": [-1, 1,7,14,20,25,29,28,22,15,7, 1],
    "강서구": [ 0, 2,8,15,21,26,30,29,23,16,8, 2],
    "송파구": [-2, 0,6,13,19,24,28,27,21,14,6, 0],
    "마포구": [-2, 0,6,13,19,24,28,27,21,14,6, 0],
}
MONTHLY_HUM = {
    "강북구": [52,48,50,54,58,68,78,76,65,55,52,54],
    "중구":   [50,46,48,52,56,66,76,74,63,53,50,52],
    "서초구": [55,50,52,56,60,70,80,78,67,57,54,56],
    "강서구": [58,53,55,58,62,72,82,80,70,60,57,59],
    "송파구": [52,48,50,54,58,68,78,76,65,55,52,54],
    "마포구": [51,47,49,53,57,67,77,75,64,54,51,53],
}

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
cri_val  = calc_cri(pm25, temp, humidity, w1, w2, w3)
level_txt, level_clr, badge_cls = cri_level(cri_val)
tv = temp if temp != 0 else 0.1
hv = humidity if humidity != 0 else 0.1
delta10  = calc_cri(pm25 + 10, temp, humidity, w1, w2, w3) - cri_val
t_safe   = threshold_pm(30,  temp, humidity, w1, w2, w3)
t_mid    = threshold_pm(70,  temp, humidity, w1, w2, w3)
t_high   = threshold_pm(120, temp, humidity, w1, w2, w3)

DISTRICTS["CRI"] = DISTRICTS.apply(
    lambda r: calc_cri(r["pm25"], r["temp"], r["humidity"], w1, w2, w3), axis=1
)
DISTRICTS["등급"] = DISTRICTS["CRI"].apply(lambda v: cri_level(v)[0])
DISTRICTS["색상"] = DISTRICTS["CRI"].apply(lambda v: cri_level(v)[1])

# ── 헤더 ──────────────────────────────────────────────────────
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown("# 서울 대기질 건강 위험도 분석")
    st.markdown('<p style="color:#9ca3af;font-size:14px;margin-top:-8px;">복합 위험지수(CRI) · PM2.5 + 기상 데이터 기반</p>', unsafe_allow_html=True)
with col_badge:
    st.markdown(f"""
    <div style="text-align:right;padding-top:18px;">
      <span style="font-family:'DM Mono',monospace;font-size:40px;font-weight:600;color:{level_clr};">{cri_val:.1f}</span>
      <br><span class="cri-badge {badge_cls}">{level_txt}</span>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── 지표 카드 ─────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("PM2.5 기여",      f"{w1*pm25:.2f}",    f"가중치 {w1}")
c2.metric("기온 기여",        f"{w2*(1/tv):.3f}",  f"가중치 {w2}")
c3.metric("습도 기여",        f"{w3*(1/hv):.3f}",  f"가중치 {w3}")
c4.metric("+10 μg/m³ 민감도", f"+{delta10:.2f}",   "CRI 증가폭")

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# 탭: 시나리오 / 자치구 비교 / 월별 변화 / 위험 지도
# ════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📈  시나리오 분석",
    "🏙️  자치구 비교",
    "📅  월별 CRI 변화",
    "🗺️  위험 지도",
])

# ── TAB 1: 시나리오 ───────────────────────────────────────────
with tab1:
    col_l, col_r = st.columns([3, 2], gap="large")

    with col_l:
        st.markdown('<p class="section-header">PM2.5 변화에 따른 CRI 시나리오</p>', unsafe_allow_html=True)
        pm_arr  = np.linspace(0, 200, 400)
        cri_arr = [calc_cri(p, temp, humidity, w1, w2, w3) for p in pm_arr]

        fig_line = go.Figure()
        zones = [(0,30,"#16a34a",0.06,"낮음"),(30,70,"#d97706",0.06,"보통"),
                 (70,120,"#ea580c",0.06,"높음"),(120,300,"#dc2626",0.06,"심각")]
        for y0, y1, clr, alpha, name in zones:
            fig_line.add_hrect(y0=y0, y1=y1, fillcolor=clr, opacity=alpha, line_width=0,
                annotation_text=name, annotation_position="left",
                annotation_font=dict(color=clr, size=11))
        for thr, clr in [(30,"#16a34a"),(70,"#d97706"),(120,"#dc2626")]:
            fig_line.add_hline(y=thr, line_color=clr, line_dash="dot", line_width=1, opacity=0.5)

        fig_line.add_trace(go.Scatter(
            x=pm_arr, y=cri_arr, mode="lines",
            line=dict(color="#3b82f6", width=2.5), name="CRI",
            hovertemplate="PM2.5: %{x:.0f} μg/m³<br>CRI: %{y:.2f}<extra></extra>",
        ))
        fig_line.add_trace(go.Scatter(
            x=[pm25], y=[cri_val], mode="markers+text",
            marker=dict(size=12, color=level_clr, line=dict(color="#fff", width=2)),
            text=[f"  현재 {cri_val:.1f}"], textposition="middle right",
            textfont=dict(color=level_clr, size=12, family="DM Mono"),
            name="현재",
        ))
        layout = dict(**BASE_LAYOUT)
        layout["height"] = 360
        layout["xaxis"] = dict(**BASE_LAYOUT["xaxis"], title="PM2.5 (μg/m³)")
        layout["yaxis"] = dict(**BASE_LAYOUT["yaxis"], title="CRI")
        fig_line.update_layout(**layout)
        st.plotly_chart(fig_line, use_container_width=True)

    with col_r:
        st.markdown('<p class="section-header">CRI 구성 요소</p>', unsafe_allow_html=True)
        comp_vals   = [w1*pm25, w2*(1/tv), w3*(1/hv)]
        comp_labels = ["PM2.5", "기온", "습도"]
        comp_colors = ["#3b82f6", "#f87171", "#34d399"]

        fig_donut = go.Figure(go.Pie(
            labels=comp_labels, values=comp_vals, hole=0.65,
            marker=dict(colors=comp_colors, line=dict(color="#fff", width=3)),
            textinfo="label+percent", textfont=dict(size=12),
            hovertemplate="%{label}: %{value:.3f}<extra></extra>",
        ))
        fig_donut.add_annotation(
            text=f"<b>{cri_val:.1f}</b>",
            font=dict(size=22, color=level_clr, family="DM Mono"), showarrow=False,
        )
        fig_donut.update_layout(
            paper_bgcolor=PAPER_BG, font=dict(family=FONT, color=TEXT_CLR),
            margin=dict(l=0,r=0,t=0,b=0), height=200, showlegend=False,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown('<p class="section-header" style="margin-top:16px;">위험 단계 전환 PM2.5</p>', unsafe_allow_html=True)
        for label, val, clr in [
            ("🟢→🟡 낮음→보통", t_safe,  "#16a34a"),
            ("🟡→🟠 보통→높음", t_mid,   "#d97706"),
            ("🟠→🔴 높음→심각", t_high,  "#dc2626"),
        ]:
            txt = f"{val} μg/m³" if val is not None else "범위 초과"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;margin-bottom:6px;
                        background:#f8f9fc;border:1px solid #e8eaf0;border-radius:8px;">
              <span style="font-size:13px;color:#6b7280;">{label}</span>
              <span style="font-family:'DM Mono',monospace;font-size:14px;color:{clr};font-weight:600;">{txt}</span>
            </div>""", unsafe_allow_html=True)

# ── TAB 2: 자치구 비교 ────────────────────────────────────────
with tab2:
    df_sorted = DISTRICTS.sort_values("CRI", ascending=True)
    col_b, col_rd = st.columns([3, 2], gap="large")

    with col_b:
        st.markdown('<p class="section-header">자치구별 CRI (가중치 반영)</p>', unsafe_allow_html=True)
        fig_bar = go.Figure(go.Bar(
            x=df_sorted["CRI"].round(2), y=df_sorted["자치구"],
            orientation="h",
            marker=dict(color=df_sorted["색상"], line=dict(width=0)),
            text=df_sorted["CRI"].round(1), textposition="outside",
            textfont=dict(family="DM Mono", size=11, color="#6b7280"),
            hovertemplate="<b>%{y}</b><br>CRI: %{x:.2f}<extra></extra>",
        ))
        layout_bar = dict(**BASE_LAYOUT)
        layout_bar["height"] = 560
        layout_bar["xaxis"] = dict(**BASE_LAYOUT["xaxis"], title="CRI",
                                    range=[0, df_sorted["CRI"].max()*1.2])
        layout_bar["yaxis"] = dict(**BASE_LAYOUT["yaxis"], tickfont=dict(size=12))
        layout_bar["bargap"] = 0.3
        fig_bar.update_layout(**layout_bar)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_rd:
        st.markdown('<p class="section-header">CRI 구성요소 레이더 (상위 위험 6개구)</p>', unsafe_allow_html=True)
        top6 = df_sorted.tail(6)
        cats = ["PM2.5 기여", "기온 기여", "습도 기여"]
        pal  = ["#3b82f6","#ef4444","#10b981","#f59e0b","#8b5cf6","#ec4899"]
        fig_radar = go.Figure()
        for i, (_, row) in enumerate(top6.iterrows()):
            tv_ = row["temp"] if row["temp"] != 0 else 0.1
            hv_ = row["humidity"] if row["humidity"] != 0 else 0.1
            vals = [w1*row["pm25"], w2*(1/tv_), w3*(1/hv_)]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=cats+[cats[0]],
                fill="toself", opacity=0.2,
                line=dict(color=pal[i], width=2),
                name=row["자치구"],
                hovertemplate="%{theta}: %{r:.3f}<extra>"+row["자치구"]+"</extra>",
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor=PLOT_BG,
                radialaxis=dict(visible=True, gridcolor=GRID_CLR, tickfont=dict(size=10)),
                angularaxis=dict(gridcolor=GRID_CLR, tickfont=dict(size=11, color=TEXT_CLR)),
            ),
            paper_bgcolor=PAPER_BG, font=dict(family=FONT, color=TEXT_CLR),
            legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=40,r=40,t=20,b=20), height=560,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown('<p class="section-header">전체 자치구 상세 데이터</p>', unsafe_allow_html=True)
    show = df_sorted[["자치구","pm25","temp","humidity","CRI","등급"]].copy()
    show.columns = ["자치구","PM2.5","기온(°C)","습도(%)","CRI","등급"]
    show["CRI"] = show["CRI"].round(2)
    st.dataframe(show.set_index("자치구"), use_container_width=True)

# ── TAB 3: 월별 CRI 변화 ─────────────────────────────────────
with tab3:
    st.markdown('<p class="section-header">주요 6개 자치구 · 월별 CRI 변화 (현재 가중치 적용)</p>', unsafe_allow_html=True)

    sel_districts = list(MONTHLY_PM.keys())
    pal_monthly = ["#3b82f6","#ef4444","#10b981","#f59e0b","#8b5cf6","#ec4899"]

    # 월별 CRI 라인 차트
    fig_monthly = go.Figure()
    for thr, clr, name in [(30,"#16a34a","낮음"),(70,"#d97706","보통"),(120,"#ea580c","높음")]:
        fig_monthly.add_hline(y=thr, line_color=clr, line_dash="dot",
                               line_width=1.2, opacity=0.5,
                               annotation_text=name, annotation_position="right",
                               annotation_font=dict(color=clr, size=10))

    for i, dist in enumerate(sel_districts):
        monthly_cri = [
            calc_cri(MONTHLY_PM[dist][m], MONTHLY_TEMP[dist][m], MONTHLY_HUM[dist][m], w1, w2, w3)
            for m in range(12)
        ]
        fig_monthly.add_trace(go.Scatter(
            x=MONTHS, y=monthly_cri,
            mode="lines+markers",
            name=dist,
            line=dict(color=pal_monthly[i], width=2.2),
            marker=dict(size=7, color=pal_monthly[i], line=dict(color="#fff", width=1.5)),
            hovertemplate=f"<b>{dist}</b><br>%{{x}}: CRI %{{y:.2f}}<extra></extra>",
        ))

    layout_m = dict(**BASE_LAYOUT)
    layout_m["height"] = 400
    layout_m["xaxis"] = dict(**BASE_LAYOUT["xaxis"], title="")
    layout_m["yaxis"] = dict(**BASE_LAYOUT["yaxis"], title="CRI")
    layout_m["hovermode"] = "x unified"
    fig_monthly.update_layout(**layout_m)
    st.plotly_chart(fig_monthly, use_container_width=True)

    # 월별 PM2.5 + CRI 서브플롯 (자치구 선택)
    st.markdown('<p class="section-header" style="margin-top:8px;">자치구별 월별 PM2.5 vs CRI 상세 비교</p>', unsafe_allow_html=True)
    selected = st.selectbox("자치구 선택", sel_districts, index=0)

    pm_sel  = MONTHLY_PM[selected]
    tmp_sel = MONTHLY_TEMP[selected]
    hum_sel = MONTHLY_HUM[selected]
    cri_sel = [calc_cri(pm_sel[m], tmp_sel[m], hum_sel[m], w1, w2, w3) for m in range(12)]
    clrs_bar = [cri_level(v)[1] for v in cri_sel]

    fig_sub = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.55, 0.45], vertical_spacing=0.06,
        subplot_titles=["CRI", "PM2.5 (μg/m³)"],
    )
    # CRI 바
    fig_sub.add_trace(go.Bar(
        x=MONTHS, y=[round(v, 2) for v in cri_sel],
        marker_color=clrs_bar, marker_line_width=0,
        name="CRI", hovertemplate="%{x}: CRI %{y:.2f}<extra></extra>",
        text=[round(v,1) for v in cri_sel], textposition="outside",
        textfont=dict(size=10, family="DM Mono"),
    ), row=1, col=1)
    # 임계선
    for thr, clr in [(30,"#16a34a"),(70,"#d97706"),(120,"#dc2626")]:
        fig_sub.add_hline(y=thr, line_color=clr, line_dash="dot",
                           line_width=1, opacity=0.5, row=1, col=1)
    # PM2.5 라인
    fig_sub.add_trace(go.Scatter(
        x=MONTHS, y=pm_sel, mode="lines+markers",
        line=dict(color="#6366f1", width=2), marker=dict(size=6),
        name="PM2.5", hovertemplate="%{x}: %{y} μg/m³<extra></extra>",
        fill="tozeroy", fillcolor="rgba(99,102,241,0.08)",
    ), row=2, col=1)

    fig_sub.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
        font=dict(family=FONT, color=TEXT_CLR, size=12),
        margin=dict(l=16, r=16, t=36, b=16),
        height=460, showlegend=False,
        xaxis=dict(gridcolor=GRID_CLR, linecolor="#e8eaf0", zeroline=False),
        xaxis2=dict(gridcolor=GRID_CLR, linecolor="#e8eaf0", zeroline=False),
        yaxis=dict(gridcolor=GRID_CLR, linecolor="#e8eaf0", zeroline=False),
        yaxis2=dict(gridcolor=GRID_CLR, linecolor="#e8eaf0", zeroline=False),
    )
    st.plotly_chart(fig_sub, use_container_width=True)

    # 월별 수치 테이블
    st.markdown('<p class="section-header">월별 상세 수치</p>', unsafe_allow_html=True)
    tbl = pd.DataFrame({
        "월":        MONTHS,
        "PM2.5":     pm_sel,
        "기온(°C)":  tmp_sel,
        "습도(%)":   hum_sel,
        "CRI":       [round(v, 2) for v in cri_sel],
        "등급":      [cri_level(v)[0] for v in cri_sel],
    })
    st.dataframe(tbl.set_index("월"), use_container_width=True)

# ── TAB 4: 위험 지도 ──────────────────────────────────────────
with tab4:
    st.markdown('<p class="section-header">자치구별 CRI 위험 지도 (마커 클릭 시 상세 정보)</p>', unsafe_allow_html=True)

    col_map, col_legend = st.columns([4, 1], gap="large")

    with col_map:
        m = folium.Map(
            location=[37.5665, 126.9780], zoom_start=11,
            tiles="CartoDB positron",
        )

        def map_color(v):
            if v < 30:  return "#16a34a"
            if v < 70:  return "#d97706"
            if v < 120: return "#ea580c"
            return "#dc2626"

        for _, row in DISTRICTS.iterrows():
            clr   = map_color(row["CRI"])
            level = cri_level(row["CRI"])[0]
            radius = max(8, min(28, row["CRI"] / 4.5))
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=radius,
                color=clr, fill=True, fill_color=clr, fill_opacity=0.65,
                weight=2,
                popup=folium.Popup(f"""
                <div style="font-family:sans-serif;min-width:170px;padding:4px;">
                  <b style="font-size:15px;color:#111827;">{row['자치구']}</b>
                  <hr style="margin:6px 0;border-color:#e8eaf0;">
                  <table style="width:100%;font-size:13px;color:#374151;">
                    <tr><td>CRI</td>
                        <td style="text-align:right;color:{clr};font-weight:700;font-family:monospace;">
                            {row['CRI']:.2f} <span style="font-size:11px;">({level})</span></td></tr>
                    <tr><td>PM2.5</td><td style="text-align:right;">{row['pm25']} μg/m³</td></tr>
                    <tr><td>기온</td><td style="text-align:right;">{row['temp']}°C</td></tr>
                    <tr><td>습도</td><td style="text-align:right;">{row['humidity']}%</td></tr>
                  </table>
                </div>""", max_width=230),
                tooltip=folium.Tooltip(
                    f"<b>{row['자치구']}</b>  CRI {row['CRI']:.1f} ({level})",
                    sticky=True,
                ),
            ).add_to(m)

        legend_html = """
        <div style="position:fixed;bottom:24px;left:24px;z-index:1000;
                    background:rgba(255,255,255,0.95);border:1px solid #e8eaf0;
                    border-radius:12px;padding:14px 18px;
                    font-family:sans-serif;font-size:13px;color:#374151;
                    box-shadow:0 2px 8px rgba(0,0,0,0.08);">
          <b style="display:block;margin-bottom:8px;font-size:14px;color:#111827;">CRI 위험 등급</b>
          <span style="color:#16a34a;">● </span> 낮음 (0–30)<br>
          <span style="color:#d97706;">● </span> 보통 (30–70)<br>
          <span style="color:#ea580c;">● </span> 높음 (70–120)<br>
          <span style="color:#dc2626;">● </span> 심각 (120+)
        </div>"""
        m.get_root().html.add_child(folium.Element(legend_html))
        st_folium(m, width="100%", height=560)

    with col_legend:
        st.markdown('<p class="section-header">자치구 순위</p>', unsafe_allow_html=True)
        ranked = DISTRICTS.sort_values("CRI", ascending=False)[["자치구","CRI","등급","색상"]]
        for _, row in ranked.iterrows():
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:8px 12px;margin-bottom:5px;
                        background:#f8f9fc;border:1px solid #e8eaf0;border-radius:8px;">
              <span style="font-size:13px;color:#374151;">{row['자치구']}</span>
              <span style="font-family:'DM Mono',monospace;font-size:12px;
                           color:{row['색상']};font-weight:600;">{row['CRI']:.1f}</span>
            </div>""", unsafe_allow_html=True)

# ── 푸터 ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;font-size:12px;color:#d1d5db;">'
    '서울시 대기질 CRI 분석 대시보드 · 데이터는 예시 값입니다</p>',
    unsafe_allow_html=True,
)
