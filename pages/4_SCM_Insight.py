"""
Page 4: SCM 인사이트

본 프로젝트의 차별화 핵심 페이지.
검수 이력 데이터에서 자동으로 인사이트를 추출하고,
Claude의 자연어 추론으로 권고를 생성한다.

이 페이지는 발표에서 가장 강력한 임팩트를 가진다:
  "비전 검수가 데이터를 만들고,
   Claude가 그 데이터에서 패턴을 읽어
   현장에 권고를 만든다."

D12: 골격 + 자동 인사이트 카드 (오늘)
D13: 채찍효과 정량화 + 시각화
D14: 향후 권고 + 통합 마무리
"""

import streamlit as st
import pandas as pd
import altair as alt
from styles import inject_global_styles, render_brand_header, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar
from scm_insights import extract_all_insights, compute_top_kpis

st.set_page_config(
    page_title="SCM 인사이트 | AI Vision",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()

ensure_session_state()
render_sidebar()
render_brand_header()

mode = st.session_state.get("mode", "worker")


# ─────────────────────────────────────────────
# 작업자 모드는 접근 불가 (관리자 전용 페이지)
# ─────────────────────────────────────────────
if mode == "worker":
    st.markdown("# SCM 인사이트")
    render_page_subtitle("SCM REASONING · ADMIN-ONLY")
    st.markdown("")
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border-left:4px solid {COLORS["accent_gold"]};border-radius:6px;'
        f'padding:24px;margin-top:20px;">'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:18px;'
        f'font-weight:700;color:{COLORS["text_primary"]};margin-bottom:8px;">'
        f'🔒 관리자 전용 페이지</div>'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};'
        f'line-height:1.7;">'
        f'SCM 인사이트 페이지는 30일 누적 데이터를 기반으로 시스템 효과와 '
        f'개선 권고를 분석합니다. 좌측 사이드바에서 <strong>📊 관리자 모드</strong>로 '
        f'전환해주세요.'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ═════════════════════════════════════════════
# 관리자 모드 — 본 페이지
# ═════════════════════════════════════════════

# 페이지 제목
st.markdown("# SCM 인사이트")
render_page_subtitle("SCM REASONING · 30-DAY PATTERN ANALYSIS · CLAUDE-POWERED")


# ─────────────────────────────────────────────
# 데이터 로드
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/inspection_history.csv")
    df["inspected_at"] = pd.to_datetime(df["inspected_at"])
    return df


@st.cache_data
def get_insights(_df_hash: int):
    """캐싱을 위해 데이터프레임 해시 기반"""
    df = load_data()
    return extract_all_insights(df), compute_top_kpis(df)


df = load_data()
df_hash = hash(tuple(df.columns)) + len(df)
insights, kpis = get_insights(df_hash)


# ─────────────────────────────────────────────
# Section 0: SCM 이론적 프레임워크 (PPT와 일관성)
# ─────────────────────────────────────────────
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["accent_gold"]};letter-spacing:0.08em;'
    f'text-transform:uppercase;margin-bottom:10px;">'
    f'SECTION 0 · SCM THEORETICAL FRAMEWORK ⭐</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div style="background:{COLORS["bg_panel"]};'
    f'border-left:4px solid {COLORS["accent_gold"]};border-radius:6px;'
    f'padding:20px 24px;margin-bottom:18px;">'
    f'<div style="font-family:\'Noto Serif KR\',serif;font-size:17px;'
    f'font-weight:700;color:{COLORS["text_primary"]};margin-bottom:8px;">'
    f'📚 본 시스템이 충족시키는 4개 SCM 이론</div>'
    f'<div style="font-size:13px;color:{COLORS["text_secondary"]};line-height:1.7;">'
    f'본 시스템(AI Vision 검수 + Dual-Unit Tracking)은 SCM 분야의 '
    f'<strong style="color:{COLORS["accent_gold"]};">4개 핵심 이론</strong>의 전제 조건을 '
    f'동시에 충족시킵니다. 단순한 시스템 구현이 아닌, 학술적 기반 위의 솔루션입니다.'
    f'</div></div>',
    unsafe_allow_html=True,
)

# 4개 SCM 이론 카드 (2x2 그리드)
theory_col1, theory_col2 = st.columns(2)

