"""
시스템 정보 — Vision LLM vs YOLO 기술 선택 논거
"""

import streamlit as st
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar, render_brand_header

st.set_page_config(page_title="시스템 정보 | SCM", page_icon="◆",
                   layout="wide", initial_sidebar_state="expanded")

inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 시스템 정보")
render_page_subtitle("VISION LLM VS YOLO · TECHNICAL JUSTIFICATION · HYBRID DIRECTION")

# ─── 인트로 ───
st.markdown(
    f'<div style="background:{COLORS["bg_panel"]};border-left:4px solid {COLORS["accent_gold"]};'
    f'border-radius:6px;padding:16px 22px;margin-bottom:20px;">'
    f'<div style="font-size:15px;color:{COLORS["text_secondary"]};line-height:1.8;">'
    f'본 시스템은 비전 검수 엔진으로 <strong style="color:{COLORS["accent_gold"]};">Claude Vision (Vision LLM)</strong>을 채택했습니다. '
    f'YOLO도 진지하게 고려했으나, 본 프로젝트의 요구사항(다품종·빠른 SKU 변경·의미적 추론)에는 Vision LLM이 더 적합했습니다.'
    f'</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ─── 좌우 비교 카드 ───
st.markdown(
    f'<div style="font-size:11px;font-weight:700;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:12px;">SIDE-BY-SIDE COMPARISON</div>',
    unsafe_allow_html=True)

col_llm, col_yolo = st.columns(2)

with col_llm:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:2px solid {COLORS["accent_gold"]};'
        f'border-radius:8px;padding:24px;position:relative;min-height:380px;">'
        f'<div style="position:absolute;top:-12px;right:20px;background:{COLORS["accent_gold"]};'
        f'color:white;padding:4px 14px;border-radius:4px;font-size:11px;font-weight:700;">✓ SELECTED</div>'
        f'<div style="font-size:11px;font-weight:700;color:{COLORS["accent_gold"]};'
        f'letter-spacing:0.08em;margin-bottom:4px;">OPTION A</div>'
        f'<div style="font-size:24px;font-weight:800;color:{COLORS["text_primary"]};'
        f'margin-bottom:4px;">Claude Vision</div>'
        f'<div style="font-size:13px;color:{COLORS["text_tertiary"]};margin-bottom:20px;">Vision LLM (Multimodal)</div>'
        f'<div style="font-size:11px;font-weight:700;color:{COLORS["status_ok"]};margin-bottom:8px;">✓ 장점</div>'
        f'<div style="font-size:14px;color:{COLORS["text_secondary"]};line-height:1.9;margin-bottom:16px;">'
        f'• 학습 데이터 불필요 (zero-shot)<br>'
        f'• 새 SKU = 라벨 등록만으로 즉시 적용<br>'
        f'• 자연어 추론 결과 반환<br>'
        f'• OCR·라벨 평가 동시 수행<br>'
        f'• 조명·각도 변화 적응 우수'
        f'</div>'
        f'<div style="font-size:11px;font-weight:700;color:{COLORS["status_warning"]};margin-bottom:8px;">⚠ 제약</div>'
        f'<div style="font-size:14px;color:{COLORS["text_secondary"]};line-height:1.9;">'
        f'• 추론 속도 2~5초/이미지<br>'
        f'• API 호출당 비용 발생<br>'
        f'• 인터넷 연결 필수'
        f'</div></div>', unsafe_allow_html=True)

