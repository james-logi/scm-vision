"""
auth.py — 간단한 비밀번호 보호
Streamlit Community Cloud Secrets에서 PASSWORD를 읽어 인증
"""

import streamlit as st
from styles import COLORS


def check_password() -> bool:
    """비밀번호 확인. 통과하면 True 반환."""

    # 이미 인증된 세션이면 바로 통과
    if st.session_state.get("authenticated"):
        return True

    # 비밀번호 가져오기 (Secrets 또는 환경변수)
    import os
    try:
        # Streamlit Cloud Secrets
        correct_pw = st.secrets.get("APP_PASSWORD", "")
    except Exception:
        correct_pw = ""

    if not correct_pw:
        # 환경변수 fallback
        correct_pw = os.environ.get("APP_PASSWORD", "cratecheck2026")

    # 로그인 화면
    st.markdown(
        f'<div style="max-width:400px;margin:80px auto;">'
        f'<div style="text-align:center;margin-bottom:32px;">'
        f'<div style="font-size:48px;margin-bottom:12px;">◆</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:24px;'
        f'font-weight:700;color:{COLORS["text_primary"]};margin-bottom:6px;">'
        f'출고 재고 검수 관리</div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
        f'color:{COLORS["accent_gold"]};letter-spacing:0.1em;">'
        f'AI VISION SYSTEM</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pw = st.text_input(
            "비밀번호",
            type="password",
            placeholder="비밀번호를 입력하세요",
            label_visibility="collapsed",
        )
        if st.button("접속", width="stretch"):
            if pw == correct_pw:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")

    return False
