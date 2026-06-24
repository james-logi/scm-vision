"""
Page 1: 생산 라인 현황
- LINE 1~10 전체 현황
- 라인별 P-Box 생산량 + NG율
- 기존 inspection_history.csv 데이터 활용
"""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import render_brand_header
from sidebar import ensure_session_state, render_sidebar, SITE_CONFIG

st.set_page_config(
    page_title="생산 라인 현황 | AI Vision",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 생산 라인 현황")
render_page_subtitle("PRODUCTION LINE · P-BOX OUTPUT · NG RATE BY LINE")


# ─── 데이터 로드 ───
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("data/inspection_history.csv")
    df["inspected_at"] = pd.to_datetime(df["inspected_at"])
    df["date"] = df["inspected_at"].dt.date
    df["is_ng"] = df["verdict"] != "OK"
    return df

df = load_data()

# ─── 기간 필터 ───
st.markdown("")
f_col1, f_col2, _ = st.columns([1, 1, 2])
with f_col1:
    period = st.selectbox(
        "조회 기간",
        ["오늘", "최근 7일", "최근 30일", "전체"],
        index=2,
        key="prod_period",
    )
with f_col2:
    all_skus = ["전체"] + sorted(df["expected_sku_name"].dropna().unique().tolist())
    sel_sku = st.selectbox("SKU 필터", all_skus, key="prod_sku")

# 기간 필터 적용
today = df["date"].max()
if period == "오늘":
    filtered = df[df["date"] == today]
elif period == "최근 7일":
    cutoff = today - timedelta(days=6)
    filtered = df[df["date"] >= cutoff]
elif period == "최근 30일":
    cutoff = today - timedelta(days=29)
    filtered = df[df["date"] >= cutoff]
else:
    filtered = df.copy()

if sel_sku != "전체":
    filtered = filtered[filtered["expected_sku_name"] == sel_sku]


# ─── 전체 KPI ───
total_pbox = len(filtered)
total_ok = len(filtered[filtered["verdict"] == "OK"])
total_ng = len(filtered[filtered["is_ng"]])
ng_rate = total_ng / total_pbox * 100 if total_pbox > 0 else 0
active_lines = filtered["line_no"].nunique()

st.markdown("")
k1, k2, k3, k4 = st.columns(4)

def kpi_card(col, label, value, unit, sub, color):
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};'
        f'border:1px solid {COLORS["border_subtle"]};border-radius:6px;'
        f'padding:16px 18px;position:relative;overflow:hidden;">'
        f'<div style="position:absolute;top:0;left:0;width:3px;height:100%;background:{color};"></div>'
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
        f'color:{COLORS["text_tertiary"]};margin-bottom:6px;letter-spacing:0.05em;">{label}</div>'
        f'<div style="font-family:\'Noto Serif KR\',serif;font-size:28px;font-weight:700;'
        f'color:{COLORS["text_primary"]};line-height:1;">{value}'
        f'<span style="font-size:13px;color:{COLORS["text_tertiary"]};margin-left:3px;">{unit}</span></div>'
        f'<div style="font-size:11px;color:{color};margin-top:6px;">{sub}</div>'
        f'</div>', unsafe_allow_html=True)

kpi_card(k1, "가동 라인", f"{active_lines}", "개", f"전체 10라인 중", COLORS["accent_cobalt"])
kpi_card(k2, "총 P-Box 생산", f"{total_pbox:,}", "Case", f"{period} 누적", COLORS["accent_gold"])
kpi_card(k3, "OK 통과", f"{total_ok:,}", "Case", f"정상 출하 가능", COLORS["status_ok"])
kpi_card(k4, "NG 발생", f"{total_ng:,}", "Case",
         f"NG율 {ng_rate:.2f}%",
         COLORS["status_warning"] if ng_rate < 3 else COLORS["status_danger"])


# ─── 라인별 현황 카드 그리드 ───
st.markdown("")
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;margin-bottom:12px;">'
    f'LINE STATUS · P-BOX COUNT · NG RATE</div>',
    unsafe_allow_html=True,
)

# 10라인 데이터 구성 (데이터 없는 라인은 비활성으로 표시)
ALL_LINES = [f"LINE-{i}" for i in range(1, 11)]

line_stats = filtered.groupby("line_no").agg(
    pbox=("crate_id", "count"),
    ok=("verdict", lambda x: (x == "OK").sum()),
    ng=("is_ng", "sum"),
).reset_index()
line_stats["ng_rate"] = (line_stats["ng"] / line_stats["pbox"] * 100).round(2)

