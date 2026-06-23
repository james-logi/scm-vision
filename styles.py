"""
출고 재고 검수 관리 - 디자인 시스템 v2
화이트 배경 + 딥블루 비즈니스 톤 (Notion / Linear 스타일)
"""

import streamlit as st


# ============================================================
# 컬러 팔레트
# ============================================================
COLORS = {
    # 배경
    "bg_deep":     "#FFFFFF",
    "bg_panel":    "#F8FAFC",
    "bg_elevated": "#F1F5F9",
    "bg_card":     "#FFFFFF",
    "border_subtle": "#E2E8F0",
    "border_strong": "#CBD5E1",

    # 텍스트
    "text_primary":   "#0F172A",
    "text_secondary": "#334155",
    "text_tertiary":  "#64748B",
    "text_muted":     "#94A3B8",

    # 브랜드 컬러
    "accent_gold":     "#1E40AF",   # 딥블루 (골드 대체)
    "accent_gold_dim": "#BFDBFE",   # 연한 블루
    "accent_cobalt":   "#0891B2",   # 틸 블루

    # 상태
    "status_ok":      "#059669",
    "status_warning": "#D97706",
    "status_danger":  "#DC2626",
    "status_info":    "#0284C7",
}


# ============================================================
# 전역 CSS
# ============================================================
def inject_global_styles():
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

    /* ── 배경/본문 ── */
    .stApp {{
        background: #FFFFFF;
        color: {COLORS['text_primary']};
        font-family: 'Noto Sans KR', 'Inter', -apple-system, sans-serif;
    }}

    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}

    /* ── 헤딩 ── */
    h1 {{
        font-family: 'Noto Sans KR', sans-serif;
        font-weight: 700;
        font-size: 1.75rem !important;
        color: {COLORS['text_primary']} !important;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem !important;
    }}
    h2, h3 {{
        font-family: 'Noto Sans KR', sans-serif;
        font-weight: 600;
        color: {COLORS['text_primary']} !important;
    }}

    /* ── 사이드바 ── */
    section[data-testid="stSidebar"] {{
        background: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }}
    section[data-testid="stSidebar"] * {{
        color: {COLORS['text_secondary']};
    }}
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label {{
        color: {COLORS['text_tertiary']} !important;
        font-size: 12px;
    }}

    /* ── 버튼 ── */
    .stButton > button {{
        background: {COLORS['accent_gold']};
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        font-size: 14px;
        padding: 8px 16px;
        transition: all 0.15s ease;
    }}
    .stButton > button:hover {{
        background: #1D4ED8;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(30,64,175,0.25);
    }}
    .stButton > button[kind="secondary"] {{
        background: white;
        color: {COLORS['text_secondary']};
        border: 1px solid {COLORS['border_subtle']};
    }}
    .stButton > button[kind="secondary"]:hover {{
        background: {COLORS['bg_elevated']};
        transform: none;
        box-shadow: none;
    }}

    /* ── 입력 필드 ── */
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stSelectbox > div > div {{
        background: white;
        border: 1px solid {COLORS['border_subtle']};
        border-radius: 6px;
        color: {COLORS['text_primary']};
        font-size: 14px;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {{
        border-color: {COLORS['accent_gold']};
        box-shadow: 0 0 0 3px rgba(30,64,175,0.1);
    }}

    /* ── 파일 업로더 ── */
    .stFileUploader > div {{
        background: {COLORS['bg_panel']};
        border: 2px dashed {COLORS['border_subtle']};
        border-radius: 8px;
    }}

    /* ── 탭 ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {COLORS['bg_panel']};
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
        border-bottom: none;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 6px;
        color: {COLORS['text_tertiary']};
        font-weight: 500;
        font-size: 14px;
        border: none;
        padding: 6px 16px;
    }}
    .stTabs [aria-selected="true"] {{
        background: white !important;
        color: {COLORS['accent_gold']} !important;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }}

    /* ── 데이터프레임 ── */
    .stDataFrame {{
        border: 1px solid {COLORS['border_subtle']};
        border-radius: 8px;
        overflow: hidden;
    }}

    /* ── 컨테이너/카드 ── */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border: 1px solid {COLORS['border_subtle']} !important;
        border-radius: 8px !important;
        background: white !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }}

    /* ── 진행률/슬라이더 ── */
    .stProgress > div > div {{
        background: {COLORS['accent_gold']};
    }}

    /* ── 알림 ── */
    .stSuccess {{ background: #ECFDF5; border-color: #059669; color: #065F46; }}
    .stError   {{ background: #FEF2F2; border-color: #DC2626; color: #991B1B; }}
    .stWarning {{ background: #FFFBEB; border-color: #D97706; color: #92400E; }}
    .stInfo    {{ background: #EFF6FF; border-color: #1E40AF; color: #1E3A8A; }}

    /* ── page_link (메뉴) ── */
    a[data-testid="stPageLink-NavLink"] {{
        background: transparent;
        border-radius: 6px;
        color: {COLORS['text_secondary']} !important;
        font-size: 14px;
        font-weight: 500;
        padding: 6px 10px;
        margin: 1px 0;
        transition: all 0.1s;
    }}
    a[data-testid="stPageLink-NavLink"]:hover {{
        background: {COLORS['bg_elevated']};
        color: {COLORS['accent_gold']} !important;
    }}

    /* ── 라디오/체크박스 ── */
    .stRadio label, .stCheckbox label {{
        color: {COLORS['text_secondary']} !important;
        font-size: 14px;
    }}

    /* ── 구분선 ── */
    hr {{
        border-color: {COLORS['border_subtle']};
        margin: 16px 0;
    }}

    /* ── spinner ── */
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


# ============================================================
# 브랜드 헤더
# ============================================================
def render_brand_header():
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;'
        f'padding-bottom:12px;margin-bottom:4px;'
        f'border-bottom:1px solid {COLORS["border_subtle"]};">'
        f'<div style="width:8px;height:8px;border-radius:2px;'
        f'background:{COLORS["accent_gold"]};"></div>'
        f'<span style="font-family:\'Inter\',sans-serif;font-size:13px;'
        f'font-weight:600;color:{COLORS["text_tertiary"]};letter-spacing:0.02em;">'
        f'출고 재고 검수 관리</span>'
        f'<span style="font-size:12px;color:{COLORS["text_muted"]};'
        f'margin-left:4px;">AI Vision System</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# 페이지 부제목
# ============================================================
def render_page_subtitle(text: str):
    st.markdown(
        f'<div style="font-size:12px;font-weight:500;'
        f'color:{COLORS["text_muted"]};letter-spacing:0.05em;'
        f'text-transform:uppercase;margin-bottom:20px;">'
        f'{text}</div>',
        unsafe_allow_html=True,
    )
