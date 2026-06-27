"""
생산·물류 흐름도 — 실제 이미지 기반 + 구역 오버레이
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
render_page_subtitle("PRODUCTION & LOGISTICS FLOW · AI VISION GATE · HUMANOID ROBOT")

# ── 이미지 base64 인코딩 ──
img_path = os.path.join(os.path.dirname(__file__), "..", "assets", "flow_image.png")
with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

# ── HTML 오버레이 컴포넌트 ──
components.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#0F172A; font-family:'Segoe UI',sans-serif; }}

.container {{
  position: relative;
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
}}

img.base {{
  width: 100%;
  border-radius: 12px;
  display: block;
}}

/* 오버레이 구역 라벨 */
.zone {{
  position: absolute;
  background: rgba(15,23,42,0.82);
  border-radius: 6px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.04em;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255,255,255,0.12);
  white-space: nowrap;
}}

/* 번호 뱃지 */
.badge {{
  position: absolute;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 900;
  border: 2px solid rgba(255,255,255,0.5);
  animation: pulse 2s ease-in-out infinite;
}}

@keyframes pulse {{
  0%,100% {{ transform: scale(1); opacity:1; }}
  50%      {{ transform: scale(1.15); opacity:0.85; }}
}}

/* AI Vision 스캔 빔 애니메이션 */
.scan-beam {{
  position: absolute;
  width: 3px;
  background: linear-gradient(to bottom, #F59E0B, transparent);
  animation: scan 1.5s ease-in-out infinite alternate;
  border-radius: 2px;
  box-shadow: 0 0 10px #F59E0B, 0 0 20px rgba(245,158,11,0.4);
}}
@keyframes scan {{
  from {{ transform: scaleY(0.6); opacity:0.6; }}
  to   {{ transform: scaleY(1.0); opacity:1.0; }}
}}

/* OK 배지 깜빡임 */
.ok-badge {{
  position: absolute;
  background: rgba(5,150,105,0.9);
  color: white;
  font-size: 12px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 20px;
  animation: blink 1.8s ease-in-out infinite;
  border: 1.5px solid #34D399;
}}
@keyframes blink {{
  0%,100% {{ opacity:1; }}
  50%      {{ opacity:0.4; }}
}}

/* 화살표 */
.arrow {{
  position: absolute;
  font-size: 22px;
  color: rgba(255,255,255,0.6);
  animation: arrowMove 1.2s ease-in-out infinite alternate;
}}
@keyframes arrowMove {{
  from {{ transform: translateX(-4px); opacity:0.5; }}
  to   {{ transform: translateX(4px);  opacity:1.0; }}
}}

/* 하단 설명 바 */
.info-bar {{
  display: flex;
  gap: 8px;
  margin-top: 10px;
  padding: 0 4px;
}}
.info-step {{
  flex: 1;
  background: rgba(30,45,95,0.95);
  border-radius: 8px;
  padding: 12px 10px;
  text-align: center;
  border-top: 3px solid transparent;
}}
.info-num  {{ font-size: 18px; font-weight: 900; line-height:1; margin-bottom:4px; }}
.info-title {{ font-size: 12px; font-weight: 700; color: #F8FAFC; margin-bottom:3px; }}
.info-desc {{ font-size: 10px; color: #94A3B8; line-height:1.5; }}
</style>
</head>
<body>
<div class="container">

  <!-- 메인 이미지 -->
  <img class="base" src="data:image/png;base64,{img_b64}" alt="물류 흐름도"/>

  <!-- ① 생산 라인 라벨 -->
  <div class="zone" style="top:5%; left:1%; color:#38BDF8; border-color:#38BDF8;">
    생산동
  </div>
  <div class="badge" style="top:8%; left:12%; background:#1E40AF; color:white;">①</div>

  <!-- ② 컨베이어 라벨 -->
  <div class="zone" style="top:5%; left:30%; color:#34D399; border-color:#34D399;">
    물류 컨베이어
  </div>
  <div class="badge" style="top:20%; left:38%; background:#059669; color:white;">②</div>

  <!-- ③ AI Vision 라벨 + 스캔빔 -->
  <div class="zone" style="top:2%; left:50%; color:#F59E0B; border-color:#F59E0B;">
    ③ AI Vision 검수 게이트
  </div>
  <div class="scan-beam" style="top:12%; left:54%; height:22%;"></div>
  <div class="scan-beam" style="top:12%; left:60%; height:22%; animation-delay:0.4s;"></div>
  <div class="ok-badge" style="top:38%; left:55%;">✓ OK</div>

  <!-- ④ 휴머노이드 로봇 라벨 -->
  <div class="zone" style="top:55%; right:2%; color:#A78BFA; border-color:#A78BFA;">
    ④ 휴머노이드 로봇
  </div>
  <div class="badge" style="top:62%; right:22%; background:#7C3AED; color:white;">④</div>

  <!-- ⑤ 창고 라벨 -->
  <div class="zone" style="top:5%; right:1%; color:#6EE7B7; border-color:#6EE7B7;">
    창고 · 출고
  </div>
  <div class="badge" style="top:8%; right:5%; background:#065F46; color:white;">⑤</div>

  <!-- 흐름 화살표 -->
  <div class="arrow" style="top:40%; left:25%;">→</div>
  <div class="arrow" style="top:40%; left:45%; animation-delay:0.3s;">→</div>
  <div class="arrow" style="top:40%; left:66%; animation-delay:0.6s;">→</div>

</div>

<!-- 하단 설명 바 -->
<div class="info-bar">
  <div class="info-step" style="border-top-color:#38BDF8;">
    <div class="info-num" style="color:#38BDF8;">①</div>
    <div class="info-title">생산 라인</div>
    <div class="info-desc">10개 LINE<br>낱개(EA) 생산</div>
  </div>
  <div class="info-step" style="border-top-color:#34D399;">
    <div class="info-num" style="color:#34D399;">②</div>
    <div class="info-title">물류 컨베이어</div>
    <div class="info-desc">P-Box 적재<br>연속 이동</div>
  </div>
  <div class="info-step" style="border-top-color:#F59E0B; background:rgba(45,27,0,0.95);">
    <div class="info-num" style="color:#F59E0B;">③</div>
    <div class="info-title">AI Vision 검수</div>
    <div class="info-desc">실시간 스캔<br>NG 즉시 차단</div>
  </div>
  <div class="info-step" style="border-top-color:#A78BFA;">
    <div class="info-num" style="color:#A78BFA;">④</div>
    <div class="info-title">휴머노이드 로봇</div>
    <div class="info-desc">P-Box 채우기<br>EA→Case 전환</div>
  </div>
  <div class="info-step" style="border-top-color:#6EE7B7;">
    <div class="info-num" style="color:#6EE7B7;">⑤</div>
    <div class="info-title">창고 · 출고</div>
    <div class="info-desc">WMS 자동 반영<br>매장별 출고</div>
  </div>
</div>

</body>
</html>
""", height=640, scrolling=False)

