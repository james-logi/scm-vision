"""
출고 검수 — 오늘 기준 -2일 ~ +5일 윈도우
과거/오늘: 실제 검수 데이터 / 미래: 생산계획 예측
"""

import streamlit as st
import pandas as pd
from datetime import timedelta, date as date_type
import datetime
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar, render_brand_header

st.set_page_config(page_title="재고 검수 | SCM", page_icon="◆",
                   layout="wide", initial_sidebar_state="expanded")

inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 재고 검수")
render_page_subtitle("INVENTORY INSPECTION · AI VISION VERIFIED · -2 DAYS ~ +5 DAYS")

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("data/inspection_history.csv")
    df["inspected_at"] = pd.to_datetime(df["inspected_at"])
    df["date"] = df["inspected_at"].dt.date
    return df

df = load_data()
TODAY = datetime.date.today()     # 실제 오늘 날짜 사용
WIN_START = TODAY - timedelta(days=2)
WIN_END   = TODAY + timedelta(days=5)
ALL_DATES = [WIN_START + timedelta(days=i) for i in range(8)]

# 일평균 (최근 14일 기준 예측용)
recent_14 = df[df["date"] >= TODAY - timedelta(days=13)]
avg_total  = len(recent_14) / 14
avg_ok     = len(recent_14[recent_14["verdict"] == "OK"]) / 14
avg_ng     = avg_total - avg_ok

# 날짜별 실제 집계
daily_actual = df[df["date"].between(WIN_START, TODAY)].groupby("date").agg(
    total=("crate_id","count"),
    ok=("verdict", lambda x: (x=="OK").sum()),
    ng=("verdict", lambda x: (x!="OK").sum()),
).reset_index()
daily_actual["ok_rate"] = (daily_actual["ok"] / daily_actual["total"] * 100).round(1)

def get_row(d):
    """날짜별 행 데이터 반환"""
    if d <= TODAY:
        row = daily_actual[daily_actual["date"] == d]
        if len(row) == 0:
            return dict(date=d, total=0, ok=0, ng=0, ok_rate=0.0, is_future=False)
        r = row.iloc[0]
        return dict(date=d, total=int(r["total"]), ok=int(r["ok"]),
                    ng=int(r["ng"]), ok_rate=float(r["ok_rate"]), is_future=False)
    else:
        t = int(round(avg_total))
        o = int(round(avg_ok))
        n = t - o
        rt = round(avg_ok / avg_total * 100, 1) if avg_total > 0 else 0.0
        return dict(date=d, total=t, ok=o, ng=n, ok_rate=rt, is_future=True)

rows = [get_row(d) for d in ALL_DATES]

# ─── KPI ───
st.markdown("")
window_ok    = sum(r["ok"]    for r in rows if not r["is_future"])
window_ng    = sum(r["ng"]    for r in rows if not r["is_future"])
planned_ok   = sum(r["ok"]    for r in rows if r["is_future"])
k1, k2, k3, k4 = st.columns(4)

def kpi(col, label, val, unit, sub, color):
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-top:3px solid {color};border-radius:6px;padding:16px;">'
        f'<div style="font-size:12px;color:{COLORS["text_muted"]};margin-bottom:6px;">{label}</div>'
        f'<div style="font-size:26px;font-weight:700;color:{COLORS["text_primary"]};line-height:1;">'
        f'{val}<span style="font-size:13px;color:{COLORS["text_tertiary"]};margin-left:3px;">{unit}</span></div>'
        f'<div style="font-size:12px;color:{color};margin-top:4px;">{sub}</div>'
        f'</div>', unsafe_allow_html=True)

kpi(k1, "오늘 기준일",       str(TODAY),          "",     "-2일 ~ +5일 관리 윈도우",  COLORS["accent_cobalt"])
kpi(k2, "실적 출고가능(OK)", f"{window_ok:,}",    "Case", "2일전~오늘 실적",         COLORS["status_ok"])
kpi(k3, "실적 NG 차단",      f"{window_ng:,}",    "Case", "2일전~오늘 차단",         COLORS["status_warning"])
kpi(k4, "향후 5일 예측",     f"{planned_ok:,}",   "Case", "출고 가능 예측",           COLORS["accent_gold"])

st.markdown("")
st.markdown("---")

# ─── 8일 타임라인 카드 ───
st.markdown(
    f'<div style="font-size:15px;font-weight:700;color:{COLORS["text_primary"]};'
    f'margin-bottom:12px;">검수 현황 타임라인 (-2일 ~ +5일)</div>',
    unsafe_allow_html=True)