with col_yolo:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-radius:8px;padding:24px;min-height:380px;">'
        f'<div style="font-size:11px;font-weight:700;color:{COLORS["text_tertiary"]};'
        f'letter-spacing:0.08em;margin-bottom:4px;">OPTION B</div>'
        f'<div style="font-size:24px;font-weight:800;color:{COLORS["text_primary"]};'
        f'margin-bottom:4px;">YOLO</div>'
        f'<div style="font-size:13px;color:{COLORS["text_tertiary"]};margin-bottom:20px;">You Only Look Once · Object Detection</div>'
        f'<div style="font-size:11px;font-weight:700;color:{COLORS["status_ok"]};margin-bottom:8px;">✓ 장점</div>'
        f'<div style="font-size:14px;color:{COLORS["text_secondary"]};line-height:1.9;margin-bottom:16px;">'
        f'• 추론 속도 50~200ms (로컬 GPU)<br>'
        f'• 학습 후 95%+ 정확도<br>'
        f'• 오프라인 동작 가능<br>'
        f'• 학습 후 추론 비용 거의 0<br>'
        f'• 실시간 컨베이어 처리 적합'
        f'</div>'
        f'<div style="font-size:11px;font-weight:700;color:{COLORS["status_warning"]};margin-bottom:8px;">⚠ 제약</div>'
        f'<div style="font-size:14px;color:{COLORS["text_secondary"]};line-height:1.9;">'
        f'• SKU당 수백 장 학습 데이터 필요<br>'
        f'• 학습 기간 1~2주 + GPU 투자<br>'
        f'• 새 SKU 추가 시 재학습 필수<br>'
        f'• 객체 좌표만 반환, 의미 추론 불가'
        f'</div></div>', unsafe_allow_html=True)

st.markdown("")
st.markdown("---")

# ─── Vision LLM 선택 이유 3가지 ───
st.markdown(
    f'<div style="font-size:11px;font-weight:700;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:12px;">WHY VISION LLM FOR THIS PROJECT</div>',
    unsafe_allow_html=True)

r1, r2, r3 = st.columns(3)
reasons = [
    (r1, "01", "SKU 확장성",
     "식품 제조 현장은 신제품 출시 주기가 짧습니다. YOLO는 SKU마다 재학습이 필요하지만, "
     "Vision LLM은 시각적 특징을 자연어로 등록하면 즉시 인식 가능합니다."),
    (r2, "02", "의미적 추론",
     "YOLO는 좌표와 클래스만 반환합니다. Vision LLM은 "
     "라벨 가독성, 적재 상태, 유통기한 등 부가 정보를 단일 호출에서 함께 반환합니다."),
    (r3, "03", "개발 일정",
     "30일 캡스톤 일정에서 YOLO 학습에 1~2주를 쓰면 다른 작업이 밀립니다. "
     "Vision LLM은 당일부터 사용 가능해 시스템 통합에 집중할 수 있었습니다."),
]
for col, num, title, body in reasons:
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-radius:8px;padding:20px;">'
        f'<div style="font-size:32px;font-weight:900;color:{COLORS["accent_gold"]};line-height:1;margin-bottom:6px;">{num}</div>'
        f'<div style="font-size:16px;font-weight:700;color:{COLORS["text_primary"]};margin-bottom:10px;">{title}</div>'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};line-height:1.8;">{body}</div>'
        f'</div>', unsafe_allow_html=True)

st.markdown("")
st.markdown("---")

# ─── 비교표 ───
st.markdown(
    f'<div style="font-size:11px;font-weight:700;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:12px;">QUICK REFERENCE TABLE</div>',
    unsafe_allow_html=True)

rows = [
    ("학습 필요",       "❌ 불필요 (zero-shot)",       "✅ 필수 (수백 장/SKU)"),
    ("개발 기간",       "당일 사용 가능",               "1~2주 학습 + GPU"),
    ("추론 속도",       "2~5초 (API)",                  "50~200ms (로컬 GPU)"),
    ("정확도",          "92~98%",                        "95%+ (학습 후)"),
    ("새 SKU 대응",     "라벨 등록만으로 즉시",          "데이터 재수집 + 재학습"),
    ("출력 형태",       "구조화 JSON + 자연어 추론",     "박스 좌표 + 클래스"),
    ("부가 기능",       "OCR · 라벨 평가 통합",          "별도 파이프라인 필요"),
    ("비용 구조",       "API 호출당 과금",               "초기 GPU 투자 후 무료"),
    ("인터넷",          "✅ 필수",                        "❌ 오프라인 가능"),
    ("적합 시나리오",   "다품종 · 빠른 SKU 변경",        "단일 품목 · 대량 처리"),
]

