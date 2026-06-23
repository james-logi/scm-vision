"""
sidebar.py — 사이드바 렌더링 공용 모듈 v2
변경: MODE 토글 삭제, 날짜/시간 표시 추가, 메뉴 프로세스 순서로 재편
"""

import streamlit as st
from datetime import datetime
from styles import COLORS


SITE_CONFIG = {
    "suwon": {"name": "롯데웰푸드 수원공장", "shift": "주간 · LINE-A", "session": "#26052301"},
    "busan": {"name": "롯데웰푸드 부산공장", "shift": "주간 · LINE-B", "session": "#26052302"},
}


def ensure_session_state():
    """세션 상태 초기화 — 모든 페이지 최상단에서 호출."""
    if "site" not in st.session_state:
        st.session_state.site = "suwon"
    # mode는 항상 admin으로 고정 (모드 구분 폐지)
    st.session_state.mode = "admin"


def safe_page_link(path: str, label: str):
    """page_link 실패 시 텍스트로 폴백"""
    try:
        st.page_link(path, label=label)
    except Exception:
        st.markdown(
            f'<div style="padding:4px 0;color:{COLORS["text_secondary"]};'
            f'font-size:13px;">▸ {label}</div>',
            unsafe_allow_html=True,
        )


def render_sidebar():
    """공용 사이드바 렌더링 — app.py + 모든 페이지에서 동일한 사이드바."""
    with st.sidebar:

        # ── 날짜 / 시간 ──
        now = datetime.now()
        st.markdown(
            f'<div style="padding:4px 0 10px 0;">'
            f'<div style="font-size:18px;font-weight:700;'
            f'color:{COLORS["text_primary"]};letter-spacing:-0.01em;">'
            f'{now.strftime("%H:%M")}'
            f'<span style="font-size:13px;font-weight:400;'
            f'color:{COLORS["text_muted"]};margin-left:6px;">'
            f'{now.strftime("%S")}초</span></div>'
            f'<div style="font-size:12px;color:{COLORS["text_tertiary"]};margin-top:2px;">'
            f'{now.strftime("%Y. %m. %d")} ({now.strftime("%a")})'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ── 브랜드 ──
        st.markdown(
            f'<div style="padding:4px 0 12px 0;">'
            f'<div style="font-size:15px;font-weight:700;'
            f'color:{COLORS["text_primary"]};">출고 재고 검수</div>'
            f'<div style="font-size:11px;color:{COLORS["text_muted"]};'
            f'margin-top:2px;letter-spacing:0.05em;">AI Vision System</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── 사이트 선택 ──
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["text_muted"]};letter-spacing:0.08em;margin-bottom:4px;">'
            f'SITE</div>',
            unsafe_allow_html=True,
        )
        site_choice = st.selectbox(
            "공장 선택",
            options=["suwon", "busan"],
            format_func=lambda x: SITE_CONFIG[x]["name"],
            index=["suwon", "busan"].index(st.session_state.site),
            label_visibility="collapsed",
        )
        if site_choice != st.session_state.site:
            st.session_state.site = site_choice
            st.rerun()

        # ── 세션 정보 ──
        cfg = SITE_CONFIG[st.session_state.site]
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;'
            f'font-size:10px;line-height:1.8;margin-top:8px;">'
            f'<span style="color:{COLORS["text_muted"]};">SHIFT</span> '
            f'<span style="color:{COLORS["text_secondary"]};">{cfg["shift"]}</span><br>'
            f'<span style="color:{COLORS["text_muted"]};">SESSION</span> '
            f'<span style="color:{COLORS["text_secondary"]};">{cfg["session"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ── 메뉴 ──
        safe_page_link("app.py", "🏠 대시보드")

        st.markdown(
            f'<div style="background:#EFF6FF;'
            f'border-left:3px solid {COLORS["accent_gold"]};'
            f'border-radius:0 4px 4px 0;padding:8px 10px;margin:10px 0 6px 0;">'
            f'<div style="font-size:11px;font-weight:600;'
            f'color:{COLORS["accent_gold"]};margin-bottom:2px;">'
            f'▶ 발표 순서대로 클릭</div>'
            f'<div style="font-size:11px;color:{COLORS["text_muted"]};">'
            f'왼쪽 메뉴 = 발표 흐름</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        safe_page_link("pages/0_KEY_Points.py",   "★  KEY Points — 핵심 메시지")

        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["text_muted"]};letter-spacing:0.08em;'
            f'margin-top:8px;margin-bottom:4px;">PROCESS  ↓</div>',
            unsafe_allow_html=True,
        )
        safe_page_link("pages/1_Production.py",  "1.  생산 라인 현황")
        safe_page_link("pages/6_Vision_Test.py",  "2.  비전 검사  ← 시연")
        safe_page_link("pages/2_Inventory.py",    "3.  재고 현황")
        safe_page_link("pages/1_Inspection.py",   "4.  출고 검수")
        safe_page_link("pages/3_Dispatch.py",     "5.  출고 처리")

        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["text_muted"]};letter-spacing:0.08em;'
            f'margin-top:8px;margin-bottom:4px;">ANALYSIS  ↓</div>',
            unsafe_allow_html=True,
        )
        safe_page_link("pages/7_Monitor.py",      "6.  검사 이력")
        safe_page_link("pages/4_SCM_Insight.py",  "7.  SCM 인사이트  ← 핵심")

        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["text_muted"]};letter-spacing:0.08em;'
            f'margin-top:10px;margin-bottom:4px;">INFO</div>',
            unsafe_allow_html=True,
        )
        safe_page_link("pages/5_Tech_Choice.py",  "시스템 정보")

        st.markdown("---")

        # ── 푸터 ──
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
            f'color:{COLORS["text_muted"]};letter-spacing:0.05em;line-height:1.6;">'
            f'INCHEON NATIONAL UNIVERSITY<br>'
            f'GRADUATE SCHOOL OF LOGISTICS<br>'
            f'POWERED BY CLAUDE'
            f'</div>',
            unsafe_allow_html=True,
        )
