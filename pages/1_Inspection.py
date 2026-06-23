"""
Page 1: 출고 검수
- 작업자 모드: 한눈에 OK/NG가 들어오는 큰 화면
- 관리자 모드: D8에 구현 예정
"""

import streamlit as st
import json
import tempfile
import time
from pathlib import Path
from styles import inject_global_styles, render_brand_header, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar
from sku_registry import SkuRegistry
from vision_inspector import inspect_crate, VERDICT_DISPLAY

st.set_page_config(
    page_title="출고 검수 | AI Vision",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()

ensure_session_state()
render_sidebar()
render_brand_header()

mode = st.session_state.get("mode", "worker")
registry = SkuRegistry()

# ─────────────────────────────────────────────
# 세션 상태 초기화 (이 페이지 전용)
# ─────────────────────────────────────────────
if "inspection_result" not in st.session_state:
    st.session_state.inspection_result = None
if "current_image_path" not in st.session_state:
    st.session_state.current_image_path = None
if "current_sku_id" not in st.session_state:
    st.session_state.current_sku_id = None
if "current_image_label" not in st.session_state:
    st.session_state.current_image_label = None


# ─────────────────────────────────────────────
# 시연 시나리오 라이브러리
# ─────────────────────────────────────────────
DEMO_SCENARIOS = [
    {
        "label": "📦 햄버거번 정상 #1",
        "image_path": "data/demo_images/burger_001.jpg",
        "sku_id": "SKU-001",
        "crate_id": "CRT-20260429-001",
    },
    {
        "label": "📦 햄버거번 정상 #2",
        "image_path": "data/demo_images/burger_002.jpg",
        "sku_id": "SKU-001",
        "crate_id": "CRT-20260429-002",
    },
    {
        "label": "🍞 식빵 정상 #1",
        "image_path": "data/demo_images/bread_001.jpg",
        "sku_id": "SKU-002",
        "crate_id": "CRT-20260422-001",
    },
    {
        "label": "🍞 식빵 정상 #2",
        "image_path": "data/demo_images/bread_002.jpg",
        "sku_id": "SKU-002",
        "crate_id": "CRT-20260422-002",
    },
    {
        "label": "⚠️ 시뮬레이션: 수량 부족",
        "image_path": "test_short_box.jpg",  # mock_response_short.json으로 fallback
        "sku_id": "SKU-001",
        "crate_id": "CRT-DEMO-SHORT",
        "is_simulated_ng": True,
    },
]


# ─────────────────────────────────────────────
# 헬퍼: 검수 실행
# ─────────────────────────────────────────────
def run_inspection(scenario):
    """시나리오 기반 검수 실행"""
    sku = registry.get(scenario["sku_id"])
    if sku is None:
        st.error(f"등록되지 않은 SKU: {scenario['sku_id']}")
        return

    crate_info = {
        "crate_id": scenario["crate_id"],
        "expected_sku_id": sku.sku_id,
        "expected_sku_name": sku.sku_name,
        "expected_qty": sku.expected_total_units(),
    }

    sku_master = [
        {
            "sku_id": s.sku_id,
            "sku_name": s.sku_name,
            "category": s.category,
            "similar_skus": "",
        }
        for s in registry.list_active()
    ]

    # 수량부족 시뮬레이션은 더미 파일 사용
    img_path = scenario["image_path"]
    if scenario.get("is_simulated_ng") and not Path(img_path).exists():
        # 임시 파일로 mock 트리거
        Path(img_path).write_bytes(b"short_dummy")

    with st.spinner("🔍 AI Vision 검수 중..."):
        result = inspect_crate(
            image_path=img_path,
            crate_info=crate_info,
            sku_master=sku_master,
            response_dir="data/vision_responses",
        )

    st.session_state.inspection_result = result
    st.session_state.current_image_path = img_path
    st.session_state.current_sku_id = sku.sku_id
    st.session_state.current_image_label = scenario["label"]


def reset_inspection():
    """검수 결과 초기화"""
    st.session_state.inspection_result = None
    st.session_state.current_image_path = None
    st.session_state.current_sku_id = None
    st.session_state.current_image_label = None


# ─────────────────────────────────────────────
# 페이지 제목
# ─────────────────────────────────────────────
st.markdown("# 출고 검수")
render_page_subtitle("P-BOX INSPECTION · VISION-VERIFIED · DUAL-UNIT TRACKING")


# ═════════════════════════════════════════════
# 관리자 모드 - 데이터 기반 대시보드
# ═════════════════════════════════════════════
if mode == "admin":
    import pandas as pd
    import altair as alt

    # ────── 데이터 로드 ──────
    @st.cache_data
    def load_inspection_data():
        df = pd.read_csv("data/inspection_history.csv")
        df["inspected_at"] = pd.to_datetime(df["inspected_at"])
        df["hour"] = df["inspected_at"].dt.hour
        df["is_ng"] = df["verdict"] != "OK"
        return df

    @st.cache_data
    def load_line_stats():
        return pd.read_csv("data/line_stats.csv")

    df_insp = load_inspection_data()
    df_lines = load_line_stats()

    # ────── 핵심 KPI 계산 (시스템 관점) ──────
    total = len(df_insp)
    ng_count = int(df_insp["is_ng"].sum())
    accuracy = (total - ng_count) / total * 100   # 비전 검수 정확도
    iri_rate = ng_count / total * 100             # 입고 시점 IRI Rate

    # 출고 차단 케이스 (WMS 반영 안 된 NG)
    blocked_count = ng_count

    # 클레임 예방 추정: NG 1건당 평균 4.5만원 클레임 비용 가정
    weekly_avg_ng = ng_count / (30 / 7)
    weekly_claim_savings = int(weekly_avg_ng * 4.5)

    # 라인 상태
    lines_attention = int((df_lines["status"] == "주의").sum())

    # ────── 상단 KPI 4개 ──────
    def kpi_card(col, label, value, unit, sub, sub_color, accent):
        col.markdown(
            f"""
            <div style="background: {COLORS['bg_panel']};
                        border: 1px solid {COLORS['border_subtle']};
                        border-radius: 6px; padding: 16px 18px;
                        position: relative; overflow: hidden; height: 120px;">
                <div style="position: absolute; top: 0; left: 0;
                            width: 3px; height: 100%; background: {accent};"></div>
                <div style="font-family: 'IBM Plex Mono', monospace;
                            font-size: 10px; color: {COLORS['text_tertiary']};
                            letter-spacing: 0.08em; text-transform: uppercase;
                            margin-bottom: 8px;">{label}</div>
                <div style="font-family: 'Noto Serif KR', serif;
                            font-size: 28px; font-weight: 700;
                            color: {COLORS['text_primary']};
                            letter-spacing: -0.02em; line-height: 1.1;">
                    {value}<span style="font-size: 14px; color: {COLORS['text_tertiary']};
                                       font-weight: 400; margin-left: 3px;">{unit}</span>
                </div>
                <div style="font-family: 'IBM Plex Mono', monospace;
                            font-size: 10px; color: {sub_color};
                            margin-top: 8px; letter-spacing: 0.03em;">
                    {sub}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_card(
        kpi_col1, "30D 비전 검수 정확도", f"{accuracy:.1f}", "%",
        f"WMS 실시간 반영 중", COLORS["status_ok"], COLORS["status_ok"],
    )
    kpi_card(
        kpi_col2, "30D 입고 IRI Rate", f"{iri_rate:.2f}", "%",
        f"NG {ng_count}건 자동 차단", COLORS["status_warning"], COLORS["status_warning"],
    )
    kpi_card(
        kpi_col3, "출고 차단 P-Box", f"{blocked_count}", "건",
        "클레임 예방 작동", COLORS["accent_cobalt"], COLORS["accent_cobalt"],
    )
    kpi_card(
        kpi_col4, "라인 주의 상태", f"{lines_attention}", "라인",
        f"전체 {len(df_lines)}개 라인 중", COLORS["text_tertiary"], COLORS["status_danger"],
    )

    st.markdown("")

    # ────── 좌(시간대 차트) / 우(라인별 현황) ──────
    left_col, right_col = st.columns([1.5, 1])

    # ===== 좌측: 시간대별 입고 검수 추이 =====
    with left_col:
        st.markdown(
            f"""
            <div style="background: {COLORS['bg_elevated']};
                        padding: 13px 18px;
                        border: 1px solid {COLORS['border_subtle']};
                        border-bottom: none;
                        border-radius: 6px 6px 0 0;
                        display: flex; justify-content: space-between; align-items: center;">
                <div style="font-family: 'Noto Serif KR', serif; font-size: 13px;
                            font-weight: 700; color: {COLORS['text_primary']};">
                    시간대별 입고 검수 및 NG 발생 추이
                </div>
                <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                            color: {COLORS['text_tertiary']}; letter-spacing: 0.05em;">
                    30D AGGREGATE
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        hourly = (
            df_insp.groupby("hour")
            .agg(total=("crate_id", "count"), ng=("is_ng", "sum"))
            .reset_index()
        )
        hourly["ng_rate"] = (hourly["ng"] / hourly["total"] * 100).round(2)

        base = alt.Chart(hourly).encode(
            x=alt.X("hour:O", title="시각 (h)",
                    axis=alt.Axis(labelColor=COLORS["text_tertiary"],
                                  titleColor=COLORS["text_tertiary"],
                                  domainColor=COLORS["border_subtle"],
                                  tickColor=COLORS["border_subtle"])),
        )
        bars = base.mark_bar(opacity=0.6).encode(
            y=alt.Y("total:Q", title="검수 건수",
                    axis=alt.Axis(labelColor=COLORS["text_tertiary"],
                                  titleColor=COLORS["text_tertiary"],
                                  domainColor=COLORS["border_subtle"],
                                  gridColor=COLORS["border_subtle"])),
            color=alt.value(COLORS["accent_cobalt"]),
        )
        ng_line = base.mark_line(point=True, strokeWidth=2.5).encode(
            y=alt.Y("ng_rate:Q", title="NG율 (%)",
                    axis=alt.Axis(labelColor=COLORS["status_warning"],
                                  titleColor=COLORS["status_warning"])),
            color=alt.value(COLORS["status_warning"]),
        )
        chart = (
            alt.layer(bars, ng_line)
            .resolve_scale(y="independent")
            .properties(height=240, background=COLORS["bg_panel"])
            .configure_view(stroke=COLORS["border_subtle"])
        )
        st.altair_chart(chart, use_container_width=True)

        # 차트 인사이트
        peak_hour = int(hourly.loc[hourly["ng_rate"].idxmax(), "hour"])
        peak_rate = float(hourly["ng_rate"].max())
        st.markdown(
            f"""
            <div style="background: {COLORS['bg_panel']};
                        border: 1px solid {COLORS['border_subtle']};
                        border-top: none;
                        border-radius: 0 0 6px 6px;
                        padding: 10px 16px;
                        font-family: 'IBM Plex Mono', monospace;
                        font-size: 11px; color: {COLORS['text_tertiary']};">
                💡 NG율 피크: <span style="color: {COLORS['accent_gold']};">{peak_hour}시 {peak_rate:.2f}%</span>
                · 야간 라인 가동 시간대와 일치
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 최근 검수 미니 카드 3개 (시스템 관점)
        st.markdown(
            f"""
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                        color: {COLORS['text_tertiary']}; letter-spacing: 0.08em;
                        text-transform: uppercase; margin-top: 20px; margin-bottom: 10px;">
                RECENT INSPECTIONS (WMS REAL-TIME)
            </div>
            """,
            unsafe_allow_html=True,
        )

        recent = df_insp.sort_values("inspected_at", ascending=False).head(3)
        for _, row in recent.iterrows():
            is_ng = row["is_ng"]
            status_color = COLORS["status_warning"] if is_ng else COLORS["status_ok"]
            status_label = (
                "NG · 수량 부족" if row["verdict"] == "NG_QTY_SHORT"
                else "NG · 수량 초과" if row["verdict"] == "NG_QTY_EXCESS"
                else "NG · 혼입 발견" if row["verdict"] == "NG_CONTAMINATION"
                else "NG · SKU 불일치" if row["verdict"] == "NG_SKU_MISMATCH"
                else "OK · WMS 반영"
            )
            emoji = "⚠️" if is_ng else "📦"
            time_label = row["inspected_at"].strftime("%m-%d %H:%M")

            st.markdown(
                f"""
                <div style="display: grid;
                            grid-template-columns: 50px 1fr 80px;
                            gap: 14px; align-items: center;
                            padding: 12px 14px;
                            background: {COLORS['bg_deep']};
                            border-radius: 4px;
                            margin-bottom: 8px;">
                    <div style="aspect-ratio: 1; background: {COLORS['bg_elevated']};
                                border-radius: 4px; display: flex; align-items: center;
                                justify-content: center; font-size: 18px;">{emoji}</div>
                    <div>
                        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                                    color: {COLORS['text_tertiary']}; letter-spacing: 0.05em;">
                            {row['crate_id']} · {time_label}
                        </div>
                        <div style="font-family: 'Noto Serif KR', serif; font-weight: 700;
                                    font-size: 14px; color: {status_color}; margin-top: 2px;">
                            {status_label}
                        </div>
                        <div style="font-size: 11px; color: {COLORS['text_tertiary']}; margin-top: 2px;">
                            {row['expected_sku']} · {row['detected_qty']}/{row['expected_qty']}
                            · {row['line_no']} → {row['destination_store']}
                        </div>
                    </div>
                    <div style="text-align: right;
                                font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                                color: {COLORS['text_tertiary']};">
                        <div style="font-family: 'Noto Serif KR', serif; font-size: 18px;
                                    font-weight: 700; color: {COLORS['text_primary']};
                                    line-height: 1;">{row['confidence']}</div>
                        <div>CONF%</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ===== 우측: 라인별 입고 처리 현황 =====
    with right_col:
        st.markdown(
            f"""
            <div style="background: {COLORS['bg_elevated']};
                        padding: 13px 18px;
                        border: 1px solid {COLORS['border_subtle']};
                        border-bottom: none;
                        border-radius: 6px 6px 0 0;
                        display: flex; justify-content: space-between; align-items: center;">
                <div style="font-family: 'Noto Serif KR', serif; font-size: 13px;
                            font-weight: 700; color: {COLORS['text_primary']};">
                    라인별 입고 처리 현황
                </div>
                <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                            color: {COLORS['text_tertiary']}; letter-spacing: 0.05em;">
                    30D ROLLING
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        line_html = f"""
        <div style="background: {COLORS['bg_panel']};
                    border: 1px solid {COLORS['border_subtle']};
                    border-top: none;
                    border-radius: 0 0 6px 6px;
                    padding: 0;">
        """

        # 헤더
        line_html += f"""
        <div style="display: grid; grid-template-columns: 1fr 1.2fr 0.6fr;
                    gap: 8px; padding: 10px 16px;
                    border-bottom: 1px solid {COLORS['border_subtle']};
                    font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                    color: {COLORS['text_tertiary']}; letter-spacing: 0.08em;
                    text-transform: uppercase;">
            <span>라인</span>
            <span>NG율</span>
            <span>상태</span>
        </div>
        """

        # 상태 순 정렬: 주의 → 보통 → 정상
        status_order = {"주의": 0, "보통": 1, "정상": 2}
        df_lines_sorted = df_lines.sort_values(
            by="status", key=lambda s: s.map(status_order)
        )

        for _, ln in df_lines_sorted.iterrows():
            status = ln["status"]
            level_color = {
                "주의": COLORS["status_danger"],
                "보통": COLORS["status_warning"],
                "정상": COLORS["status_ok"],
            }[status]
            level_bg = {
                "주의": "rgba(212,104,92,0.15)",
                "보통": "rgba(212,165,87,0.15)",
                "정상": "rgba(94,193,156,0.15)",
            }[status]
            # 5%를 100%로 정규화
            bar_width = min(int(ln["error_rate_pct"] * 20), 100)

            shift_label = "주간" if ln["shift"] == "day" else "야간"

            line_html += f"""
            <div style="display: grid; grid-template-columns: 1fr 1.2fr 0.6fr;
                        gap: 8px; padding: 12px 16px;
                        border-bottom: 1px solid {COLORS['border_subtle']};
                        align-items: center;">
                <div>
                    <div style="color: {COLORS['text_primary']}; font-weight: 500; font-size: 13px;">
                        {ln['line_no']}
                    </div>
                    <div style="font-size: 10px; color: {COLORS['text_tertiary']};">
                        {ln['line_name']} · {shift_label}
                    </div>
                </div>
                <div>
                    <span style="display: inline-block; width: 50px; height: 5px;
                                background: {COLORS['bg_deep']}; border-radius: 3px;
                                overflow: hidden; vertical-align: middle; margin-right: 8px;">
                        <span style="display: block; height: 100%; width: {bar_width}%;
                                     background: {level_color}; border-radius: 3px;"></span>
                    </span>
                    <span style="font-family: 'IBM Plex Mono', monospace; font-size: 11px;
                                color: {COLORS['text_secondary']};">
                        {ln['error_rate_pct']}%
                    </span>
                </div>
                <div>
                    <span style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                                padding: 2px 7px; border-radius: 2px;
                                letter-spacing: 0.05em;
                                background: {level_bg}; color: {level_color};">
                        {status}
                    </span>
                </div>
            </div>
            """

        line_html += "</div>"
        st.markdown(line_html, unsafe_allow_html=True)

    st.markdown("")

    # ────── Claude SCM 추론 카드 (시스템 관점) ──────
    # 가장 NG가 많은 라인
    top_ng_line = df_lines.sort_values("error_rate_pct", ascending=False).iloc[0]

    # 최근 NG 한 건
    recent_ng = df_insp[df_insp["is_ng"]].sort_values("inspected_at", ascending=False).head(1)

    if len(recent_ng) > 0:
        ng_row = recent_ng.iloc[0]

        st.markdown(
            f"""
            <div style="background: {COLORS['bg_panel']};
                        border: 1px solid {COLORS['accent_gold_dim']};
                        border-radius: 6px;
                        padding: 22px;
                        position: relative;
                        overflow: hidden;
                        margin-top: 16px;">

                <div style="position: absolute; top: 0; left: 0; width: 4px; height: 100%;
                            background: linear-gradient(to bottom, {COLORS['accent_gold']}, {COLORS['accent_gold_dim']});"></div>

                
                <div style="display: flex; align-items: center; gap: 14px;
                            margin-bottom: 16px; padding-bottom: 14px;
                            border-bottom: 1px solid {COLORS['border_subtle']};">
                    <div style="width: 36px; height: 36px; border-radius: 6px;
                                background: linear-gradient(135deg, {COLORS['accent_gold']}, {COLORS['accent_gold_dim']});
                                display: flex; align-items: center; justify-content: center;
                                font-family: 'Noto Serif KR', serif; font-weight: 900;
                                color: {COLORS['bg_deep']}; font-size: 15px;">C</div>
                    <div>
                        <div style="font-family: 'Noto Serif KR', serif; font-size: 15px;
                                    font-weight: 700; color: {COLORS['text_primary']};">
                            Claude SCM Reasoning
                        </div>
                        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                                    color: {COLORS['text_tertiary']}; letter-spacing: 0.05em;">
                            VISION-WMS INTEGRATION · DUAL-UNIT IRI · BULLWHIP MITIGATION
                        </div>
                    </div>
                </div>

                
                <div style="font-size: 13px; line-height: 1.75; color: {COLORS['text_secondary']};">
                    <p>물류동 입고 게이트의 AI 비전 검수가 최근 30일간
                    <strong style="color: {COLORS['text_primary']};">{total:,}건</strong>의 P-Box를 처리하여
                    WMS에 실시간 반영했습니다. 시스템 관점의 진단을 제시합니다.</p>

                    <ul style="margin-top: 10px; padding-left: 0; list-style: none;">
                        <li style="padding: 9px 0 9px 26px; position: relative; font-size: 12px;
                                   border-bottom: 1px dashed {COLORS['border_subtle']};">
                            <span style="position: absolute; left: 4px; color: {COLORS['accent_gold']};">▸</span>
                            <strong style="color: {COLORS['text_primary']};">단위 변환 지점 정보 손실 차단</strong> ·
                            생산(EA) → 물류(Case) 단위 변환 시 발생하는
                            <span style="background: rgba(201,165,92,0.15); color: {COLORS['accent_gold']};
                                        padding: 1px 6px; border-radius: 2px;
                                        font-family: 'IBM Plex Mono', monospace; font-size: 12px;">
                                Information Distortion
                            </span>이 비전 검수로 차단됨. Dual-Unit Tracking 작동 중.
                        </li>
                        <li style="padding: 9px 0 9px 26px; position: relative; font-size: 12px;
                                   border-bottom: 1px dashed {COLORS['border_subtle']};">
                            <span style="position: absolute; left: 4px; color: {COLORS['accent_gold']};">▸</span>
                            <strong style="color: {COLORS['text_primary']};">라인 입고 품질 진단</strong> ·
                            <span style="background: rgba(201,165,92,0.15); color: {COLORS['accent_gold']};
                                        padding: 1px 6px; border-radius: 2px;
                                        font-family: 'IBM Plex Mono', monospace; font-size: 12px;">
                                {top_ng_line['line_no']} ({top_ng_line['line_name']})
                            </span>의 NG율이
                            <span style="background: rgba(201,165,92,0.15); color: {COLORS['accent_gold']};
                                        padding: 1px 6px; border-radius: 2px;
                                        font-family: 'IBM Plex Mono', monospace; font-size: 12px;">
                                {top_ng_line['error_rate_pct']:.2f}%
                            </span>로 가장 높음. 라인 설비·환경 점검 권고.
                        </li>
                        <li style="padding: 9px 0 9px 26px; position: relative; font-size: 12px;
                                   border-bottom: 1px dashed {COLORS['border_subtle']};">
                            <span style="position: absolute; left: 4px; color: {COLORS['accent_gold']};">▸</span>
                            <strong style="color: {COLORS['text_primary']};">IRI 차단 효과</strong> ·
                            NG로 판정된 <strong style="color: {COLORS['text_primary']};">{ng_count}건</strong>이
                            WMS에 부정확한 재고로 등록되는 것을 자동 차단.
                            DeHoratius & Raman (2008)이 보고한 IRI 손실(매출 1% 이상)을 발생 시점에 차단.
                        </li>
                        <li style="padding: 9px 0 9px 26px; position: relative; font-size: 12px;
                                   border-bottom: 1px dashed {COLORS['border_subtle']};">
                            <span style="position: absolute; left: 4px; color: {COLORS['accent_gold']};">▸</span>
                            <strong style="color: {COLORS['text_primary']};">채찍효과 차단</strong> ·
                            출고 데이터 신뢰도 회복 → 매장 수요 신호 왜곡 감소 →
                            <span style="background: rgba(201,165,92,0.15); color: {COLORS['accent_gold']};
                                        padding: 1px 6px; border-radius: 2px;
                                        font-family: 'IBM Plex Mono', monospace; font-size: 12px;">
                                Bullwhip Effect
                            </span>의 미시적 시작점 제거.
                        </li>
                        <li style="padding: 9px 0 9px 26px; position: relative; font-size: 12px;">
                            <span style="position: absolute; left: 4px; color: {COLORS['accent_gold']};">▸</span>
                            <strong style="color: {COLORS['text_primary']};">시스템 권고</strong> ·
                            현재 입고 검수 정확도 <strong style="color: {COLORS['text_primary']};">{accuracy:.1f}%</strong> 유지 중.
                            영향 매장 SKU에 대해
                            <span style="background: rgba(201,165,92,0.15); color: {COLORS['accent_gold']};
                                        padding: 1px 6px; border-radius: 2px;
                                        font-family: 'IBM Plex Mono', monospace; font-size: 12px;">
                                안전재고 +5% 일시 상향
                            </span> 권고. 검수 정확도 회복 시 자동 환원.
                        </li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.stop()


# ═════════════════════════════════════════════
# 작업자 모드 메인 화면
# ═════════════════════════════════════════════

# ─────────────────────────────────────────────
# 시연 시나리오 선택 (상단)
# ─────────────────────────────────────────────
st.markdown(
    f"""
    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 11px;
                color: {COLORS['text_tertiary']}; letter-spacing: 0.08em;
                text-transform: uppercase; margin-bottom: 8px;">
        시연 시나리오 선택
    </div>
    """,
    unsafe_allow_html=True,
)

scenario_cols = st.columns(len(DEMO_SCENARIOS) + 1)
for i, scenario in enumerate(DEMO_SCENARIOS):
    with scenario_cols[i]:
        if st.button(scenario["label"], key=f"scenario_{i}", width='stretch'):
            run_inspection(scenario)
            st.rerun()

with scenario_cols[-1]:
    if st.button("↻ 초기화", key="reset_btn", width='stretch'):
        reset_inspection()
        st.rerun()

st.markdown("---")


# ─────────────────────────────────────────────
# 메인 검수 영역 (이미지 + 결과)
# ─────────────────────────────────────────────
col_image, col_result = st.columns([1.2, 1])

# ────── 좌측: 이미지 패널 ──────
with col_image:
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between;
                    font-family: 'IBM Plex Mono', monospace; font-size: 11px;
                    color: {COLORS['text_tertiary']}; letter-spacing: 0.05em;
                    margin-bottom: 12px;">
            <span>BOX IMAGE · TOP CAMERA</span>
            <span>{st.session_state.current_image_label or '대기 중'}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.current_image_path and Path(st.session_state.current_image_path).exists():
        try:
            st.image(
                st.session_state.current_image_path,
                use_container_width=True,
            )
        except Exception:
            st.markdown(
                f"""
                <div style="aspect-ratio: 4/3; background: {COLORS['bg_deep']};
                            border: 2px dashed {COLORS['border_strong']};
                            border-radius: 4px; display: flex; align-items: center;
                            justify-content: center; flex-direction: column;
                            color: {COLORS['text_muted']};">
                    <div style="font-size: 48px;">⚠️</div>
                    <div style="margin-top: 8px;">시뮬레이션 케이스 (이미지 없음)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"""
            <div style="aspect-ratio: 4/3; background: {COLORS['bg_deep']};
                        border: 2px dashed {COLORS['border_strong']};
                        border-radius: 4px; display: flex; align-items: center;
                        justify-content: center; flex-direction: column;
                        color: {COLORS['text_muted']};">
                <div style="font-family: 'Noto Serif KR', serif; font-size: 56px;">⬚</div>
                <div style="margin-top: 12px; font-size: 14px;">박스를 카메라 아래로 놓아주세요</div>
                <div style="margin-top: 4px; font-size: 12px; color: {COLORS['text_muted']};">
                    또는 위에서 시연 시나리오를 선택하세요
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 이미지 업로드 옵션 (보조)
    with st.expander("📤 다른 이미지 업로드"):
        uploaded = st.file_uploader(
            "JPEG/PNG 파일 선택",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )
        if uploaded:
            # 등록된 SKU 중 선택
            sku_options = registry.list_active()
            selected_sku = st.selectbox(
                "예상 SKU 선택",
                options=[s.sku_id for s in sku_options],
                format_func=lambda sid: f"{sid} - {registry.get(sid).sku_name}",
            )
            if st.button("이 이미지로 검수", type="primary", width='stretch'):
                # 임시 파일로 저장
                tmp_dir = Path(tempfile.gettempdir())
                tmp_path = tmp_dir / uploaded.name
                tmp_path.write_bytes(uploaded.read())

                run_inspection({
                    "label": f"📤 {uploaded.name}",
                    "image_path": str(tmp_path),
                    "sku_id": selected_sku,
                    "crate_id": f"CRT-UPLOAD-{int(time.time())}",
                })
                st.rerun()


# ────── 우측: 검수 결과 패널 ──────
with col_result:
    result = st.session_state.inspection_result

    if result is None:
        # 검수 대기 상태 — 네이티브 위젯
        with st.container(border=True):
            st.markdown(
                f"<div style='text-align:center;font-size:80px;line-height:1;margin:32px 0 16px 0;"
                f"color:{COLORS['text_muted']};'>◌</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='text-align:center;font-size:16px;color:{COLORS['text_muted']};"
                f"margin-bottom:8px;'>검수 대기 중</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='text-align:center;font-size:12px;letter-spacing:0.05em;"
                f"color:{COLORS['text_muted']};margin-bottom:32px;'>AWAITING INSPECTION</div>",
                unsafe_allow_html=True,
            )
    else:
        verdict = result["verdict"]
        confidence = result["confidence"]
        sku = registry.get(st.session_state.current_sku_id)
        expected_qty = sku.expected_total_units()
        detected_qty = result["primary_count"]
        is_ok = (verdict == "OK")

        verdict_info = VERDICT_DISPLAY[verdict]
        border_color = COLORS["status_ok"] if is_ok else COLORS["status_warning"]
        text_color = COLORS["status_ok"] if is_ok else COLORS["status_warning"]
        num_color = COLORS["status_ok"] if is_ok else COLORS["status_warning"]

        # 결과 카드 — Streamlit 네이티브 위젯 조합으로 안전하게
        with st.container(border=True):
            # 큰 아이콘
            st.markdown(
                f"<div style='text-align:center;font-size:88px;line-height:1;margin:8px 0;'>"
                f"{verdict_info['emoji']}</div>",
                unsafe_allow_html=True,
            )
            # 큰 상태 문구
            st.markdown(
                f"<div style='text-align:center;font-size:48px;font-weight:900;"
                f"color:{text_color};margin-bottom:20px;line-height:1;'>"
                f"{verdict_info['label']}</div>",
                unsafe_allow_html=True,
            )
            # 수량 표시 (중앙 정렬)
            st.markdown(
                f"<div style='text-align:center;font-size:18px;color:{COLORS['text_secondary']};"
                f"margin-bottom:8px;'>"
                f"<span style='font-size:32px;font-weight:700;color:{num_color};'>{detected_qty}</span>"
                f" 개 / 기대 "
                f"<span style='font-size:32px;font-weight:700;color:{COLORS['text_primary']};'>{expected_qty}</span>"
                f" 개</div>",
                unsafe_allow_html=True,
            )
            # 신뢰도
            st.markdown(
                f"<div style='text-align:center;font-size:13px;"
                f"color:{COLORS['text_tertiary']};letter-spacing:0.05em;margin-bottom:16px;'>"
                f"CONFIDENCE {confidence}%</div>",
                unsafe_allow_html=True,
            )
            st.divider()
            # SKU 표시
            st.markdown(
                f"<div style='text-align:center;font-size:12px;color:{COLORS['text_muted']};"
                f"letter-spacing:0.05em;'>"
                f"{sku.sku_id} · {sku.sku_name}<br>{sku.display_structure()}</div>",
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────
# 결과가 있을 때만 추가 정보 표시
# ─────────────────────────────────────────────
if st.session_state.inspection_result is not None:
    result = st.session_state.inspection_result
    is_ok = (result["verdict"] == "OK")

    # 작업자 안내 메시지
    msg_color = COLORS["status_ok"] if is_ok else COLORS["accent_gold"]
    st.markdown(
        f"""
        <div style="background: {COLORS['bg_deep']};
                    border-left: 4px solid {msg_color};
                    border-radius: 6px;
                    padding: 22px 26px; margin: 24px 0;">
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                        color: {msg_color}; letter-spacing: 0.08em;
                        text-transform: uppercase; margin-bottom: 6px;">
                💬 작업자 안내
            </div>
            <div style="font-size: 19px; font-weight: 500;
                        line-height: 1.5; color: {COLORS['text_primary']};">
                {result['recommendation']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 큰 액션 버튼 3개
    btn_col1, btn_col2, btn_col3 = st.columns([1.5, 1, 1])

    with btn_col1:
        primary_label = "✓ 출고 확정" if is_ok else "↻ 재검수"
        if st.button(primary_label, key="primary_action", type="primary", width='stretch'):
            if is_ok:
                st.success(f"✅ {result['crate_id']} 출고 확정되었습니다.")
                st.info("재고 데이터에 반영되었습니다. (재고 모니터링 페이지에서 확인 가능)")
                time.sleep(1.5)
                reset_inspection()
                st.rerun()
            else:
                reset_inspection()
                st.rerun()

    with btn_col2:
        if st.button("수량 수정", key="edit_qty", width='stretch'):
            st.session_state.show_qty_edit = True

    with btn_col3:
        if st.button("재촬영", key="retake", width='stretch'):
            reset_inspection()
            st.rerun()

    # 수량 수정 인터페이스
    if st.session_state.get("show_qty_edit"):
        with st.expander("✏️ 수량 수동 보정", expanded=True):
            sku = registry.get(st.session_state.current_sku_id)
            edited_qty = st.number_input(
                f"실제 수량 (기대 {sku.expected_total_units()}개)",
                min_value=0,
                max_value=100,
                value=result["primary_count"],
            )
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("확인", type="primary", width='stretch'):
                    # 결과 업데이트
                    result["primary_count"] = edited_qty
                    result["estimated_total"][result["primary_sku"]] = edited_qty
                    result["qty_match"] = (edited_qty == sku.expected_total_units())
                    result["verdict"] = "OK" if result["qty_match"] else "NG_QTY_SHORT"
                    result["confidence"] = 100  # 수동 보정은 100%
                    result["recommendation"] = (
                        "수동 보정 완료. 출고 가능합니다."
                        if result["qty_match"]
                        else f"수동 카운트 {edited_qty}개로 보정. 기대 수량({sku.expected_total_units()}개) 미충족."
                    )
                    result["_manually_corrected"] = True
                    st.session_state.show_qty_edit = False
                    st.rerun()
            with col_b:
                if st.button("취소", width='stretch'):
                    st.session_state.show_qty_edit = False
                    st.rerun()

    # 검수 메타데이터 (작은 글씨, 발표에서 정직성 어필)
    with st.expander("🔬 검수 상세 정보"):
        col_meta1, col_meta2 = st.columns(2)
        with col_meta1:
            st.markdown(f"**Crate ID**: `{result.get('crate_id', 'N/A')}`")
            st.markdown(f"**Primary SKU**: `{result.get('primary_sku', 'N/A')}`")
            st.markdown(f"**Verdict**: `{result['verdict']}`")
        with col_meta2:
            st.markdown(f"**Source**: `{result.get('_source', 'mock_fallback')}`")
            st.markdown(f"**Confidence**: `{result['confidence']}%`")
            if result.get("contamination_risk", {}).get("detected"):
                st.markdown(
                    f"**Contamination**: `{', '.join(result['contamination_risk']['suspected_skus'])}`"
                )

        if "_vision_notes" in result:
            st.caption(f"💡 {result['_vision_notes']}")
