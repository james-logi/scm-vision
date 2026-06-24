"""
생산·물류 흐름도 — 고퀄리티 애니메이션
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
    f'</div></div>', unsafe_allow_html=True)

components.html("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#f8fafc;font-family:'Segoe UI',sans-serif;}
canvas{display:block;}
#info{display:flex;justify-content:space-around;padding:12px 20px;
      background:#fff;border-top:1px solid #E2E8F0;}
.step{text-align:center;flex:1;padding:8px 4px;}
.step-num{font-size:20px;font-weight:900;line-height:1;}
.step-title{font-size:12px;font-weight:700;margin:4px 0 2px;color:#0F172A;}
.step-desc{font-size:11px;color:#64748B;line-height:1.4;}
</style>
</head>
<body>
<canvas id="c"></canvas>
<div id="info">
  <div class="step">
    <div class="step-num" style="color:#0891B2">①</div>
    <div class="step-title">생산동</div>
    <div class="step-desc">10개 라인<br>낱개(EA) 생산</div>
  </div>
  <div class="step">
    <div class="step-num" style="color:#D97706">②</div>
    <div class="step-title">작업실</div>
    <div class="step-desc">수작업 P-Box 채우기<br>⚠ 단위 변환 지점</div>
  </div>
  <div class="step">
    <div class="step-num" style="color:#0891B2">③</div>
    <div class="step-title">물류 컨베이어</div>
    <div class="step-desc">P-Box 이동<br>물류동 배출</div>
  </div>
  <div class="step">
    <div class="step-num" style="color:#F59E0B">④</div>
    <div class="step-title">AI Vision 🔬</div>
    <div class="step-desc">실시간 검수<br>NG 즉시 차단</div>
  </div>
  <div class="step">
    <div class="step-num" style="color:#059669">⑤</div>
    <div class="step-title">창고 / 출고</div>
    <div class="step-desc">적재 & WMS 반영<br>매장별 출고 분류</div>
  </div>
</div>

<script>
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
const W = canvas.width  = window.innerWidth  || 980;
const H = canvas.height = 360;

let t = 0;

// ── 구역 경계 ──
const zones = {
  prod:   { x: 0,         w: W*0.18 },
  work:   { x: W*0.18,    w: W*0.22 },
  conv:   { x: W*0.40,    w: W*0.22 },
  vision: { x: W*0.62,    w: W*0.12 },
  ware:   { x: W*0.74,    w: W*0.26 },
};

// ── 빵 아이템 ──
const breads = [];
for(let i=0;i<6;i++){
  breads.push({
    x: Math.random()*W*0.15 + 15,
    y: 130 + (i%2)*100,
    speed: 1.2 + Math.random()*0.4,
    color: i%2===0 ? '#F97316' : '#16A34A',
    r: 13
  });
}

// ── P-Box ──
const pboxes = [];
for(let i=0;i<3;i++){
  pboxes.push({
    x: W*0.40 + i*(W*0.08),
    y: 155,
    speed: 1.0,
    filled: true
  });
}

function drawBackground(){
  ctx.fillStyle = '#f8fafc';
  ctx.fillRect(0,0,W,H);

  // 구역 배경
  const zColors = ['#EFF6FF','#FFFBEB','#F0F9FF','#FFFDE7','#F0FDF4'];
  const zList = Object.values(zones);
  zList.forEach((z,i)=>{
    ctx.fillStyle = zColors[i];
    ctx.fillRect(z.x, 0, z.w, H-80);
  });

  // 구역 구분선
  [W*0.18, W*0.40, W*0.62, W*0.74].forEach(x=>{
    ctx.setLineDash([8,8]);
    ctx.strokeStyle='#94A3B8';
    ctx.lineWidth=1.5;
    ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H-80); ctx.stroke();
    ctx.setLineDash([]);
  });

  // 구역 라벨
  const labels = [
    {x:W*0.09, text:'생산동', color:'#1E40AF'},
    {x:W*0.29, text:'작업실', color:'#D97706'},
    {x:W*0.51, text:'물류 컨베이어', color:'#0891B2'},
    {x:W*0.68, text:'AI Vision', color:'#D97706'},
    {x:W*0.87, text:'물류동 · 창고', color:'#059669'},
  ];
  labels.forEach(l=>{
    ctx.font='bold 13px Segoe UI';
    ctx.fillStyle=l.color;
    ctx.textAlign='center';
    ctx.fillText(l.text, l.x, 22);
  });
}

function drawConveyor(x,y,w,h){
  // 컨베이어 몸체
  const grad = ctx.createLinearGradient(x,y,x,y+h);
  grad.addColorStop(0,'#64748B');
  grad.addColorStop(0.5,'#475569');
  grad.addColorStop(1,'#334155');
  ctx.fillStyle=grad;
  ctx.beginPath();
  ctx.roundRect(x,y,w,h,4);
  ctx.fill();

  // 롤러
  const rollerCount = Math.floor(w/22);
  for(let i=0;i<rollerCount;i++){
    const rx = x + 11 + i*22;
    ctx.fillStyle='#94A3B8';
    ctx.beginPath();
    ctx.ellipse(rx, y+h/2, 4, h/2-1, 0, 0, Math.PI*2);
    ctx.fill();
  }

  // 벨트 라인 (이동 효과)
  ctx.strokeStyle='rgba(255,255,255,0.15)';
  ctx.lineWidth=1;
  const offset = (t*1.5) % 22;
  for(let i=-1; i<w/22+1; i++){
    const lx = x + i*22 + offset;
    ctx.beginPath();
    ctx.moveTo(lx, y+2);
    ctx.lineTo(lx, y+h-2);
    ctx.stroke();
  }
}

function drawBread(x,y,r,color){
  // 빵 몸체
  ctx.save();
  const grad = ctx.createRadialGradient(x-r*0.3,y-r*0.3,r*0.1, x,y,r);
  grad.addColorStop(0, color==='#F97316'?'#FB923C':'#4ADE80');
  grad.addColorStop(1, color);
  ctx.fillStyle=grad;
  ctx.beginPath();
  ctx.ellipse(x,y,r,r*0.65,0,0,Math.PI*2);
  ctx.fill();
  // 윤기
  ctx.fillStyle='rgba(255,255,255,0.3)';
  ctx.beginPath();
  ctx.ellipse(x-r*0.2,y-r*0.2,r*0.35,r*0.2,-0.3,0,Math.PI*2);
  ctx.fill();
  // 깨 표시
  if(color==='#F97316'){
    ctx.fillStyle='#FDE68A';
    for(let i=0;i<5;i++){
      const sx=x+(Math.cos(i*1.2)*r*0.4), sy=y+(Math.sin(i*1.2)*r*0.3);
      ctx.beginPath(); ctx.ellipse(sx,sy,1.5,1,i*0.5,0,Math.PI*2); ctx.fill();
    }
  }
  ctx.restore();
}

function drawPBox(x,y,w,h,filled){
  ctx.save();
  // 박스 측면 (3D효과)
  ctx.fillStyle='#1E3A8A';
  ctx.beginPath();
  ctx.moveTo(x+w, y);
  ctx.lineTo(x+w+8, y-6);
  ctx.lineTo(x+w+8, y+h-6);
  ctx.lineTo(x+w, y+h);
  ctx.fill();
  // 박스 윗면
  ctx.fillStyle='#3B82F6';
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x+w, y);
  ctx.lineTo(x+w+8, y-6);
  ctx.lineTo(x+8, y-6);
  ctx.fill();
  // 박스 앞면
  const grad = ctx.createLinearGradient(x,y,x+w,y+h);
  grad.addColorStop(0,'#2563EB');
  grad.addColorStop(1,'#1D4ED8');
  ctx.fillStyle=grad;
  ctx.fillRect(x,y,w,h);
  // 테두리
  ctx.strokeStyle='#1E3A8A';
  ctx.lineWidth=1.5;
  ctx.strokeRect(x,y,w,h);
  // 내용물 (빵)
  if(filled){
    const colors=['#F97316','#F97316','#16A34A','#F97316'];
    for(let r=0;r<2;r++){
      for(let c=0;c<2;c++){
        const bx=x+6+c*13, by=y+5+r*9;
        ctx.fillStyle=colors[r*2+c];
        ctx.beginPath();
        ctx.ellipse(bx,by,5,3.5,0,0,Math.PI*2);
        ctx.fill();
      }
    }
  }
  ctx.restore();
}

// ── 휴머노이드 작업자 ──
function drawHumanoid(x,y,armAngle){
  ctx.save();
  ctx.translate(x,y);
  const scale=1.15;
  ctx.scale(scale,scale);

  // 그림자
  ctx.fillStyle='rgba(0,0,0,0.08)';
  ctx.beginPath();
  ctx.ellipse(0,68,18,5,0,0,Math.PI*2);
  ctx.fill();

  // 다리
  ctx.strokeStyle='#334155'; ctx.lineWidth=7; ctx.lineCap='round';
  ctx.beginPath(); ctx.moveTo(-5,42); ctx.lineTo(-8,65); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(5,42);  ctx.lineTo(8,65);  ctx.stroke();
  // 신발
  ctx.fillStyle='#1E293B';
  ctx.beginPath(); ctx.ellipse(-8,65,8,4,0,0,Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.ellipse(8,65,8,4,0,0,Math.PI*2); ctx.fill();

  // 몸통
  const bodyGrad = ctx.createLinearGradient(-12,10,12,40);
  bodyGrad.addColorStop(0,'#2563EB');
  bodyGrad.addColorStop(1,'#1D4ED8');
  ctx.fillStyle=bodyGrad;
  ctx.beginPath();
  ctx.roundRect(-13,15,26,28,5);
  ctx.fill();
  // 작업복 라인
  ctx.strokeStyle='rgba(255,255,255,0.2)'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(0,15); ctx.lineTo(0,43); ctx.stroke();

  // 팔 (동적)
  ctx.strokeStyle='#1E293B'; ctx.lineWidth=6; ctx.lineCap='round';
  // 왼팔 (박스를 향해)
  ctx.beginPath();
  ctx.moveTo(-13,22);
  ctx.quadraticCurveTo(-28,30+armAngle, -22,42+armAngle*0.5);
  ctx.stroke();
  // 오른팔
  ctx.beginPath();
  ctx.moveTo(13,22);
  ctx.quadraticCurveTo(28,30-armAngle, 22,42-armAngle*0.5);
  ctx.stroke();
  // 손
  ctx.fillStyle='#FBBF24';
  ctx.beginPath(); ctx.arc(-22,42+armAngle*0.5,4,0,Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(22,42-armAngle*0.5,4,0,Math.PI*2); ctx.fill();

  // 목
  ctx.fillStyle='#FBBF24';
  ctx.beginPath(); ctx.ellipse(0,12,5,6,0,0,Math.PI*2); ctx.fill();
  // 머리
  const headGrad = ctx.createRadialGradient(-3,-8,2,0,0,14);
  headGrad.addColorStop(0,'#FDE68A');
  headGrad.addColorStop(1,'#F59E0B');
  ctx.fillStyle=headGrad;
  ctx.beginPath(); ctx.ellipse(0,-2,13,14,0,0,Math.PI*2); ctx.fill();
  // 헬멧
  ctx.fillStyle='#F59E0B';
  ctx.beginPath();
  ctx.ellipse(0,-8,13,8,0,Math.PI,Math.PI*2);
  ctx.fill();
  ctx.fillStyle='#D97706';
  ctx.fillRect(-13,-10,26,4);
  // 눈
  ctx.fillStyle='#1E293B';
  ctx.beginPath(); ctx.arc(-4,0,2.5,0,Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(4,0,2.5,0,Math.PI*2); ctx.fill();
  // 눈빛
  ctx.fillStyle='white';
  ctx.beginPath(); ctx.arc(-3.2,-0.8,1,0,Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(4.8,-0.8,1,0,Math.PI*2); ctx.fill();

  ctx.restore();
}

function drawVisionCamera(x,y,scanAngle){
  ctx.save();
  ctx.translate(x,y);
  // 카메라 본체
  const camGrad = ctx.createLinearGradient(-15,0,15,20);
  camGrad.addColorStop(0,'#FCD34D');
  camGrad.addColorStop(1,'#D97706');
  ctx.fillStyle=camGrad;
  ctx.beginPath(); ctx.roundRect(-15,0,30,22,4); ctx.fill();
  ctx.strokeStyle='#B45309'; ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.roundRect(-15,0,30,22,4); ctx.stroke();
  // 렌즈
  ctx.fillStyle='#1E293B';
  ctx.beginPath(); ctx.arc(0,11,7,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='#0EA5E9';
  ctx.beginPath(); ctx.arc(0,11,5,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='rgba(255,255,255,0.5)';
  ctx.beginPath(); ctx.arc(-2,9,2,0,Math.PI*2); ctx.fill();
  // 마운트
  ctx.fillStyle='#475569';
  ctx.fillRect(-3,-12,6,12);
  ctx.fillRect(-8,-15,16,5);

  // 스캔 빔
  const alpha = 0.15 + 0.15*Math.sin(scanAngle);
  const beamGrad = ctx.createLinearGradient(0,22,0,110);
  beamGrad.addColorStop(0,`rgba(245,158,11,${alpha+0.3})`);
  beamGrad.addColorStop(0.5,`rgba(245,158,11,${alpha+0.1})`);
  beamGrad.addColorStop(1,`rgba(245,158,11,0)`);
  ctx.fillStyle=beamGrad;
  ctx.beginPath();
  ctx.moveTo(-3,22);
  ctx.lineTo(-28,110);
  ctx.lineTo(28,110);
  ctx.lineTo(3,22);
  ctx.fill();

  // 스캔 라인 (수평 sweep)
  const sweepY = 60 + 40*Math.sin(scanAngle*2);
  ctx.strokeStyle=`rgba(245,158,11,${0.6+0.4*Math.sin(scanAngle)})`;
  ctx.lineWidth=2;
  ctx.setLineDash([4,4]);
  ctx.beginPath(); ctx.moveTo(-25,sweepY); ctx.lineTo(25,sweepY); ctx.stroke();
  ctx.setLineDash([]);
  ctx.restore();
}

function drawWarehouseStack(x,y,cols,rows,color,delay){
  for(let r=0;r<rows;r++){
    for(let c=0;c<cols;c++){
      const bx=x+c*32, by=y-r*26;
      const floatY = Math.sin(t*0.03+delay+r*0.5)*2;
      drawPBox(bx, by+floatY, 28, 22, true);
    }
  }
}

// 화살표
function drawArrow(x,y){
  ctx.save();
  ctx.fillStyle='#94A3B8';
  ctx.font='bold 22px Segoe UI';
  ctx.textAlign='center';
  const anim = Math.sin(t*0.08)*3;
  ctx.fillText('›', x+anim, y);
  ctx.restore();
}

// OK/NG 배지
function drawBadge(x,y,ok,blink){
  ctx.save();
  const alpha = blink ? (0.5+0.5*Math.sin(t*0.1)) : 1;
  ctx.globalAlpha=alpha;
  ctx.fillStyle=ok?'#ECFDF5':'#FEF2F2';
  ctx.strokeStyle=ok?'#059669':'#DC2626';
  ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.roundRect(x-22,y-10,44,20,10); ctx.fill(); ctx.stroke();
  ctx.fillStyle=ok?'#059669':'#DC2626';
  ctx.font='bold 11px Segoe UI';
  ctx.textAlign='center';
  ctx.fillText(ok?'✓ OK':'✗ NG', x, y+4);
  ctx.restore();
}

// 하단 빨간 화살표
function drawBottomArrow(){
  ctx.save();
  const y=H-30;
  const grad=ctx.createLinearGradient(30,y,W-20,y);
  grad.addColorStop(0,'#EF4444');
  grad.addColorStop(1,'#DC2626');
  ctx.fillStyle=grad;
  ctx.beginPath();
  ctx.roundRect(30,y-5,W-70,10,5);
  ctx.fill();
  // 화살촉
  ctx.beginPath();
  ctx.moveTo(W-40,y-13);
  ctx.lineTo(W-20,y);
  ctx.lineTo(W-40,y+13);
  ctx.fill();
  // 텍스트
  ctx.fillStyle='#EF4444';
  ctx.font='11px Segoe UI';
  ctx.textAlign='center';
  ctx.fillText('생산 → 물류 흐름', W/2, y+22);
  ctx.restore();
}

function animate(){
  t++;
  ctx.clearRect(0,0,W,H);
  drawBackground();

  // 컨베이어
  drawConveyor(20,140,W*0.16,20);      // 생산 상단
  drawConveyor(20,240,W*0.16,20);      // 생산 하단
  drawConveyor(W*0.40,165,W*0.20,20);  // 물류

  // 빵 이동 (생산 라인)
  breads.forEach(b=>{
    b.x += b.speed;
    if(b.x > W*0.17+20) b.x = 15;
    drawBread(b.x, b.y, b.r, b.color);
  });

  // 작업자
  const armAngle = Math.sin(t*0.06)*12;
  drawHumanoid(W*0.27, 100, armAngle);

  // 공박스 (전실)
  drawPBox(W*0.22, 60, 36, 28, false);
  // 채우는 중인 박스
  drawPBox(W*0.30, 150, 36, 28, true);

  // P-Box 이동 (물류 컨베이어)
  pboxes.forEach((b,i)=>{
    b.x += b.speed;
    if(b.x > W*0.61) b.x = W*0.40;
    drawPBox(b.x, b.y, 34, 26, true);
  });

  // AI Vision 카메라
  const scanAngle = t*0.06;
  drawVisionCamera(W*0.65, 40, scanAngle);
  drawVisionCamera(W*0.65, 170, scanAngle+Math.PI);

  // OK/NG 배지
  const okCycle = Math.floor(t/80)%2===0;
  drawBadge(W*0.70, 110, okCycle, true);

  // 창고 스택
  drawWarehouseStack(W*0.76, 210, 2, 3, '#2563EB', 0);
  drawWarehouseStack(W*0.84, 195, 2, 2, '#EA580C', 1);
  drawWarehouseStack(W*0.92, 220, 2, 3, '#2563EB', 2);

  // 출고 대기 (우측 끝)
  ctx.save();
  ctx.font='bold 12px Segoe UI';
  ctx.fillStyle='#059669';
  ctx.textAlign='center';
  ctx.fillText('출고 준비', W*0.96, 260);
  ctx.restore();

  // 화살표
  drawArrow(W*0.195, 175);
  drawArrow(W*0.385, 175);
  drawArrow(W*0.615, 175);
  drawArrow(W*0.73,  175);

  // 하단 흐름 화살표
  drawBottomArrow();

  requestAnimationFrame(animate);
}

animate();
</script>
</body>
</html>
""", height=500, scrolling=False)