theories = [
    {
        "col": theory_col1,
        "title": "재고관리 (Inventory Management)",
        "subtitle": "EOQ · Safety Stock · Reorder Point",
        "body": "재고의 정확성은 EOQ(경제적 주문량), Safety Stock, Reorder Point 등 모든 재고 관리 모델의 전제 조건이다.",
        "link": "정확한 재고 = 모든 재고 모델의 전제조건",
        "color": COLORS["accent_cobalt"],
    },
    {
        "col": theory_col2,
        "title": "IRI (Inventory Record Inaccuracy)",
        "subtitle": "DeHoratius & Raman (2008)",
        "body": "전통적 재고 시스템에서 평균 65%의 부정확성이 관찰되며, 이는 매장 단위 운영 결정의 정확도를 훼손한다.",
        "link": f"본 시스템: 65% → {kpis['iri_rate_pct']:.2f}% ({65 - kpis['iri_rate_pct']:.1f}%p 개선)",
        "color": COLORS["status_warning"],
    },
    {
        "col": theory_col1,
        "title": "Bullwhip Effect (채찍효과)",
        "subtitle": "Lee, Padmanabhan & Whang (1997)",
        "body": "공급망 상류로 갈수록 수요 변동성이 증폭되는 현상. 4대 원인 중 정보 왜곡과 재고 부정확성이 핵심.",
        "link": "① 정보 왜곡 + ④ 재고 부정확성 동시 차단",
        "color": COLORS["accent_gold"],
    },
    {
        "col": theory_col2,
        "title": "JIT · VMI · Information Visibility",
        "subtitle": "Ohno · Lee & Whang",
        "body": "JIT, VMI 같은 advanced SCM 기법은 모두 정확한 재고 데이터를 전제로 한다. 정보 가시성이 SCM 성과의 핵심.",
        "link": "Advanced SCM 기법의 기반 인프라 제공",
        "color": COLORS["status_ok"],
    },
]

for t in theories:
    with t["col"]:
        st.markdown(
            f'<div style="background:{COLORS["bg_panel"]};'
            f'border:1px solid {COLORS["border_subtle"]};'
            f'border-left:3px solid {t["color"]};border-radius:6px;'
            f'padding:16px 20px;margin-bottom:12px;height:175px;">'
            # 제목
            f'<div style="font-family:\'Noto Serif KR\',serif;font-size:15px;'
            f'font-weight:700;color:{t["color"]};margin-bottom:4px;line-height:1.3;">'
            f'{t["title"]}</div>'
            # 출처/모델
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["text_muted"]};letter-spacing:0.05em;margin-bottom:10px;">'
            f'{t["subtitle"]}</div>'
            # 본문
            f'<div style="font-size:12px;line-height:1.6;color:{COLORS["text_secondary"]};'
            f'margin-bottom:10px;">{t["body"]}</div>'
            # 본 시스템 연결
            f'<div style="background:{COLORS["bg_deep"]};border-radius:4px;'
            f'padding:8px 12px;font-family:\'IBM Plex Mono\',monospace;'
            f'font-size:11px;color:{t["color"]};line-height:1.4;">'
            f'▸ {t["link"]}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# Section 1: 상단 KPI - 시스템 효과 요약
# ─────────────────────────────────────────────
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;'
    f'text-transform:uppercase;margin-bottom:10px;margin-top:24px;">'
    f'SECTION 1 · SYSTEM IMPACT SUMMARY</div>',
    unsafe_allow_html=True,
)


def kpi_card(col, label, value, unit, sub, sub_color, accent):
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:1px solid {COLORS["border_subtle"]};border-radius:6px;'
        f'padding:16px 18px;position:relative;overflow:hidden;height:120px;">'
        f'<div style="position:absolute;top:0;left:0;width:3px;height:100%;'
        f'background:{accent};"></div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;'
        f'text-transform:uppercase;margin-bottom:8px;">{label}</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:28px;'
        f'font-weight:700;color:{COLORS["text_primary"]};'
        f'letter-spacing:-0.02em;line-height:1.1;">'
        f'{value}<span style="font-size:14px;color:{COLORS["text_tertiary"]};'
        f'font-weight:400;margin-left:3px;">{unit}</span></div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{sub_color};margin-top:8px;letter-spacing:0.03em;">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


k1, k2, k3, k4 = st.columns(4)
kpi_card(k1, "30일 누적 검수", f"{kpis['total_inspections']:,}", "건",
         "All P-Box 100% scanning", COLORS["status_ok"], COLORS["accent_cobalt"])
kpi_card(k2, "비전 검수 정확도", f"{kpis['accuracy_pct']:.2f}", "%",
         "IRI 차단 검증", COLORS["status_ok"], COLORS["accent_gold"])
kpi_card(k3, "출고 차단 NG", f"{kpis['ng_blocked']}", "건",
         f"IRI Rate {kpis['iri_rate_pct']:.2f}%", COLORS["status_warning"], COLORS["status_warning"])
kpi_card(k4, "추정 클레임 절감", f"{kpis['estimated_savings_krw']//10000}", "만원",
         "30일 누적 추정", COLORS["status_ok"], COLORS["status_ok"])