cols = st.columns(8)
for col, r in zip(cols, rows):
    is_today  = (r["date"] == TODAY)
    is_future = r["is_future"]

    if is_today:
        border = f'border:2px solid {COLORS["accent_gold"]}'
        bg     = "#FFFBEB"
        badge  = f'<div style="background:{COLORS["accent_gold"]};color:white;' \
                 f'font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;' \
                 f'text-align:center;margin-bottom:6px;">오늘</div>'
    elif is_future:
        border = f'border:1px dashed {COLORS["border_subtle"]}'
        bg     = "#F8FAFC"
        badge  = f'<div style="background:#EFF6FF;color:{COLORS["accent_cobalt"]};' \
                 f'font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;' \
                 f'text-align:center;margin-bottom:6px;">예정</div>'
    else:
        border = f'border:1px solid {COLORS["border_subtle"]}'
        bg     = "white"
        badge  = f'<div style="background:#F0FDF4;color:{COLORS["status_ok"]};' \
                 f'font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;' \
                 f'text-align:center;margin-bottom:6px;">실적</div>'

    weekdays = ["월","화","수","목","금","토","일"]
    wd = weekdays[r["date"].weekday()]
    date_str = f'{r["date"].month}/{r["date"].day}({wd})'

    ok_color  = COLORS["status_ok"] if r["ok"] > 0 else COLORS["text_muted"]
    ng_color  = COLORS["status_warning"] if r["ng"] > 0 else COLORS["text_muted"]

    col.markdown(
        f'<div style="{border};background:{bg};border-radius:8px;padding:12px 8px;'
        f'text-align:center;">'
        f'{badge}'
        f'<div style="font-size:13px;font-weight:600;color:{COLORS["text_primary"]};'
        f'margin-bottom:8px;">{date_str}</div>'
        f'<div style="font-size:11px;color:{COLORS["text_muted"]};margin-bottom:2px;">OK</div>'
        f'<div style="font-size:18px;font-weight:700;color:{ok_color};">{r["ok"]}</div>'
        f'<div style="font-size:11px;color:{COLORS["text_muted"]};margin-top:6px;margin-bottom:2px;">NG</div>'
        f'<div style="font-size:15px;font-weight:700;color:{ng_color};">{r["ng"]}</div>'
        f'<div style="font-size:10px;color:{COLORS["text_muted"]};margin-top:6px;">'
        f'{"정확도" if not is_future else "예측"} {r["ok_rate"]}%</div>'
        f'</div>', unsafe_allow_html=True)

st.markdown("")
st.markdown("---")

# ─── 상세 테이블 ───
tab1, tab2 = st.tabs(["📋 날짜별 상세", "🚫 NG 내역"])

with tab1:
    h = st.columns([1.2, 0.8, 1, 1, 1, 1.5])
    for col, label in zip(h, ["날짜","구분","총 검수","출고가능(OK)","출고불가(NG)","검수 정확도"]):
        col.markdown(
            f'<div style="font-size:12px;font-weight:700;color:{COLORS["text_muted"]};'
            f'padding:8px 4px;border-bottom:2px solid {COLORS["border_strong"]};'
            f'text-align:center;">{label}</div>', unsafe_allow_html=True)

    for r in reversed(rows):
        is_future = r["is_future"]
        is_today  = (r["date"] == TODAY)
        bg = "#FFFBEB" if is_today else ("white" if not is_future else "#F8FAFC")
        tag = "예정" if is_future else ("오늘" if is_today else "실적")
        tag_color = (COLORS["accent_gold"] if is_today
                     else COLORS["accent_cobalt"] if is_future
                     else COLORS["status_ok"])

        weekdays = ["월","화","수","목","금","토","일"]
        wd = weekdays[r["date"].weekday()]
        date_str = f'{r["date"]} ({wd})'

        row = st.columns([1.2, 0.8, 1, 1, 1, 1.5])
        vals = [
            (date_str,                     COLORS["text_primary"],   "left"),
            (tag,                          tag_color,                "center"),
            (f'{r["total"]:,}',            COLORS["text_secondary"], "center"),
            (f'{r["ok"]:,}',               COLORS["status_ok"],      "center"),
            (f'{r["ng"]:,}' if r["ng"]>0 else "—",
                                           COLORS["status_warning"] if r["ng"]>0 else COLORS["text_muted"],
                                                                     "center"),
            (f'{r["ok_rate"]}%',           COLORS["accent_gold"],    "center"),
        ]
        for col, (val, color, align) in zip(row, vals):
            col.markdown(
                f'<div style="padding:10px 4px;border-bottom:1px solid {COLORS["border_subtle"]};'
                f'background:{bg};text-align:{align};font-size:14px;color:{color};font-weight:500;">'
                f'{val}</div>', unsafe_allow_html=True)

with tab2:
    df_ng = df[df["date"].between(WIN_START, TODAY) & (df["verdict"] != "OK")]
    if df_ng.empty:
        st.success("최근 2일간 NG 없음")
    else:
        ng_disp = df_ng[["date","line_no","expected_sku_name","verdict",
                          "expected_qty","detected_qty"]].copy()
        verdict_map = {"NG_QTY_SHORT":"수량 부족","NG_QTY_EXCESS":"수량 초과",
                       "NG_CONTAMINATION":"혼입 불량","NG_SKU_MISMATCH":"SKU 불일치"}
        ng_disp["verdict"] = ng_disp["verdict"].map(verdict_map).fillna(ng_disp["verdict"])
        ng_disp.columns = ["날짜","라인","상품명","판정","기대수량","검출수량"]
        st.dataframe(ng_disp.sort_values("날짜", ascending=False),
                     use_container_width=True, hide_index=True, height=380)
        st.markdown(
            f'<div style="background:#FEF2F2;border-left:3px solid {COLORS["status_danger"]};'
            f'padding:12px 16px;border-radius:4px;font-size:13px;color:{COLORS["status_danger"]};">'
            f'⚠ {len(df_ng)}건 출고 차단 — 재검수 또는 폐기 처리 필요'
            f'</div>', unsafe_allow_html=True)
