"""
Page 5: 기술 선택 논거
- Vision LLM (Claude) vs YOLO 비교
- 본 프로젝트가 Vision LLM을 선택한 명확한 이유
- 한계 인정 + 하이브리드 확장 방향
- 발표·보고서의 기술 정당성 확보
"""

import streamlit as st
from styles import inject_global_styles, render_brand_header, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar

st.set_page_config(
    page_title="기술 선택 논거 | AI Vision",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()

ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 기술 선택 논거")
render_page_subtitle("VISION LLM VS YOLO · TECHNICAL JUSTIFICATION")


# ─────────────────────────────────────────────
# 인트로
# ─────────────────────────────────────────────
st.markdown(
    f"""
    <div class="panel" style="border-left: 3px solid {COLORS['accent_gold']};">
        <p style="font-size: 14px; line-height: 1.8; color: {COLORS['text_secondary']}; margin: 0;">
            본 시스템은 비전 검수 엔진으로
            <strong style="color: {COLORS['accent_gold']};">Claude Vision (Vision LLM)</strong>을 채택했습니다.
            객체 인식 분야의 대표 모델인
            <strong style="color: {COLORS['text_primary']};">YOLO</strong>도 진지하게 고려했으나,
            본 프로젝트의 요구사항에는 Vision LLM이 더 적합한 것으로 판단했습니다.
            본 페이지는 이 기술 결정의 근거를 명문화하며,
            한계와 향후 확장 방향을 함께 제시합니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# 좌우 비교 카드
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f"""
    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                color: {COLORS['text_tertiary']}; letter-spacing: 0.08em;
                text-transform: uppercase; margin-bottom: 10px;">
        SIDE-BY-SIDE COMPARISON
    </div>
    """,
    unsafe_allow_html=True,
)

col_llm, col_yolo = st.columns(2)

# ── 좌측: Vision LLM (선택됨, 골드 강조) ──
with col_llm:
    st.markdown(
        f"""
        <div style="background: {COLORS['bg_panel']};
                    border: 2px solid {COLORS['accent_gold']};
                    border-radius: 8px;
                    padding: 24px;
                    position: relative;
                    min-height: 500px;">

            
            <div style="position: absolute; top: -12px; right: 20px;
                        background: {COLORS['accent_gold']};
                        color: {COLORS['bg_deep']};
                        padding: 4px 12px; border-radius: 4px;
                        font-family: 'IBM Plex Mono', monospace;
                        font-size: 10px; font-weight: 700;
                        letter-spacing: 0.1em;">
                ✓ SELECTED
            </div>

            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 11px;
                        color: {COLORS['accent_gold']}; letter-spacing: 0.08em;">
                OPTION A
            </div>
            <div style="font-family: 'Noto Serif KR', serif;
                        font-size: 26px; font-weight: 700;
                        color: {COLORS['text_primary']};
                        margin: 4px 0 4px 0;">
                Claude Vision
            </div>
            <div style="font-size: 12px; color: {COLORS['text_tertiary']}; margin-bottom: 20px;">
                Vision LLM (Multimodal LLM)
            </div>

            
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                        color: {COLORS['status_ok']}; letter-spacing: 0.08em;
                        margin-bottom: 10px;">
                ✓ STRENGTHS
            </div>
            <ul style="font-size: 13px; line-height: 1.8; color: {COLORS['text_secondary']};
                       padding-left: 18px; margin-bottom: 20px;">
                <li>학습 데이터 불필요 (zero-shot 인식)</li>
                <li>새 SKU 추가 = 라벨 텍스트 등록만으로 즉시 적용</li>
                <li>자연어 추론 결과 반환 (단순 좌표가 아닌 의미)</li>
                <li>유통기한 OCR, 라벨 가독성 평가 동시 수행</li>
                <li>제조 환경 변화(조명·각도) 적응력 우수</li>
            </ul>

            
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                        color: {COLORS['status_warning']}; letter-spacing: 0.08em;
                        margin-bottom: 10px;">
                ⚠ LIMITATIONS
            </div>
            <ul style="font-size: 13px; line-height: 1.8; color: {COLORS['text_secondary']};
                       padding-left: 18px;">
                <li>추론 속도 2~5초/이미지 (API 왕복)</li>
                <li>호출당 API 비용 발생</li>
                <li>인터넷 연결 필수</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── 우측: YOLO (대조군) ──
with col_yolo:
    st.markdown(
        f"""
        <div style="background: {COLORS['bg_panel']};
                    border: 1px solid {COLORS['border_subtle']};
                    border-radius: 8px;
                    padding: 24px;
                    min-height: 500px;">

            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 11px;
                        color: {COLORS['text_tertiary']}; letter-spacing: 0.08em;">
                OPTION B
            </div>
            <div style="font-family: 'Noto Serif KR', serif;
                        font-size: 26px; font-weight: 700;
                        color: {COLORS['text_primary']};
                        margin: 4px 0 4px 0;">
                YOLO
            </div>
            <div style="font-size: 12px; color: {COLORS['text_tertiary']}; margin-bottom: 20px;">
                You Only Look Once · Object Detection
            </div>

            
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                        color: {COLORS['status_ok']}; letter-spacing: 0.08em;
                        margin-bottom: 10px;">
                ✓ STRENGTHS
            </div>
            <ul style="font-size: 13px; line-height: 1.8; color: {COLORS['text_secondary']};
                       padding-left: 18px; margin-bottom: 20px;">
                <li>추론 속도 50~200ms (로컬 GPU)</li>
                <li>충분히 학습된 경우 95%+ 정확도</li>
                <li>오프라인 동작 가능 (인터넷 불필요)</li>
                <li>학습 후 추론 비용 거의 0</li>
                <li>실시간 컨베이어 처리에 적합</li>
            </ul>

            
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                        color: {COLORS['status_warning']}; letter-spacing: 0.08em;
                        margin-bottom: 10px;">
                ⚠ LIMITATIONS
            </div>
            <ul style="font-size: 13px; line-height: 1.8; color: {COLORS['text_secondary']};
                       padding-left: 18px;">
                <li>학습 데이터셋 수집·라벨링 필요 (SKU당 수백 장)</li>
                <li>학습 기간 1~2주 + GPU 자원 투자</li>
                <li>새 SKU 추가 시 재학습 필수</li>
                <li>객체 좌표만 반환, 의미적 추론 불가</li>
                <li>유통기한·라벨 분석은 별도 OCR 필요</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# 우리 프로젝트엔 왜 Vision LLM인가 (3가지 이유)
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f"""
    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                color: {COLORS['text_tertiary']}; letter-spacing: 0.08em;
                text-transform: uppercase; margin-top: 24px; margin-bottom: 10px;">
        WHY VISION LLM FOR THIS PROJECT
    </div>
    """,
    unsafe_allow_html=True,
)

reason_col1, reason_col2, reason_col3 = st.columns(3)

reasons = [
    {
        "col": reason_col1,
        "num": "01",
        "title": "SKU 확장성",
        "body": (
            "식품 제조 현장은 신제품 출시 주기가 짧고 SKU가 빈번하게 추가됩니다. "
            "YOLO는 매번 데이터 수집·재학습이 필요하지만, Vision LLM은 "
            "<strong>SKU 등록부에 시각적 특징을 자연어로 기술</strong>하면 즉시 인식 가능합니다."
        ),
    },
    {
        "col": reason_col2,
        "num": "02",
        "title": "의미적 추론",
        "body": (
            "YOLO는 좌표와 클래스만 반환합니다. Vision LLM은 "
            "<strong>라벨 가독성, 비닐 반사 영향, 적재 정렬 상태, 유통기한</strong> 같은 "
            "운영에 필요한 부가 정보를 단일 호출에서 함께 반환합니다."
        ),
    },
    {
        "col": reason_col3,
        "num": "03",
        "title": "개발 일정",
        "body": (
            "30일짜리 캡스톤 일정에서 YOLO 학습 데이터 수집·라벨링·학습에 "
            "1~2주를 쓰면 다른 작업이 밀립니다. Vision LLM은 "
            "<strong>당일부터 사용 가능</strong>하여 전체 시스템 통합에 집중할 수 있었습니다."
        ),
    },
]

for r in reasons:
    with r["col"]:
        st.markdown(
            f"""
            <div style="background: {COLORS['bg_panel']};
                        border: 1px solid {COLORS['border_subtle']};
                        border-radius: 6px;
                        padding: 20px;
                        height: 200px;">
                <div style="font-family: 'Noto Serif KR', serif;
                            font-size: 36px; font-weight: 900;
                            color: {COLORS['accent_gold']};
                            line-height: 1; margin-bottom: 4px;">
                    {r['num']}
                </div>
                <div style="font-family: 'Noto Serif KR', serif;
                            font-size: 17px; font-weight: 700;
                            color: {COLORS['text_primary']};
                            margin-bottom: 10px;">
                    {r['title']}
                </div>
                <div style="font-size: 12px; line-height: 1.7;
                            color: {COLORS['text_secondary']};">
                    {r['body']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# 한계 인정 + 하이브리드 확장 방향
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f"""
    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                color: {COLORS['text_tertiary']}; letter-spacing: 0.08em;
                text-transform: uppercase; margin-top: 24px; margin-bottom: 10px;">
        FUTURE DIRECTION · HYBRID ARCHITECTURE
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div style="background: {COLORS['bg_panel']};
                border: 1px solid {COLORS['accent_gold_dim']};
                border-left: 4px solid {COLORS['accent_gold']};
                border-radius: 6px;
                padding: 24px;">
        <div style="font-family: 'Noto Serif KR', serif; font-size: 17px;
                    font-weight: 700; color: {COLORS['text_primary']};
                    margin-bottom: 12px;">
            한계 인정 — 그리고 확장 방향
        </div>
        <p style="font-size: 13px; line-height: 1.85; color: {COLORS['text_secondary']};
                  margin-bottom: 16px;">
            Vision LLM의 추론 속도(2~5초/이미지)는 컨베이어 풀스피드 환경에서 명백한 약점입니다.
            대량 처리가 요구되는 운영 환경에서는 두 기술의 강점을 결합한
            <strong style="color: {COLORS['accent_gold']};">하이브리드 구조</strong>가 더 적합합니다.
        </p>

        <div style="background: {COLORS['bg_deep']};
                    border-radius: 4px; padding: 16px;
                    font-family: 'IBM Plex Mono', monospace; font-size: 12px;
                    color: {COLORS['text_secondary']}; line-height: 1.9;">
            <div style="color: {COLORS['accent_gold']}; margin-bottom: 8px;">
                [Hybrid Pipeline]
            </div>
            <div>
                ① <span style="color: {COLORS['accent_cobalt']};">YOLO</span>
                : 모든 P-Box를 빠르게 1차 스캔 (50ms/박스, 정상 흐름 유지)
            </div>
            <div>
                ② 카운트 불일치 또는 confidence &lt; 임계값 → NG 후보로 플래그
            </div>
            <div>
                ③ <span style="color: {COLORS['accent_gold']};">Vision LLM (Claude)</span>
                : NG 후보만 정밀 분석 (혼입 검출, 라벨 검증, 자연어 권고)
            </div>
            <div>
                ④ 결과를 WMS에 통합 반영 + 작업자에게 자연어 안내
            </div>
        </div>

        <p style="font-size: 12px; line-height: 1.8; color: {COLORS['text_tertiary']};
                  margin-top: 16px; margin-bottom: 0;">
            ※ 본 프로토타입은 Vision LLM 단독 구조로 구현되었으며,
            위 하이브리드 구조는 <strong style="color: {COLORS['text_secondary']};">후속 연구 과제</strong>로 남깁니다.
            본 프로젝트의 핵심 기여는 비전 검수 + WMS 실시간 통합 + Dual-Unit Tracking
            아키텍처의 검증이며, 비전 모델 자체는 교체 가능한 컴포넌트로 설계되었습니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# 비교표 (요약, 1페이지 분량)
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f"""
    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                color: {COLORS['text_tertiary']}; letter-spacing: 0.08em;
                text-transform: uppercase; margin-top: 24px; margin-bottom: 10px;">
        QUICK REFERENCE TABLE
    </div>
    """,
    unsafe_allow_html=True,
)

# 비교 표
comparison_rows = [
    ("학습 필요", "❌ 불필요 (zero-shot)", "✅ 필수 (수백 장/SKU)"),
    ("개발 기간", "당일 사용 가능", "1~2주 학습 + GPU 자원"),
    ("추론 속도", "2~5초 (API)", "50~200ms (로컬 GPU)"),
    ("정확도 (본 데이터)", "92~98%", "95%+ (학습 후)"),
    ("새 SKU 대응", "라벨 등록만으로 즉시", "데이터 재수집 + 재학습"),
    ("출력 형태", "구조화 JSON + 자연어 추론", "박스 좌표 + 클래스 라벨"),
    ("부가 기능", "OCR · 라벨 평가 · 추론 통합", "별도 파이프라인 필요"),
    ("비용 구조", "API 호출당 과금", "초기 GPU 투자 → 무료"),
    ("인터넷 의존", "✅ 필수", "❌ 오프라인 가능"),
    ("적합 시나리오", "다품종 · 변경 잦은 환경", "단일 품목 · 대량 처리"),
]

table_html = f"""
<div style="background: {COLORS['bg_panel']};
            border: 1px solid {COLORS['border_subtle']};
            border-radius: 6px; overflow: hidden;">
    
    <div style="display: grid; grid-template-columns: 1fr 1.4fr 1.4fr;
                background: {COLORS['bg_elevated']};
                padding: 12px 18px;
                border-bottom: 1px solid {COLORS['border_subtle']};
                font-family: 'IBM Plex Mono', monospace; font-size: 11px;
                color: {COLORS['text_tertiary']};
                letter-spacing: 0.08em; text-transform: uppercase;">
        <div>항목</div>
        <div style="color: {COLORS['accent_gold']};">Vision LLM (선택)</div>
        <div>YOLO</div>
    </div>
"""

for i, (item, llm, yolo) in enumerate(comparison_rows):
    bg = COLORS["bg_deep"] if i % 2 == 0 else COLORS["bg_panel"]
    table_html += f"""
    <div style="display: grid; grid-template-columns: 1fr 1.4fr 1.4fr;
                background: {bg};
                padding: 12px 18px;
                border-bottom: 1px solid {COLORS['border_subtle']};
                font-size: 13px; align-items: center;">
        <div style="color: {COLORS['text_tertiary']};">{item}</div>
        <div style="color: {COLORS['text_primary']};">{llm}</div>
        <div style="color: {COLORS['text_secondary']};">{yolo}</div>
    </div>
    """

table_html += "</div>"
st.markdown(table_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 푸터
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 32px;
                font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                color: {COLORS['text_muted']}; letter-spacing: 0.08em;">
        SCM CAPSTONE · INCHEON NATIONAL UNIVERSITY · GRADUATE SCHOOL OF LOGISTICS
    </div>
    """,
    unsafe_allow_html=True,
)