# 카드 5개씩 2줄
rows = [ALL_LINES[:5], ALL_LINES[5:]]
for row_lines in rows:
    cols = st.columns(5)
    for col, line_id in zip(cols, row_lines):
        row = line_stats[line_stats["line_no"] == line_id]
        is_active = len(row) > 0

        if is_active:
            r = row.iloc[0]
            pbox = int(r["pbox"])
            ok = int(r["ok"])
            ng = int(r["ng"])
            ng_r = float(r["ng_rate"])

            # NG율에 따른 상태색
            if ng_r == 0:
                status_color = COLORS["status_ok"]
                status_label = "정상"
            elif ng_r < 2:
                status_color = COLORS["accent_gold"]
                status_label = "주의"
            elif ng_r < 4:
                status_color = COLORS["status_warning"]
                status_label = "경고"
            else:
                status_color = COLORS["status_danger"]
                status_label = "위험"

            col.markdown(
                f'<div style="background:{COLORS["bg_panel"]};'
                f'border:1px solid {COLORS["border_subtle"]};'
                f'border-top:3px solid {status_color};'
                f'border-radius:6px;padding:14px 12px;">'

                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'margin-bottom:10px;">'
                f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
                f'font-weight:700;color:{COLORS["text_primary"]};">{line_id}</div>'
                f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;'
                f'color:{status_color};background:{COLORS["bg_deep"]};'
                f'padding:2px 6px;border-radius:3px;">{status_label}</div>'
                f'</div>'

                # P-Box 수량
                f'<div style="font-family:\'Noto Serif KR\',serif;font-size:22px;'
                f'font-weight:700;color:{COLORS["text_primary"]};line-height:1;">{pbox:,}'
                f'<span style="font-size:11px;color:{COLORS["text_muted"]}"> Case</span></div>'

                # OK / NG
                f'<div style="display:flex;gap:6px;margin-top:8px;">'
                f'<div style="flex:1;background:{COLORS["bg_deep"]};border-radius:4px;'
                f'padding:5px;text-align:center;">'
                f'<div style="font-size:9px;color:{COLORS["text_muted"]};">OK</div>'
                f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:13px;'
                f'font-weight:700;color:{COLORS["status_ok"]};">{ok:,}</div>'
                f'</div>'
                f'<div style="flex:1;background:{COLORS["bg_deep"]};border-radius:4px;'
                f'padding:5px;text-align:center;">'
                f'<div style="font-size:9px;color:{COLORS["text_muted"]};">NG</div>'
                f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:13px;'
                f'font-weight:700;color:{status_color};">{ng:,}</div>'
                f'</div>'
                f'</div>'

                # NG율 게이지
                f'<div style="margin-top:8px;">'
                f'<div style="display:flex;justify-content:space-between;'
                f'font-size:9px;color:{COLORS["text_muted"]};margin-bottom:2px;">'
                f'<span>NG율</span><span style="color:{status_color};font-weight:700;">{ng_r:.1f}%</span>'
                f'</div>'
                f'<div style="height:4px;background:{COLORS["bg_deep"]};border-radius:2px;">'
                f'<div style="height:100%;width:{min(ng_r*10, 100):.0f}%;'
                f'background:{status_color};border-radius:2px;"></div>'
                f'</div></div>'

                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            # 비활성 라인
            col.markdown(
                f'<div style="background:{COLORS["bg_panel"]};'
                f'border:1px solid {COLORS["border_subtle"]};'
                f'border-top:3px solid {COLORS["text_muted"]};'
                f'border-radius:6px;padding:14px 12px;opacity:0.5;">'
                f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
                f'font-weight:700;color:{COLORS["text_muted"]};">{line_id}</div>'
                f'<div style="font-size:11px;color:{COLORS["text_muted"]};margin-top:10px;'
                f'text-align:center;padding:20px 0;">비활성</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("")  # 행 간격


# ─── 라인별 일별 추이 차트 ───
st.markdown("---")
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;'
    f'color:{COLORS["text_tertiary"]};letter-spacing:0.08em;margin-bottom:10px;">'
    f'DAILY TREND BY LINE</div>',
    unsafe_allow_html=True,
)

chart_tab1, chart_tab2 = st.tabs(["📦 P-Box 생산량 추이", "⚠️ 라인별 NG율 추이"])

daily_line = filtered.groupby(["date", "line_no"]).agg(
    pbox=("crate_id", "count"),
    ng=("is_ng", "sum"),
).reset_index()
daily_line["ng_rate"] = (daily_line["ng"] / daily_line["pbox"] * 100).round(2)
daily_line["date"] = pd.to_datetime(daily_line["date"])
daily_line["date_str"] = daily_line["date"].dt.strftime("%m-%d")

active_line_ids = sorted(daily_line["line_no"].unique().tolist())
color_range = [
    COLORS["accent_cobalt"], COLORS["accent_gold"], COLORS["status_ok"],
    COLORS["status_warning"], "#a78bfa", "#f472b6",
]

with chart_tab1:
    bars = alt.Chart(daily_line).mark_bar().encode(
        x=alt.X("date_str:N", title="날짜", sort=None,
            axis=alt.Axis(labelColor=COLORS["text_tertiary"], titleColor=COLORS["text_tertiary"])),
        y=alt.Y("pbox:Q", title="P-Box (Case)",
            axis=alt.Axis(labelColor=COLORS["text_tertiary"], titleColor=COLORS["text_tertiary"])),
        color=alt.Color("line_no:N",
            scale=alt.Scale(domain=active_line_ids, range=color_range[:len(active_line_ids)]),
            legend=alt.Legend(labelColor=COLORS["text_secondary"], titleColor=COLORS["text_secondary"])),
        tooltip=[alt.Tooltip("date_str:N", title="날짜"),
                 alt.Tooltip("line_no:N", title="라인"),
                 alt.Tooltip("pbox:Q", title="P-Box"),
                 alt.Tooltip("ng:Q", title="NG")],
    ).properties(height=260, background=COLORS["bg_panel"]).configure_view(
        stroke=COLORS["border_subtle"])
    st.altair_chart(bars, use_container_width=True)

with chart_tab2:
    lines = alt.Chart(daily_line).mark_line(point=True).encode(
        x=alt.X("date_str:N", title="날짜", sort=None,
            axis=alt.Axis(labelColor=COLORS["text_tertiary"], titleColor=COLORS["text_tertiary"])),
        y=alt.Y("ng_rate:Q", title="NG율 (%)",
            axis=alt.Axis(labelColor=COLORS["text_tertiary"], titleColor=COLORS["text_tertiary"])),
        color=alt.Color("line_no:N",
            scale=alt.Scale(domain=active_line_ids, range=color_range[:len(active_line_ids)]),
            legend=alt.Legend(labelColor=COLORS["text_secondary"], titleColor=COLORS["text_secondary"])),
        tooltip=[alt.Tooltip("date_str:N", title="날짜"),
                 alt.Tooltip("line_no:N", title="라인"),
                 alt.Tooltip("ng_rate:Q", title="NG율(%)"),
                 alt.Tooltip("pbox:Q", title="총P-Box")],
    ).properties(height=260, background=COLORS["bg_panel"]).configure_view(
        stroke=COLORS["border_subtle"])
    st.altair_chart(lines, use_container_width=True)


# ─── SKU × 라인 매트릭스 ───
st.markdown("---")
st.markdown(
    f'<div style="font-size:11px;font-weight:700;color:{COLORS["text_muted"]};'
    f'letter-spacing:0.08em;margin-bottom:12px;">SKU × LINE MATRIX · P-BOX COUNT</div>',
    unsafe_allow_html=True,
)

matrix = filtered.pivot_table(
    index="expected_sku_name", columns="line_no",
    values="crate_id", aggfunc="count", fill_value=0,
)

if not matrix.empty:
    lines_in_matrix = sorted(matrix.columns.tolist())
    max_val = matrix.values.max() if matrix.values.max() > 0 else 1

    # 헤더
    header_cols = st.columns([2] + [1] * len(lines_in_matrix))
    header_cols[0].markdown(
        f'<div style="font-size:13px;font-weight:700;color:{COLORS["text_muted"]};'
        f'padding:8px 4px;border-bottom:2px solid {COLORS["border_strong"]};">SKU</div>',
        unsafe_allow_html=True)
    for col, line in zip(header_cols[1:], lines_in_matrix):
        col.markdown(
            f'<div style="font-size:13px;font-weight:700;color:{COLORS["accent_cobalt"]};'
            f'padding:8px 4px;border-bottom:2px solid {COLORS["border_strong"]};'
            f'text-align:center;">{line}</div>', unsafe_allow_html=True)

    # 행
    for sku_name, row in matrix.iterrows():
        row_cols = st.columns([2] + [1] * len(lines_in_matrix))
        row_cols[0].markdown(
            f'<div style="font-size:14px;font-weight:600;color:{COLORS["text_primary"]};'
            f'padding:10px 4px;border-bottom:1px solid {COLORS["border_subtle"]};">'
            f'{sku_name}</div>', unsafe_allow_html=True)
        for col, line in zip(row_cols[1:], lines_in_matrix):
            val = int(row.get(line, 0))
            intensity = int(val / max_val * 100)
            bg = f"rgba(8,145,178,{intensity/100 * 0.25 + 0.03})" if val > 0 else "transparent"
            color = COLORS["accent_cobalt"] if val > 0 else COLORS["text_muted"]
            col.markdown(
                f'<div style="text-align:center;padding:10px 4px;'
                f'border-bottom:1px solid {COLORS["border_subtle"]};'
                f'background:{bg};border-radius:4px;">'
                f'<span style="font-size:15px;font-weight:700;color:{color};">'
                f'{"—" if val == 0 else val}</span>'
                f'</div>', unsafe_allow_html=True)
else:
    st.info("해당 기간 데이터가 없습니다.")
