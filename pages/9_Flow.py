"""
생산·물류 흐름도 — Figure AI 로봇 + 연속 컨베이어
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
render_page_subtitle("PRODUCTION & LOGISTICS FLOW · HUMANOID ROBOT · AI VISION GATE")

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
body{background:#0F172A;font-family:'Segoe UI',sans-serif;}
canvas{display:block;}
</style>
</head>
<body>
<canvas id="c"></canvas>
<script>
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
cv.width  = window.innerWidth || 980;
cv.height = 440;
const W = cv.width, H = cv.height;

let t = 0;

// ── 레이아웃 ──
const CY1 = 170;  // 컨베이어1 Y
const CY2 = 290;  // 컨베이어2 Y
const CH  = 24;   // 컨베이어 높이
const CX1 = 10;   // 컨베이어 시작 X
const CX2 = W-10; // 컨베이어 끝 X

// 구역 경계
const Z1 = W*0.20;  // 생산동 끝
const Z2 = W*0.44;  // 작업실 끝
const Z3 = W*0.65;  // AI Vision 끝
const Z4 = W*0.80;  // 창고 시작

// ── 유틸 ──
function rr(x,y,w,h,r){
  ctx.beginPath();
  ctx.roundRect(x,y,w,h,r||0);
}

// ── 배경 ──
function drawBG(){
  const bg=ctx.createLinearGradient(0,0,0,H);
  bg.addColorStop(0,'#0F172A');
  bg.addColorStop(1,'#1E293B');
  ctx.fillStyle=bg; ctx.fillRect(0,0,W,H);

  // 구역 배경
  const zones=[
    {x:0,      w:Z1,    c:'rgba(14,165,233,0.06)'},
    {x:Z1,     w:Z2-Z1, c:'rgba(245,158,11,0.07)'},
    {x:Z2,     w:Z3-Z2, c:'rgba(16,185,129,0.06)'},
    {x:Z3,     w:Z4-Z3, c:'rgba(245,158,11,0.08)'},
    {x:Z4,     w:W-Z4,  c:'rgba(14,165,233,0.06)'},
  ];
  zones.forEach(z=>{
    ctx.fillStyle=z.c;
    ctx.fillRect(z.x,0,z.w,H);
  });

  // 구역 구분선
  [Z1,Z2,Z3,Z4].forEach(x=>{
    ctx.setLineDash([6,8]);
    ctx.strokeStyle='rgba(148,163,184,0.3)';
    ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H-50); ctx.stroke();
    ctx.setLineDash([]);
  });

  // 구역 라벨
  const labels=[
    {x:Z1/2,           t:'생산동',       c:'#38BDF8'},
    {x:(Z1+Z2)/2,      t:'작업실',       c:'#FCD34D'},
    {x:(Z2+Z3)/2,      t:'물류 컨베이어', c:'#34D399'},
    {x:(Z3+Z4)/2,      t:'AI Vision',    c:'#FCD34D'},
    {x:(Z4+W)/2,       t:'물류동 · 창고', c:'#6EE7B7'},
  ];
  ctx.textAlign='center';
  labels.forEach(l=>{
    ctx.font='bold 13px Segoe UI';
    ctx.fillStyle=l.c;
    // 라벨 배경
    const tw=ctx.measureText(l.t).width;
    ctx.fillStyle='rgba(15,23,42,0.7)';
    rr(l.x-tw/2-8,6,tw+16,20,4); ctx.fill();
    ctx.fillStyle=l.c;
    ctx.fillText(l.t, l.x, 20);
  });
}

// ── 연속 컨베이어 ──
function drawConveyor(y){
  // 레일 본체
  const g=ctx.createLinearGradient(0,y,0,y+CH);
  g.addColorStop(0,'#334155');
  g.addColorStop(0.4,'#475569');
  g.addColorStop(1,'#1E293B');
  ctx.fillStyle=g;
  rr(CX1,y,CX2-CX1,CH,3); ctx.fill();

  // 상단 하이라이트
  ctx.fillStyle='rgba(148,163,184,0.25)';
  ctx.fillRect(CX1,y,CX2-CX1,3);

  // 롤러
  ctx.fillStyle='#64748B';
  for(let x=CX1+12;x<CX2-CX1;x+=24){
    ctx.beginPath();
    ctx.ellipse(x, y+CH/2, 3.5, CH/2-2, 0, 0, Math.PI*2);
    ctx.fill();
    ctx.fillStyle='#475569';
    ctx.beginPath();
    ctx.ellipse(x, y+CH/2, 2, CH/2-3, 0, 0, Math.PI*2);
    ctx.fill();
    ctx.fillStyle='#64748B';
  }

  // 이동 효과 (빛줄기)
  const off=(t*1.8)%24;
  ctx.strokeStyle='rgba(56,189,248,0.12)';
  ctx.lineWidth=1;
  for(let x=CX1-24+off;x<CX2;x+=24){
    ctx.beginPath(); ctx.moveTo(x,y+2); ctx.lineTo(x,y+CH-2); ctx.stroke();
  }

  // 측면 레일
  ctx.fillStyle='#94A3B8';
  ctx.fillRect(CX1, y-3, CX2-CX1, 4);
  ctx.fillRect(CX1, y+CH-1, CX2-CX1, 4);
}

// ── 빵 아이템 ──
function drawBread(x,y,type){
  ctx.save();
  if(type===0){ // 주황 빵
    const g=ctx.createRadialGradient(x-4,y-3,2,x,y,12);
    g.addColorStop(0,'#FB923C'); g.addColorStop(1,'#EA580C');
    ctx.fillStyle=g;
    ctx.beginPath(); ctx.ellipse(x,y,12,8,0,0,Math.PI*2); ctx.fill();
    // 깨
    ctx.fillStyle='#FDE68A';
    for(let i=0;i<6;i++){
      const a=i*1.05, r=5;
      ctx.beginPath(); ctx.ellipse(x+Math.cos(a)*r,y+Math.sin(a)*r*0.65,1.2,0.8,a,0,Math.PI*2); ctx.fill();
    }
    // 윤기
    ctx.fillStyle='rgba(255,255,255,0.25)';
    ctx.beginPath(); ctx.ellipse(x-3,y-3,5,3,-0.3,0,Math.PI*2); ctx.fill();
  } else { // 초록 제품
    const g=ctx.createRadialGradient(x-3,y-2,2,x,y,11);
    g.addColorStop(0,'#4ADE80'); g.addColorStop(1,'#16A34A');
    ctx.fillStyle=g;
    ctx.beginPath(); ctx.ellipse(x,y,11,7.5,0,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='rgba(255,255,255,0.2)';
    ctx.beginPath(); ctx.ellipse(x-3,y-2,4,2.5,-0.3,0,Math.PI*2); ctx.fill();
  }
  ctx.restore();
}

// ── P-Box (3D) ──
function drawPBox(x,y,w,h,filled,alpha){
  ctx.save(); ctx.globalAlpha=alpha||1;
  const dep=8;
  // 우측면
  const sr=ctx.createLinearGradient(x+w,y,x+w+dep,y+h);
  sr.addColorStop(0,'#1E3A8A'); sr.addColorStop(1,'#1e2d5f');
  ctx.fillStyle=sr;
  ctx.beginPath();
  ctx.moveTo(x+w,y); ctx.lineTo(x+w+dep,y-dep);
  ctx.lineTo(x+w+dep,y+h-dep); ctx.lineTo(x+w,y+h);
  ctx.fill();
  // 윗면
  const st=ctx.createLinearGradient(x,y,x+w,y-dep);
  st.addColorStop(0,'#3B82F6'); st.addColorStop(1,'#2563EB');
  ctx.fillStyle=st;
  ctx.beginPath();
  ctx.moveTo(x,y); ctx.lineTo(x+w,y);
  ctx.lineTo(x+w+dep,y-dep); ctx.lineTo(x+dep,y-dep);
  ctx.fill();
  // 앞면
  const sf=ctx.createLinearGradient(x,y,x,y+h);
  sf.addColorStop(0,'#3B82F6'); sf.addColorStop(1,'#1D4ED8');
  ctx.fillStyle=sf;
  ctx.fillRect(x,y,w,h);
  // 테두리
  ctx.strokeStyle='rgba(147,197,253,0.4)'; ctx.lineWidth=1;
  ctx.strokeRect(x,y,w,h);
  // 빵 내용물
  if(filled){
    const bc=['#F97316','#EA580C','#16A34A','#F97316'];
    for(let r=0;r<2;r++) for(let c=0;c<2;c++){
      ctx.fillStyle=bc[r*2+c];
      ctx.beginPath();
      ctx.ellipse(x+7+c*11, y+6+r*8, 4,3,0,0,Math.PI*2);
      ctx.fill();
    }
  }
  ctx.restore();
}

// ── Figure AI 휴머노이드 로봇 ──
function drawFigureRobot(x, y, armPhase){
  ctx.save();
  ctx.translate(x,y);
  const p = armPhase; // 0~1 사이클

  // 그림자
  const sg=ctx.createRadialGradient(0,78,0,0,78,22);
  sg.addColorStop(0,'rgba(0,0,0,0.4)'); sg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=sg;
  ctx.beginPath(); ctx.ellipse(0,78,22,6,0,0,Math.PI*2); ctx.fill();

  // ── 다리 ──
  // 왼쪽 다리
  const lly = Math.sin(p*Math.PI*2)*5;
  // 허벅지
  ctx.fillStyle='#334155';
  rr(-10,46,9,18,3); ctx.fill();
  rr(1,46+lly,9,18,3); ctx.fill();
  // 무릎 조인트
  ctx.fillStyle='#475569';
  ctx.beginPath(); ctx.arc(-5,64,4.5,0,Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(5,64+lly,4.5,0,Math.PI*2); ctx.fill();
  // 종아리
  ctx.fillStyle='#1E293B';
  rr(-11,64,9,14,2); ctx.fill();
  rr(2,64+lly,9,14,2); ctx.fill();
  // 발
  const fg=ctx.createLinearGradient(-14,76,14,80);
  fg.addColorStop(0,'#334155'); fg.addColorStop(1,'#1E293B');
  ctx.fillStyle=fg;
  rr(-14,76,16,6,2); ctx.fill();
  rr(-2,76+lly,16,6,2); ctx.fill();

  // ── 허리 ──
  const wg=ctx.createLinearGradient(-12,38,12,46);
  wg.addColorStop(0,'#334155'); wg.addColorStop(1,'#1E293B');
  ctx.fillStyle=wg;
  rr(-11,38,22,10,3); ctx.fill();
  // 허리 라인
  ctx.strokeStyle='rgba(56,189,248,0.5)'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.moveTo(-10,42); ctx.lineTo(10,42); ctx.stroke();

  // ── 몸통 ──
  const tg=ctx.createLinearGradient(-14,10,14,38);
  tg.addColorStop(0,'#374151'); tg.addColorStop(1,'#1F2937');
  ctx.fillStyle=tg;
  rr(-14,10,28,30,4); ctx.fill();
  // 가슴 패널
  const pg=ctx.createLinearGradient(-8,14,8,32);
  pg.addColorStop(0,'rgba(56,189,248,0.15)');
  pg.addColorStop(1,'rgba(56,189,248,0.05)');
  ctx.fillStyle=pg;
  rr(-8,14,16,20,3); ctx.fill();
  ctx.strokeStyle='rgba(56,189,248,0.4)'; ctx.lineWidth=0.8;
  rr(-8,14,16,20,3); ctx.stroke();
  // 가슴 LED 점
  ctx.fillStyle=`rgba(56,189,248,${0.7+0.3*Math.sin(t*0.08)})`;
  ctx.beginPath(); ctx.arc(0,22,2.5,0,Math.PI*2); ctx.fill();
  // 복부 라인
  ctx.strokeStyle='rgba(100,116,139,0.6)'; ctx.lineWidth=0.8;
  [-4,0,4].forEach(lx=>{
    ctx.beginPath(); ctx.moveTo(lx,26); ctx.lineTo(lx,36); ctx.stroke();
  });

  // ── 어깨 ──
  ctx.fillStyle='#4B5563';
  ctx.beginPath(); ctx.arc(-16,14,6,0,Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(16,14,6,0,Math.PI*2); ctx.fill();

  // ── 팔 (동적 - 박스 집는 동작) ──
  const la = Math.sin(p*Math.PI*2)*18;  // 왼팔 각도
  const ra = Math.cos(p*Math.PI*2)*15;  // 오른팔 각도

  // 왼팔
  ctx.save();
  ctx.translate(-16,16); ctx.rotate((la-15)*Math.PI/180);
  ctx.fillStyle='#374151';
  rr(-4,0,8,16,3); ctx.fill();
  // 왼팔 팔꿈치
  ctx.fillStyle='#4B5563';
  ctx.beginPath(); ctx.arc(0,16,4,0,Math.PI*2); ctx.fill();
  // 왼쪽 아래팔
  ctx.translate(0,16); ctx.rotate(la*0.5*Math.PI/180);
  ctx.fillStyle='#1F2937';
  rr(-3.5,0,7,14,2); ctx.fill();
  // 왼손
  ctx.fillStyle='#374151';
  rr(-5,14,10,7,3); ctx.fill();
  ctx.restore();

  // 오른팔
  ctx.save();
  ctx.translate(16,16); ctx.rotate((-ra+15)*Math.PI/180);
  ctx.fillStyle='#374151';
  rr(-4,0,8,16,3); ctx.fill();
  ctx.fillStyle='#4B5563';
  ctx.beginPath(); ctx.arc(0,16,4,0,Math.PI*2); ctx.fill();
  ctx.translate(0,16); ctx.rotate(-ra*0.5*Math.PI/180);
  ctx.fillStyle='#1F2937';
  rr(-3.5,0,7,14,2); ctx.fill();
  ctx.fillStyle='#374151';
  rr(-5,14,10,7,3); ctx.fill();
  ctx.restore();

  // ── 목 ──
  ctx.fillStyle='#374151';
  rr(-4,3,8,9,2); ctx.fill();

  // ── 머리 ──
  const hg=ctx.createLinearGradient(-13,-20,13,5);
  hg.addColorStop(0,'#374151'); hg.addColorStop(1,'#1F2937');
  ctx.fillStyle=hg;
  rr(-12,-20,24,26,6); ctx.fill();
  // 머리 테두리
  ctx.strokeStyle='rgba(56,189,248,0.25)'; ctx.lineWidth=1;
  rr(-12,-20,24,26,6); ctx.stroke();

  // 눈 (LED 바 스타일 - Figure AI 특징)
  const eyeAlpha = 0.7+0.3*Math.sin(t*0.07);
  const eyeGrad=ctx.createLinearGradient(-8,-9,8,-9);
  eyeGrad.addColorStop(0,'rgba(56,189,248,0)');
  eyeGrad.addColorStop(0.3,`rgba(56,189,248,${eyeAlpha})`);
  eyeGrad.addColorStop(0.7,`rgba(56,189,248,${eyeAlpha})`);
  eyeGrad.addColorStop(1,'rgba(56,189,248,0)');
  ctx.fillStyle=eyeGrad;
  rr(-8,-12,16,5,2); ctx.fill();

  // 눈 내부 스캔 라인
  ctx.fillStyle=`rgba(186,230,253,${eyeAlpha})`;
  const scanX = -6 + ((t*0.08)%12);
  rr(scanX,-11.5,3,4,1); ctx.fill();

  // 바이저 반사
  ctx.fillStyle='rgba(255,255,255,0.04)';
  rr(-10,-19,20,10,4); ctx.fill();

  // 귀 (센서)
  ctx.fillStyle='#4B5563';
  rr(-14,-12,4,8,2); ctx.fill();
  rr(10,-12,4,8,2); ctx.fill();
  ctx.fillStyle=`rgba(56,189,248,${0.5+0.5*Math.sin(t*0.05)})`;
  ctx.beginPath(); ctx.arc(-12,-8,1.5,0,Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(12,-8,1.5,0,Math.PI*2); ctx.fill();

  ctx.restore();
}

// ── AI Vision 카메라 ──
function drawVisionCamera(x,y,flip){
  ctx.save(); ctx.translate(x,y); if(flip) ctx.scale(1,-1);

  // 마운트 암
  ctx.fillStyle='#334155';
  ctx.fillRect(-3,-28,6,28);
  ctx.fillRect(-10,-32,20,6);

  // 카메라 본체
  const cg=ctx.createLinearGradient(-16,0,16,24);
  cg.addColorStop(0,'#F59E0B'); cg.addColorStop(1,'#B45309');
  ctx.fillStyle=cg;
  rr(-16,0,32,24,4); ctx.fill();
  ctx.strokeStyle='#78350F'; ctx.lineWidth=1.2;
  rr(-16,0,32,24,4); ctx.stroke();

  // 렌즈
  ctx.fillStyle='#0F172A';
  ctx.beginPath(); ctx.arc(0,12,8,0,Math.PI*2); ctx.fill();
  const lg=ctx.createRadialGradient(-3,9,1,0,12,8);
  lg.addColorStop(0,'rgba(56,189,248,0.8)');
  lg.addColorStop(0.6,'rgba(14,165,233,0.4)');
  lg.addColorStop(1,'rgba(2,132,199,0.1)');
  ctx.fillStyle=lg;
  ctx.beginPath(); ctx.arc(0,12,7,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='rgba(255,255,255,0.5)';
  ctx.beginPath(); ctx.arc(-2,10,2.5,0,Math.PI*2); ctx.fill();

  // LED 상태 표시
  ctx.fillStyle=`rgba(52,211,153,${0.6+0.4*Math.sin(t*0.09)})`;
  ctx.beginPath(); ctx.arc(10,4,3,0,Math.PI*2); ctx.fill();

  // 스캔 빔
  const ba = 0.12+0.08*Math.sin(t*0.06);
  const bg=ctx.createLinearGradient(0,24,0,130);
  bg.addColorStop(0,`rgba(245,158,11,${ba+0.25})`);
  bg.addColorStop(0.5,`rgba(245,158,11,${ba})`);
  bg.addColorStop(1,'rgba(245,158,11,0)');
  ctx.fillStyle=bg;
  ctx.beginPath();
  ctx.moveTo(-4,24); ctx.lineTo(-34,130); ctx.lineTo(34,130); ctx.lineTo(4,24);
  ctx.fill();

  // 수평 스캔 라인
  const sy=50+50*Math.sin(t*0.08);
  ctx.strokeStyle=`rgba(245,158,11,${0.5+0.4*Math.abs(Math.sin(t*0.08))})`;
  ctx.lineWidth=1.5; ctx.setLineDash([3,3]);
  ctx.beginPath(); ctx.moveTo(-30+sy*0.3,sy); ctx.lineTo(30-sy*0.3,sy); ctx.stroke();
  ctx.setLineDash([]);
  ctx.restore();
}

// ── 창고 스택 ──
function drawStack(x,y,cols,rows,phase){
  for(let r=0;r<rows;r++){
    for(let c=0;c<cols;c++){
      const fy=Math.sin(t*0.025+phase+r*0.8)*2;
      drawPBox(x+c*33, y-r*26+fy, 29,22, true);
    }
  }
}

// ── 빨간 흐름 화살표 ──
function drawFlowArrow(){
  const y=H-28;
  const g=ctx.createLinearGradient(20,y,W-20,y);
  g.addColorStop(0,'#DC2626'); g.addColorStop(0.7,'#EF4444'); g.addColorStop(1,'#DC2626');
  ctx.fillStyle=g;
  ctx.fillRect(20,y-5,W-60,10);
  // 화살촉
  ctx.beginPath();
  ctx.moveTo(W-40,y-14); ctx.lineTo(W-18,y); ctx.lineTo(W-40,y+14);
  ctx.fill();
  ctx.fillStyle='rgba(252,165,165,0.5)';
  ctx.font='11px Segoe UI'; ctx.textAlign='center';
  ctx.fillText('생산 → 물류 흐름', W/2, y+22);
}

// ── 방향 화살표 ──
function drawArrow(x,y){
  const ax=Math.sin(t*0.07)*4;
  ctx.save();
  ctx.fillStyle='rgba(148,163,184,0.7)';
  ctx.font='bold 18px Segoe UI';
  ctx.textAlign='center';
  ctx.fillText('▶', x+ax, y);
  ctx.restore();
}

// ── OK/NG 배지 ──
function drawBadge(x,y,ok){
  const cycle=Math.floor(t/90)%2;
  const show=ok?(cycle===0):(cycle===1);
  const alpha=show?(0.6+0.4*Math.sin(t*0.1)):0.2;
  ctx.save(); ctx.globalAlpha=alpha;
  ctx.fillStyle=ok?'rgba(6,78,59,0.8)':'rgba(127,29,29,0.8)';
  rr(x-24,y-11,48,22,11); ctx.fill();
  ctx.strokeStyle=ok?'#34D399':'#F87171'; ctx.lineWidth=1.5;
  rr(x-24,y-11,48,22,11); ctx.stroke();
  ctx.fillStyle=ok?'#6EE7B7':'#FCA5A5';
  ctx.font='bold 11px Segoe UI'; ctx.textAlign='center';
  ctx.fillText(ok?'✓  OK':'✗  NG', x, y+4);
  ctx.restore();
}

// ── 아이템 데이터 ──
const breads1=[];
const breads2=[];
const pboxes =[];

for(let i=0;i<7;i++){
  breads1.push({ x: i*(W*0.25/5)+20, spd:1.3+Math.random()*0.3 });
  breads2.push({ x: i*(W*0.25/5)+30, spd:1.1+Math.random()*0.3 });
}
for(let i=0;i<4;i++){
  pboxes.push({ x: W*0.44+i*(W*0.05+20), spd:0.9 });
}

function animate(){
  t++;
  ctx.clearRect(0,0,W,H);
  drawBG();

  // 컨베이어 (연속)
  drawConveyor(CY1);
  drawConveyor(CY2);

  // 빵 이동 (컨베이어1 - 생산~작업실)
  breads1.forEach(b=>{
    b.x+=b.spd;
    if(b.x>Z2-10) b.x=-10;
    if(b.x>CX1 && b.x<Z2)
      drawBread(b.x, CY1-12, 0);
  });
  // 빵 이동 (컨베이어2)
  breads2.forEach(b=>{
    b.x+=b.spd;
    if(b.x>Z2-10) b.x=-10;
    if(b.x>CX1 && b.x<Z2)
      drawBread(b.x, CY2-12, 1);
  });

  // P-Box 이동 (작업실 이후)
  pboxes.forEach((b,i)=>{
    b.x+=b.spd;
    if(b.x>Z3-10) b.x=Z2+5;
    drawPBox(b.x, CY1-26, 32,24, true);
    drawPBox(b.x+15, CY2-26, 32,24, true);
  });

  // Figure AI 로봇 (라인1)
  const phase1=(t*0.012)%(Math.PI*2);
  drawFigureRobot(Z1+(Z2-Z1)*0.38, CY1-70, phase1);

  // Figure AI 로봇 (라인2)
  const phase2=(t*0.012+Math.PI)%(Math.PI*2);
  drawFigureRobot(Z1+(Z2-Z1)*0.62, CY2-70, phase2);

  // 비어있는 P-Box (작업실)
  drawPBox(Z1+30, CY1-60, 32,24, false);
  drawPBox(Z1+30, CY2-60, 32,24, false);

  // AI Vision 카메라
  drawVisionCamera(Z3+15, CY1-75, false);
  drawVisionCamera(Z3+15, CY2+75, true);

  // OK/NG 배지
  drawBadge(Z3+55, CY1-30, true);
  drawBadge(Z3+55, CY2+10, false);

  // 창고 스택
  drawStack(Z4+10,  CY1+40, 2,4, 0);
  drawStack(Z4+80,  CY1+40, 2,3, 1);
  drawStack(Z4+148, CY1+40, 2,4, 2);

  // 화살표
  drawArrow(Z1-15, CY1-5);
  drawArrow(Z2-15, CY1-5);
  drawArrow(Z3-15, CY1-5);
  drawArrow(Z4-15, CY1-5);

  // 흐름 화살표
  drawFlowArrow();

  requestAnimationFrame(animate);
}

// roundRect 폴리필
if(!CanvasRenderingContext2D.prototype.roundRect){
  CanvasRenderingContext2D.prototype.roundRect=function(x,y,w,h,r){
    this.beginPath();
    this.moveTo(x+r,y);
    this.lineTo(x+w-r,y); this.quadraticCurveTo(x+w,y,x+w,y+r);
    this.lineTo(x+w,y+h-r); this.quadraticCurveTo(x+w,y+h,x+w-r,y+h);
    this.lineTo(x+r,y+h); this.quadraticCurveTo(x,y+h,x,y+h-r);
    this.lineTo(x,y+r); this.quadraticCurveTo(x,y,x+r,y);
    this.closePath();
  };
}

animate();
</script>
</body>
</html>
""", height=470, scrolling=False)

