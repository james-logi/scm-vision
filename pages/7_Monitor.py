"""
Page 7: 검사 이력 모니터링
- 상품별 / 날짜별 검사 수량 현황
- 검색 / 필터
- 일별 차트
- inspection_log.py 공유 데이터 사용
"""

import streamlit as st
import pandas as pd
import altair as alt
from styles import inject_global_styles, render_brand_header, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar
from inspection_log import InspectionLog

st.set_page_config(
    page_title="검사 이력 | AI Vision",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 검사 이력 모니터링")
render_page_subtitle("INSPECTION LOG · DAILY QUANTITY · SEARCH & FILTER")


# ─── 데이터 로드 ───
@st.cache_data(ttl=30)
def load_log():
    return InspectionLog.load()

@st.cache_data(ttl=30)
def load_summary():
    return InspectionLog.daily_summary()

df = load_log()
summary = load_summary()


# ─── 데이터 없을 때 ───
if df.empty:
    st.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border-left:4px solid {COLORS["accent_gold"]};border-radius:6px;'
        f'padding:32px;text-align:center;margin-top:20px;">'
        f'<div style="font-size:48px;margin-bottom:12px;">📋</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:18px;'
        f'font-weight:700;color:{COLORS["text_primary"]};margin-bottom:8px;">'
        f'검사 이력이 없습니다</div>'
        f'<div style="font-size:13px;color:{COLORS["text_secondary"]};line-height:1.7;">'
        f'[6. 비전 검사 테스트] 페이지에서 이미지를 검사하면<br>'
        f'결과가 자동으로 여기에 기록됩니다.'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()


# ─── 상단 KPI ───
total_inspections = len(df)
ok_count = len(df[df["verdict"] == "OK"])
ng_count = len(df[df["verdict"] == "NG"])
unclassified = len(df[df["verdict"] == "UNCLASSIFIED"])
total_qty = int(df[df["verdict"] == "OK"]["quantity"].sum())
days_count = df["date"].nunique()

k1, k2, k3, k4 = st.columns(4)

def kpi(col, label, value, unit, sub, color):
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:1px solid {COLORS["border_subtle"]};border-radius:6px;'
        f'padding:16px;position:relative;overflow:hidden;">'
        f'<div style="position:absolute;top:0;left:0;width:3px;height:100%;'
        f'background:{color};"></div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["text_tertiary"]};margin-bottom:8px;">{label}</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:28px;'
        f'font-weight:700;color:{COLORS["text_primary"]};">'
        f'{value}<span style="font-size:13px;color:{COLORS["text_tertiary"]};'
        f'margin-left:3px;">{unit}</span></div>'
        f'<div style="font-size:10px;color:{color};margin-top:6px;">{sub}</div>'
        f'</div>', unsafe_allow_html=True)

kpi(k1, "총 검사 건수", f"{total_inspections:,}", "건",
    f"{days_count}일 누적", COLORS["accent_cobalt"])
kpi(k2, "OK 통과 수량", f"{total_qty:,}", "EA",
    f"OK {ok_count}건", COLORS["status_ok"])
kpi(k3, "NG 판정", f"{ng_count:,}", "건",
    f"NG율 {ng_count/total_inspections*100:.1f}%" if total_inspections else "0%",
    COLORS["status_warning"])
kpi(k4, "미분류 건수", f"{unclassified:,}", "건",
    "새 SKU 등록 필요", COLORS["text_tertiary"])


st.markdown("")


# ─── 탭: 차트 / 테이블 / 상세 ───
chart_tab, table_tab, detail_tab = st.tabs(["📊 차트", "📋 일별 집계 표", "🔍 상세 검색"])


