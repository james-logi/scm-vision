"""
Page 3: 출고 처리
- 매장 선택 → P-Box 선택 → 출고 확정 워크플로우
- 워크플로우의 마지막 액션 화면
- D11: UI 구현 / D12: 출고 확정 로직 추가 예정
"""

import streamlit as st
import pandas as pd
import hashlib
from styles import inject_global_styles, render_brand_header, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar
from sku_registry import SkuRegistry

st.set_page_config(
    page_title="출고 처리 | AI Vision",
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
# 데이터 로드 + 출고 상태 부여 (Page 2와 동일 로직)
# ─────────────────────────────────────────────
@st.cache_data
def load_inspection_data():
    df = pd.read_csv("data/inspection_history.csv")
    df["inspected_at"] = pd.to_datetime(df["inspected_at"])
    df["is_ng"] = df["verdict"] != "OK"

    latest = df["inspected_at"].max()
    cutoff = latest - pd.Timedelta(days=7)

    def assign_status(row):
        if row["is_ng"]:
            return "blocked"
        if row["inspected_at"] < cutoff:
            return "dispatched"
        h = int(hashlib.md5(row["crate_id"].encode()).hexdigest()[:4], 16)
        return "in_stock" if (h % 10) < 6 else "dispatched"

    df["status"] = df.apply(assign_status, axis=1)
    return df


df_all = load_inspection_data()


# ─────────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────────
if "dispatched_in_session" not in st.session_state:
    st.session_state.dispatched_in_session = set()
if "selected_crates" not in st.session_state:
    st.session_state.selected_crates = set()
if "selected_store" not in st.session_state:
    st.session_state.selected_store = None


# ─────────────────────────────────────────────
# 출고 대기 박스만 필터링 (세션에서 출고된 건 제외)
# ─────────────────────────────────────────────
df_stock = df_all[
    (df_all["status"] == "in_stock")
    & (~df_all["crate_id"].isin(st.session_state.dispatched_in_session))
].copy()


# ─────────────────────────────────────────────
# 페이지 제목
# ─────────────────────────────────────────────
st.markdown("# 출고 처리")
render_page_subtitle("DISPATCH MANAGEMENT · STORE-BY-STORE FULFILLMENT")


# ─────────────────────────────────────────────
# 상단 요약 KPI
# ─────────────────────────────────────────────
total_stock_pbox = len(df_stock)
total_stock_units = int(df_stock["detected_qty"].sum())
total_stores_pending = df_stock["destination_store"].nunique()
dispatched_today = len(st.session_state.dispatched_in_session)


def kpi_card(col, label, value, unit, sub, sub_color, accent):
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:1px solid {COLORS["border_subtle"]};'
        f'border-radius:6px;padding:16px 18px;position:relative;'
        f'overflow:hidden;height:120px;">'
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
kpi_card(k1, "출고 대기 P-Box", f"{total_stock_pbox:,}", "Case",
         "WMS 검증 완료", COLORS["status_ok"], COLORS["accent_cobalt"])
kpi_card(k2, "출고 대기 단위", f"{total_stock_units:,}", "EA",
         "Dual-Unit Tracking", COLORS["status_ok"], COLORS["accent_gold"])
kpi_card(k3, "출고 예정 매장", f"{total_stores_pending}", "곳",
         "선택 후 처리", COLORS["text_tertiary"], COLORS["text_secondary"])
kpi_card(k4, "금일 세션 출고", f"{dispatched_today}", "Case",
         "본 세션 누적", COLORS["status_ok"], COLORS["status_ok"])


st.markdown("")

# 출고 대기 박스 없는 경우
if total_stock_pbox == 0:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border-left:4px solid {COLORS["status_ok"]};'
        f'border-radius:6px;padding:24px;margin-top:20px;">'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:18px;'
        f'font-weight:700;color:{COLORS["text_primary"]};margin-bottom:8px;">'
        f'✅ 모든 출고가 완료되었습니다</div>'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};'
        f'line-height:1.7;">'
        f'현재 출고 대기 중인 P-Box가 없습니다. 새로운 입고가 발생하면 이 페이지에 다시 표시됩니다.'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ─────────────────────────────────────────────
# 매장별 그룹핑
# ─────────────────────────────────────────────
store_groups = (
    df_stock.groupby("destination_store")
    .agg(
        pbox=("crate_id", "count"),
        units=("detected_qty", "sum"),
        skus=("expected_sku", lambda x: list(set(x))),
    )
    .reset_index()
    .sort_values("pbox", ascending=False)
)


# ─────────────────────────────────────────────
# 좌(매장 리스트) / 우(선택 매장의 박스들)
# ─────────────────────────────────────────────
left_col, right_col = st.columns([1, 2])