# ─────────────────────────────────────────────
# Section 2: Claude SCM Reasoning - 자동 추출 인사이트
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["accent_gold"]};letter-spacing:0.08em;'
    f'text-transform:uppercase;margin-top:32px;margin-bottom:10px;">'
    f'SECTION 2 · CLAUDE SCM REASONING ⭐</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div style="background:{COLORS["bg_panel"]};'
    f'border-left:4px solid {COLORS["accent_gold"]};border-radius:6px;'
    f'padding:20px 24px;margin-bottom:18px;">'
    f'<div style="font-family:\'Noto Serif KR\',serif;font-size:16px;'
    f'font-weight:700;color:{COLORS["text_primary"]};margin-bottom:6px;">'
    f'🧠 Claude가 30일 데이터에서 발견한 패턴</div>'
    f'<div style="font-size:13px;color:{COLORS["text_secondary"]};'
    f'line-height:1.7;">'
    f'검수 이력 {kpis["total_inspections"]:,}건을 분석하여 자동으로 추출된 '
    f'<strong style="color:{COLORS["accent_gold"]};">{len(insights)}개의 인사이트</strong>입니다. '
    f'각 카드는 데이터에서 발견한 사실(Finding), 그 의미(Reasoning), 권고 조치(Recommendation)로 '
    f'구성됩니다.'
    f'</div></div>',
    unsafe_allow_html=True,
)


# 인사이트 카드 렌더링
SEVERITY_COLORS = {
    "high": COLORS["status_warning"],
    "medium": COLORS["accent_gold"],
    "low": COLORS["status_ok"],
}
SEVERITY_LABELS = {
    "high": "🚨 HIGH PRIORITY",
    "medium": "⚠️ MEDIUM PRIORITY",
    "low": "✅ INFO",
}
CATEGORY_LABELS = {
    "ANOMALY": "이상 패턴 탐지",
    "TREND": "추세 변화",
    "EFFECT": "시스템 효과",
    "RECOMMENDATION": "권고 사항",
}


for ins in insights:
    sev_color = SEVERITY_COLORS.get(ins.severity, COLORS["text_secondary"])
    sev_label = SEVERITY_LABELS.get(ins.severity, ins.severity.upper())
    cat_label = CATEGORY_LABELS.get(ins.category, ins.category)

    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:1px solid {COLORS["border_subtle"]};'
        f'border-left:4px solid {sev_color};border-radius:6px;'
        f'padding:20px 24px;margin-bottom:14px;">'

        f'<div style="display:grid;grid-template-columns:1fr auto;'
        f'gap:20px;align-items:start;">'

        # 좌측: 텍스트 영역
        f'<div>'
        # 상단 라벨
        f'<div style="display:flex;gap:12px;align-items:center;margin-bottom:10px;">'
        f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{sev_color};letter-spacing:0.08em;font-weight:700;">'
        f'#{ins.rank} · {sev_label}</span>'
        f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
        f'color:{COLORS["text_muted"]};letter-spacing:0.05em;'
        f'padding:2px 8px;background:{COLORS["bg_deep"]};border-radius:3px;">'
        f'{cat_label}</span>'
        f'</div>'

        # 타이틀
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:18px;'
        f'font-weight:700;color:{COLORS["text_primary"]};margin-bottom:14px;'
        f'letter-spacing:-0.02em;">{ins.title}</div>'

        # Finding
        f'<div style="margin-bottom:12px;">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
        f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;'
        f'margin-bottom:4px;">▸ FINDING (발견 사실)</div>'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};'
        f'line-height:1.6;">{ins.finding}</div>'
        f'</div>'

        # Reasoning
        f'<div style="margin-bottom:12px;">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
        f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;'
        f'margin-bottom:4px;">▸ REASONING (해석)</div>'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};'
        f'line-height:1.6;">{ins.reasoning}</div>'
        f'</div>'

        # Recommendation
        f'<div style="margin-top:14px;padding-top:12px;'
        f'border-top:1px solid {COLORS["border_subtle"]};">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
        f'color:{sev_color};letter-spacing:0.08em;margin-bottom:4px;'
        f'font-weight:700;">▸ RECOMMENDATION (권고)</div>'
        f'<div style="font-size:13px;color:{COLORS["text_primary"]};'
        f'line-height:1.6;font-weight:500;">{ins.recommendation}</div>'
        f'</div>'

        f'</div>'  # 좌측 끝

        # 우측: 강조 수치 카드
        f'<div style="background:{COLORS["bg_deep"]};border-radius:6px;'
        f'padding:18px 22px;text-align:center;min-width:160px;'
        f'border:1px solid {sev_color};">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
        f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;'
        f'text-transform:uppercase;margin-bottom:6px;">METRIC</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:32px;'
        f'font-weight:900;color:{sev_color};line-height:1;'
        f'letter-spacing:-0.04em;">{ins.metric_value}</div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["text_secondary"]};margin-top:6px;'
        f'letter-spacing:0.03em;">{ins.metric_label}</div>'
        f'</div>'  # 우측 끝

        f'</div></div>',  # grid + card 끝
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Section 3: 학술 이론 연결 - 채찍효과 (D13에서 시각화 보강 예정)
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;'
    f'text-transform:uppercase;margin-top:32px;margin-bottom:10px;">'
    f'SECTION 3 · THEORETICAL FOUNDATION</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div style="background:{COLORS["bg_panel"]};'
    f'border:1px solid {COLORS["border_subtle"]};border-radius:6px;'
    f'padding:24px;">'

    f'<div style="font-family:\'Noto Serif KR\',serif;font-size:17px;'
    f'font-weight:700;color:{COLORS["text_primary"]};margin-bottom:14px;">'
    f'📚 채찍효과(Bullwhip Effect) 차단 메커니즘</div>'

    f'<div style="font-size:13px;line-height:1.85;color:{COLORS["text_secondary"]};'
    f'margin-bottom:18px;">'
    f'Lee, Padmanabhan & Whang(1997)은 공급망에서 정보가 상류로 전달될수록 '
    f'수요 변동성이 증폭되는 현상을 <strong style="color:{COLORS["text_primary"]};">'
    f'채찍효과</strong>로 정의했다. '
    f'그 네 가지 원인 중 본 시스템이 직접 차단하는 것은 '
    f'<strong style="color:{COLORS["accent_gold"]};">①정보 왜곡(Demand Signal Processing)</strong>과 '
    f'<strong style="color:{COLORS["accent_gold"]};">④재고 부정확성(Inventory Inaccuracy)</strong>이다.'
    f'</div>'

    f'<div style="background:{COLORS["bg_deep"]};padding:18px;border-radius:6px;'
    f'font-family:\'IBM Plex Mono\',monospace;font-size:12px;line-height:1.9;'
    f'color:{COLORS["text_secondary"]};">'
    f'<div style="color:{COLORS["accent_gold"]};margin-bottom:10px;'
    f'font-weight:700;">[차단 메커니즘]</div>'
    f'<div>① <span style="color:{COLORS["accent_cobalt"]};">단위 변환 게이트</span>에서 '
    f'비전 검수 → P-Box(Case)와 개별 단위(EA) 동시 추적</div>'
    f'<div>② <span style="color:{COLORS["accent_gold"]};">실시간 WMS 통합</span> → '
    f'재고 부정확성 차단 (IRI Rate {kpis["iri_rate_pct"]:.2f}%)</div>'
    f'<div>③ 정확한 수요 신호 → 발주 예측 정확도 향상</div>'
    f'<div>④ 채찍효과의 <span style="color:{COLORS["status_ok"]};">미시적 시작점 제거</span></div>'
    f'</div>'

    f'<div style="margin-top:14px;font-size:11px;color:{COLORS["text_tertiary"]};'
    f'font-style:italic;">'
    f'※ 참고: Lee, H. L., Padmanabhan, V., & Whang, S. (1997). '
    f'Information distortion in a supply chain: The bullwhip effect. '
    f'<em>Management Science, 43(4), 546-558.</em>'
    f'</div>'

    f'</div>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# Section 3.5: 채찍효과 차단 메커니즘 다이어그램 (SVG)
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;'
    f'text-transform:uppercase;margin-top:24px;margin-bottom:10px;">'
    f'SECTION 3.5 · INTERCEPTION ARCHITECTURE</div>',
    unsafe_allow_html=True,
)