# ─── 차트 탭 ───
with chart_tab:
    if summary.empty:
        st.info("OK 판정 데이터가 없습니다.")
    else:
        from sku_registry import SkuRegistry
        _registry = SkuRegistry()

        # Case(박스) 수량 계산: EA ÷ SKU별 박스당 단위
        def get_units_per_box(sku_name):
            for s in _registry.list_active():
                if s.sku_name == sku_name:
                    u = s.expected_total_units()
                    return u if u > 0 else 1
            return 1

        summary["units_per_box"] = summary["sku_name"].apply(get_units_per_box)
        summary["total_boxes"] = (summary["total_qty"] / summary["units_per_box"]).apply(
            lambda x: max(1, round(x)))

        # EA/Case 토글
        unit_mode = st.radio(
            "수량 단위",
            ["EA (낱개)", "Case (박스)", "EA + Case 동시"],
            horizontal=True,
            key="chart_unit",
        )

        sku_names = ["전체"] + sorted(summary["sku_name"].unique().tolist())
        selected_sku = st.selectbox("상품 선택", sku_names, key="chart_sku")

        chart_data = summary.copy()
        if selected_sku != "전체":
            chart_data = chart_data[chart_data["sku_name"] == selected_sku]

        chart_data["date_str"] = chart_data["date"].dt.strftime("%m-%d")

        st.markdown(
            f'<div style="background:{COLORS["bg_elevated"]};padding:12px 18px;'
            f'border:1px solid {COLORS["border_subtle"]};border-bottom:none;'
            f'border-radius:6px 6px 0 0;">'
            f'<div style="font-family:\'Noto Serif KR\',serif;font-size:13px;'
            f'font-weight:700;color:{COLORS["text_primary"]};">날짜별 수량 추이</div>'
            f'</div>', unsafe_allow_html=True)

        if unit_mode == "EA + Case 동시":
            # EA와 Case를 나란히 표시 (wide-format → long-format)
            import pandas as pd
            ea_df = chart_data[["date", "sku_name", "date_str", "total_qty"]].copy()
            ea_df["단위"] = "EA (낱개)"
            ea_df = ea_df.rename(columns={"total_qty": "수량"})

            case_df = chart_data[["date", "sku_name", "date_str", "total_boxes"]].copy()
            case_df["단위"] = "Case (박스)"
            case_df = case_df.rename(columns={"total_boxes": "수량"})

            long_df = pd.concat([ea_df, case_df], ignore_index=True)

            bars = alt.Chart(long_df).mark_bar().encode(
                x=alt.X("date_str:N", title="날짜", sort=None,
                    axis=alt.Axis(labelColor=COLORS["text_tertiary"],
                                  titleColor=COLORS["text_tertiary"])),
                y=alt.Y("수량:Q", title="수량",
                    axis=alt.Axis(labelColor=COLORS["text_tertiary"],
                                  titleColor=COLORS["text_tertiary"])),
                color=alt.Color("단위:N",
                    scale=alt.Scale(
                        domain=["EA (낱개)", "Case (박스)"],
                        range=[COLORS["accent_cobalt"], COLORS["accent_gold"]]
                    ),
                    legend=alt.Legend(labelColor=COLORS["text_secondary"],
                                      titleColor=COLORS["text_secondary"])),
                xOffset="단위:N",
                tooltip=[alt.Tooltip("date_str:N", title="날짜"),
                         alt.Tooltip("sku_name:N", title="상품"),
                         alt.Tooltip("단위:N", title="단위"),
                         alt.Tooltip("수량:Q", title="수량")],
            )
            text = alt.Chart(long_df).mark_text(
                dy=-6, fontSize=10, fontWeight="bold",
                color=COLORS["text_primary"],
            ).encode(
                x=alt.X("date_str:N", sort=None),
                y=alt.Y("수량:Q"),
                xOffset="단위:N",
                text=alt.Text("수량:Q"),
            )
            final_chart = (bars + text).properties(
                height=280, background=COLORS["bg_panel"]
            ).configure_view(stroke=COLORS["border_subtle"])

        else:
            qty_field = "total_qty" if "EA" in unit_mode else "total_boxes"
            qty_label = "수량 (EA)" if "EA" in unit_mode else "수량 (Case)"
            bar_color = COLORS["accent_cobalt"] if "EA" in unit_mode else COLORS["accent_gold"]

            bars = alt.Chart(chart_data).mark_bar(color=bar_color).encode(
                x=alt.X("date_str:N", title="날짜", sort=None,
                    axis=alt.Axis(labelColor=COLORS["text_tertiary"],
                                  titleColor=COLORS["text_tertiary"])),
                y=alt.Y(f"{qty_field}:Q", title=qty_label,
                    axis=alt.Axis(labelColor=COLORS["text_tertiary"],
                                  titleColor=COLORS["text_tertiary"])),
                color=alt.Color("sku_name:N",
                    scale=alt.Scale(range=[COLORS["accent_cobalt"], COLORS["accent_gold"],
                                           COLORS["status_ok"], COLORS["status_warning"]]),
                    legend=alt.Legend(labelColor=COLORS["text_secondary"],
                                      titleColor=COLORS["text_secondary"])),
                tooltip=[alt.Tooltip("date_str:N", title="날짜"),
                         alt.Tooltip("sku_name:N", title="상품"),
                         alt.Tooltip(f"{qty_field}:Q", title=qty_label),
                         alt.Tooltip("ok_count:Q", title="OK건수"),
                         alt.Tooltip("ng_count:Q", title="NG건수")],
            )
            text = alt.Chart(chart_data).mark_text(
                dy=-6, fontSize=11, fontWeight="bold",
                color=COLORS["text_primary"],
            ).encode(
                x=alt.X("date_str:N", sort=None),
                y=alt.Y(f"{qty_field}:Q"),
                color=alt.Color("sku_name:N",
                    scale=alt.Scale(range=[COLORS["accent_cobalt"], COLORS["accent_gold"],
                                           COLORS["status_ok"], COLORS["status_warning"]])),
                text=alt.Text(f"{qty_field}:Q"),
            )
            final_chart = (bars + text).properties(
                height=280, background=COLORS["bg_panel"]
            ).configure_view(stroke=COLORS["border_subtle"])

        st.altair_chart(final_chart, use_container_width=True)

        # 상품별 누적 수량 (EA + Case 함께 표기)
        st.markdown("")
        total_by_sku = summary.groupby("sku_name").agg(
            total_qty=("total_qty", "sum"),
            total_boxes=("total_boxes", "sum"),
        ).reset_index().sort_values("total_qty", ascending=False)

        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
            f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;margin-bottom:10px;">'
            f'CUMULATIVE QUANTITY BY SKU</div>', unsafe_allow_html=True)

        max_q = total_by_sku["total_qty"].max() if len(total_by_sku) > 0 else 1
        for _, row in total_by_sku.iterrows():
            pct = int(row["total_qty"] / max_q * 100)
            st.markdown(
                f'<div style="display:flex;gap:12px;align-items:center;margin-bottom:10px;">'
                f'<div style="min-width:140px;font-size:13px;color:{COLORS["text_secondary"]};">'
                f'{row["sku_name"]}</div>'
                f'<div style="flex:1;height:10px;background:{COLORS["bg_deep"]};'
                f'border-radius:4px;overflow:hidden;">'
                f'<div style="height:100%;width:{pct}%;'
                f'background:linear-gradient(to right,{COLORS["accent_cobalt"]},{COLORS["accent_gold"]});'
                f'border-radius:4px;"></div></div>'
                f'<div style="min-width:140px;text-align:right;'
                f'font-family:\'IBM Plex Mono\',monospace;font-size:12px;">'
                f'<span style="color:{COLORS["accent_gold"]}">'
                f'{int(row["total_qty"]):,} EA</span>'
                f'<span style="color:{COLORS["text_muted"]};margin:0 4px;">|</span>'
                f'<span style="color:{COLORS["accent_cobalt"]}">'
                f'{int(row["total_boxes"]):,} Case</span>'
                f'</div>'
                f'</div>', unsafe_allow_html=True)