st.markdown("")
st.markdown("---")

# 단계별 설명
st.markdown(
    f'<div style="font-size:11px;font-weight:700;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:14px;">PROCESS STEPS · 단계별 설명</div>',
    unsafe_allow_html=True)

cols = st.columns(5)
steps = [
    (cols[0],"①","생산 라인",COLORS["accent_cobalt"],
     "10개 생산 라인에서 낱개(EA) 단위로 빵을 생산합니다."),
    (cols[1],"②","작업실\n(P-Box 채우기)",COLORS["status_warning"],
     "휴머노이드 로봇이 낱개 빵을 P-Box에 담습니다. EA→Case 전환 지점으로 정보 손실 위험 구간입니다."),
    (cols[2],"③","물류 컨베이어",COLORS["accent_cobalt"],
     "P-Box가 연속 컨베이어로 이동합니다. 두 라인이 병렬로 운영됩니다."),
    (cols[3],"④","AI Vision 검수",COLORS["accent_gold"],
     "AI Vision이 P-Box를 실시간 분석해 SKU와 수량을 판정합니다. NG는 즉시 차단됩니다."),
    (cols[4],"⑤","창고 적재\n& 출고",COLORS["status_ok"],
     "OK 판정된 P-Box만 창고에 적재됩니다. WMS 자동 반영 후 매장별 출고됩니다."),
]
for col,num,title,color,desc in steps:
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-top:3px solid {color};border-radius:8px;padding:16px;">'
        f'<div style="font-size:22px;font-weight:900;color:{color};margin-bottom:4px;">{num}</div>'
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
