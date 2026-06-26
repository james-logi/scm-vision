"""
Page 6: 검사 이력
inspection_history.csv 기반 30일 누적 성과 시각화
"""

import streamlit as st
import pandas as pd
import altair as alt
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar, render_brand_header
from data_config import calc_savings, PBOX_UNIT, AVG_PRICE_PER_EA

st.set_page_config(page_title="검사 이력 | SCM", page_icon="◆",
                   layout="wide", initial_sidebar_state="expanded")

inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 검사 이력")
render_page_subtitle("INSPECTION LOG · 30 DAYS · EA / CASE CHART")

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("data/inspection_history.csv")
    df["inspected_at"] = pd.to_datetime(df["inspected_at"])
    df["date"]         = df["inspected_at"].dt.date
    df["date_dt"]      = pd.to_datetime(df["date"])
    return df

df = load_data()
df_ok = df[df["verdict"] == "OK"]
df_ng = df[df["verdict"] != "OK"]

# ─── KPI ───
st.markdown("")
k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, val, unit, label, sub, color):
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-top:3px solid {color};border-radius:6px;padding:16px;text-align:center;">'
        f'<div style="font-size:24px;font-weight:900;color:{color};line-height:1;">{val}'
        f'<span style="font-size:13px;color:{COLORS["text_tertiary"]};margin-left:2px;">{unit}</span></div>'
        f'<div style="font-size:13px;font-weight:600;color:{COLORS["text_primary"]};margin-top:6px;">{label}</div>'
        f'<div style="font-size:11px;color:{COLORS["text_muted"]};margin-top:2px;">{sub}</div>'
        f'</div>', unsafe_allow_html=True)

total = len(df)
ok    = len(df_ok)
ng    = len(df_ng)
acc   = ok / total * 100 if total > 0 else 0
days  = df["date"].nunique()

kpi(k1, f"{total:,}",            "건",  "누적 검수",   f"{days}일간",              COLORS["accent_cobalt"])
kpi(k2, f"{acc:.2f}",            "%",   "비전 정확도", "AI Vision 판정",           COLORS["accent_gold"])
kpi(k3, f"{ng:,}",               "건",  "NG 차단",     "출고 불가 차단",            COLORS["status_warning"])
kpi(k4, f"{calc_savings(ng):,}", "원",  "추정 절감",   f"NG 1건당 {PBOX_UNIT*AVG_PRICE_PER_EA:,}원", COLORS["status_ok"])
kpi(k5, f"{df['expected_sku_name'].nunique()}", "종", "취급 SKU", "검수 상품 종류", COLORS["text_secondary"])

st.markdown("")
st.markdown("---")

# ─── 탭 ───
tab1, tab2, tab3 = st.tabs(["📊 성과 차트", "📋 일별 집계", "🔍 상세 검색"])

# ── 탭1: 차트 ──
with tab1:
    c1, c2 = st.columns([1, 3])
    with c1:
        unit_mode = st.radio("단위", ["Case (P-Box)", "EA (낱개)"], index=0)
    with c2:
        sku_list = ["전체"] + sorted(df["expected_sku_name"].dropna().unique().tolist())
        sel_sku = st.selectbox("상품", sku_list, key="chart_sku")

    df_c = df.copy() if sel_sku == "전체" else df[df["expected_sku_name"] == sel_sku].copy()

    if unit_mode == "Case (P-Box)":
        daily = df_c.groupby("date_dt").agg(
            ok=("verdict", lambda x: (x=="OK").sum()),
            ng=("verdict", lambda x: (x!="OK").sum()),
        ).reset_index().rename(columns={"date_dt":"date"})
        y_label = "P-Box 수 (Case)"
    else:
        daily = df_c.groupby("date_dt").agg(
            ok=("detected_qty", lambda x: x[df_c.loc[x.index,"verdict"]=="OK"].sum()),
            ng=("detected_qty", lambda x: x[df_c.loc[x.index,"verdict"]!="OK"].sum()),
        ).reset_index().rename(columns={"date_dt":"date"})
        y_label = "낱개 수 (EA)"

    daily_melted = daily.melt(id_vars="date", value_vars=["ok","ng"],
                              var_name="판정", value_name="수량")
    daily_melted["판정"] = daily_melted["판정"].map({"ok":"OK","ng":"NG"})

    chart = alt.Chart(daily_melted).mark_bar().encode(
        x=alt.X("date:T", title="날짜", axis=alt.Axis(format="%m/%d")),
        y=alt.Y("수량:Q", title=y_label),
        color=alt.Color("판정:N", scale=alt.Scale(
            domain=["OK","NG"], range=[COLORS["status_ok"], COLORS["status_warning"]]
        )),
        tooltip=["date:T","판정:N","수량:Q"],
    ).properties(height=320).configure_view(
        stroke=COLORS["border_subtle"]
    ).configure_axis(
        labelColor=COLORS["text_secondary"], titleColor=COLORS["text_secondary"],
        gridColor=COLORS["border_subtle"]
    )
    st.altair_chart(chart, use_container_width=True)

    # 막대 위 숫자 (총합)
    tot_ok = int(daily["ok"].sum())
    tot_ng = int(daily["ng"].sum())
    m1, m2, m3 = st.columns(3)
    m1.metric("OK 합계", f"{tot_ok:,}", f"+{unit_mode.split()[0]}")
    m2.metric("NG 합계", f"{tot_ng:,}", delta_color="inverse")
    m3.metric("정확도", f"{tot_ok/(tot_ok+tot_ng)*100:.2f}%" if (tot_ok+tot_ng)>0 else "—")

# ── 탭2: 일별 집계 ──
with tab2:
    daily_agg = df.groupby("date").agg(
        총검수=("crate_id","count"),
        OK=("verdict", lambda x:(x=="OK").sum()),
        NG=("verdict", lambda x:(x!="OK").sum()),
        EA합계=("detected_qty","sum"),
    ).reset_index().sort_values("date", ascending=False)
    daily_agg["정확도(%)"] = (daily_agg["OK"] / daily_agg["총검수"] * 100).round(2)
    daily_agg["절감액(원)"] = daily_agg["NG"].apply(calc_savings)
    st.dataframe(daily_agg, use_container_width=True, hide_index=True, height=420)

# ── 탭3: 상세 검색 ──
with tab3:
    f1, f2, f3 = st.columns(3)
    with f1:
        sku_f = st.selectbox("상품", ["전체"] + sorted(df["expected_sku_name"].dropna().unique().tolist()), key="search_sku")
    with f2:
        verdict_f = st.selectbox("판정", ["전체","OK","NG"])
    with f3:
        line_f = st.selectbox("라인", ["전체"] + sorted(df["line_no"].dropna().unique().tolist()))

    df_s = df.copy()
    if sku_f != "전체":     df_s = df_s[df_s["expected_sku_name"] == sku_f]
    if verdict_f != "전체": df_s = df_s[df_s["verdict"] == verdict_f] if verdict_f == "OK" else df_s[df_s["verdict"] != "OK"]
    if line_f != "전체":    df_s = df_s[df_s["line_no"] == line_f]

    show = df_s[["date","line_no","expected_sku_name","expected_qty","detected_qty","verdict"]].copy()
    show.columns = ["날짜","라인","상품명","기대수량","검출수량","판정"]
    show = show.sort_values("날짜", ascending=False)

    st.markdown(f'<div style="font-size:13px;color:{COLORS["text_muted"]};margin-bottom:8px;">총 {len(show):,}건</div>', unsafe_allow_html=True)
    st.dataframe(show, use_container_width=True, hide_index=True, height=400)