# ===== 좌측: 매장 선택 =====
with left_col:
    st.markdown(
        f'<div style="background:{COLORS["bg_elevated"]};'
        f'padding:13px 18px;border:1px solid {COLORS["border_subtle"]};'
        f'border-bottom:none;border-radius:6px 6px 0 0;">'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:13px;'
        f'font-weight:700;color:{COLORS["text_primary"]};">'
        f'출고 매장 선택</div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["text_tertiary"]};letter-spacing:0.05em;'
        f'margin-top:2px;">SELECT DESTINATION STORE</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # 매장 카드 리스트
    store_list_html = (
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:1px solid {COLORS["border_subtle"]};'
        f'border-top:none;border-radius:0 0 6px 6px;padding:8px;">'
    )
    st.markdown(store_list_html, unsafe_allow_html=True)

    # 각 매장은 버튼으로 표현
    for _, row in store_groups.iterrows():
        store = row["destination_store"]
        is_selected = (st.session_state.selected_store == store)

        # 선택 상태 시각화
        btn_label = f"{'● ' if is_selected else '○ '}{store}  ({row['pbox']} Case · {int(row['units'])} EA)"

        if st.button(
            btn_label,
            key=f"store_btn_{store}",
            width='stretch',
            type="primary" if is_selected else "secondary",
        ):
            # 매장 변경 시 선택된 박스도 초기화
            if st.session_state.selected_store != store:
                st.session_state.selected_crates = set()
            st.session_state.selected_store = store
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ===== 우측: 선택된 매장의 박스 =====
with right_col:
    if st.session_state.selected_store is None:
        # 매장 미선택 시 안내
        st.markdown(
            f'<div style="background:{COLORS["bg_panel"]};'
            f'border:2px dashed {COLORS["border_strong"]};'
            f'border-radius:8px;padding:60px 40px;text-align:center;'
            f'min-height:400px;display:flex;flex-direction:column;'
            f'justify-content:center;align-items:center;'
            f'color:{COLORS["text_muted"]};">'
            f'<div style="font-family:\'Noto Serif KR\',serif;font-size:64px;'
            f'line-height:1;margin-bottom:16px;">⬚</div>'
            f'<div style="font-size:14px;margin-bottom:6px;">왼쪽에서 매장을 선택해주세요</div>'
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
            f'color:{COLORS["text_muted"]};letter-spacing:0.05em;">'
            f'SELECT A STORE FROM THE LEFT</div></div>',
            unsafe_allow_html=True,
        )
    else:
        store = st.session_state.selected_store
        store_boxes = df_stock[df_stock["destination_store"] == store].copy()
        store_boxes = store_boxes.sort_values("inspected_at", ascending=False)

        # 헤더
        st.markdown(
            f'<div style="background:{COLORS["bg_elevated"]};'
            f'padding:13px 18px;border:1px solid {COLORS["border_subtle"]};'
            f'border-bottom:none;border-radius:6px 6px 0 0;'
            f'display:flex;justify-content:space-between;align-items:center;">'
            f'<div>'
            f'<div style="font-family:\'Noto Serif KR\',serif;font-size:14px;'
            f'font-weight:700;color:{COLORS["text_primary"]};">'
            f'{store} 출고 대기 박스</div>'
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["text_tertiary"]};letter-spacing:0.05em;margin-top:2px;">'
            f'{len(store_boxes)} CASE · {int(store_boxes["detected_qty"].sum())} EA</div>'
            f'</div>'
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["text_tertiary"]};letter-spacing:0.05em;">'
            f'PENDING DISPATCH</div></div>',
            unsafe_allow_html=True,
        )

        # 전체 선택 / 해제 버튼
        st.markdown(
            f'<div style="background:{COLORS["bg_panel"]};'
            f'border:1px solid {COLORS["border_subtle"]};border-bottom:none;'
            f'padding:10px 18px;">',
            unsafe_allow_html=True,
        )
        sel_col1, sel_col2, sel_col3 = st.columns([1, 1, 3])
        with sel_col1:
            if st.button("✓ 전체 선택", key="select_all", width='stretch'):
                st.session_state.selected_crates = set(store_boxes["crate_id"].tolist())
                st.rerun()
        with sel_col2:
            if st.button("✗ 전체 해제", key="deselect_all", width='stretch'):
                st.session_state.selected_crates = set()
                st.rerun()
        with sel_col3:
            selected_count = len(
                st.session_state.selected_crates & set(store_boxes["crate_id"].tolist())
            )
            st.markdown(
                f'<div style="font-family:\'IBM Plex Mono\',monospace;'
                f'font-size:12px;color:{COLORS["text_secondary"]};'
                f'padding-top:8px;text-align:right;">'
                f'선택: <span style="color:{COLORS["accent_gold"]};font-size:14px;'
                f'font-weight:700;">{selected_count}</span> / {len(store_boxes)} Case'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # 박스 리스트 (체크박스 + 정보)
        boxes_html_container = (
            f'<div style="background:{COLORS["bg_panel"]};'
            f'border:1px solid {COLORS["border_subtle"]};border-top:none;'
            f'border-radius:0 0 6px 6px;padding:0;max-height:500px;'
            f'overflow-y:auto;">'
        )
        st.markdown(boxes_html_container, unsafe_allow_html=True)

        # 각 박스를 체크박스 + 정보로 표시
        for idx, row in store_boxes.iterrows():
            crate_id = row["crate_id"]
            is_selected = crate_id in st.session_state.selected_crates

            box_col1, box_col2 = st.columns([0.08, 0.92])
            with box_col1:
                # 체크박스 - rerun 없이 세션 상태에 직접 반영
                new_state = st.checkbox(
                    " ",
                    value=is_selected,
                    key=f"crate_check_{crate_id}",
                    label_visibility="collapsed",
                )
                # 상태가 바뀌면 세션에 반영 (rerun 안 함 - 자연스러운 UX)
                if new_state:
                    st.session_state.selected_crates.add(crate_id)
                else:
                    st.session_state.selected_crates.discard(crate_id)

            with box_col2:
                # 박스 정보 카드
                sku = registry.get(row["expected_sku"])
                sku_name = sku.sku_name if sku else row["expected_sku"]
                time_label = row["inspected_at"].strftime("%m-%d %H:%M")

                # 선택 상태에 따른 배경
                bg = COLORS["bg_elevated"] if is_selected else COLORS["bg_deep"]
                accent = COLORS["accent_gold"] if is_selected else COLORS["border_subtle"]

                st.markdown(
                    f'<div style="background:{bg};border:1px solid {accent};'
                    f'border-radius:4px;padding:10px 14px;margin-bottom:6px;">'
                    f'<div style="display:grid;grid-template-columns:1fr auto auto;'
                    f'gap:14px;align-items:center;">'
                    f'<div>'
                    f'<div style="font-family:\'IBM Plex Mono\',monospace;'
                    f'font-size:11px;color:{COLORS["text_secondary"]};'
                    f'letter-spacing:0.03em;">{crate_id}</div>'
                    f'<div style="font-size:12px;color:{COLORS["text_tertiary"]};'
                    f'margin-top:2px;">{row["expected_sku"]} · {sku_name} · {row["line_no"]}</div>'
                    f'</div>'
                    f'<div style="text-align:right;">'
                    f'<div style="font-family:\'Noto Serif KR\',serif;font-size:16px;'
                    f'font-weight:700;color:{COLORS["text_primary"]};line-height:1;">'
                    f'{row["detected_qty"]}<span style="font-size:10px;'
                    f'color:{COLORS["text_tertiary"]};">EA</span></div>'
                    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
                    f'color:{COLORS["text_tertiary"]};letter-spacing:0.05em;">'
                    f'{time_label}</div>'
                    f'</div>'
                    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
                    f'color:{COLORS["status_ok"]};padding:2px 8px;'
                    f'background:rgba(94,193,156,0.15);border-radius:2px;">'
                    f'WMS OK</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 하단: 출고 요약 + 확정 버튼
# ─────────────────────────────────────────────
if st.session_state.selected_store and st.session_state.selected_crates:
    store = st.session_state.selected_store
    store_boxes = df_stock[df_stock["destination_store"] == store]
    selected_boxes = store_boxes[
        store_boxes["crate_id"].isin(st.session_state.selected_crates)
    ]

    if len(selected_boxes) > 0:
        # SKU별 합계
        sku_summary = (
            selected_boxes.groupby("expected_sku")
            .agg(pbox=("crate_id", "count"), units=("detected_qty", "sum"))
            .reset_index()
        )

        st.markdown("")
        st.markdown(
            f'<div style="background:{COLORS["bg_panel"]};'
            f'border:2px solid {COLORS["accent_gold"]};border-radius:6px;'
            f'padding:24px;margin-top:16px;">'
            f'<div style="display:flex;justify-content:space-between;'
            f'align-items:center;margin-bottom:18px;'
            f'padding-bottom:14px;border-bottom:1px solid {COLORS["border_subtle"]};">'
            f'<div>'
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["accent_gold"]};letter-spacing:0.08em;'
            f'text-transform:uppercase;margin-bottom:4px;">DISPATCH SUMMARY</div>'
            f'<div style="font-family:\'Noto Serif KR\',serif;font-size:18px;'
            f'font-weight:700;color:{COLORS["text_primary"]};">'
            f'{store} 출고 요약</div>'
            f'</div>'
            f'<div style="text-align:right;">'
            f'<div style="font-family:\'Noto Serif KR\',serif;font-size:32px;'
            f'font-weight:700;color:{COLORS["accent_gold"]};line-height:1;">'
            f'{len(selected_boxes)}<span style="font-size:14px;'
            f'color:{COLORS["text_tertiary"]};margin-left:4px;">Case</span></div>'
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
            f'color:{COLORS["text_secondary"]};margin-top:2px;">'
            f'{int(selected_boxes["detected_qty"].sum())} EA · '
            f'{selected_boxes["expected_sku"].nunique()} SKU</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        # SKU별 상세
        sku_rows_html = '<div style="margin-bottom:18px;">'
        for _, row in sku_summary.iterrows():
            sku = registry.get(row["expected_sku"])
            sku_name = sku.sku_name if sku else row["expected_sku"]
            sku_rows_html += (
                f'<div style="display:grid;grid-template-columns:1fr auto auto;'
                f'gap:14px;align-items:center;padding:10px 14px;'
                f'background:{COLORS["bg_deep"]};border-radius:4px;margin-bottom:6px;">'
                f'<div>'
                f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
                f'color:{COLORS["text_tertiary"]};">{row["expected_sku"]}</span> '
                f'<span style="font-family:\'Noto Serif KR\',serif;font-size:14px;'
                f'font-weight:500;color:{COLORS["text_primary"]};margin-left:6px;">'
                f'{sku_name}</span>'
                f'</div>'
                f'<div style="font-family:\'Noto Serif KR\',serif;font-size:18px;'
                f'font-weight:700;color:{COLORS["accent_cobalt"]};">'
                f'{row["pbox"]}<span style="font-size:10px;'
                f'color:{COLORS["text_tertiary"]};margin-left:2px;">Case</span></div>'
                f'<div style="font-family:\'Noto Serif KR\',serif;font-size:18px;'
                f'font-weight:700;color:{COLORS["accent_gold"]};">'
                f'{int(row["units"])}<span style="font-size:10px;'
                f'color:{COLORS["text_tertiary"]};margin-left:2px;">EA</span></div>'
                f'</div>'
            )
        sku_rows_html += "</div>"
        st.markdown(sku_rows_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # 출고 확정 버튼 (큰)
        confirm_col1, confirm_col2 = st.columns([1, 3])
        with confirm_col2:
            if st.button(
                f"🚚 {store}으로 {len(selected_boxes)}건 출고 확정",
                key="confirm_dispatch",
                type="primary",
                width='stretch',
            ):
                # D11에서는 UI만 완성, 실제 로직은 D12에서 정교화
                dispatched_ids = set(selected_boxes["crate_id"].tolist())
                st.session_state.dispatched_in_session.update(dispatched_ids)
                st.session_state.selected_crates = set()

                st.success(
                    f"✅ {store}으로 {len(dispatched_ids)}건 출고 완료. "
                    f"WMS에 자동 반영되었습니다."
                )
                st.balloons()
                # 잠시 후 자동 새로고침
                import time
                time.sleep(2)
                st.rerun()
        with confirm_col1:
            if st.button("✗ 선택 취소", key="cancel_selection", width='stretch'):
                st.session_state.selected_crates = set()
                st.rerun()


# ═════════════════════════════════════════════
# 관리자 모드 — 출고 이력 분석
# ═════════════════════════════════════════════
if mode == "admin":
    st.markdown("")
    st.markdown(
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;'
        f'text-transform:uppercase;margin-top:32px;margin-bottom:10px;">'
        f'▸ ADMIN-ONLY · DISPATCH ANALYTICS</div>',
        unsafe_allow_html=True,
    )

    # 30일 누적 출고 통계
    df_dispatched_30d = df_all[df_all["status"] == "dispatched"]
    df_blocked_30d = df_all[df_all["status"] == "blocked"]

    # 매장별 출고 완료 통계
    store_dispatch_stats = (
        df_dispatched_30d.groupby("destination_store")
        .agg(
            cases=("crate_id", "count"),
            units=("detected_qty", "sum"),
        )
        .reset_index()
        .sort_values("cases", ascending=False)
    )

    # 상단 KPI 3개
    admin_k1, admin_k2, admin_k3 = st.columns(3)

    kpi_card(
        admin_k1, "30일 누적 출고", f"{len(df_dispatched_30d):,}", "Case",
        f"{int(df_dispatched_30d['detected_qty'].sum()):,} EA",
        COLORS["status_ok"], COLORS["status_ok"],
    )
    kpi_card(
        admin_k2, "출고 차단 (NG)", f"{len(df_blocked_30d):,}", "Case",
        "사전 클레임 방지", COLORS["status_warning"], COLORS["status_warning"],
    )
    kpi_card(
        admin_k3, "평균 매장당 출고", f"{int(store_dispatch_stats['cases'].mean())}", "Case",
        f"{store_dispatch_stats['destination_store'].nunique()}개 매장 평균",
        COLORS["text_tertiary"], COLORS["accent_cobalt"],
    )

    st.markdown("")

    # 매장별 출고 완료 추세 (간단한 막대 차트)
    st.markdown(
        f'<div style="background:{COLORS["bg_elevated"]};padding:13px 18px;'
        f'border:1px solid {COLORS["border_subtle"]};border-bottom:none;'
        f'border-radius:6px 6px 0 0;">'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:13px;'
        f'font-weight:700;color:{COLORS["text_primary"]};">'
        f'매장별 30일 출고 완료 현황</div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["text_tertiary"]};letter-spacing:0.05em;margin-top:2px;">'
        f'30D DISPATCH PERFORMANCE BY STORE</div></div>',
        unsafe_allow_html=True,
    )

    max_cases = store_dispatch_stats["cases"].max() if len(store_dispatch_stats) > 0 else 1
    chart_html = (
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:1px solid {COLORS["border_subtle"]};border-top:none;'
        f'border-radius:0 0 6px 6px;padding:18px;">'
    )
    for _, row in store_dispatch_stats.iterrows():
        bar_pct = int(row["cases"] / max_cases * 100)
        chart_html += (
            f'<div style="display:grid;grid-template-columns:110px 1fr 120px;'
            f'gap:14px;align-items:center;padding:8px 0;'
            f'border-bottom:1px solid {COLORS["border_subtle"]};">'
            f'<div style="font-size:13px;color:{COLORS["text_secondary"]};">'
            f'{row["destination_store"]}</div>'
            f'<div>'
            f'<span style="display:inline-block;width:100%;height:6px;'
            f'background:{COLORS["bg_deep"]};border-radius:3px;overflow:hidden;'
            f'vertical-align:middle;">'
            f'<span style="display:block;height:100%;width:{bar_pct}%;'
            f'background:linear-gradient(to right,{COLORS["accent_cobalt"]},'
            f'{COLORS["accent_gold"]});border-radius:3px;"></span>'
            f'</span></div>'
            f'<div style="text-align:right;'
            f'font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
            f'color:{COLORS["text_secondary"]};">'
            f'{row["cases"]}<span style="color:{COLORS["text_tertiary"]};"> Case · </span>'
            f'{int(row["units"])}<span style="color:{COLORS["text_tertiary"]};"> EA</span>'
            f'</div></div>'
        )
    chart_html += "</div>"
    st.markdown(chart_html, unsafe_allow_html=True)

    # 인사이트 카드
    top_store = store_dispatch_stats.iloc[0] if len(store_dispatch_stats) > 0 else None
    if top_store is not None:
        st.markdown("")
        st.markdown(
            f'<div style="background:{COLORS["bg_panel"]};'
            f'border-left:4px solid {COLORS["accent_gold"]};border-radius:6px;'
            f'padding:18px 22px;margin-top:16px;">'
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["accent_gold"]};letter-spacing:0.08em;'
            f'text-transform:uppercase;margin-bottom:8px;">'
            f'📈 SCM INSIGHT</div>'
            f'<div style="font-size:13px;line-height:1.7;'
            f'color:{COLORS["text_secondary"]};">'
            f'30일간 가장 많이 출고된 매장은 '
            f'<strong style="color:{COLORS["text_primary"]};">{top_store["destination_store"]}</strong>'
            f'으로, 총 <strong style="color:{COLORS["accent_gold"]};">'
            f'{top_store["cases"]}건</strong>의 P-Box('
            f'<strong style="color:{COLORS["accent_gold"]};">{int(top_store["units"]):,}개 단위</strong>)를 '
            f'출고했습니다. 매장별 출고 패턴은 발주 예측의 핵심 변수입니다. '
            f'정확한 출고 데이터가 누적될수록 채찍효과의 미시적 시작점이 차단되며, '
            f'생산-물류-매장 간 정보 동기화가 강화됩니다.'
            f'</div></div>',
            unsafe_allow_html=True,
        )
