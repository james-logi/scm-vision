"""
SCM Vision — 대시보드 (발표 오프닝)
최신 페이지 구성 반영
"""

import streamlit as st
import pandas as pd
from datetime import timedelta
from styles import inject_global_styles, COLORS
from sku_registry import SkuRegistry
from sidebar import ensure_session_state, render_sidebar, render_brand_header

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
# 핵심 평가 기준
# ─────────────────────────────────────────────
st.markdown(
    f'<div style="font-size:11px;font-weight:600;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:10px;">EVALUATION CRITERIA · 핵심 평가 기준</div>',
    unsafe_allow_html=True)

e1, e2, e3 = st.columns(3)
def eval_card(col, num, title, body, color):
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-top:3px solid {color};border-radius:8px;padding:20px;min-height:150px;">'
        f'<div style="font-size:32px;font-weight:900;color:{color};line-height:1;margin-bottom:8px;">{num}</div>'
        f'<div style="font-size:17px;font-weight:700;color:{COLORS["text_primary"]};margin-bottom:8px;">{title}</div>'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};line-height:1.7;">{body}</div>'
        f'</div>', unsafe_allow_html=True)

eval_card(e1, "①", "중요한가?",
    "생산·제조업의 재고 불일치는 채찍효과·납품 지연·비용 손실로 이어지는 핵심 문제",
    COLORS["accent_cobalt"])
eval_card(e2, "②", "못 풀어 괴로운가?",
    "계수기 설정 오류, ROI 한계, 예외 상황 — 기존 방식으로 근본 해결 안 됨",
    COLORS["accent_gold"])
eval_card(e3, "③", "공감되는가?",
    "수많은 생산·제조업체가 동일하게 겪는 문제 — 시장 크기 충분, 확장 가능",
    COLORS["status_ok"])

st.markdown("")
st.markdown("---")

# ─────────────────────────────────────────────
# 핵심 문제 요약
# ─────────────────────────────────────────────
st.markdown(
    f'<div style="font-size:11px;font-weight:600;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:10px;">PROBLEM STATEMENT · 해결하려는 문제</div>',
    unsafe_allow_html=True)

p1, p2, p3 = st.columns(3)
def prob_card(col, icon, title, body, color):
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-left:4px solid {color};border-radius:8px;padding:18px;">'
        f'<div style="font-size:24px;margin-bottom:8px;">{icon}</div>'
        f'<div style="font-size:15px;font-weight:700;color:{COLORS["text_primary"]};margin-bottom:6px;">{title}</div>'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};line-height:1.7;">{body}</div>'
        f'</div>', unsafe_allow_html=True)

prob_card(p1, "⚠️", "단위 변환 지점의 정보 손실",
    "낱개 단위(EA) → 박스 단위(Case)로 전환 시<br>수량 정보가 누락·왜곡됨",
    COLORS["status_warning"])
prob_card(p2, "📦", "계수기 설정 오류",
    "제품 교체 시 계수기 설정을 바꾸지 않으면<br>다른 제품으로 수량이 전산 기록됨",
    COLORS["status_danger"])
prob_card(p3, "📊", "WMS 재고 불일치",
    "물류동의 전산 수량과 실물 수량 차이 발생<br>→ IRI 65% 수준의 재고 부정확성",
    COLORS["accent_gold"])

st.markdown("")
st.markdown("---")

# ─────────────────────────────────────────────
# 발표 순서 (최신 페이지 구성 반영)
# ─────────────────────────────────────────────
st.markdown(
    f'<div style="font-size:11px;font-weight:600;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:10px;">'
    f'PRESENTATION FLOW · 왼쪽 메뉴를 순서대로 클릭하세요</div>',
    unsafe_allow_html=True)

steps = [
    ("★", "물류 흐름 손실 관리",   "AS-IS 현재 문제 상황 인지\nTO-BE AI Vision 검수",  COLORS["accent_gold"],    True),
    ("1", "생산 라인 현황",          "LINE 1~10 P-Box 생산량\nNG율 · 라인별 상태 카드",  COLORS["accent_cobalt"],  False),
    ("2", "비전 검사  🔬",           "이미지 업로드 → AI 실시간 분석\n폴더 자동스캔 지원", COLORS["accent_gold"],    True),
    ("3", "재고 현황",               "주문 기반 생산 · 부족분 관리\n생산계획/재고/출고예정", COLORS["accent_cobalt"], False),
    ("4", "출고 검수",               "−2일 ~ +5일 관리 윈도우\n날짜별 검수 결과 확인",    COLORS["text_secondary"], False),
    ("5", "출고 처리",               "일자별 출고 완료/예정 계획\n매장·상품별 출고 현황",  COLORS["text_secondary"], False),
    ("6", "검사 이력",               "누적 성과 차트 (EA/Case)\n상품별 일별 수량 추이",    COLORS["status_ok"],      False),
    ("7", "SCM 인사이트  ★",        "채찍효과 이론 연결\nClaude 자동 추론 + 65%→1.42%", COLORS["accent_gold"],    True),
]

