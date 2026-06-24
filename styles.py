"""
출고 재고 검수 관리 - 디자인 시스템 v3
화이트 배경 · 폰트 크기 강화 · 발표용 임팩트 디자인
"""

import streamlit as st


COLORS = {
    "bg_deep":       "#FFFFFF",
    "bg_panel":      "#F8FAFC",
    "bg_elevated":   "#F1F5F9",
    "bg_card":       "#FFFFFF",
    "border_subtle": "#E2E8F0",
    "border_strong": "#CBD5E1",

    "text_primary":   "#0F172A",
    "text_secondary": "#334155",
    "text_tertiary":  "#64748B",
    "text_muted":     "#94A3B8",

    "accent_gold":     "#1E40AF",
    "accent_gold_dim": "#BFDBFE",
    "accent_cobalt":   "#0891B2",

    "status_ok":      "#059669",
    "status_warning": "#D97706",
    "status_danger":  "#DC2626",
    "status_info":    "#0284C7",
}


def inject_global_styles():
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;900&family=Inter:wght@400;500;600;700&display=swap');

    /* ── Streamlit 자동 메뉴 완전 숨김 ── */
    section[data-testid="stSidebarNav"],
    section[data-testid="stSidebarNav"] ~ div,
    div[data-testid="stSidebarNavItems"],
    ul[data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavLink"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
        max-height: 0 !important;
        overflow: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* ── 전체 기본 폰트 크기 ── */
    html, body, [class*="css"] {{
        font-size: 16px;
    }}

    /* ── 배경 ── */
    .stApp {{
        background: #FFFFFF;
        color: {COLORS['text_primary']};
        font-family: 'Noto Sans KR', 'Inter', -apple-system, sans-serif;
        font-size: 16px;
    }}

    .main .block-container {{
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1440px;
    }}

    /* ── 일반 텍스트 (selectbox 제외) ── */
    p, li {{
        font-size: 15px;
        line-height: 1.7;
    }}

    /* ── Selectbox / Dropdown 글자 강제 표시 ── */
    .stSelectbox div[data-baseweb="select"] span,
    .stSelectbox div[data-baseweb="select"] div,
    .stSelectbox [data-baseweb="select"] > div,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {{
        color: {COLORS['text_primary']} !important;
        font-size: 15px !important;
    }}
    /* 드롭다운 옵션 목록 */
    ul[data-baseweb="menu"] li,
    li[role="option"],
    div[role="option"] {{
        color: {COLORS['text_primary']} !important;
        font-size: 15px !important;
        background: white !important;
    }}
    li[role="option"]:hover,
    div[role="option"]:hover {{
        background: #EFF6FF !important;
    }}
    /* 선택된 옵션 */
    li[aria-selected="true"],
    div[aria-selected="true"] {{
        background: #EFF6FF !important;
        color: {COLORS['accent_gold']} !important;
    }}
    /* Radio, Checkbox 레이블 */
    .stRadio label p,
    .stCheckbox label p {{
        color: {COLORS['text_secondary']} !important;
        font-size: 15px !important;
    }}

    /* ── 헤딩 ── */
    h1 {{
        font-family: 'Noto Sans KR', sans-serif;
        font-weight: 700;
        font-size: 2rem !important;
        color: {COLORS['text_primary']} !important;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem !important;
        line-height: 1.3 !important;
    }}
    h2 {{
        font-size: 1.5rem !important;
        font-weight: 700;
        color: {COLORS['text_primary']} !important;
    }}
    h3 {{
        font-size: 1.2rem !important;
        font-weight: 600;
        color: {COLORS['text_primary']} !important;
    }}

    /* ── 사이드바 ── */
    section[data-testid="stSidebar"] {{
        background: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }}
    /* 상단 여백 제거 */
    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 0.5rem !important;
    }}
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: 1rem !important;
    }}
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {{
        font-size: 14px;
    }}

    /* ── 사이드바 메뉴 링크 ── */
    a[data-testid="stPageLink-NavLink"] {{
        border-radius: 8px;
        color: {COLORS['text_secondary']} !important;
        font-size: 15px !important;
        font-weight: 500;
        padding: 8px 12px !important;
        margin: 2px 0;
        display: block;
        transition: all 0.1s;
        text-decoration: none !important;
    }}
    a[data-testid="stPageLink-NavLink"]:hover {{
        background: #EFF6FF !important;
        color: {COLORS['accent_gold']} !important;
    }}

    /* ── 버튼 ── */
    .stButton > button {{
        background: {COLORS['accent_gold']};
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 16px !important;
        padding: 10px 20px;
        transition: all 0.15s ease;
        letter-spacing: 0.01em;
    }}
    .stButton > button:hover {{
        background: #1D4ED8;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(30,64,175,0.3);
    }}
    .stButton > button[kind="secondary"] {{
        background: white;
        color: {COLORS['text_secondary']};
        border: 1.5px solid {COLORS['border_subtle']};
    }}
    .stButton > button[kind="secondary"]:hover {{
        background: {COLORS['bg_elevated']};
        border-color: {COLORS['border_strong']};
        transform: none;
        box-shadow: none;
    }}

    /* ── 입력 필드 ── */
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stSelectbox > div > div,
    .stNumberInput input {{
        background: white;
        border: 1.5px solid {COLORS['border_subtle']};
        border-radius: 8px;
        color: {COLORS['text_primary']};
        font-size: 15px !important;
        padding: 10px 14px;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {{
        border-color: {COLORS['accent_gold']};
        box-shadow: 0 0 0 3px rgba(30,64,175,0.12);
        outline: none;
    }}
    .stTextInput label, .stTextArea label,
    .stSelectbox label, .stNumberInput label {{
        font-size: 14px !important;
        font-weight: 600;
        color: {COLORS['text_secondary']} !important;
        margin-bottom: 4px;
    }}

    /* ── 파일 업로더 ── */
    .stFileUploader > div {{
        background: {COLORS['bg_panel']};
        border: 2px dashed {COLORS['border_subtle']};
        border-radius: 10px;
        padding: 1.5rem;
    }}

    /* ── 탭 ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {COLORS['bg_panel']};
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 8px;
        color: {COLORS['text_tertiary']};
        font-weight: 500;
        font-size: 15px !important;
        border: none;
        padding: 8px 20px;
    }}
    .stTabs [aria-selected="true"] {{
        background: white !important;
        color: {COLORS['accent_gold']} !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }}

    /* ── 카드/컨테이너 ── */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border: 1.5px solid {COLORS['border_subtle']} !important;
        border-radius: 10px !important;
        background: white !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        padding: 4px;
    }}

    /* ── 데이터프레임 ── */
    .stDataFrame {{
        border: 1.5px solid {COLORS['border_subtle']};
        border-radius: 10px;
        overflow: hidden;
        font-size: 14px !important;
    }}

    /* ── 라디오/체크박스 ── */
    .stRadio label, .stCheckbox label {{
        color: {COLORS['text_secondary']} !important;
        font-size: 15px !important;
        font-weight: 500;
    }}

    /* ── 알림 ── */
    .stSuccess, .stError, .stWarning, .stInfo {{
        font-size: 15px !important;
        border-radius: 8px;
        padding: 12px 16px;
    }}
    .stSuccess {{ background: #ECFDF5; border-left: 4px solid #059669; color: #065F46; }}
    .stError   {{ background: #FEF2F2; border-left: 4px solid #DC2626; color: #991B1B; }}
    .stWarning {{ background: #FFFBEB; border-left: 4px solid #D97706; color: #92400E; }}
    .stInfo    {{ background: #EFF6FF; border-left: 4px solid #1E40AF; color: #1E3A8A; }}

    /* ── 진행률 ── */
    .stProgress > div > div {{
        background: {COLORS['accent_gold']};
        border-radius: 4px;
    }}

    /* ── 구분선 ── */
    hr {{
        border: none;
        border-top: 1.5px solid {COLORS['border_subtle']};
        margin: 20px 0;
    }}

    /* ── 스피너 ── */
    .stSpinner > div {{
        border-top-color: {COLORS['accent_gold']} !important;
    }}

    /* 스크롤바 */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {COLORS['bg_panel']}; }}
    ::-webkit-scrollbar-thumb {{ background: {COLORS['border_strong']}; border-radius: 3px; }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_brand_header():
    """상단 헤더 — 프로젝트 정보 + 우측 날짜"""
    from datetime import datetime
    now = datetime.now()
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    wd = weekdays[now.weekday()]
    st.markdown(
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;'
        f'padding:16px 0 18px 0;margin-bottom:8px;'
        f'border-bottom:2px solid {COLORS["border_subtle"]};">'
        f'<div>'
        f'<div style="font-size:12px;font-weight:700;color:{COLORS["accent_gold"]};'
        f'letter-spacing:0.06em;margin-bottom:6px;">SCM</div>'
        f'<div style="font-size:22px;font-weight:800;color:{COLORS["text_primary"]};'
        f'line-height:1.3;letter-spacing:-0.02em;margin-bottom:8px;">'
        f'AI 머신비전 기반 실시간 생산·재고 검증 시스템</div>'
        f'<div style="font-size:14px;color:{COLORS["text_tertiary"]};'
        f'font-weight:500;line-height:1.6;">'
        f'인천대학교 동북아물류대학원 &nbsp;·&nbsp; 발표자 &nbsp;정승현'
        f'</div></div>'
        f'<div style="text-align:right;flex-shrink:0;padding-left:24px;">'
        f'<div style="font-size:20px;font-weight:700;color:{COLORS["text_primary"]};'
        f'line-height:1.4;">'
        f'{now.strftime("%Y년 %m월 %d일")}</div>'
        f'<div style="font-size:13px;color:{COLORS["text_muted"]};'
        f'margin-top:4px;font-weight:500;">{now.strftime("%A")} ({wd})'
        f'</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_page_subtitle(text: str):
    st.markdown(
        f'<div style="font-size:13px;font-weight:600;'
        f'color:{COLORS["text_muted"]};letter-spacing:0.06em;'
        f'text-transform:uppercase;margin-bottom:24px;">'
        f'{text}</div>',
        unsafe_allow_html=True,
    )
