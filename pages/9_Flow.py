"""
생산·물류 흐름도 — 실사 이미지 + 흐름 오버레이
생산동 → 휴머노이드(Pick&Place) → AI Vision → 창고/출고
"""
import streamlit as st
import streamlit.components.v1 as components
import base64, os
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar, render_brand_header

st.set_page_config(page_title="생산·물류 흐름도 | SCM", page_icon="◆",
                   layout="wide", initial_sidebar_state="expanded")
inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 생산·물류 흐름도")
render_page_subtitle("PRODUCTION & LOGISTICS FLOW · PICK & PLACE · AI VISION GATE")

img_path = os.path.join(os.path.dirname(__file__), "..", "assets", "flow_image.png")
with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

components.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0F172A; font-family:'Segoe UI',sans-serif; }}

.wrap {{
  position: relative;
  width: 100%;
  user-select: none;
}}

.main-img {{
  width: 100%;
  display: block;
  border-radius: 10px;
}}

/* ── 구역 라벨 ── */
.label {{
  position: absolute;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(10,15,35,0.88);
  border-radius: 8px;
  padding: 7px 14px;
  backdrop-filter: blur(6px);
  border: 1.5px solid;
  white-space: nowrap;
  pointer-events: none;
}}
.label-num {{
  width: 26px; height: 26px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 900;
  flex-shrink: 0;
}}
.label-text {{
  display: flex; flex-direction: column; gap: 1px;
}}
.label-title {{ font-size: 13px; font-weight: 700; }}
.label-sub   {{ font-size: 10px; opacity: 0.7; }}

/* ── 연결 화살표 ── */
.flow-arrow {{
  position: absolute;
  font-size: 20px;
  font-weight: 900;
  animation: arrowPulse 1.2s ease-in-out infinite alternate;
  pointer-events: none;
  text-shadow: 0 0 8px currentColor;
}}
@keyframes arrowPulse {{
  from {{ opacity: 0.4; transform: translateX(-3px); }}
  to   {{ opacity: 1.0; transform: translateX(3px);  }}
}}

/* ── AI Vision 스캔빔 ── */
.scan-beam {{
  position: absolute;
  border-radius: 2px;
  animation: beamPulse 1.5s ease-in-out infinite alternate;
  pointer-events: none;
}}
@keyframes beamPulse {{
  from {{ opacity: 0.5; transform: scaleY(0.7); }}
  to   {{ opacity: 1.0; transform: scaleY(1.0); }}
}}