# 흐름도: 생산 → 검수 게이트 → WMS → 매장 (Streamlit 네이티브)
flow_col1, flow_arrow1, flow_col2, flow_arrow2, flow_col3, flow_arrow3, flow_col4 = st.columns([1.2, 0.2, 1.8, 0.2, 1.2, 0.2, 1.2])

with flow_col1:
    st.markdown(
        f'<div style="background:{COLORS["bg_elevated"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-radius:6px;padding:16px;text-align:center;height:140px;">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
        f'color:{COLORS["text_muted"]};letter-spacing:0.08em;">STAGE 1</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:16px;font-weight:700;'
        f'color:{COLORS["text_primary"]};margin:8px 0;">생산동</div>'
        f'<div style="font-size:11px;color:{COLORS["text_tertiary"]};">P-Box 적재</div>'
        f'</div>', unsafe_allow_html=True)

with flow_arrow1:
    st.markdown(f'<div style="text-align:center;padding-top:55px;font-size:20px;'
        f'color:{COLORS["text_muted"]};">→</div>', unsafe_allow_html=True)

with flow_col2:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:2.5px solid {COLORS["accent_gold"]};'
        f'border-radius:8px;padding:16px;text-align:center;height:140px;">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;font-weight:700;'
        f'color:{COLORS["accent_gold"]};letter-spacing:0.08em;">★ INTERCEPTION POINT ★</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:16px;font-weight:900;'
        f'color:{COLORS["text_primary"]};margin:6px 0;">비전 검수 게이트</div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;font-weight:700;'
        f'color:{COLORS["accent_gold"]};">CASE × EA 동시 추적</div>'
        f'<div style="font-size:10px;color:{COLORS["text_tertiary"]};margin-top:4px;">'
        f'정확도 {kpis["accuracy_pct"]:.2f}% · NG 차단 {kpis["ng_blocked"]}건</div>'
        f'</div>', unsafe_allow_html=True)

