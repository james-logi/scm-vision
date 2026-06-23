"""
출고 재고 검수 관리 - 디자인 시스템
HTML 프로토타입의 다크 네이비 + 무광 골드 톤을 Streamlit에 주입.
"""

import streamlit as st


# ============================================================
# 컬러 팔레트 (HTML 프로토타입과 동일)
# ============================================================
COLORS = {
    "bg_deep": "#0a1429",
    "bg_panel": "#111d3a",
    "bg_elevated": "#182850",
    "bg_card": "#1c2f5c",
    "border_subtle": "#243760",
    "border_strong": "#34507c",

    "text_primary": "#f1f5fa",
    "text_secondary": "#a8b8cf",
    "text_tertiary": "#6a7c9c",
    "text_muted": "#4a5a7a",

    "accent_gold": "#c9a55c",
    "accent_gold_dim": "#8a7340",
    "accent_cobalt": "#4a7fc8",

    "status_ok": "#5ec19c",
    "status_warning": "#d4a557",
    "status_danger": "#d4685c",
    "status_info": "#6a9bd1",
}


# ============================================================
# 전역 CSS 주입
# ============================================================
def inject_global_styles():
    """Streamlit 페이지 진입 시 호출. HTML 프로토타입의 톤을 적용."""

    css = f"""
    <style>
    /* ── 한글 폰트 ── */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;700;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');

    /* ── 배경/본문 ── */
    .stApp {{
        background: {COLORS['bg_deep']};
        background-image:
            radial-gradient(circle at 15% 10%, rgba(74, 127, 200, 0.06), transparent 50%),
            radial-gradient(circle at 85% 90%, rgba(201, 165, 92, 0.04), transparent 50%);
        color: {COLORS['text_primary']};
        font-family: 'Pretendard', -apple-system, sans-serif;
    }}

    /* 메인 컨텐츠 영역 */
    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}

    /* ── 헤딩 ── */
    h1, h2, h3 {{
        font-family: 'Noto Serif KR', serif;
        color: {COLORS['text_primary']};
        letter-spacing: -0.02em;
    }}

    /* ── 사이드바 ── */
    section[data-testid="stSidebar"] {{
        background: {COLORS['bg_panel']};
        border-right: 1px solid {COLORS['border_subtle']};
    }}

    section[data-testid="stSidebar"] * {{
        color: {COLORS['text_secondary']};
    }}

    /* ── 버튼 ── */
    .stButton button {{
        background: {COLORS['bg_elevated']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border_strong']};
        border-radius: 4px;
        font-weight: 500;
        transition: all 0.15s;
    }}

    .stButton button:hover {{
        background: {COLORS['bg_card']};
        border-color: {COLORS['accent_gold_dim']};
        color: {COLORS['text_primary']};
    }}

    /* Primary 버튼 (type="primary") */
    .stButton button[kind="primary"] {{
        background: {COLORS['accent_gold']};
        color: {COLORS['bg_deep']};
        border-color: {COLORS['accent_gold']};
        font-weight: 600;
    }}

    .stButton button[kind="primary"]:hover {{
        background: #d6b366;
    }}

    /* ── Selectbox ── */
    div[data-baseweb="select"] > div {{
        background: {COLORS['bg_deep']};
        border: 1px solid {COLORS['border_strong']};
        color: {COLORS['text_secondary']};
    }}

    /* ── 라디오/토글 ── */
    div[data-testid="stRadio"] label {{
        color: {COLORS['text_secondary']};
    }}

    /* ── 메트릭 카드 ── */
    div[data-testid="stMetric"] {{
        background: {COLORS['bg_panel']};
        border: 1px solid {COLORS['border_subtle']};
        border-left: 3px solid {COLORS['accent_cobalt']};
        border-radius: 6px;
        padding: 16px 18px;
    }}

    div[data-testid="stMetricLabel"] {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px !important;
        color: {COLORS['text_tertiary']} !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}

    div[data-testid="stMetricValue"] {{
        font-family: 'Noto Serif KR', serif !important;
        font-weight: 700 !important;
        color: {COLORS['text_primary']} !important;
    }}

    /* ── 데이터프레임 ── */
    div[data-testid="stDataFrame"] {{
        background: {COLORS['bg_panel']};
        border: 1px solid {COLORS['border_subtle']};
        border-radius: 4px;
    }}

    /* ── 알림 박스 ── */
    div[data-testid="stAlert"] {{
        background: {COLORS['bg_panel']};
        border-left: 4px solid {COLORS['accent_gold']};
        color: {COLORS['text_primary']};
    }}

    /* ── 구분선 ── */
    hr {{
        border-color: {COLORS['border_subtle']};
    }}

    /* ── 코드 블록 ── */
    code {{
        background: {COLORS['bg_deep']} !important;
        color: {COLORS['accent_gold']} !important;
        font-family: 'IBM Plex Mono', monospace !important;
        padding: 2px 6px;
        border-radius: 2px;
    }}

    /* ── 탭 ── */
    button[data-baseweb="tab"] {{
        color: {COLORS['text_tertiary']} !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {COLORS['accent_gold']} !important;
        border-bottom-color: {COLORS['accent_gold']} !important;
    }}

    /* ── Streamlit 기본 헤더/푸터 숨김 ── */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* ── 사이드바 자체는 무조건 표시되도록 강제 ──
       Streamlit 1.57.0이 인라인 style로 height:0을 직접 박아넣어서 사이드바를 숨김.
       data-testid 셀렉터 + 클래스 셀렉터를 모두 사용해서 어떤 경우에도 적용되도록. */
    section[data-testid="stSidebar"],
    section.stSidebar,
    [class*="stSidebar"] {{
        display: block !important;
        visibility: visible !important;
        width: 244px !important;
        min-width: 244px !important;
        max-width: 244px !important;
        height: auto !important;
        min-height: 100vh !important;
        transform: none !important;
        margin-left: 0 !important;
        left: 0 !important;
        position: relative !important;
    }}

    /* ── 사이드바가 펼친 상태일 때 메인 컨텐츠 위치 보정 ── */
    section[data-testid="stSidebar"][aria-expanded="true"] ~ section.main {{
        margin-left: 244px !important;
    }}

    /* ── 사이드바 토글 버튼(collapsed control) 표시 강제 ── */
    [data-testid="stSidebarCollapsedControl"] {{
        display: flex !important;
        visibility: visible !important;
    }}

    /* ── 자동 페이지 목록 nav 영역만 정확히 숨김 ──
       구체적인 태그+testid 조합으로 다른 요소에 영향 없도록. */
    ul[data-testid="stSidebarNavItems"] {{
        display: none !important;
    }}
    hr[data-testid="stSidebarNavSeparator"] {{
        display: none !important;
    }}
    div[data-testid="stSidebarNavSeparator"] {{
        display: none !important;
    }}

    /* ── 상단 브랜드 헤더 (커스텀) ── */
    .brand-header {{
        background: rgba(10, 20, 41, 0.95);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid {COLORS['border_subtle']};
        padding: 14px 0;
        margin: -1.5rem -1rem 1.5rem -1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-left: 32px;
        padding-right: 32px;
    }}

    .brand-mark {{
        font-family: 'Noto Serif KR', serif;
        font-weight: 900;
        font-size: 20px;
        color: {COLORS['text_primary']};
    }}

    .brand-mark::before {{
        content: '◆';
        color: {COLORS['accent_gold']};
        margin-right: 8px;
        font-size: 13px;
    }}

    .brand-sub {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        color: {COLORS['accent_gold']};
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-left: 8px;
    }}

    .brand-affiliation {{
        font-size: 11px;
        color: {COLORS['text_tertiary']};
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding-left: 16px;
        border-left: 1px solid {COLORS['border_subtle']};
        margin-left: 16px;
    }}

    .brand-affiliation strong {{
        color: {COLORS['text_secondary']};
        font-weight: 500;
    }}

    /* ── 페이지 소제목 ── */
    .page-subtitle {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        color: {COLORS['text_tertiary']};
        letter-spacing: 0.05em;
        margin-bottom: 24px;
        margin-top: -8px;
    }}

    /* ── 패널 카드 ── */
    .panel {{
        background: {COLORS['bg_panel']};
        border: 1px solid {COLORS['border_subtle']};
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 16px;
    }}

    .panel-title {{
        font-family: 'Noto Serif KR', serif;
        font-size: 14px;
        font-weight: 700;
        color: {COLORS['text_primary']};
        padding-bottom: 12px;
        border-bottom: 1px solid {COLORS['border_subtle']};
        margin-bottom: 16px;
    }}

    /* ── 상태 뱃지 ── */
    .badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 3px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.05em;
    }}

    .badge-ok {{
        background: rgba(94,193,156,0.15);
        color: {COLORS['status_ok']};
    }}

    .badge-warning {{
        background: rgba(212,165,87,0.15);
        color: {COLORS['status_warning']};
    }}

    .badge-danger {{
        background: rgba(212,104,92,0.15);
        color: {COLORS['status_danger']};
    }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ============================================================
# 공통 헤더 컴포넌트
# ============================================================
def render_brand_header():
    """모든 페이지 상단에 표시되는 브랜드 헤더."""
    st.markdown(
        """
        <div class="brand-header">
            <div>
                <span class="brand-mark">출고 재고 검수 관리</span>
                <span class="brand-sub">AI VISION</span>
                <span class="brand-affiliation"><strong>인천대학교 동북아물류대학원</strong></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_subtitle(text: str):
    """페이지별 영문 서브타이틀."""
    st.markdown(f'<div class="page-subtitle">{text}</div>', unsafe_allow_html=True)