st.markdown("")
st.markdown("---")

# ─── 단계별 설명 ───
st.markdown(
    f'<div style="font-size:11px;font-weight:700;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:14px;">PROCESS STEPS · 단계별 설명</div>',
    unsafe_allow_html=True)

cols = st.columns(5)
steps = [
    (cols[0], "①", "생산 라인",         COLORS["accent_cobalt"],
     "10개 생산 라인에서 낱개(EA) 단위로 빵을 생산합니다."),
    (cols[1], "②", "작업실\n(P-Box 채우기)", COLORS["status_warning"],
     "작업자가 낱개 빵을 P-Box에 담습니다. EA→Case 전환 지점으로 정보 손실 위험 구간입니다."),
    (cols[2], "③", "물류 컨베이어",      COLORS["accent_cobalt"],
     "P-Box가 컨베이어에 올려져 물류동으로 이동합니다."),
    (cols[3], "④", "AI Vision 검수",     COLORS["accent_gold"],
     "AI Vision이 P-Box를 실시간 분석해 SKU·수량을 판정합니다. NG 즉시 차단합니다."),
    (cols[4], "⑤", "창고 적재\n& 출고",  COLORS["status_ok"],
     "OK 판정된 P-Box만 창고에 적재됩니다. WMS 자동 반영 후 매장별로 출고됩니다."),
]
for col, num, title, color, desc in steps:
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-top:3px solid {color};border-radius:8px;padding:16px;">'
        f'<div style="font-size:22px;font-weight:900;color:{color};line-height:1;margin-bottom:4px;">{num}</div>'
        f'<div style="font-size:13px;font-weight:700;color:{COLORS["text_primary"]};margin-bottom:6px;white-space:pre-line;">{title}</div>'
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