with flow_arrow2:
    st.markdown(f'<div style="text-align:center;padding-top:45px;">'
        f'<div style="font-size:20px;color:{COLORS["status_ok"]};">→</div>'
        f'<div style="font-size:9px;color:{COLORS["status_ok"]};">OK</div>'
        f'</div>', unsafe_allow_html=True)

with flow_col3:
    st.markdown(
        f'<div style="background:{COLORS["bg_elevated"]};border:1px solid {COLORS["accent_cobalt"]};'
        f'border-radius:6px;padding:16px;text-align:center;height:140px;">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
        f'color:{COLORS["accent_cobalt"]};letter-spacing:0.08em;">STAGE 3</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:16px;font-weight:700;'
        f'color:{COLORS["text_primary"]};margin:8px 0;">WMS 통합</div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["accent_cobalt"]};">Dual-Unit Tracking</div>'
        f'</div>', unsafe_allow_html=True)

with flow_arrow3:
    st.markdown(f'<div style="text-align:center;padding-top:55px;font-size:20px;'
        f'color:{COLORS["text_muted"]};">→</div>', unsafe_allow_html=True)

with flow_col4:
    st.markdown(
        f'<div style="background:{COLORS["bg_elevated"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-radius:6px;padding:16px;text-align:center;height:140px;">'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
        f'color:{COLORS["text_muted"]};letter-spacing:0.08em;">STAGE 4</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:16px;font-weight:700;'
        f'color:{COLORS["text_primary"]};margin:8px 0;">매장 · 대리점</div>'
        f'<div style="font-size:10px;color:{COLORS["text_tertiary"]};">정확한 재고 = 정확한 발주</div>'
        f'</div>', unsafe_allow_html=True)

# 하단 설명
st.markdown(
    f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
    f'border-radius:6px;padding:16px 20px;margin-top:12px;text-align:center;">'
    f'<span style="color:{COLORS["accent_gold"]};font-weight:700;">단위 변환 지점</span>'
    f'(개별 단위 → 박스 단위)에 디지털 게이트를 설치하여, '
    f'<span style="color:{COLORS["text_primary"]};font-weight:700;">정보 손실(IRI)</span>을 원천 차단합니다. '
    f'이는 채찍효과의 <span style="color:{COLORS["status_ok"]};font-weight:700;">'
    f'미시적 시작점에서의 개입</span>입니다.'
    f'</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Section 3.6: 30일 검수 정확도 추세 차트
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;'
    f'text-transform:uppercase;margin-top:24px;margin-bottom:10px;">'
    f'SECTION 3.6 · 30-DAY ACCURACY STABILITY</div>',
    unsafe_allow_html=True,
)

# 일자별 NG율 계산
daily_stats = df.copy()
daily_stats["date"] = daily_stats["inspected_at"].dt.date
daily_stats["is_ng"] = daily_stats["verdict"] != "OK"

daily_agg = daily_stats.groupby("date").agg(
    total=("crate_id", "count"),
    ng=("is_ng", "sum"),
).reset_index()
daily_agg["ng_rate"] = (daily_agg["ng"] / daily_agg["total"] * 100).round(2)
daily_agg["date"] = pd.to_datetime(daily_agg["date"])

avg_ng_rate = daily_agg["ng_rate"].mean()

# 컨테이너 헤더
st.markdown(
    f'<div style="background:{COLORS["bg_elevated"]};padding:13px 18px;'
    f'border:1px solid {COLORS["border_subtle"]};border-bottom:none;'
    f'border-radius:6px 6px 0 0;">'
    f'<div style="font-family:\'Noto Serif KR\',serif;font-size:13px;'
    f'font-weight:700;color:{COLORS["text_primary"]};">'
    f'일자별 NG 검출률 추세</div>'
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.05em;margin-top:2px;">'
    f'30D NG RATE · AVERAGE LINE OVERLAID</div></div>',
    unsafe_allow_html=True,
)

# 추세 차트 (Altair)
bar_chart = alt.Chart(daily_agg).mark_bar(
    color=COLORS["accent_cobalt"],
    opacity=0.85,
).encode(
    x=alt.X("date:T", title="날짜",
            axis=alt.Axis(
                labelColor=COLORS["text_tertiary"],
                titleColor=COLORS["text_tertiary"],
                domainColor=COLORS["border_subtle"],
                gridColor=COLORS["border_subtle"],
                format="%m-%d",
            )),
    y=alt.Y("ng_rate:Q", title="NG율 (%)",
            axis=alt.Axis(
                labelColor=COLORS["text_tertiary"],
                titleColor=COLORS["text_tertiary"],
                domainColor=COLORS["border_subtle"],
                gridColor=COLORS["border_subtle"],
            )),
    tooltip=[
        alt.Tooltip("date:T", title="날짜", format="%m-%d"),
        alt.Tooltip("ng_rate:Q", title="NG율(%)"),
        alt.Tooltip("total:Q", title="총 검수"),
        alt.Tooltip("ng:Q", title="NG"),
    ],
)