/* ── OK 배지 ── */
.ok-badge {{
  position: absolute;
  background: rgba(5,150,105,0.92);
  color: #fff;
  font-size: 11px; font-weight: 800;
  padding: 4px 10px;
  border-radius: 20px;
  border: 1.5px solid #34D399;
  animation: badgeBlink 1.8s ease-in-out infinite;
  pointer-events: none;
}}
@keyframes badgeBlink {{
  0%,100% {{ opacity:1; box-shadow: 0 0 8px #34D399; }}
  50%      {{ opacity:0.4; box-shadow: none; }}
}}

/* ── 하단 스텝 바 ── */
.step-bar {{
  display: flex;
  gap: 6px;
  margin-top: 10px;
}}
.step {{
  flex: 1;
  background: #1E293B;
  border-radius: 8px;
  padding: 12px 10px;
  text-align: center;
  border-top: 3px solid;
}}
.step-n   {{ font-size: 17px; font-weight: 900; line-height:1; margin-bottom:4px; }}
.step-t   {{ font-size: 12px; font-weight: 700; color:#F1F5F9; margin-bottom:3px; }}
.step-d   {{ font-size: 10px; color:#94A3B8; line-height:1.5; }}
</style>
</head>
<body>

<div class="wrap">
  <img class="main-img" src="data:image/png;base64,{img_b64}"/>

  <!-- ① 생산동 — 이미지 좌측 컨베이어 시작부분 -->
  <div class="label" style="top:4%; left:1%;
    border-color:#38BDF8; color:#38BDF8;">
    <div class="label-num" style="background:#1E40AF; color:#fff;">①</div>
    <div class="label-text">
      <span class="label-title">생산동</span>
      <span class="label-sub">컨베이어 시작</span>
    </div>
  </div>

  <!-- 화살표 ①→② -->
  <div class="flow-arrow" style="top:38%; left:56%; color:#CBD5E1;">→</div>

  <!-- ② 휴머노이드 — 이미지 우측 로봇 -->
  <div class="label" style="top:4%; right:3%;
    border-color:#A78BFA; color:#A78BFA;">
    <div class="label-num" style="background:#7C3AED; color:#fff;">②</div>
    <div class="label-text">
      <span class="label-title">휴머노이드 로봇</span>
      <span class="label-sub">Pick & Place</span>
    </div>
  </div>

  <!-- 화살표 ②→③ (아래→왼쪽 방향 표시) -->
  <div class="flow-arrow" style="top:58%; left:53%;
    color:#CBD5E1; animation-delay:0.3s; transform:rotate(180deg);">→</div>

  <!-- ③ AI Vision — 이미지 중앙 상단 카메라 게이트 -->
  <div class="label" style="top:4%; left:37%;
    border-color:#F59E0B; color:#F59E0B;">
    <div class="label-num" style="background:#B45309; color:#fff;">③</div>
    <div class="label-text">
      <span class="label-title">AI Vision 검수</span>
      <span class="label-sub">재검수 컨베이어</span>
    </div>
  </div>

  <!-- 스캔빔 (카메라 아래) -->
  <div class="scan-beam" style="top:18%; left:47%;
    width:3px; height:18%;
    background:linear-gradient(to bottom,#F59E0B,transparent);
    box-shadow:0 0 10px #F59E0B;"></div>
  <div class="scan-beam" style="top:18%; left:52%;
    width:3px; height:18%;
    background:linear-gradient(to bottom,#F59E0B,transparent);
    box-shadow:0 0 10px #F59E0B;
    animation-delay:0.5s;"></div>

  <!-- OK 배지 -->
  <div class="ok-badge" style="top:40%; left:42%;">✓ OK</div>

  <!-- 화살표 ③→④ -->
  <div class="flow-arrow" style="top:38%; left:27%;
    color:#CBD5E1; animation-delay:0.6s;">→</div>

  <!-- ④ 창고/출고 — 이미지 우상단 -->
  <div class="label" style="top:4%; left:1%; margin-top:52px;
    border-color:#34D399; color:#34D399;">
    <div class="label-num" style="background:#065F46; color:#fff;">④</div>
    <div class="label-text">
      <span class="label-title">창고 · 출고</span>
      <span class="label-sub">WMS 반영</span>
    </div>
  </div>

</div>

<!-- 하단 스텝 바 -->
<div class="step-bar">
  <div class="step" style="border-top-color:#38BDF8;">
    <div class="step-n" style="color:#38BDF8;">①</div>
    <div class="step-t">생산동</div>
    <div class="step-d">생산 라인에서<br>컨베이어로 이동</div>
  </div>
  <div class="step" style="border-top-color:#A78BFA;">
    <div class="step-n" style="color:#A78BFA;">②</div>
    <div class="step-t">휴머노이드</div>
    <div class="step-d">빵 집어 P-Box에<br>Pick & Place</div>
  </div>
  <div class="step" style="border-top-color:#F59E0B; background:#1C1400;">
    <div class="step-n" style="color:#F59E0B;">③</div>
    <div class="step-t">AI Vision</div>
    <div class="step-d">P-Box 컨베이어 재진입<br>SKU·수량 실시간 판정</div>
  </div>
  <div class="step" style="border-top-color:#34D399;">
    <div class="step-n" style="color:#34D399;">④</div>
    <div class="step-t">창고 · 출고</div>
    <div class="step-d">OK만 입고<br>WMS 자동 반영</div>
  </div>
</div>

</body>
</html>
""", height=660, scrolling=False)

st.markdown("")
st.markdown("---")

st.markdown(
    f'<div style="font-size:11px;font-weight:700;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:14px;">PROCESS DETAIL · 단계별 상세</div>',
    unsafe_allow_html=True)

cols = st.columns(4)
steps = [
    (cols[0], "①", "생산동", COLORS["accent_cobalt"],
     "생산 라인에서 낱개(EA) 단위로 제품이 생산되어 컨베이어 위에 올려집니다."),
    (cols[1], "②", "휴머노이드\nPick & Place", "#7C3AED",
     "휴머노이드 로봇이 컨베이어에서 빵을 집어 P-Box에 담습니다. 이 지점이 EA→Case 단위 전환 구간입니다."),
    (cols[2], "③", "AI Vision 검수", COLORS["accent_gold"],
     "P-Box가 검수 컨베이어로 재진입해 AI Vision 게이트를 통과합니다. SKU·수량 실시간 판정 후 NG는 즉시 차단합니다."),
    (cols[3], "④", "창고 · 출고", COLORS["status_ok"],
     "OK 판정된 P-Box만 창고에 적재됩니다. WMS에 자동 반영 후 매장별 수량에 따라 출고됩니다."),
]
for col, num, title, color, desc in steps:
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-top:3px solid {color};border-radius:8px;padding:16px;">'
        f'<div style="font-size:22px;font-weight:900;color:{color};margin-bottom:4px;">{num}</div>'
        f'<div style="font-size:13px;font-weight:700;color:{COLORS["text_primary"]};'
        f'margin-bottom:6px;white-space:pre-line;">{title}</div>'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};line-height:1.7;">{desc}</div>'
        f'</div>', unsafe_allow_html=True)

st.markdown("")
st.markdown(
    f'<div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:8px;padding:18px 24px;">'
    f'<div style="font-size:15px;font-weight:700;color:{COLORS["accent_gold"]};margin-bottom:8px;">'
    f'⭐ 핵심 — AI Vision을 단위 변환 지점에 설치하는 이유</div>'
    f'<div style="font-size:14px;color:{COLORS["text_secondary"]};line-height:1.9;">'
    f'낱개(EA) → 박스(Case)로 전환되는 순간 개별 수량 정보가 압축됩니다. '
    f'이 지점 직후 P-Box를 AI Vision으로 검수하면 '
    f'<strong style="color:{COLORS["status_danger"]};">정보 손실(IRI)</strong>을 원천 차단할 수 있습니다. '
    f'이것이 채찍효과(Bullwhip Effect)의 <strong style="color:{COLORS["accent_gold"]};">'
    f'미시적 시작점에서의 개입</strong>입니다.'
    f'</div></div>', unsafe_allow_html=True)