# ─── 일별 집계 표 탭 ───
with table_tab:
    if summary.empty:
        st.info("데이터 없음")
    else:
        # 필터
        f1, f2 = st.columns(2)
        with f1:
            sku_opts = ["전체"] + sorted(summary["sku_name"].unique().tolist())
            t_sku = st.selectbox("상품", sku_opts, key="table_sku")
        with f2:
            dates = sorted(summary["date"].dt.strftime("%Y-%m-%d").unique().tolist(), reverse=True)
            t_date = st.selectbox("날짜", ["전체"] + dates, key="table_date")

        disp = summary.copy()
        if t_sku != "전체":
            disp = disp[disp["sku_name"] == t_sku]
        if t_date != "전체":
            disp = disp[disp["date"].dt.strftime("%Y-%m-%d") == t_date]

        disp_show = pd.DataFrame({
            "날짜": disp["date"].dt.strftime("%Y-%m-%d"),
            "상품명": disp["sku_name"],
            "OK 수량(EA)": disp["total_qty"].astype(int),
            "OK 건수": disp["ok_count"].astype(int),
            "NG 건수": disp["ng_count"].astype(int),
        })
        st.dataframe(disp_show, use_container_width=True, hide_index=True, height=400)

        # 합계 행
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
            f'color:{COLORS["accent_gold"]};margin-top:8px;">'
            f'합계: {int(disp["total_qty"].sum()):,} EA · '
            f'OK {int(disp["ok_count"].sum())}건 · '
            f'NG {int(disp["ng_count"].sum())}건'
            f'</div>', unsafe_allow_html=True)