# 평균선 추가
avg_line = alt.Chart(pd.DataFrame({"avg": [avg_ng_rate]})).mark_rule(
    color=COLORS["accent_gold"],
    strokeWidth=2,
    strokeDash=[6, 4],
).encode(
    y="avg:Q",
)

# 평균선 라벨
avg_label = alt.Chart(pd.DataFrame({
    "avg": [avg_ng_rate],
    "label": [f"평균 {avg_ng_rate:.2f}%"],
})).mark_text(
    color=COLORS["accent_gold"],
    fontSize=11,
    align="left",
    dx=5,
    dy=-8,
).encode(
    y="avg:Q",
    text="label:N",
)

trend_chart = (bar_chart + avg_line + avg_label).properties(
    height=240,
    background=COLORS["bg_panel"],
).configure_view(stroke=COLORS["border_subtle"])

st.altair_chart(trend_chart, use_container_width=True)

# 차트 하단 인사이트
trend_insight_html = (
    f'<div style="background:{COLORS["bg_panel"]};'
    f'border:1px solid {COLORS["border_subtle"]};border-top:none;'
    f'border-radius:0 0 6px 6px;padding:14px 18px;'
    f'font-size:12px;color:{COLORS["text_tertiary"]};">'
    f'💡 30일간 NG율은 평균 {avg_ng_rate:.2f}%, 표준편차 {daily_agg["ng_rate"].std():.2f}%로 '
    f'<strong style="color:{COLORS["status_ok"]};">안정적 운영</strong>을 유지하고 있습니다. '
    f'주말(검수 건수 감소 구간)에도 시스템 동작이 일관됨을 확인할 수 있습니다.'
    f'</div>'
)
st.markdown(trend_insight_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Section 4: 시스템 도입 효과 (Before/After 추정)
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;'
    f'text-transform:uppercase;margin-top:24px;margin-bottom:10px;">'
    f'SECTION 4 · ESTIMATED IMPACT (BEFORE vs AFTER)</div>',
    unsafe_allow_html=True,
)

# 학술 인용 기반 추정치
# DeHoratius & Raman (2008): RFID·바코드 기반에서도 65% 부정확
# 우리 시스템: NG 차단 → 사실상 0%에 가까운 IRI

dehoratius_iri = 65.0  # 학술 인용
our_iri = kpis["iri_rate_pct"]  # 우리 시스템 실측
improvement = dehoratius_iri - our_iri

