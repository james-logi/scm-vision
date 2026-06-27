"""
5 Why — 근본 원인 분석 (편집 가능)
"""
import streamlit as st
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar, render_brand_header

st.set_page_config(page_title="5 Why | SCM", page_icon="◆",
                   layout="wide", initial_sidebar_state="expanded")
inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 5 Why — 근본 원인 분석")
render_page_subtitle("ROOT CAUSE ANALYSIS · EDITABLE")

DEFAULT = """문제 현상: 물류동 전산 재고와 실물 재고가 일치하지 않는다

Why 1. 왜 전산 재고와 실물이 다른가?
→ 생산에서 물류동으로 P-Box가 이동하는 과정에서 수량 정보가 손실되기 때문

Why 2. 왜 수량 정보가 손실되는가?
→ 낱개(EA) → 박스(Case)로 단위가 전환되는 지점에서 계수기 설정 오류와 수작업 오차가 발생하기 때문

Why 3. 왜 단위 전환 지점에서 오차가 발생하는가?
→ 제품이 바뀔 때마다 계수기를 수동으로 재설정해야 하고, 이를 자동으로 검증하는 수단이 없기 때문

Why 4. 왜 자동 검증 수단이 없었는가?
→ 기존 비전 기술(YOLO 등)은 60종 다품종 환경에서 SKU마다 재학습이 필요해 ROI와 유연성 면에서 도입이 어려웠기 때문

Why 5. 왜 기존 기술로는 ROI가 안 맞는가?
→ 학습 데이터 수집·재학습·GPU 투자 비용이 크고, 신제품 출시 주기가 짧은 식품 제조 환경의 속도를 따라가지 못하기 때문

근본 원인 (Root Cause):
EA→Case 단위 전환 지점에 기존 기술로는 대응하기 어려운 자동 검증 공백이 존재한다

해결책:
Claude Vision LLM — 학습 없이 즉시 적용, SKU 등록만으로 확장, 의미적 추론으로 수량·종류 동시 검증
→ IRI 65% → 1.42% 개선 / NG 38건 차단 = 불량 출고 원천 차단"""

if "whys_text"    not in st.session_state: st.session_state.whys_text    = DEFAULT
if "whys_editing" not in st.session_state: st.session_state.whys_editing = False

# ─── 편집 버튼 ───
_, btn_col = st.columns([5, 1])
with btn_col:
    if st.session_state.whys_editing:
        if st.button("💾 저장", type="primary", key="w_save"):
            st.session_state.whys_editing = False
            st.rerun()
        if st.button("↩ 취소", key="w_cancel"):
            st.session_state.whys_editing = False
            st.rerun()
    else:
        if st.button("✏️ 편집", key="w_edit"):
            st.session_state.whys_editing = True
            st.rerun()

# ─── 편집 모드 ───
if st.session_state.whys_editing:
    st.session_state.whys_text = st.text_area(
        "내용",
        value=st.session_state.whys_text,
        height=440,
        label_visibility="collapsed",
        key="w_area",
    )
    if st.button("🔄 기본값으로 초기화", key="w_reset"):
        st.session_state.whys_text = DEFAULT
        st.rerun()

# ─── 표시 모드 ───
else:
    def render_line(line):
        line = line.strip()
        if not line:
            return ""
        if line.startswith("문제 현상"):
            return (
                f'<div style="background:{COLORS["bg_panel"]};'
                f'border-left:4px solid {COLORS["status_danger"]};'
                f'border-radius:6px;padding:14px 20px;margin-bottom:16px;">'
                f'<div style="font-size:15px;font-weight:700;'
                f'color:{COLORS["status_danger"]};line-height:1.6;">⚠ {line}</div>'
                f'</div>'
            )
        if line.startswith("Why"):
            parts = line.split(".", 1)
            num  = parts[0].replace("Why","").strip()
            rest = parts[1].strip() if len(parts) > 1 else ""
            return (
                f'<div style="background:{COLORS["bg_panel"]};'
                f'border:1px solid {COLORS["border_subtle"]};'
                f'border-left:4px solid {COLORS["accent_cobalt"]};'
                f'border-radius:6px;padding:14px 20px;margin-bottom:6px;">'
                f'<span style="font-size:20px;font-weight:900;'
                f'color:{COLORS["accent_cobalt"]};">Why {num}</span>'
                f'<span style="font-size:15px;font-weight:700;'
                f'color:{COLORS["text_primary"]};margin-left:12px;">{rest}</span>'
                f'</div>'
            )
        if line.startswith("→"):
            return (
                f'<div style="font-size:14px;color:{COLORS["text_secondary"]};'
                f'padding:4px 0 12px 36px;line-height:1.8;">{line}</div>'
            )
        if line.startswith("근본 원인"):
            rest = line.replace("근본 원인 (Root Cause):","").strip()
            return (
                f'<div style="background:#FEF2F2;'
                f'border-left:4px solid {COLORS["status_danger"]};'
                f'border-radius:6px;padding:16px 20px;margin-top:16px;margin-bottom:8px;">'
                f'<div style="font-size:11px;font-weight:700;'
                f'color:{COLORS["status_danger"]};letter-spacing:0.08em;margin-bottom:6px;">'
                f'🔴 근본 원인 (Root Cause)</div>'
                f'<div style="font-size:15px;font-weight:600;'
                f'color:{COLORS["text_primary"]};line-height:1.7;">{rest}</div>'
                f'</div>'
            )
        if line.startswith("해결책"):
            rest = line.replace("해결책:","").strip()
            return (
                f'<div style="background:#ECFDF5;'
                f'border-left:4px solid {COLORS["status_ok"]};'
                f'border-radius:6px;padding:16px 20px;margin-top:8px;">'
                f'<div style="font-size:11px;font-weight:700;'
                f'color:{COLORS["status_ok"]};letter-spacing:0.08em;margin-bottom:6px;">'
                f'✅ 해결책</div>'
                f'<div style="font-size:14px;color:{COLORS["text_primary"]};'
                f'line-height:1.8;">{rest}</div>'
                f'</div>'
            )
        return ""

    parts = [render_line(l) for l in st.session_state.whys_text.split("\n")]
    st.markdown("".join(p for p in parts if p), unsafe_allow_html=True)
