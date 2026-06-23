"""
Page 2: 재고 모니터링
- 비전 검수가 완료된 P-Box들이 WMS에 어떻게 쌓여있는지 표시
- 핵심 컨셉: Dual-Unit Tracking (Case + EA 동시 표시)
- 작업자 모드: 단순한 현황 / 관리자 모드: 상세 분석 추가
"""

import streamlit as st
import pandas as pd
import altair as alt
from styles import inject_global_styles, render_brand_header, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar
from sku_registry import SkuRegistry

st.set_page_config(
    page_title="재고 모니터링 | AI Vision",
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
# 데이터 로드
# ─────────────────────────────────────────────
@st.cache_data
def load_inspection_data():
    df = pd.read_csv("data/inspection_history.csv")
    df["inspected_at"] = pd.to_datetime(df["inspected_at"])
    df["is_ng"] = df["verdict"] != "OK"
    return df


df_insp = load_inspection_data()

# ─────────────────────────────────────────────
# 가상 출고 상태 부여
# 실제로는 별도 DB 컬럼이지만, 시뮬레이션상 시간 기준으로 매핑:
#   - 최근 7일치 OK 박스 중 60%: 출고 대기 (in_stock)
#   - 그 외 OK 박스: 출고 완료 (dispatched)
#   - NG 박스: 출고 차단 (blocked)
# ─────────────────────────────────────────────
latest_date = df_insp["inspected_at"].max()
cutoff = latest_date - pd.Timedelta(days=7)

# 결정론적 상태 부여 (seed 효과)
import hashlib

def assign_status(row):
    if row["is_ng"]:
        return "blocked"
    if row["inspected_at"] < cutoff:
        return "dispatched"
    # 최근 7일 OK 박스: crate_id 해시로 결정
    h = int(hashlib.md5(row["crate_id"].encode()).hexdigest()[:4], 16)
    return "in_stock" if (h % 10) < 6 else "dispatched"

df_insp["status"] = df_insp.apply(assign_status, axis=1)


# ─────────────────────────────────────────────
# 페이지 제목
# ─────────────────────────────────────────────
st.markdown("# 재고 모니터링")
render_page_subtitle("INVENTORY DASHBOARD · DUAL-UNIT TRACKING · WMS REAL-TIME")


# ─────────────────────────────────────────────
# 상단 KPI: 시스템 현황 요약
# ─────────────────────────────────────────────
# 출고 대기 (in_stock) P-Box들의 통계
df_stock = df_insp[df_insp["status"] == "in_stock"].copy()
df_dispatched = df_insp[df_insp["status"] == "dispatched"].copy()
df_blocked = df_insp[df_insp["status"] == "blocked"].copy()

total_pbox_stock = len(df_stock)
total_units_stock = int(df_stock["detected_qty"].sum())
total_pbox_dispatched_today = len(df_dispatched[df_dispatched["inspected_at"] >= latest_date.normalize()])
total_blocked = len(df_blocked)


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
                {value:,}<span style="font-size: 14px; color: {COLORS['text_tertiary']};
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


k1, k2, k3, k4 = st.columns(4)
kpi_card(
    k1, "출고 대기 P-Box", total_pbox_stock, "Case",
    "WMS 실시간 반영", COLORS["status_ok"], COLORS["accent_cobalt"],
)
kpi_card(
    k2, "출고 대기 개별 단위", total_units_stock, "EA",
    "Dual-Unit Tracking", COLORS["status_ok"], COLORS["accent_gold"],
)
kpi_card(
    k3, "금일 출고 완료", total_pbox_dispatched_today, "Case",
    "검증된 재고 출고", COLORS["status_ok"], COLORS["status_ok"],
)
kpi_card(
    k4, "출고 차단 (NG)", total_blocked, "Case",
    "30일 누적 자동 차단", COLORS["status_warning"], COLORS["status_warning"],
)


# ─────────────────────────────────────────────
# 핵심 패널: SKU별 재고 (Dual-Unit Tracking 시각화)
# ─────────────────────────────────────────────
st.markdown("")

left_col, right_col = st.columns([1.2, 1])

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
                SKU별 재고 현황 (Dual-Unit)
            </div>
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                        color: {COLORS['text_tertiary']}; letter-spacing: 0.05em;">
                CASE × EA TRACKING
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # SKU별 집계
    sku_summary = df_stock.groupby("expected_sku").agg(
        pbox_count=("crate_id", "count"),
        unit_count=("detected_qty", "sum"),
    ).reset_index()

    # SKU별 카드 — 개별 렌더링 (Streamlit 1.57.0 호환)
    for _, row in sku_summary.iterrows():
        sku = registry.get(row["expected_sku"])
        if sku is None:
            continue
        sku_lines = df_stock[df_stock["expected_sku"] == row["expected_sku"]]["line_no"].nunique()

        with st.container(border=True):
            # SKU 정보 라인
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:baseline;">'
                f'<div>'
                f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
                f'color:{COLORS["text_tertiary"]};letter-spacing:0.05em;">{sku.sku_id}</span>'
                f'<span style="font-family:\'Noto Serif KR\',serif;font-size:16px;font-weight:700;'
                f'color:{COLORS["text_primary"]};margin-left:8px;">{sku.sku_name}</span>'
                f'</div>'
                f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
                f'color:{COLORS["text_tertiary"]};">{sku.display_structure()}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            # Case × EA × Line 그리드
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(
                    f'<div style="text-align:center;">'
                    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
                    f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;">CASE</div>'
                    f'<div style="font-family:\'Noto Serif KR\',serif;font-size:24px;font-weight:700;'
                    f'color:{COLORS["accent_cobalt"]};line-height:1.1;">{row["pbox_count"]}</div>'
                    f'<div style="font-size:9px;color:{COLORS["text_muted"]};">P-Box</div>'
                    f'</div>', unsafe_allow_html=True)
            with m2:
                st.markdown(
                    f'<div style="text-align:center;">'
                    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
                    f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;">EA</div>'
                    f'<div style="font-family:\'Noto Serif KR\',serif;font-size:24px;font-weight:700;'
                    f'color:{COLORS["accent_gold"]};line-height:1.1;">{int(row["unit_count"]):,}</div>'
                    f'<div style="font-size:9px;color:{COLORS["text_muted"]};">개별 단위</div>'
                    f'</div>', unsafe_allow_html=True)
            with m3:
                st.markdown(
                    f'<div style="text-align:center;">'
                    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
                    f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;">LINE</div>'
                    f'<div style="font-family:\'Noto Serif KR\',serif;font-size:24px;font-weight:700;'
                    f'color:{COLORS["text_primary"]};line-height:1.1;">{sku_lines}</div>'
                    f'<div style="font-size:9px;color:{COLORS["text_muted"]};">생산 라인</div>'
                    f'</div>', unsafe_allow_html=True)

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
                매장별 출고 대기
            </div>
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                        color: {COLORS['text_tertiary']}; letter-spacing: 0.05em;">
                PENDING DISPATCH
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 매장별 집계
    store_summary = df_stock.groupby("destination_store").agg(
        pbox=("crate_id", "count"),
        units=("detected_qty", "sum"),
    ).reset_index().sort_values("pbox", ascending=False)

    max_pbox = store_summary["pbox"].max() if len(store_summary) > 0 else 1

    # 매장별 카드 — 개별 렌더링 (Streamlit 1.57.0 호환)
    for _, row in store_summary.iterrows():
        bar_pct = int(row["pbox"] / max_pbox * 100)
        st.markdown(
            f'<div style="display:flex;gap:10px;align-items:center;padding:6px 0;'
            f'border-bottom:1px solid {COLORS["border_subtle"]};">'
            f'<div style="font-size:12px;color:{COLORS["text_secondary"]};min-width:80px;">'
            f'{row["destination_store"]}</div>'
            f'<div style="flex:1;height:5px;background:{COLORS["bg_deep"]};border-radius:3px;overflow:hidden;">'
            f'<div style="height:100%;width:{bar_pct}%;background:{COLORS["accent_cobalt"]};'
            f'border-radius:3px;"></div></div>'
            f'<div style="text-align:right;font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
            f'color:{COLORS["text_secondary"]};min-width:70px;">'
            f'{row["pbox"]}<span style="color:{COLORS["text_tertiary"]};">/{int(row["units"])}EA</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# 작업자 모드는 여기서 마무리, 관리자 모드는 상세 분석 추가
# ─────────────────────────────────────────────
if mode == "worker":
    # 작업자용 단순 안내
    st.markdown("")
    st.info(
        f"💡 현재 출고 대기 중인 P-Box는 **{total_pbox_stock}건** ({total_units_stock:,}개 단위)입니다. "
        f"출고 처리를 진행하려면 [출고 처리] 페이지로 이동하세요."
    )
    st.stop()


# ═════════════════════════════════════════════
# 관리자 모드 — 상세 분석
# ═════════════════════════════════════════════
st.markdown("")
st.markdown(
    f"""
    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                color: {COLORS['text_tertiary']}; letter-spacing: 0.08em;
                text-transform: uppercase; margin-top: 16px; margin-bottom: 10px;">
        ▸ ADMIN-ONLY · DETAILED ANALYSIS
    </div>
    """,
    unsafe_allow_html=True,
)

# ────── 일자별 입고 추이 차트 ──────
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
            일자별 입고 추이 · SKU 구성
        </div>
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                    color: {COLORS['text_tertiary']}; letter-spacing: 0.05em;">
            30D · STACKED BY SKU
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 일자별 + SKU별 검수 건수
daily_sku = df_insp.copy()
daily_sku["date"] = daily_sku["inspected_at"].dt.date
daily_agg = daily_sku.groupby(["date", "expected_sku"]).size().reset_index(name="count")

# 차트
sku_colors = {
    "SKU-001": COLORS["accent_gold"],
    "SKU-002": COLORS["accent_cobalt"],
}

chart = (
    alt.Chart(daily_agg)
    .mark_bar()
    .encode(
        x=alt.X(
            "date:T", title="날짜",
            axis=alt.Axis(
                labelColor=COLORS["text_tertiary"],
                titleColor=COLORS["text_tertiary"],
                domainColor=COLORS["border_subtle"],
                gridColor=COLORS["border_subtle"],
                format="%m-%d",
            ),
        ),
        y=alt.Y(
            "count:Q", title="검수 건수",
            axis=alt.Axis(
                labelColor=COLORS["text_tertiary"],
                titleColor=COLORS["text_tertiary"],
                domainColor=COLORS["border_subtle"],
                gridColor=COLORS["border_subtle"],
            ),
        ),
        color=alt.Color(
            "expected_sku:N",
            scale=alt.Scale(
                domain=list(sku_colors.keys()),
                range=list(sku_colors.values()),
            ),
            legend=alt.Legend(
                title="SKU",
                titleColor=COLORS["text_secondary"],
                labelColor=COLORS["text_secondary"],
                orient="top-right",
            ),
        ),
    )
    .properties(height=220, background=COLORS["bg_panel"])
    .configure_view(stroke=COLORS["border_subtle"])
)

st.altair_chart(chart, use_container_width=True)


# ────── SKU × 매장 매트릭스 + 라인 × SKU 매트릭스 ──────
st.markdown("")
matrix_left, matrix_right = st.columns(2)

# ===== 좌측: SKU × 매장 출고 대기 매트릭스 =====
with matrix_left:
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
                SKU × 매장 출고 대기 매트릭스
            </div>
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                        color: {COLORS['text_tertiary']}; letter-spacing: 0.05em;">
                IN-STOCK · CASE
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # SKU × 매장 피벗 (현재 출고 대기 박스만)
    sku_store_pivot = df_stock.pivot_table(
        index="expected_sku",
        columns="destination_store",
        values="crate_id",
        aggfunc="count",
        fill_value=0,
    ).reset_index().melt(
        id_vars="expected_sku",
        var_name="store",
        value_name="count",
    )

    heatmap = (
        alt.Chart(sku_store_pivot)
        .mark_rect()
        .encode(
            x=alt.X(
                "store:N", title="매장",
                sort=alt.EncodingSortField(field="count", op="sum", order="descending"),
                axis=alt.Axis(
                    labelColor=COLORS["text_tertiary"],
                    titleColor=COLORS["text_tertiary"],
                    domainColor=COLORS["border_subtle"],
                    labelAngle=-30,
                ),
            ),
            y=alt.Y(
                "expected_sku:N", title="SKU",
                axis=alt.Axis(
                    labelColor=COLORS["text_tertiary"],
                    titleColor=COLORS["text_tertiary"],
                    domainColor=COLORS["border_subtle"],
                ),
            ),
            color=alt.Color(
                "count:Q",
                title="박스 수",
                scale=alt.Scale(
                    range=[COLORS["bg_deep"], COLORS["accent_gold"]],
                ),
                legend=alt.Legend(
                    titleColor=COLORS["text_secondary"],
                    labelColor=COLORS["text_secondary"],
                    orient="right",
                ),
            ),
            tooltip=[
                alt.Tooltip("expected_sku:N", title="SKU"),
                alt.Tooltip("store:N", title="매장"),
                alt.Tooltip("count:Q", title="박스"),
            ],
        )
        .properties(height=180, background=COLORS["bg_panel"])
        .configure_view(stroke=COLORS["border_subtle"])
    )

    # 수치 라벨 오버레이
    text = (
        alt.Chart(sku_store_pivot)
        .mark_text(fontSize=12, fontWeight="bold")
        .encode(
            x=alt.X(
                "store:N",
                sort=alt.EncodingSortField(field="count", op="sum", order="descending"),
            ),
            y="expected_sku:N",
            text="count:Q",
            color=alt.condition(
                "datum.count > 25",
                alt.value(COLORS["bg_deep"]),
                alt.value(COLORS["text_secondary"]),
            ),
        )
    )

    combined = (
        alt.layer(heatmap, text)
        .properties(height=180, background=COLORS["bg_panel"])
        .configure_view(stroke=COLORS["border_subtle"])
    )

    st.altair_chart(combined, use_container_width=True)

    # 인사이트
    st.markdown(
        f"""
        <div style="background: {COLORS['bg_panel']};
                    border: 1px solid {COLORS['border_subtle']};
                    border-top: none;
                    border-radius: 0 0 6px 6px;
                    padding: 10px 16px;
                    font-family: 'IBM Plex Mono', monospace;
                    font-size: 11px; color: {COLORS['text_tertiary']};
                    margin-top: -16px;">
            💡 <span style="color: {COLORS['accent_gold']};">SKU-001</span>은 수도권(강남·분당·잠실·홍대) 집중,
            <span style="color: {COLORS['accent_cobalt']};">SKU-002</span>는 외곽(종로·수원·일산) 집중 — 수요 패턴 분화
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===== 우측: 라인 × SKU 생산 매트릭스 =====
with matrix_right:
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
                라인 × SKU 30일 생산 매트릭스
            </div>
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                        color: {COLORS['text_tertiary']}; letter-spacing: 0.05em;">
                30D · CASE
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 라인 × SKU 피벗
    line_sku_pivot = df_insp.pivot_table(
        index="line_no",
        columns="expected_sku",
        values="crate_id",
        aggfunc="count",
        fill_value=0,
    ).reset_index().melt(
        id_vars="line_no",
        var_name="sku",
        value_name="count",
    )

    line_heatmap = (
        alt.Chart(line_sku_pivot)
        .mark_rect()
        .encode(
            x=alt.X(
                "sku:N", title="SKU",
                axis=alt.Axis(
                    labelColor=COLORS["text_tertiary"],
                    titleColor=COLORS["text_tertiary"],
                    domainColor=COLORS["border_subtle"],
                ),
            ),
            y=alt.Y(
                "line_no:N", title="라인",
                axis=alt.Axis(
                    labelColor=COLORS["text_tertiary"],
                    titleColor=COLORS["text_tertiary"],
                    domainColor=COLORS["border_subtle"],
                ),
            ),
            color=alt.Color(
                "count:Q",
                title="박스 수",
                scale=alt.Scale(
                    range=[COLORS["bg_deep"], COLORS["accent_cobalt"]],
                ),
                legend=alt.Legend(
                    titleColor=COLORS["text_secondary"],
                    labelColor=COLORS["text_secondary"],
                    orient="right",
                ),
            ),
            tooltip=[
                alt.Tooltip("line_no:N", title="라인"),
                alt.Tooltip("sku:N", title="SKU"),
                alt.Tooltip("count:Q", title="박스"),
            ],
        )
        .properties(height=180, background=COLORS["bg_panel"])
    )

    # 라인 매트릭스 수치 라벨
    line_text = (
        alt.Chart(line_sku_pivot)
        .mark_text(fontSize=12, fontWeight="bold")
        .encode(
            x="sku:N",
            y="line_no:N",
            text="count:Q",
            color=alt.condition(
                "datum.count > 300",
                alt.value(COLORS["text_primary"]),
                alt.value(COLORS["text_secondary"]),
            ),
        )
    )

    line_combined = (
        alt.layer(line_heatmap, line_text)
        .properties(height=180, background=COLORS["bg_panel"])
        .configure_view(stroke=COLORS["border_subtle"])
    )

    st.altair_chart(line_combined, use_container_width=True)

    st.markdown(
        f"""
        <div style="background: {COLORS['bg_panel']};
                    border: 1px solid {COLORS['border_subtle']};
                    border-top: none;
                    border-radius: 0 0 6px 6px;
                    padding: 10px 16px;
                    font-family: 'IBM Plex Mono', monospace;
                    font-size: 11px; color: {COLORS['text_tertiary']};
                    margin-top: -16px;">
            💡 <span style="color: {COLORS['accent_cobalt']};">LINE-1, 2</span>: SKU-001 전담 |
            <span style="color: {COLORS['accent_gold']};">LINE-5</span>: SKU-002 전담 |
            나머지: 혼합 생산
        </div>
        """,
        unsafe_allow_html=True,
    )


# ────── P-Box 리스트 (필터링) ──────
st.markdown("")
st.markdown(
    f"""
    <div style="font-family: 'Noto Serif KR', serif; font-size: 14px;
                font-weight: 700; color: {COLORS['text_primary']};
                margin-top: 16px; margin-bottom: 12px;">
        📦 P-Box 리스트 (필터링 가능)
    </div>
    """,
    unsafe_allow_html=True,
)

# 필터 옵션
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    status_filter = st.selectbox(
        "상태",
        options=["전체", "출고 대기", "출고 완료", "출고 차단(NG)"],
    )

with filter_col2:
    sku_filter = st.selectbox(
        "SKU",
        options=["전체"] + sorted(df_insp["expected_sku"].unique().tolist()),
    )

with filter_col3:
    line_filter = st.selectbox(
        "라인",
        options=["전체"] + sorted(df_insp["line_no"].unique().tolist()),
    )

with filter_col4:
    store_filter = st.selectbox(
        "매장",
        options=["전체"] + sorted(df_insp["destination_store"].unique().tolist()),
    )

# 필터 적용
filtered = df_insp.copy()
status_map = {
    "출고 대기": "in_stock",
    "출고 완료": "dispatched",
    "출고 차단(NG)": "blocked",
}
if status_filter != "전체":
    filtered = filtered[filtered["status"] == status_map[status_filter]]
if sku_filter != "전체":
    filtered = filtered[filtered["expected_sku"] == sku_filter]
if line_filter != "전체":
    filtered = filtered[filtered["line_no"] == line_filter]
if store_filter != "전체":
    filtered = filtered[filtered["destination_store"] == store_filter]

# 최근 50건만 표시 (성능 + UX)
filtered_display = filtered.sort_values("inspected_at", ascending=False).head(50)


# 상태 라벨 변환
def status_label(s):
    return {
        "in_stock": "🔵 출고 대기",
        "dispatched": "✅ 출고 완료",
        "blocked": "⚠️ 출고 차단",
    }.get(s, s)


display_df = pd.DataFrame({
    "검수 시각": filtered_display["inspected_at"].dt.strftime("%m-%d %H:%M"),
    "Crate ID": filtered_display["crate_id"],
    "라인": filtered_display["line_no"],
    "SKU": filtered_display["expected_sku"],
    "수량 (검출/기대)": filtered_display.apply(
        lambda r: f"{r['detected_qty']} / {r['expected_qty']}", axis=1
    ),
    "매장": filtered_display["destination_store"],
    "신뢰도": filtered_display["confidence"].apply(lambda x: f"{x}%"),
    "상태": filtered_display["status"].apply(status_label),
})

st.markdown(
    f"""
    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 11px;
                color: {COLORS['text_tertiary']}; margin-bottom: 6px;">
        필터링 결과: {len(filtered):,}건 (최근 50건만 표시)
    </div>
    """,
    unsafe_allow_html=True,
)

st.dataframe(
    display_df,
    hide_index=True,
    use_container_width=True,
    height=400,
)


# ────── 출고 차단 케이스 자동 알림 ──────
if total_blocked > 0:
    st.markdown("")
    st.markdown(
        f"""
        <div style="background: {COLORS['bg_panel']};
                    border-left: 4px solid {COLORS['status_warning']};
                    border-radius: 6px;
                    padding: 18px 22px; margin-top: 20px;">
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px;
                        color: {COLORS['status_warning']}; letter-spacing: 0.08em;
                        text-transform: uppercase; margin-bottom: 8px;">
                ⚠️ 시스템 알림 · 출고 차단 케이스
            </div>
            <div style="font-size: 14px; line-height: 1.7; color: {COLORS['text_secondary']};">
                30일간 비전 검수에서 NG로 판정된 <strong style="color: {COLORS['text_primary']};">{total_blocked}건</strong>의
                P-Box가 출고 처리에서 자동 차단되었습니다. 이는 WMS에 부정확한 재고가 등록되는 것을 방지하며,
                <span style="color: {COLORS['accent_gold']};">매장 클레임의 사전 차단 효과</span>를 만듭니다.
                상세 분석은 <strong>출고 검수</strong> 페이지의 관리자 모드에서 확인하실 수 있습니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
