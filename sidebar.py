"""
sidebar.py — 사이드바 + 상단 헤더 v3
- 프로젝트 정보 (제목/학교/발표자)
- 날짜/시간 우측 상단 고정
- 발표 순서 메뉴
- Streamlit 자동 생성 메뉴 숨김
"""

import streamlit as st
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
from styles import COLORS, render_brand_header as _base_header


SITE_CONFIG = {
    "suwon": {"name": "롯데웰푸드 수원공장", "shift": "주간 · LINE-A", "session": "#26052301"},
    "busan": {"name": "롯데웰푸드 부산공장", "shift": "주간 · LINE-B", "session": "#26052302"},
}


def ensure_session_state():
    if "site" not in st.session_state:
        st.session_state.site = "suwon"
    st.session_state.mode = "admin"


def safe_page_link(path: str, label: str):
    try:
        st.page_link(path, label=label)
    except Exception:
        st.markdown(
            f'<div style="padding:4px 8px;color:{COLORS["text_secondary"]};'
            f'font-size:14px;">▸ {label}</div>',
            unsafe_allow_html=True,
        )


def render_brand_header():
    """상단 헤더 — 프로젝트 정보 + 우측 날짜/시간"""
    now = datetime.now(KST)
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    wd = weekdays[now.weekday()]

    st.markdown(
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;'
        f'padding-bottom:14px;margin-bottom:6px;'
        f'border-bottom:2px solid {COLORS["border_subtle"]};">'
        f'<div>'
        f'<div style="font-size:11px;font-weight:600;color:{COLORS["accent_gold"]};'
        f'letter-spacing:0.04em;margin-bottom:4px;">SCM</div>'
        f'<div style="font-size:17px;font-weight:700;color:{COLORS["text_primary"]};'
        f'line-height:1.35;">AI 머신비전 기반 실시간 생산·재고 검증 시스템</div>'
        f'<div style="font-size:12px;color:{COLORS["text_tertiary"]};margin-top:4px;">'
        f'인천대학교 동북아물류대학원 &nbsp;·&nbsp; 발표자 정승현</div>'
        f'</div>'
        f'<div style="text-align:right;flex-shrink:0;">'
        f'<div style="font-size:15px;font-weight:600;color:{COLORS["text_primary"]};'
        f'line-height:1.5;">{now.strftime("%Y년 %m월 %d일")}</div>'
        f'<div style="font-size:12px;color:{COLORS["text_muted"]};margin-top:2px;">'
        f'{now.strftime("%A")}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_sidebar():
    # Streamlit 자동 생성 메뉴 숨기기 + 사이드바 스타일
    st.markdown(
        """<style>
        /* Streamlit 자동 생성 페이지 목록 숨김 */
        section[data-testid="stSidebarNav"],
        section[data-testid="stSidebarNav"] ~ div {
            display: none !important;
            height: 0 !important;
            overflow: hidden !important;
        }

        /* 사이드바 상단 여백 */
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 0.5rem !important;
        }

        /* 메뉴 링크 */
        a[data-testid="stPageLink-NavLink"] {
            border-radius: 6px;
            padding: 6px 10px !important;
            font-size: 14px !important;
            font-weight: 500;
            color: #334155 !important;
            margin: 1px 0;
            display: block;
        }
        a[data-testid="stPageLink-NavLink"]:hover {
            background: #EFF6FF !important;
            color: #1E40AF !important;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        # ── 프로젝트 정보 ──
        st.markdown(
            f'<div style="padding:8px 4px 12px 4px;">'
            f'<div style="font-size:11px;font-weight:600;'
            f'color:{COLORS["accent_gold"]};letter-spacing:0.04em;'
            f'margin-bottom:6px;">SCM</div>'
            f'<div style="font-size:14px;font-weight:700;'
            f'color:{COLORS["text_primary"]};line-height:1.4;">'
            f'AI 머신비전 기반<br>생산·재고 검증 시스템</div>'
            f'<div style="font-size:11px;color:{COLORS["text_tertiary"]};'
            f'margin-top:6px;line-height:1.7;">'
            f'인천대학교 동북아물류대학원<br>'
            f'발표자 · 정승현'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        st.divider()

        # ── 발표 메뉴 ──
        safe_page_link("app.py", "🏠  대시보드")
        safe_page_link("pages/0_5Why.py", "5 Why")

        st.markdown(
            f'<div style="font-size:11px;font-weight:600;'
            f'color:{COLORS["text_muted"]};letter-spacing:0.06em;'
            f'margin:10px 0 4px 0;">핵심 메시지</div>',
            unsafe_allow_html=True,
        )
        safe_page_link("pages/0_KEY_Points.py", "생산·재고 손실 관리")
        safe_page_link("pages/9_Flow.py",       "물류 흐름도  🏭")

        st.markdown(
            f'<div style="font-size:11px;font-weight:600;'
            f'color:{COLORS["text_muted"]};letter-spacing:0.06em;'
            f'margin:10px 0 4px 0;">프로세스 흐름</div>',
            unsafe_allow_html=True,
        )
        safe_page_link("pages/1_Production.py", "1.  생산 라인 현황")
        safe_page_link("pages/6_Vision_Test.py", "2.  비전 검사  🔬")
        safe_page_link("pages/1_Inspection.py",  "3.  재고 검수")
        safe_page_link("pages/2_Inventory.py",   "4.  재고 현황")
        safe_page_link("pages/3_Dispatch.py",    "5.  출고 처리")

        st.markdown(
            f'<div style="font-size:11px;font-weight:600;'
            f'color:{COLORS["text_muted"]};letter-spacing:0.06em;'
            f'margin:10px 0 4px 0;">분석 · 인사이트</div>',
            unsafe_allow_html=True,
        )
        safe_page_link("pages/7_Monitor.py",     "6.  검사 이력")
        safe_page_link("pages/4_SCM_Insight.py", "7.  SCM 인사이트")

        st.divider()

        safe_page_link("pages/5_Tech_Choice.py", "시스템 정보")
