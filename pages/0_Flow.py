"""
생산·물류 흐름도 — 애니메이션 페이지
생산동 → 전실(P-Box 채우기) → 물류 컨베이어 → 창고 적재 → 출고
"""

import streamlit as st
import streamlit.components.v1 as components
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar, render_brand_header

st.set_page_config(page_title="생산·물류 흐름도 | SCM", page_icon="◆",
                   layout="wide", initial_sidebar_state="expanded")

inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 생산·물류 흐름도")
render_page_subtitle("PRODUCTION & LOGISTICS FLOW · P-BOX FILLING · AI VISION GATE")

st.markdown(
    f'<div style="background:#EFF6FF;border-left:4px solid {COLORS["accent_cobalt"]};'
    f'border-radius:6px;padding:14px 20px;margin-bottom:20px;">'
    f'<div style="font-size:15px;color:{COLORS["text_secondary"]};line-height:1.8;">'
    f'생산된 빵이 P-Box에 담겨 물류동으로 이동하는 전체 흐름입니다. '
    f'<strong style="color:{COLORS["accent_gold"]};">AI Vision 검수 게이트</strong>는 '
    f'단위 변환 지점(낱개→박스)에 설치되어 정보 손실을 원천 차단합니다.'
    f'</div></div>',
    unsafe_allow_html=True)

