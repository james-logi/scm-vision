"""
출고 재고 검수 관리 | AI VISION
발표용 대시보드 — 오프닝 슬라이드
"""

import streamlit as st
import pandas as pd
import os
from styles import inject_global_styles, render_brand_header, COLORS
from sku_registry import SkuRegistry
from sidebar import ensure_session_state, render_sidebar, SITE_CONFIG

st.set_page_config(
    page_title="AI 머신비전 기반 실시간 생산·재고 검증 시스템",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("")

# ─────────────────────────────────────────────
# 핵심 평가 기준 3가지
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.1em;margin-bottom:12px;">'
    f'EVALUATION CRITERIA · 핵심 평가 기준</div>',
    unsafe_allow_html=True,
)

e1, e2, e3 = st.columns(3)

def eval_card(col, num, title, body, color):
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:1px solid {COLORS["border_subtle"]};'
        f'border-top:3px solid {color};border-radius:6px;'
        f'padding:20px;height:160px;">'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:32px;'
        f'font-weight:900;color:{color};line-height:1;margin-bottom:8px;">{num}</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:16px;'
        f'font-weight:700;color:{COLORS["text_primary"]};margin-bottom:8px;">{title}</div>'
        f'<div style="font-size:12px;color:{COLORS["text_secondary"]};'
        f'line-height:1.6;">{body}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

eval_card(e1, "①", "중요한가?",
    "생산·제조업의 재고 불일치는<br>채찍효과·납품 지연·비용 손실로 이어지는 핵심 문제",
    COLORS["accent_cobalt"])
eval_card(e2, "②", "못 풀어 괴로운가?",
    "계수기 설정 오류, ROI 한계,<br>예외 상황 — 기존 방식으로 해결 안 됨",
    COLORS["accent_gold"])
eval_card(e3, "③", "공감되는가?",
    "수많은 생산·제조업체가 동일하게<br>겪는 문제 — 시장 크기 충분",
    COLORS["status_ok"])


# ─────────────────────────────────────────────
# 발표 진행 순서 (클릭 안내)
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.1em;margin-bottom:12px;">'
    f'PRESENTATION FLOW · 왼쪽 메뉴를 순서대로 클릭하세요</div>',
    unsafe_allow_html=True,
)

steps = [
    ("★", "KEY Points",     "문제 vs 해결 핵심 비교",          COLORS["accent_gold"]),
    ("1", "생산 라인 현황",   "10개 라인 P-Box 생산량·NG율",     COLORS["accent_cobalt"]),
    ("2", "비전 검사",        "AI가 실시간으로 이미지 분석 시연", COLORS["accent_gold"]),
    ("3", "재고 현황",        "Dual-Unit · Case × EA 추적",      COLORS["accent_cobalt"]),
    ("4", "출고 검수",        "출고 전 최종 확인·NG 필터",        COLORS["text_secondary"]),
    ("5", "출고 처리",        "매장별 출고 확정",                  COLORS["text_secondary"]),
    ("6", "검사 이력",        "30일 성과 데이터 시각화",          COLORS["status_ok"]),
    ("7", "SCM 인사이트",     "학술 이론 연결 + Claude 자동 추론",COLORS["accent_gold"]),
]

# 한 줄에 4개씩
row1 = steps[:4]
row2 = steps[4:]

for row in [row1, row2]:
    cols = st.columns(4)
    for col, (num, title, desc, color) in zip(cols, row):
        col.markdown(
            f'<div style="background:{COLORS["bg_panel"]};'
            f'border:1px solid {COLORS["border_subtle"]};border-radius:6px;'
            f'padding:14px;text-align:center;">'
            f'<div style="font-family:\'Noto Serif KR\',serif;font-size:22px;'
            f'font-weight:900;color:{color};line-height:1;margin-bottom:6px;">{num}</div>'
            f'<div style="font-family:\'Noto Serif KR\',serif;font-size:13px;'
            f'font-weight:700;color:{COLORS["text_primary"]};margin-bottom:4px;">{title}</div>'
            f'<div style="font-size:11px;color:{COLORS["text_muted"]};line-height:1.5;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("")


# ─────────────────────────────────────────────
# KPI 요약 (30일 데이터 기반)
# ─────────────────────────────────────────────
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.1em;margin-bottom:12px;">'
    f'SYSTEM PERFORMANCE · 30일 누적 성과</div>',
    unsafe_allow_html=True,
)

try:
    df = pd.read_csv("data/inspection_history.csv")
    total = len(df)
    ok = len(df[df["verdict"] == "OK"])
    ng = len(df[df["verdict"] != "OK"])
    acc = ok / total * 100 if total > 0 else 0
    registry = SkuRegistry()
    sku_count = len(registry.list_active())

    k1, k2, k3, k4, k5 = st.columns(5)

    def kpi(col, val, unit, label, color):
        col.markdown(
            f'<div style="background:{COLORS["bg_panel"]};'
            f'border:1px solid {COLORS["border_subtle"]};border-radius:6px;'
            f'padding:16px;text-align:center;">'
            f'<div style="font-family:\'Noto Serif KR\',serif;font-size:26px;'
            f'font-weight:900;color:{color};line-height:1;">{val}'
            f'<span style="font-size:13px;color:{COLORS["text_tertiary"]};'
            f'margin-left:2px;">{unit}</span></div>'
            f'<div style="font-size:11px;color:{COLORS["text_muted"]};'
            f'margin-top:6px;">{label}</div>'
            f'</div>', unsafe_allow_html=True)

    kpi(k1, f"{total:,}", "건", "누적 검수", COLORS["accent_cobalt"])
    kpi(k2, f"{acc:.1f}", "%", "비전 정확도", COLORS["accent_gold"])
    kpi(k3, f"{ng:,}", "건", "NG 차단", COLORS["status_warning"])
    kpi(k4, f"{ng*10000:,}", "원", "추정 절감", COLORS["status_ok"])
    kpi(k5, f"{sku_count}", "종", "등록 SKU", COLORS["text_secondary"])

except Exception:
    st.info("데이터를 불러오는 중입니다.")


# ─────────────────────────────────────────────
# 푸터
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f'<div style="text-align:center;padding-top:20px;'
    f'border-top:1px solid {COLORS["border_subtle"]};">'
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_muted"]};letter-spacing:0.08em;">'
    f'INCHEON NATIONAL UNIVERSITY · GRADUATE SCHOOL OF LOGISTICS · '
    f'<span style="color:{COLORS["accent_gold"]};">POWERED BY CLAUDE</span>'
    f'</div></div>',
    unsafe_allow_html=True,
)