before_after_html = f'''
<div style="background:{COLORS["bg_panel"]};
            border:1px solid {COLORS["border_subtle"]};border-radius:6px;
            padding:24px;">

    <div style="display:grid;grid-template-columns:1fr 80px 1fr;gap:18px;align-items:center;">

        
        <div style="background:{COLORS["bg_deep"]};border-radius:6px;
                    padding:24px;border-left:4px solid {COLORS["status_warning"]};">
            <div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;
                        color:{COLORS["status_warning"]};letter-spacing:0.08em;
                        margin-bottom:8px;">BEFORE · 전통적 시스템</div>
            <div style="font-family:\'Noto Serif KR\',serif;font-size:42px;
                        font-weight:900;color:{COLORS["status_warning"]};
                        line-height:1;letter-spacing:-0.04em;">
                65<span style="font-size:24px;">%</span>
            </div>
            <div style="font-size:12px;color:{COLORS["text_tertiary"]};
                        margin-top:8px;">IRI Rate (재고 부정확성)</div>
            <div style="font-size:11px;color:{COLORS["text_muted"]};
                        margin-top:12px;font-style:italic;line-height:1.5;">
                DeHoratius &amp; Raman (2008)이 측정한 RFID·바코드 기반<br>
                재고 시스템의 평균 부정확성 수준
            </div>
        </div>

        
        <div style="text-align:center;font-size:32px;color:{COLORS["accent_gold"]};">→</div>

        
        <div style="background:{COLORS["bg_deep"]};border-radius:6px;
                    padding:24px;border-left:4px solid {COLORS["status_ok"]};">
            <div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;
                        color:{COLORS["status_ok"]};letter-spacing:0.08em;
                        margin-bottom:8px;">AFTER · 본 시스템 (실측)</div>
            <div style="font-family:\'Noto Serif KR\',serif;font-size:42px;
                        font-weight:900;color:{COLORS["status_ok"]};
                        line-height:1;letter-spacing:-0.04em;">
                {our_iri:.2f}<span style="font-size:24px;">%</span>
            </div>
            <div style="font-size:12px;color:{COLORS["text_tertiary"]};
                        margin-top:8px;">IRI Rate (실측)</div>
            <div style="font-size:11px;color:{COLORS["text_muted"]};
                        margin-top:12px;font-style:italic;line-height:1.5;">
                30일 누적 {kpis["total_inspections"]:,}건 검수 기준<br>
                AI 비전 + Dual-Unit Tracking
            </div>
        </div>
    </div>

    
    <div style="margin-top:24px;background:linear-gradient(135deg,
                {COLORS["bg_deep"]}, {COLORS["bg_panel"]});
                border-radius:6px;padding:20px;text-align:center;
                border:1px solid {COLORS["accent_gold_dim"]};">
        <div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;
                    color:{COLORS["accent_gold"]};letter-spacing:0.08em;
                    margin-bottom:8px;">★ ESTIMATED IMPROVEMENT</div>
        <div style="font-family:\'Noto Serif KR\',serif;font-size:32px;
                    font-weight:900;color:{COLORS["accent_gold"]};
                    line-height:1;">
            {improvement:.1f}<span style="font-size:20px;">%p 개선</span>
        </div>
        <div style="font-size:12px;color:{COLORS["text_secondary"]};
                    margin-top:10px;line-height:1.7;max-width:680px;
                    margin-left:auto;margin-right:auto;">
            전통적 재고 시스템 대비 정보 정확성 <strong style="color:{COLORS["accent_gold"]};">{improvement:.1f}%p 개선</strong>은 
            매장 단위 재고 신뢰도 회복 → 발주 정확도 향상 → 
            <strong style="color:{COLORS["status_ok"]};">채찍효과 차단</strong>으로 이어집니다.
        </div>
    </div>

    
    <div style="margin-top:18px;font-size:10px;color:{COLORS["text_muted"]};
                font-style:italic;line-height:1.6;">
        ※ DeHoratius, N., &amp; Raman, A. (2008). Inventory record inaccuracy: 
        An empirical analysis. <em>Management Science, 54(4), 627-641.</em><br>
        ※ 본 비교는 본 시스템의 실측 데이터를 학술 인용 수치와 대조한 것이며, 
        실제 운영 환경에서는 다양한 변수(SKU 다양성, 매장 규모)에 따라 결과가 달라질 수 있습니다.
    </div>
</div>
'''
st.markdown(before_after_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Section 5: 향후 권고 사항 (Roadmap)
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;'
    f'text-transform:uppercase;margin-top:32px;margin-bottom:10px;">'
    f'SECTION 5 · ROADMAP &amp; FUTURE WORK</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div style="background:{COLORS["bg_panel"]};'
    f'border-left:4px solid {COLORS["accent_cobalt"]};border-radius:6px;'
    f'padding:20px 24px;margin-bottom:18px;">'
    f'<div style="font-family:\'Noto Serif KR\',serif;font-size:16px;'
    f'font-weight:700;color:{COLORS["text_primary"]};margin-bottom:6px;">'
    f'🛣 본 프로토타입의 후속 확장 방향</div>'
    f'<div style="font-size:13px;color:{COLORS["text_secondary"]};line-height:1.7;">'
    f'본 시스템은 30일 데이터 기반의 검증된 프로토타입입니다. 운영 환경 전환 시 '
    f'다음 세 가지 확장이 자연스러운 다음 단계입니다.'
    f'</div></div>',
    unsafe_allow_html=True,
)

# 3개 권고 카드
rec_col1, rec_col2, rec_col3 = st.columns(3)

recommendations = [
    {
        "col": rec_col1,
        "num": "01",
        "icon": "⚡",
        "title": "하이브리드 비전 구조",
        "subtitle": "YOLO + Vision LLM",
        "body": (
            "현재는 Vision LLM 단독 구조이나, 컨베이어 풀스피드 환경에서는 "
            "<strong>YOLO를 1차 필터로, Vision LLM을 NG 후보 정밀 분석에</strong> 활용하는 "
            "하이브리드 구조가 적합합니다. 추론 속도와 SKU 확장성을 동시에 확보합니다."
        ),
        "link_text": "▸ 자세한 비교는 [5. 기술 선택 논거] 페이지 참조",
        "accent": COLORS["accent_gold"],
    },
    {
        "col": rec_col2,
        "num": "02",
        "icon": "📦",
        "title": "SKU 동적 확장",
        "subtitle": "Registry-Based Onboarding",
        "body": (
            "현재 2종 SKU(햄버거번·식빵)로 검증된 시스템은 "
            "<strong>SkuRegistry 모듈을 통해 신규 SKU를 라벨 텍스트만으로 즉시 등록</strong>할 수 있도록 설계되었습니다. "
            "식품 제조 현장의 신제품 출시 주기에 대응 가능합니다."
        ),
        "link_text": "▸ 신규 SKU = 라벨 텍스트 등록 + 시각적 특징 기술",
        "accent": COLORS["accent_cobalt"],
    },
    {
        "col": rec_col3,
        "num": "03",
        "icon": "🏭",
        "title": "다공장 확장",
        "subtitle": "Multi-Site Deployment",
        "body": (
            "현재는 수원공장 중심이나, 사이드바의 <strong>SITE 토글로 부산공장 등 "
            "추가 공장이 즉시 연결</strong>되는 구조입니다. 공장별 검수 데이터를 통합하면 "
            "전사 차원의 SCM 인사이트 추출이 가능합니다."
        ),
        "link_text": "▸ 사이드바 SITE 선택으로 즉시 전환 가능",
        "accent": COLORS["status_ok"],
    },
]