# ─── 애니메이션 컴포넌트 ───
components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #fff; font-family: 'Noto Sans KR', sans-serif; overflow: hidden; }

  .flow-wrap {
    width: 100%; height: 420px; position: relative;
    background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
    border: 1px solid #E2E8F0; border-radius: 10px; overflow: hidden;
  }

  /* 구역 구분선 */
  .zone-line {
    position: absolute; top: 0; bottom: 0; width: 2px;
    background: repeating-linear-gradient(to bottom, #CBD5E1 0px, #CBD5E1 8px, transparent 8px, transparent 16px);
  }

  /* 구역 라벨 */
  .zone-label {
    position: absolute; top: 14px;
    font-size: 13px; font-weight: 700; color: #1E40AF;
    letter-spacing: 0.03em;
    background: rgba(255,255,255,0.9);
    padding: 4px 10px; border-radius: 20px;
    border: 1px solid #BFDBFE;
  }

  /* 컨베이어 벨트 */
  .conveyor {
    position: absolute; height: 22px;
    background: #475569; border-radius: 3px;
    overflow: hidden;
  }
  .conveyor-belt {
    position: absolute; top: 0; left: 0; width: 200%; height: 100%;
    background: repeating-linear-gradient(
      90deg, #475569 0px, #475569 20px, #64748B 20px, #64748B 22px
    );
    animation: beltMove 1.2s linear infinite;
  }
  @keyframes beltMove {
    from { transform: translateX(0); }
    to   { transform: translateX(-22px); }
  }

  /* 빵 아이템 */
  .bread {
    position: absolute; width: 26px; height: 18px;
    background: #F97316; border-radius: 50% 50% 40% 40%;
    border-bottom: 3px solid #EA580C;
    animation: moveBread linear infinite;
  }
  .bread::after {
    content: ''; position: absolute; top: 3px; left: 4px;
    width: 18px; height: 8px;
    background: rgba(255,255,255,0.25);
    border-radius: 50%;
  }
  @keyframes moveBread {
    0%   { transform: translateX(0); opacity: 1; }
    85%  { opacity: 1; }
    100% { transform: translateX(220px); opacity: 0; }
  }

  /* P-Box */
  .pbox {
    position: absolute; width: 34px; height: 28px;
    background: #1D4ED8; border-radius: 3px;
    border-bottom: 4px solid #1E3A8A;
    border-right: 3px solid #1E3A8A;
    display: flex; align-items: center; justify-content: center;
  }
  .pbox::before {
    content: ''; position: absolute; top: 0; right: -3px;
    width: 3px; height: 100%;
    background: #1E3A8A;
  }
  .pbox-content {
    display: flex; gap: 2px; flex-wrap: wrap;
    width: 24px; justify-content: center;
  }
  .pbox-bread {
    width: 7px; height: 5px; background: #F97316; border-radius: 50%;
  }

  /* P-Box 이동 애니메이션 */
  .pbox-move {
    animation: movePbox linear infinite;
  }
  @keyframes movePbox {
    0%   { transform: translateX(0); opacity: 1; }
    85%  { opacity: 1; }
    100% { transform: translateX(250px); opacity: 0; }
  }

  /* 작업자 */
  .worker {
    position: absolute;
    animation: workerAnim 1.5s ease-in-out infinite alternate;
  }
  @keyframes workerAnim {
    0%   { transform: translateY(0px); }
    100% { transform: translateY(-5px); }
  }

  /* AI 비전 게이트 */
  .vision-gate {
    position: absolute;
    display: flex; flex-direction: column; align-items: center;
    animation: gatePulse 1.8s ease-in-out infinite;
  }
  .gate-beam {
    width: 4px; height: 110px; background: #F59E0B;
    border-radius: 2px;
    box-shadow: 0 0 12px #F59E0B, 0 0 24px rgba(245,158,11,0.4);
  }
  .gate-label {
    font-size: 10px; font-weight: 800; color: #D97706;
    margin-top: 4px; letter-spacing: 0.05em;
    background: #FFFBEB; border: 1px solid #FCD34D;
    padding: 2px 7px; border-radius: 4px;
  }
  @keyframes gatePulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  /* 적재 박스 스택 */
  .stack-group {
    position: absolute;
    display: flex; flex-direction: column-reverse; gap: 2px;
    animation: stackGrow 3s ease-in-out infinite alternate;
  }
  @keyframes stackGrow {
    0%   { transform: translateY(0px); }
    100% { transform: translateY(-8px); }
  }
  .stack-row { display: flex; gap: 2px; }
  .stack-box {
    width: 28px; height: 22px;
    background: #2563EB; border-radius: 2px;
    border-bottom: 3px solid #1E3A8A;
    border-right: 2px solid #1E3A8A;
    display: flex; align-items: center; justify-content: center;
  }
  .stack-box-orange {
    background: #EA580C; border-bottom-color: #C2410C; border-right-color: #C2410C;
  }
  .stack-dot { width: 4px; height: 4px; background: rgba(255,255,255,0.5); border-radius: 50%; }

  /* 화살표 */
  .arrow {
    position: absolute; color: #94A3B8; font-size: 20px; font-weight: 900;
    animation: arrowPulse 1.2s ease-in-out infinite alternate;
  }
  @keyframes arrowPulse {
    from { opacity: 0.4; transform: translateX(-3px); }
    to   { opacity: 1; transform: translateX(3px); }
  }

  /* 빨간 화살표 바닥 */
  .bottom-arrow {
    position: absolute; bottom: 18px; left: 30px; right: 30px; height: 8px;
    background: linear-gradient(90deg, #EF4444, #DC2626);
    border-radius: 0 4px 4px 0;
  }
  .bottom-arrow::after {
    content: ''; position: absolute; right: -14px; top: -6px;
    border-left: 18px solid #DC2626; border-top: 10px solid transparent;
    border-bottom: 10px solid transparent;
  }
  .bottom-label {
    position: absolute; bottom: 5px; left: 50%; transform: translateX(-50%);
    font-size: 11px; color: #94A3B8;
  }

  /* 구역 설명 */
  .zone-desc {
    position: absolute; bottom: 44px;
    font-size: 11px; color: #64748B; text-align: center;
    line-height: 1.5;
  }
  .highlight { color: #1D4ED8; font-weight: 700; }
</style>
</head>
<body>
<div class="flow-wrap">

  <!-- 구역 구분선 -->
  <div class="zone-line" style="left:175px;"></div>
  <div class="zone-line" style="left:395px;"></div>
  <div class="zone-line" style="left:640px;"></div>
  <div class="zone-line" style="left:850px;"></div>

  <!-- 구역 라벨 -->
  <div class="zone-label" style="left:20px;">생산동</div>
  <div class="zone-label" style="left:190px;">전실 (수작업)</div>
  <div class="zone-label" style="left:415px;">물류 컨베이어</div>
  <div class="zone-label" style="left:660px; background:#FFFBEB; border-color:#FCD34D; color:#D97706;">
    AI Vision 검수 🔬
  </div>
  <div class="zone-label" style="left:870px;">창고 / 출고</div>

  <!-- ① 생산동 컨베이어 (상단) -->
  <div class="conveyor" style="left:20px; right:830px; top:120px; width:150px;">
    <div class="conveyor-belt"></div>
  </div>
  <!-- 빵 아이템들 (상단 라인) -->
  <div class="bread" style="top:108px; left:30px; animation-duration:2.2s; animation-delay:0s;"></div>
  <div class="bread" style="top:108px; left:75px; animation-duration:2.2s; animation-delay:0.7s;"></div>
  <div class="bread" style="top:108px; left:120px; animation-duration:2.2s; animation-delay:1.4s;"></div>

  <!-- ① 생산동 컨베이어 (하단) -->
  <div class="conveyor" style="left:20px; top:230px; width:150px;">
    <div class="conveyor-belt"></div>
  </div>
  <!-- 빵 아이템들 (하단 라인, 초록) -->
  <div style="position:absolute; top:218px; left:30px; width:26px; height:18px;
              background:#16A34A; border-radius:50% 50% 40% 40%;
              border-bottom:3px solid #15803D;
              animation: moveBread 2.5s linear infinite; animation-delay:0.3s;"></div>
  <div style="position:absolute; top:218px; left:85px; width:26px; height:18px;
              background:#16A34A; border-radius:50% 50% 40% 40%;
              border-bottom:3px solid #15803D;
              animation: moveBread 2.5s linear infinite; animation-delay:1.1s;"></div>

  <!-- ② 전실: 작업자 SVG -->
  <svg class="worker" style="left:220px; top:90px;" width="40" height="100" viewBox="0 0 40 100">
    <!-- 머리 -->
    <circle cx="20" cy="12" r="10" fill="#1E293B"/>
    <!-- 몸 -->
    <line x1="20" y1="22" x2="20" y2="55" stroke="#1E293B" stroke-width="4" stroke-linecap="round"/>
    <!-- 팔 (들어올리는 동작) -->
    <line x1="20" y1="32" x2="6" y2="48" stroke="#1E293B" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="20" y1="32" x2="34" y2="42" stroke="#1E293B" stroke-width="3.5" stroke-linecap="round"/>
    <!-- 다리 -->
    <line x1="20" y1="55" x2="10" y2="75" stroke="#1E293B" stroke-width="3.5" stroke-linecap="round"/>
    <line x1="20" y1="55" x2="30" y2="75" stroke="#1E293B" stroke-width="3.5" stroke-linecap="round"/>
  </svg>

  <!-- ② 전실: P-Box 채우는 작업 -->
  <div class="pbox" style="left:265px; top:148px;">
    <div class="pbox-content">
      <div class="pbox-bread"></div><div class="pbox-bread"></div>
      <div class="pbox-bread"></div><div class="pbox-bread"></div>
    </div>
  </div>

  <!-- 빵→박스 투입 화살표 -->
  <div style="position:absolute; top:128px; left:253px; font-size:13px; color:#F97316; font-weight:700;
              animation: arrowPulse 1s ease-in-out infinite alternate;">↘</div>

  <!-- ③ 물류 컨베이어 -->
  <div class="conveyor" style="left:400px; top:175px; width:220px;">
    <div class="conveyor-belt"></div>
  </div>
  <!-- P-Box 이동 -->
  <div style="position:absolute; top:160px; left:405px; animation: movePbox 2.8s linear infinite; animation-delay:0s;">
    <div class="pbox"><div class="pbox-content">
      <div class="pbox-bread"></div><div class="pbox-bread"></div>
      <div class="pbox-bread"></div><div class="pbox-bread"></div>
      <div class="pbox-bread"></div><div class="pbox-bread"></div>
    </div></div>
  </div>
  <div style="position:absolute; top:160px; left:455px; animation: movePbox 2.8s linear infinite; animation-delay:1.4s;">
    <div class="pbox"><div class="pbox-content">
      <div class="pbox-bread"></div><div class="pbox-bread"></div>
      <div class="pbox-bread"></div><div class="pbox-bread"></div>
    </div></div>
  </div>

  <!-- ④ AI Vision 게이트 -->
  <div class="vision-gate" style="left:642px; top:85px;">
    <div class="gate-beam"></div>
    <div class="gate-label">AI VISION</div>
  </div>

  <!-- 검수 후 OK 배지 -->
  <div style="position:absolute; top:155px; left:655px;
              background:#ECFDF5; border:1.5px solid #059669; border-radius:20px;
              font-size:10px; font-weight:800; color:#059669;
              padding:2px 8px;
              animation: gatePulse 1.8s ease-in-out infinite;">✅ OK</div>
  <div style="position:absolute; top:195px; left:655px;
              background:#FEF2F2; border:1.5px solid #DC2626; border-radius:20px;
              font-size:10px; font-weight:800; color:#DC2626;
              padding:2px 8px;
              animation: gatePulse 1.8s ease-in-out infinite; animation-delay:0.9s;">❌ NG</div>

  <!-- ⑤ 창고 스택 -->
  <!-- 스택 1 (주황) -->
  <div class="stack-group" style="left:880px; top:150px; animation-delay:0s;">
    <div class="stack-row">
      <div class="stack-box stack-box-orange"><div class="stack-dot"></div></div>
      <div class="stack-box stack-box-orange"><div class="stack-dot"></div></div>
    </div>
    <div class="stack-row">
      <div class="stack-box stack-box-orange"><div class="stack-dot"></div></div>
      <div class="stack-box stack-box-orange"><div class="stack-dot"></div></div>
    </div>
    <div class="stack-row">
      <div class="stack-box stack-box-orange"><div class="stack-dot"></div></div>
      <div class="stack-box stack-box-orange"><div class="stack-dot"></div></div>
    </div>
  </div>
  <!-- 스택 2 (파랑) -->
  <div class="stack-group" style="left:945px; top:168px; animation-delay:0.6s;">
    <div class="stack-row">
      <div class="stack-box"><div class="stack-dot"></div></div>
      <div class="stack-box"><div class="stack-dot"></div></div>
    </div>
    <div class="stack-row">
      <div class="stack-box"><div class="stack-dot"></div></div>
      <div class="stack-box"><div class="stack-dot"></div></div>
    </div>
  </div>
  <!-- 스택 3 (파랑) -->
  <div class="stack-group" style="left:1010px; top:180px; animation-delay:1.2s;">
    <div class="stack-row">
      <div class="stack-box"><div class="stack-dot"></div></div>
      <div class="stack-box"><div class="stack-dot"></div></div>
    </div>
  </div>

  <!-- 화살표들 -->
  <div class="arrow" style="left:168px; top:160px;">→</div>
  <div class="arrow" style="left:310px; top:165px; animation-delay:0.3s;">→</div>
  <div class="arrow" style="left:625px; top:165px; animation-delay:0.6s;">→</div>
  <div class="arrow" style="left:690px; top:165px; animation-delay:0.9s;">→</div>
  <div class="arrow" style="left:860px; top:165px; animation-delay:0.3s;">→</div>

  <!-- 하단 빨간 화살표 -->
  <div class="bottom-arrow"></div>
  <div class="bottom-label">생산 → 물류 흐름</div>

  <!-- 구역 설명 텍스트 -->
  <div class="zone-desc" style="left:10px; width:155px;">
    생산 라인<br>
    <span class="highlight">10개 LINE</span><br>
    낱개 제품 생산
  </div>
  <div class="zone-desc" style="left:178px; width:210px;">
    수작업으로 P-Box 채우기<br>
    <span class="highlight">EA → Case 전환</span><br>
    ⚠ 정보 손실 발생 지점
  </div>
  <div class="zone-desc" style="left:400px; width:220px;">
    물류 컨베이어<br>
    <span class="highlight">P-Box 이동</span><br>
    물류동으로 배출
  </div>
  <div class="zone-desc" style="left:638px; width:195px;">
    <span style="color:#D97706; font-weight:700;">AI Vision 검수 게이트</span><br>
    수량·SKU 실시간 판정<br>
    NG 즉시 차단
  </div>
  <div class="zone-desc" style="left:855px; width:200px;">
    <span class="highlight">창고 적재 · 출고 대기</span><br>
    재고 현황 WMS 반영<br>
    매장별 출고 분류
  </div>

</div>
</body>
</html>
""", height=440, scrolling=False)

st.markdown("")
st.markdown("---")

# ─── 단계별 설명 ───
st.markdown(
    f'<div style="font-size:11px;font-weight:700;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:14px;">PROCESS STEPS · 단계별 설명</div>',
    unsafe_allow_html=True)

s1, s2, s3, s4, s5 = st.columns(5)

steps = [
    (s1, "①", "생산 라인",
     COLORS["accent_cobalt"],
     "10개 생산 라인에서 낱개(EA) 단위로 빵을 생산합니다. 각 라인은 독립적으로 운영되며 SKU별로 분리됩니다."),
    (s2, "②", "P-Box 채우기\n(수작업)",
     COLORS["status_warning"],
     "작업자가 생산된 빵을 P-Box(플라스틱 박스)에 담습니다. 이 시점이 EA→Case 단위 변환 지점으로 정보 손실 위험 구간입니다."),
    (s3, "③", "물류 컨베이어",
     COLORS["accent_cobalt"],
     "채워진 P-Box가 물류 컨베이어에 올라져 물류동으로 이동합니다. 박스 단위로 이동하며 층적 후 창고로 배출됩니다."),
    (s4, "④", "AI Vision\n검수 게이트",
     COLORS["accent_gold"],
     "AI Vision이 P-Box 이미지를 분석해 SKU와 수량을 실시간 판정합니다. NG 차단으로 불량 출고를 원천 방지합니다."),
    (s5, "⑤", "창고 적재\n& 출고",
     COLORS["status_ok"],
     "OK 판정된 P-Box만 창고에 적재됩니다. WMS에 재고가 자동 반영되고, 매장별 주문에 따라 출고 분류됩니다."),
]

for col, num, title, color, desc in steps:
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-top:3px solid {color};border-radius:8px;padding:16px;">'
        f'<div style="font-size:22px;font-weight:900;color:{color};line-height:1;margin-bottom:6px;">{num}</div>'
        f'<div style="font-size:14px;font-weight:700;color:{COLORS["text_primary"]};margin-bottom:8px;white-space:pre-line;">{title}</div>'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};line-height:1.7;">{desc}</div>'
        f'</div>', unsafe_allow_html=True)

st.markdown("")

# ─── 핵심 포인트 ───
st.markdown(
    f'<div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:8px;padding:18px 24px;">'
    f'<div style="font-size:15px;font-weight:700;color:{COLORS["accent_gold"]};margin-bottom:10px;">'
    f'⭐ 핵심 — AI Vision을 단위 변환 지점에 설치하는 이유</div>'
    f'<div style="font-size:14px;color:{COLORS["text_secondary"]};line-height:1.9;">'
    f'낱개(EA) → 박스(Case)로 전환되는 순간, 개별 수량 정보가 압축됩니다. '
    f'이 지점에 AI Vision 게이트를 설치하면 압축 직전에 수량을 검증할 수 있어 '
    f'<strong style="color:{COLORS["status_danger"]};">정보 손실(IRI)</strong>을 원천 차단합니다.<br>'
    f'이것이 채찍효과(Bullwhip Effect)의 <strong style="color:{COLORS["accent_gold"]};">미시적 시작점에서의 개입</strong>입니다.'
    f'</div></div>', unsafe_allow_html=True)