st.markdown("")
st.markdown("---")

# 단계별 설명
st.markdown(
    f'<div style="font-size:11px;font-weight:700;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:14px;">PROCESS STEPS · 단계별 설명</div>',
    unsafe_allow_html=True)

cols = st.columns(5)
steps = [
    (cols[0],"①","생산 라인",         COLORS["accent_cobalt"],
     "10개 생산 라인에서 낱개(EA) 단위로 빵을 생산합니다."),
    (cols[1],"②","물류 컨베이어",      COLORS["status_ok"],
     "생산된 빵이 P-Box에 담겨 컨베이어를 타고 물류동으로 이동합니다."),
    (cols[2],"③","AI Vision 검수",     COLORS["accent_gold"],
     "AI Vision 카메라가 P-Box를 실시간 분석해 SKU·수량을 판정합니다. NG는 즉시 차단됩니다."),
    (cols[3],"④","휴머노이드 로봇",    "#7C3AED",
     "로봇이 P-Box에 빵을 담습니다. EA→Case 전환 지점으로 정보 손실 위험 구간입니다."),
    (cols[4],"⑤","창고 적재 & 출고",  COLORS["status_ok"],
     "OK 판정된 P-Box만 창고에 적재됩니다. WMS 자동 반영 후 매장별 출고됩니다."),
]
for col, num, title, color, desc in steps:
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-top:3px solid {color};border-radius:8px;padding:16px;">'
        f'<div style="font-size:22px;font-weight:900;color:{color};margin-bottom:4px;">{num}</div>'
        f'<div style="font-size:13px;font-weight:700;color:{COLORS["text_primary"]};margin-bottom:6px;">{title}</div>'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};line-height:1.7;">{desc}</div>'
        f'</div>', unsafe_allow_html=True)

st.markdown("")
st.markdown(
    f'<div style="background:#FFFBEB;border:1px solid #FCD34D;border-radius:8px;padding:18px 24px;">'
    f'<div style="font-size:15px;font-weight:700;color:{COLORS["accent_gold"]};margin-bottom:8px;">'
    f'⭐ 핵심 — AI Vision을 단위 변환 지점에 설치하는 이유</div>'
    f'<div style="font-size:14px;color:{COLORS["text_secondary"]};line-height:1.9;">'
    f'낱개(EA) → 박스(Case)로 전환되는 순간 개별 수량 정보가 압축됩니다. '
    f'이 지점에 AI Vision 게이트를 설치하면 압축 직전에 수량을 검증하여 '
    f'<strong style="color:{COLORS["status_danger"]};">정보 손실(IRI)</strong>을 원천 차단합니다. '
    f'이것이 채찍효과(Bullwhip Effect)의 <strong style="color:{COLORS["accent_gold"]};">미시적 시작점에서의 개입</strong>입니다.'
    f'</div></div>', unsafe_allow_html=True)