for r in recommendations:
    with r["col"]:
        st.markdown(
            f'<div style="background:{COLORS["bg_panel"]};'
            f'border:1px solid {COLORS["border_subtle"]};border-radius:6px;'
            f'padding:24px;height:340px;display:flex;flex-direction:column;">'

            # 상단: 번호 + 아이콘
            f'<div style="display:flex;justify-content:space-between;'
            f'align-items:flex-start;margin-bottom:14px;">'
            f'<div style="font-family:\'Noto Serif KR\',serif;font-size:32px;'
            f'font-weight:900;color:{r["accent"]};line-height:1;'
            f'letter-spacing:-0.04em;">{r["num"]}</div>'
            f'<div style="font-size:28px;">{r["icon"]}</div>'
            f'</div>'

            # 타이틀
            f'<div style="font-family:\'Noto Serif KR\',serif;font-size:17px;'
            f'font-weight:700;color:{COLORS["text_primary"]};line-height:1.3;">'
            f'{r["title"]}</div>'

            # 서브타이틀
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{r["accent"]};letter-spacing:0.08em;margin-top:4px;'
            f'margin-bottom:12px;">{r["subtitle"]}</div>'

            # 본문
            f'<div style="font-size:12px;line-height:1.7;'
            f'color:{COLORS["text_secondary"]};flex-grow:1;">'
            f'{r["body"]}</div>'

            # 링크/참조
            f'<div style="margin-top:14px;padding-top:12px;'
            f'border-top:1px solid {COLORS["border_subtle"]};'
            f'font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{r["accent"]};line-height:1.5;">'
            f'{r["link_text"]}</div>'

            f'</div>',
            unsafe_allow_html=True,
        )

# 마무리 선언문
st.markdown("")
st.markdown(
    f'<div style="background:linear-gradient(135deg,'
    f'{COLORS["bg_deep"]},{COLORS["bg_panel"]});'
    f'border:1px solid {COLORS["accent_gold_dim"]};border-radius:6px;'
    f'padding:28px;margin-top:18px;text-align:center;">'

    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["accent_gold"]};letter-spacing:0.12em;'
    f'margin-bottom:14px;">★ CLOSING STATEMENT</div>'

    f'<div style="font-family:\'Noto Serif KR\',serif;font-size:20px;'
    f'font-weight:700;color:{COLORS["text_primary"]};line-height:1.5;'
    f'letter-spacing:-0.02em;max-width:780px;'
    f'margin-left:auto;margin-right:auto;">'
    f'단위 변환 지점에 디지털 게이트를 설치하라.<br>'
    f'<span style="color:{COLORS["accent_gold"]};">정확한 데이터는 정확한 의사결정으로,</span><br>'
    f'정확한 의사결정은 채찍효과 차단으로 이어진다.'
    f'</div>'

    f'<div style="margin-top:18px;font-size:12px;'
    f'color:{COLORS["text_tertiary"]};line-height:1.7;'
    f'max-width:680px;margin-left:auto;margin-right:auto;">'
    f'본 프로토타입은 식품 제조 공장의 출고 검수 시점에 '
    f'<strong style="color:{COLORS["text_secondary"]};">Dual-Unit Tracking</strong>과 '
    f'<strong style="color:{COLORS["text_secondary"]};">AI 비전 검수</strong>를 결합하여, '
    f'정보 손실의 미시적 시작점을 차단하는 SCM 솔루션을 제시합니다.'
    f'</div>'

    f'</div>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# 푸터
# ─────────────────────────────────────────────
st.markdown("")
st.markdown(
    f'<div style="text-align:center;margin-top:48px;padding-top:24px;'
    f'border-top:1px solid {COLORS["border_subtle"]};'
    f'font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_muted"]};letter-spacing:0.08em;">'
    f'SCM CAPSTONE · INCHEON NATIONAL UNIVERSITY · GRADUATE SCHOOL OF LOGISTICS<br>'
    f'<span style="color:{COLORS["accent_gold"]};">POWERED BY CLAUDE</span> · '
    f'30D INSPECTION DATA · {len(insights)} AUTO-GENERATED INSIGHTS'
    f'</div>',
    unsafe_allow_html=True,
)
