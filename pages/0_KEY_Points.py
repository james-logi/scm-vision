"""
Page 0: KEY Points — 손실 vs 개선 시나리오 비교

본 페이지는 PPT의 KEY POINT A/B 슬라이드와 1:1 대응되는 시스템 화면.
발표 시 슬라이드 ↔ 시스템 화면을 빠르게 전환하면서 일관된 메시지 전달.

좌측: AS-IS (재고 부정확성 → 6가지 손실)
우측: TO-BE (AI Vision 검수 → 6가지 개선)
"""

import streamlit as st
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import render_brand_header
from sidebar import ensure_session_state, render_sidebar

st.set_page_config(
    page_title="KEY Points | AI Vision",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()

ensure_session_state()
render_sidebar()
render_brand_header()


# ─────────────────────────────────────────────
# 페이지 제목
# ─────────────────────────────────────────────
st.markdown("# 생산·출고 물류 흐름 손실 관리")
render_page_subtitle("AS-IS 현재 문제 상황 · TO-BE AI Vision 검수 / 모니터링")


# ─────────────────────────────────────────────
# 인트로 메시지
# ─────────────────────────────────────────────
st.markdown(
    f'<div style="background:{COLORS["bg_panel"]};'
    f'border-left:4px solid {COLORS["accent_gold"]};border-radius:6px;'
    f'padding:20px 24px;margin-top:18px;margin-bottom:24px;">'
    f'<div style="font-size:17px;font-weight:700;color:{COLORS["text_primary"]};margin-bottom:8px;">'
    f'생산 완료 후 물류동으로 이동하는 과정에서 발생하는 손실</div>'
    f'<div style="font-size:15px;line-height:1.7;color:{COLORS["text_secondary"]};">'
    f'생산과 출고 사이의 물류 흐름에서 수량 불일치가 발생합니다. '
    f'<strong style="color:{COLORS["status_warning"]};">현재 문제 상황</strong>과 '
    f'<strong style="color:{COLORS["accent_gold"]};">AI Vision 검수 도입 후 개선</strong>을 '
    f'항목별로 비교합니다.'
    f'</div></div>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# 좌우 시나리오 컨테이너 (제목 줄)
# ─────────────────────────────────────────────
title_col1, title_col2 = st.columns(2)

with title_col1:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:2px solid {COLORS["status_warning"]};border-radius:6px 6px 0 0;'
        f'padding:14px 20px;border-bottom:none;">'
        f'<div style="display:flex;align-items:center;gap:12px;">'
        f'<div style="background:{COLORS["status_warning"]};color:white;'
        f'padding:4px 12px;border-radius:4px;font-size:11px;font-weight:700;">⚠ AS-IS</div>'
        f'<div style="font-size:18px;font-weight:700;color:{COLORS["text_primary"]};">'
        f'현재 문제 상황 인지</div>'
        f'</div>'
        f'<div style="font-size:12px;color:{COLORS["text_tertiary"]};margin-top:6px;">'
        f'물류 흐름 중 발생하는 수량 불일치 및 연쇄 손실</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

with title_col2:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:2px solid {COLORS["accent_gold"]};border-radius:6px 6px 0 0;'
        f'padding:14px 20px;border-bottom:none;">'
        f'<div style="display:flex;align-items:center;gap:12px;">'
        f'<div style="background:{COLORS["accent_gold"]};color:white;'
        f'padding:4px 12px;border-radius:4px;font-size:11px;font-weight:700;">✓ TO-BE</div>'
        f'<div style="font-size:18px;font-weight:700;color:{COLORS["text_primary"]};">'
        f'AI Vision 검수 / 모니터링</div>'
        f'</div>'
        f'<div style="font-size:12px;color:{COLORS["text_tertiary"]};margin-top:6px;">'
        f'실시간 검수로 정보 손실 차단 및 재고 정확성 확보</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# 시나리오 트리거 박스
# ─────────────────────────────────────────────
trigger_col1, trigger_col2 = st.columns(2)

with trigger_col1:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:2px solid {COLORS["status_warning"]};border-top:none;border-bottom:none;'
        f'padding:18px 20px;">'
        f'<div style="display:flex;gap:10px;align-items:flex-start;">'
        f'<div style="font-size:24px;">🏭</div>'
        f'<div style="flex:1;">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["status_warning"]};letter-spacing:0.08em;'
        f'font-weight:700;margin-bottom:4px;">시나리오 트리거</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:15px;'
        f'font-weight:700;color:{COLORS["text_primary"]};line-height:1.5;">'
        f'생산 후 재고 창고로 입고했으나,<br>'
        f'재고 시스템 수량과 실물이 불일치'
        f'</div></div></div></div>',
        unsafe_allow_html=True,
    )

with trigger_col2:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:2px solid {COLORS["accent_gold"]};border-top:none;border-bottom:none;'
        f'padding:18px 20px;">'
        f'<div style="display:flex;gap:10px;align-items:flex-start;">'
        f'<div style="font-size:24px;">🤖</div>'
        f'<div style="flex:1;">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["accent_gold"]};letter-spacing:0.08em;'
        f'font-weight:700;margin-bottom:4px;">시나리오 트리거</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:15px;'
        f'font-weight:700;color:{COLORS["text_primary"]};line-height:1.5;">'
        f'생산 → 입고 시점에 AI Vision 검수,<br>'
        f'시스템 수량을 실시간 업데이트'
        f'</div></div></div></div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# 6개 항목 1:1 대응 카드
# ─────────────────────────────────────────────
items = [
    {
        "loss": {"icon": "🔁", "title": "추가 생산 요청",
                 "body": "부족분 보충을 위한 라인 재가동, 생산 계획 차질"},
        "improve": {"icon": "✅", "title": "추가 생산 감소",
                    "body": "정확한 재고로 부족분 사전 방지, 생산 계획 안정화"},
    },
    {
        "loss": {"icon": "💸", "title": "재고 손실",
                 "body": "장부와 실물 차이, 재고자산 정확성 훼손"},
        "improve": {"icon": "📊", "title": "재고 정확성 확보",
                    "body": "Dual-Unit Tracking으로 장부 = 실물 일치"},
    },
    {
        "loss": {"icon": "⏱️", "title": "납품 지연",
                 "body": "매장 발주 대응 실패, Lead Time 증가"},
        "improve": {"icon": "⚡", "title": "납품 적시성 향상",
                    "body": "검증된 재고로 즉시 출고, Lead Time 단축"},
    },
    {
        "loss": {"icon": "😞", "title": "고객 불만 증가",
                 "body": "매장 클레임 누적, 신뢰도 하락"},
        "improve": {"icon": "😊", "title": "고객 만족도 회복",
                    "body": "매장 클레임 사전 차단, 신뢰도 회복"},
    },
    {
        "loss": {"icon": "📈", "title": "생산 비용 상승",
                 "body": "재작업, 추가 라인 가동, 인건비·자재비 증가"},
        "improve": {"icon": "💰", "title": "생산 비용 절감",
                    "body": "재작업 감소, 라인 효율, 인건비·자재비 안정"},
    },
    {
        "loss": {"icon": "📦", "title": "재고 운영비 증가",
                 "body": "안전재고 과잉 보유, 창고 회전율 저하"},
        "improve": {"icon": "📉", "title": "운영비 절감",
                    "body": "안전재고 최적화, 창고 회전율 향상"},
    },
]


def render_card(item, color):
    """한 카드 렌더링"""
    return (
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border-left:2px solid {color};'
        f'border-right:2px solid {color};'
        f'padding:14px 18px;'
        f'border-top:1px solid {COLORS["border_subtle"]};">'
        f'<div style="display:flex;gap:14px;align-items:flex-start;">'
        f'<div style="font-size:28px;line-height:1;flex-shrink:0;'
        f'background:{COLORS["bg_deep"]};border-radius:6px;'
        f'width:48px;height:48px;display:flex;align-items:center;'
        f'justify-content:center;">{item["icon"]}</div>'
        f'<div style="flex:1;">'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:15px;'
        f'font-weight:700;color:{color};margin-bottom:4px;line-height:1.3;">'
        f'{item["title"]}</div>'
        f'<div style="font-size:12px;line-height:1.6;color:{COLORS["text_secondary"]};">'
        f'{item["body"]}</div>'
        f'</div></div></div>'
    )


for i, pair in enumerate(items):
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(render_card(pair["loss"], COLORS["status_warning"]),
                    unsafe_allow_html=True)
    with col_r:
        st.markdown(render_card(pair["improve"], COLORS["accent_gold"]),
                    unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 하단 결론
# ─────────────────────────────────────────────
result_col1, result_col2 = st.columns(2)

with result_col1:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:2px solid {COLORS["status_warning"]};'
        f'border-top:1px solid {COLORS["border_subtle"]};'
        f'border-radius:0 0 6px 6px;padding:16px 20px;">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["status_warning"]};letter-spacing:0.08em;'
        f'font-weight:700;margin-bottom:6px;">→ 결국</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:14px;'
        f'color:{COLORS["text_primary"]};line-height:1.6;font-style:italic;">'
        f'공급망 전체에 비효율 누적, '
        f'<strong style="color:{COLORS["status_warning"]};">SCM 성과 지표</strong>'
        f'(정확도, 회전율, Lead Time, 고객 만족도) 동시 악화'
        f'</div></div>',
        unsafe_allow_html=True,
    )

with result_col2:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:2px solid {COLORS["accent_gold"]};'
        f'border-top:1px solid {COLORS["border_subtle"]};'
        f'border-radius:0 0 6px 6px;padding:16px 20px;">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["accent_gold"]};letter-spacing:0.08em;'
        f'font-weight:700;margin-bottom:6px;">→ 결과</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:14px;'
        f'color:{COLORS["text_primary"]};line-height:1.6;font-style:italic;">'
        f'공급망 전반의 효율 개선, '
        f'<strong style="color:{COLORS["accent_gold"]};">SCM 4대 지표</strong>'
        f'(재고 정확성, 회전율, Lead Time, 고객 만족도) 동시 향상'
        f'</div></div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# 하단 — 다음 단계 안내