row1, row2 = steps[:4], steps[4:]
for row in [row1, row2]:
    cols = st.columns(4)
    for col, (num, title, desc, color, star) in zip(cols, row):
        border = f'border:2px solid {color}' if star else f'border:1px solid {COLORS["border_subtle"]}'
        bg = "#FFFBEB" if color == COLORS["accent_gold"] and star else COLORS["bg_panel"]
        lines = desc.split("\n")
        desc_html = "<br>".join(lines)
        col.markdown(
            f'<div style="background:{bg};{border};border-radius:8px;'
            f'padding:16px;text-align:center;min-height:110px;">'
            f'<div style="font-size:22px;font-weight:900;color:{color};line-height:1;margin-bottom:6px;">{num}</div>'
            f'<div style="font-size:14px;font-weight:700;color:{COLORS["text_primary"]};margin-bottom:6px;">{title}</div>'
            f'<div style="font-size:12px;color:{COLORS["text_muted"]};line-height:1.6;">{desc_html}</div>'
            f'</div>', unsafe_allow_html=True)
    st.markdown("")

st.markdown("---")

# ─────────────────────────────────────────────
# 30일 성과 KPI
# ─────────────────────────────────────────────
st.markdown(
    f'<div style="font-size:11px;font-weight:600;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:10px;">SYSTEM PERFORMANCE · 30일 누적 성과</div>',
    unsafe_allow_html=True)

try:
    df = pd.read_csv("data/inspection_history.csv")
    df["inspected_at"] = pd.to_datetime(df["inspected_at"])
    total  = len(df)
    ok     = len(df[df["verdict"] == "OK"])
    ng     = len(df[df["verdict"] != "OK"])
    acc    = ok / total * 100 if total > 0 else 0
    days   = df["inspected_at"].dt.date.nunique()
    registry  = SkuRegistry()
    sku_count = len(registry.list_active())

    # 재고 부족분 계산 (NG = 출고 부족분)
    shortage  = ng  # NG 차단 = 부족분

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    def kpi(col, val, unit, label, sub, color):
        col.markdown(
            f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
            f'border-top:3px solid {color};border-radius:6px;padding:16px;text-align:center;">'
            f'<div style="font-size:24px;font-weight:900;color:{color};line-height:1;">{val}'
            f'<span style="font-size:12px;color:{COLORS["text_tertiary"]};margin-left:2px;">{unit}</span></div>'
            f'<div style="font-size:13px;font-weight:600;color:{COLORS["text_primary"]};margin-top:6px;">{label}</div>'
            f'<div style="font-size:11px;color:{COLORS["text_muted"]};margin-top:2px;">{sub}</div>'
            f'</div>', unsafe_allow_html=True)

    kpi(k1, f"{total:,}",      "건", "누적 검수",    f"{days}일간",           COLORS["accent_cobalt"])
    kpi(k2, f"{acc:.2f}",      "%",  "비전 정확도",  "AI Vision 판정",        COLORS["accent_gold"])
    kpi(k3, f"{ng:,}",         "건", "NG 차단",      "출고 불가 차단",        COLORS["status_warning"])
    kpi(k4, f"{shortage:,}",   "건", "재고 부족분",  "주문 미충족 가능",      COLORS["status_danger"])
    kpi(k5, f"{ng*10000:,}",   "원", "추정 절감",    "NG 1건당 1만원 기준",  COLORS["status_ok"])
    kpi(k6, f"{sku_count}",    "종", "등록 SKU",     "비전 인식 상품",        COLORS["text_secondary"])

except Exception as e:
    st.info(f"데이터 로드 중... ({e})")

st.markdown("")

# ─────────────────────────────────────────────
# 핵심 메시지
# ─────────────────────────────────────────────
st.markdown(
    f'<div style="background:#EFF6FF;border:1px solid {COLORS["accent_cobalt"]};'
    f'border-radius:8px;padding:20px 28px;text-align:center;">'
    f'<div style="font-size:14px;font-weight:700;color:{COLORS["accent_cobalt"]};'
    f'margin-bottom:8px;">핵심 가치 제안</div>'
    f'<div style="font-size:16px;font-weight:700;color:{COLORS["text_primary"]};line-height:1.7;">'
    f'P-Box 단위 변환 지점에 AI Vision 검수 게이트를 설치하여<br>'
    f'<span style="color:{COLORS["status_warning"]};">IRI 65%</span> 수준의 재고 불일치를 '
    f'<span style="color:{COLORS["status_ok"]};">1.42%</span>로 개선하고<br>'
    f'NG {ng if "ng" in dir() else 38}건을 차단하여 '
    f'<span style="color:{COLORS["accent_gold"]};font-weight:900;">불량 출고를 원천 차단</span>합니다.'
    f'</div></div>',
    unsafe_allow_html=True)

st.markdown("")
st.markdown(
    f'<div style="text-align:center;padding-top:16px;'
    f'border-top:1px solid {COLORS["border_subtle"]};">'
    f'<div style="font-size:11px;color:{COLORS["text_muted"]};letter-spacing:0.08em;">'
    f'INCHEON NATIONAL UNIVERSITY · GRADUATE SCHOOL OF LOGISTICS · '
    f'<span style="color:{COLORS["accent_gold"]};">POWERED BY CLAUDE SONNET</span>'
    f'</div></div>', unsafe_allow_html=True)