# ─── 상세 검색 탭 ───
with detail_tab:
    st.markdown(
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["text_tertiary"]};margin-bottom:12px;">'
        f'DETAILED LOG · {len(df):,} RECORDS</div>', unsafe_allow_html=True)

    d1, d2, d3 = st.columns(3)
    with d1:
        verdict_opts = ["전체", "OK", "NG", "UNCLASSIFIED"]
        d_verdict = st.selectbox("판정 결과", verdict_opts, key="d_verdict")
    with d2:
        sku_opts2 = ["전체"] + sorted(df["sku_name"].dropna().unique().tolist())
        d_sku = st.selectbox("상품명", sku_opts2, key="d_sku")
    with d3:
        dates2 = ["전체"] + sorted(
            df["date"].dt.strftime("%Y-%m-%d").unique().tolist(), reverse=True)
        d_date = st.selectbox("날짜", dates2, key="d_date")

    filtered = df.copy()
    if d_verdict != "전체":
        filtered = filtered[filtered["verdict"] == d_verdict]
    if d_sku != "전체":
        filtered = filtered[filtered["sku_name"] == d_sku]
    if d_date != "전체":
        filtered = filtered[filtered["date"].dt.strftime("%Y-%m-%d") == d_date]

    filtered_show = filtered.sort_values("timestamp", ascending=False).head(200)
    disp2 = pd.DataFrame({
        "시각": filtered_show["timestamp"].dt.strftime("%m-%d %H:%M:%S"),
        "상품명": filtered_show["sku_name"],
        "판정": filtered_show["verdict"],
        "수량(EA)": filtered_show["quantity"].astype(int),
        "신뢰도(%)": filtered_show["confidence"].astype(int),
        "소요시간(초)": filtered_show["elapsed"],
        "이미지": filtered_show["image_name"],
    })
    st.markdown(
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
        f'color:{COLORS["text_tertiary"]};margin-bottom:6px;">'
        f'검색 결과: {len(filtered):,}건 (최대 200건 표시)</div>',
        unsafe_allow_html=True)
    st.dataframe(disp2, use_container_width=True, hide_index=True, height=440)