# 헤더
h = st.columns([1.2, 1.5, 1.5])
for col, label, color in zip(h, ["항목", "Vision LLM ✓ 선택", "YOLO"],
                              [COLORS["text_muted"], COLORS["accent_gold"], COLORS["text_secondary"]]):
    col.markdown(
        f'<div style="font-size:13px;font-weight:700;color:{color};'
        f'padding:10px 4px;border-bottom:2px solid {COLORS["border_strong"]};'
        f'text-align:center;">{label}</div>', unsafe_allow_html=True)

for i, (item, llm, yolo) in enumerate(rows):
    bg = COLORS["bg_panel"] if i % 2 == 0 else "white"
    r = st.columns([1.2, 1.5, 1.5])
    for col, val, color in [
        (r[0], item, COLORS["text_tertiary"]),
        (r[1], llm,  COLORS["text_primary"]),
        (r[2], yolo, COLORS["text_secondary"]),
    ]:
        col.markdown(
            f'<div style="padding:10px 4px;border-bottom:1px solid {COLORS["border_subtle"]};'
            f'background:{bg};text-align:center;font-size:14px;color:{color};">'
            f'{val}</div>', unsafe_allow_html=True)

st.markdown("")
st.markdown("---")

# ─── 하이브리드 확장 방향 ───
st.markdown(
    f'<div style="font-size:11px;font-weight:700;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:12px;">FUTURE DIRECTION · HYBRID ARCHITECTURE</div>',
    unsafe_allow_html=True)

st.markdown(
    f'<div style="background:{COLORS["bg_panel"]};border-left:4px solid {COLORS["accent_gold"]};'
    f'border-radius:6px;padding:22px 28px;">'
    f'<div style="font-size:16px;font-weight:700;color:{COLORS["text_primary"]};margin-bottom:12px;">'
    f'한계 인정 — 그리고 확장 방향</div>'
    f'<div style="font-size:14px;line-height:1.85;color:{COLORS["text_secondary"]};margin-bottom:18px;">'
    f'Vision LLM의 추론 속도(2~5초/이미지)는 컨베이어 풀스피드 환경에서 약점입니다. '
    f'대량 처리 환경에서는 두 기술의 강점을 결합한 '
    f'<strong style="color:{COLORS["accent_gold"]};">하이브리드 구조</strong>가 더 적합합니다.'
    f'</div>'
    f'<div style="background:#F8FAFC;border-radius:6px;padding:16px 20px;'
    f'font-size:14px;color:{COLORS["text_secondary"]};line-height:2.0;">'
    f'<div style="font-weight:700;color:{COLORS["accent_gold"]};margin-bottom:8px;">[Hybrid Pipeline]</div>'
    f'① <strong style="color:{COLORS["accent_cobalt"]};">YOLO</strong> : 모든 P-Box를 빠르게 1차 스캔 (50ms/박스)<br>'
    f'② 카운트 불일치 또는 confidence &lt; 임계값 → NG 후보 플래그<br>'
    f'③ <strong style="color:{COLORS["accent_gold"]};">Vision LLM</strong> : NG 후보만 정밀 분석 (혼입 검출·라벨 검증·자연어 권고)<br>'
    f'④ 결과를 WMS에 통합 반영 + 작업자에게 자연어 안내'
    f'</div>'
    f'<div style="font-size:13px;color:{COLORS["text_muted"]};margin-top:14px;">'
    f'※ 본 프로토타입은 Vision LLM 단독 구조이며, 하이브리드 구조는 후속 과제입니다. '
    f'비전 모델 자체는 <strong>교체 가능한 컴포넌트</strong>로 설계되었습니다.'
    f'</div></div>', unsafe_allow_html=True)
