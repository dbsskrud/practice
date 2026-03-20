st.markdown(textwrap.dedent(f"""
<div class="info-panel">
  <div class="info-header">
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
      <div>
        <div style="font-size:0.72rem; color:#4facfe; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:4px;">
          선택 지역
        </div>
        <div style="font-size:1.8rem; font-weight:900; color:#e8f4ff; line-height:1.1;">
          {gu}
        </div>
      </div>
      {rank_badge_html}
    </div>
    <div class="quote-box" style="margin-top:14px; margin-bottom:0;">
      {row['한줄평']}
    </div>
  </div>

  <div class="info-body">
    <div class="section-title">핵심 지표</div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px;">
      <div class="stat-card">
        <div class="stat-label">💰 평균 월세</div>
        <div class="stat-value">{row['평균월세']}<span style="font-size:1rem;color:#7a8fa8;">만원</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-label">🛒 생활물가 {price_icon}</div>
        <div class="stat-value" style="font-size:1.05rem;">{price_text}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">🏛 문화공간</div>
        <div class="stat-value">{row['전체문화공간']}<span style="font-size:0.85rem;color:#7a8fa8;">개소</span></div>
        <div class="stat-sub">도서관 {row['도서관수']}개 포함</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">🌳 공원 / 녹지</div>
        <div class="stat-value">{row['공원수']}<span style="font-size:0.85rem;color:#7a8fa8;">개소</span></div>
      </div>
    </div>

    <div class="section-title">지하철 노선</div>
    <div style="margin-bottom:14px;">{line_tags}</div>

    <div class="section-title">대표 역세권</div>
    <div style="font-size:0.85rem; color:#b8d4f0; margin-bottom:14px;">
      🚉 {row['대표역']}
    </div>

    <div class="section-title">추천 점수</div>
    <div style="background:rgba(74,144,217,0.08); border-radius:10px; padding:10px 14px; border:1px solid rgba(74,144,217,0.2);">
      <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:#7a8fa8; margin-bottom:5px;">
        <span>종합 추천 점수</span>
        <span style="color:#4facfe; font-weight:700;">{row['total_score']:.2f}점</span>
      </div>
      <div style="background:#1a2a3a; border-radius:6px; height:8px; overflow:hidden;">
        <div style="width:{score_pct}%; height:100%; background:linear-gradient(90deg,#4facfe,#00f2fe); border-radius:6px;"></div>
      </div>
    </div>
  </div>
</div>
"""), unsafe_allow_html=True)
