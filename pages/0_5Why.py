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
    text = st.session_state.whys_text.strip()
    # 멀티라인 블록 파싱: 연속된 줄을 블록으로 묶음
    blocks = []
    current_key  = None
    current_lines = []

    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            if current_key:
                blocks.append((current_key, " ".join(current_lines)))
                current_key, current_lines = None, []
            continue
        if line.startswith("문제 현상"):
            if current_key:
                blocks.append((current_key, " ".join(current_lines)))
            current_key, current_lines = "problem", [line]
        elif line.startswith("Why"):
            if current_key:
                blocks.append((current_key, " ".join(current_lines)))
            current_key, current_lines = "why", [line]
        elif line.startswith("→"):
            if current_key == "why":
                current_lines.append(line)
            else:
                blocks.append(("arrow", line))
        elif line.startswith("근본 원인"):
            if current_key:
                blocks.append((current_key, " ".join(current_lines)))
            current_key, current_lines = "root", [line.replace("근본 원인 (Root Cause):","").strip()]
        elif line.startswith("해결책"):
            if current_key:
                blocks.append((current_key, " ".join(current_lines)))
            current_key, current_lines = "solution", [line.replace("해결책:","").strip()]
        else:
            if current_key:
                current_lines.append(line)
            else:
                blocks.append(("text", line))

    if current_key:
        blocks.append((current_key, " ".join(current_lines)))

    html = ""
    for btype, content in blocks:
        if btype == "problem":
            html += (
                f'<div style="background:{COLORS["bg_panel"]};'
                f'border-left:4px solid {COLORS["status_danger"]};'
                f'border-radius:6px;padding:14px 20px;margin-bottom:16px;">'
                f'<div style="font-size:15px;font-weight:700;'
                f'color:{COLORS["status_danger"]};line-height:1.6;">⚠ {content}</div>'
                f'</div>'
            )
        elif btype == "why":
            lines_w = content.split(" ", 2)
            num_part = lines_w[0].replace("Why","").replace(".","").strip() if lines_w else ""
            rest_part = content.split(".", 1)[1].strip() if "." in content else content
            # 화살표 줄 분리
            parts_w = content.split("→", 1)
            title_w = parts_w[0].strip()
            arrow_w = "→" + parts_w[1].strip() if len(parts_w) > 1 else ""
            num_w = title_w.split(".", 1)[0].replace("Why","").strip()
            q_w   = title_w.split(".", 1)[1].strip() if "." in title_w else title_w
            html += (
                f'<div style="background:{COLORS["bg_panel"]};'
                f'border:1px solid {COLORS["border_subtle"]};'
                f'border-left:4px solid {COLORS["accent_cobalt"]};'
                f'border-radius:6px;padding:14px 20px;margin-bottom:4px;">'
                f'<span style="font-size:20px;font-weight:900;color:{COLORS["accent_cobalt"]};">Why {num_w}</span>'
                f'<span style="font-size:15px;font-weight:700;color:{COLORS["text_primary"]};margin-left:12px;">{q_w}</span>'
                f'</div>'
            )
            if arrow_w:
                html += (
                    f'<div style="font-size:14px;color:{COLORS["text_secondary"]};'
                    f'padding:4px 0 12px 36px;line-height:1.8;">{arrow_w}</div>'
                )
        elif btype == "arrow":
            html += (
                f'<div style="font-size:14px;color:{COLORS["text_secondary"]};'
                f'padding:4px 0 12px 36px;line-height:1.8;">{content}</div>'
            )
        elif btype == "root":
            html += (
                f'<div style="background:#FEF2F2;'
                f'border-left:4px solid {COLORS["status_danger"]};'
                f'border-radius:6px;padding:16px 20px;margin-top:16px;margin-bottom:8px;">'
                f'<div style="font-size:11px;font-weight:700;color:{COLORS["status_danger"]};'
                f'letter-spacing:0.08em;margin-bottom:8px;">🔴 근본 원인 (Root Cause)</div>'
                f'<div style="font-size:15px;font-weight:600;color:{COLORS["text_primary"]};'
                f'line-height:1.7;">{content}</div>'
                f'</div>'
            )
        elif btype == "solution":
            html += (
                f'<div style="background:#ECFDF5;'
                f'border-left:4px solid {COLORS["status_ok"]};'
                f'border-radius:6px;padding:16px 20px;margin-top:8px;">'
                f'<div style="font-size:11px;font-weight:700;color:{COLORS["status_ok"]};'
                f'letter-spacing:0.08em;margin-bottom:8px;">✅ 해결책</div>'
                f'<div style="font-size:14px;color:{COLORS["text_primary"]};'
                f'line-height:1.8;">{content}</div>'
                f'</div>'
            )
        elif btype == "text":
            html += (
                f'<div style="font-size:14px;color:{COLORS["text_secondary"]};'
                f'padding:4px 0;line-height:1.7;">{content}</div>'
            )

    st.markdown(html, unsafe_allow_html=True)
