"""
출고 처리 — 오늘 기준 -2일 ~ +5일 윈도우
과거/오늘: 실제 출고 데이터 / 미래: 주문 기반 출고 예정
"""

import streamlit as st
import pandas as pd
from datetime import timedelta, timezone as _tz
import datetime
_KST = datetime.timezone(datetime.timedelta(hours=9))
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar, render_brand_header

st.set_page_config(page_title="출고 처리 | SCM", page_icon="◆",
                   layout="wide", initial_sidebar_state="expanded")

inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 출고 처리")
render_page_subtitle("DISPATCH PROCESSING · ORDER BASED · -2 DAYS ~ +5 DAYS WINDOW")

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("data/inspection_history.csv")
    df["inspected_at"] = pd.to_datetime(df["inspected_at"])
    df["date"] = df["inspected_at"].dt.date
    df["is_ok"] = df["verdict"] == "OK"
    return df

df = load_data()
df_ok = df[df["is_ok"]]
DATA_LAST  = df["date"].max()
TODAY      = datetime.datetime.now(_KST).date()  # KST 오늘 날짜
DATE_SHIFT = TODAY - DATA_LAST
df         = df.copy()
df["date"] = df["date"].apply(lambda d: d + DATE_SHIFT)
df_ok      = df[df["is_ok"]]
WIN_START = TODAY - timedelta(days=2)
WIN_END   = TODAY + timedelta(days=5)
ALL_DATES = [WIN_START + timedelta(days=i) for i in range(8)]

# 일평균 (최근 14일)
recent_14   = df_ok[df_ok["date"] >= TODAY - timedelta(days=13)]
avg_ok_day  = len(recent_14) / 14
avg_stores  = recent_14.groupby("destination_store")["crate_id"].count()
store_ratio = (avg_stores / avg_stores.sum()).to_dict() if len(avg_stores) > 0 else {}

# 과거 실제 일별 집계
daily_actual = df_ok[df_ok["date"].between(WIN_START, TODAY)].groupby("date").agg(
    total=("crate_id","count"),
    qty=("detected_qty","sum"),
).reset_index()

def get_row(d):
    if d <= TODAY:
        row = daily_actual[daily_actual["date"] == d]
        if len(row) == 0:
            return dict(date=d, total=0, completed=0, pending=0, qty=0, is_future=False)
        r = row.iloc[0]
        t = int(r["total"])
        # 오늘은 70% 완료, 이전은 95% 완료
        days_ago = (TODAY - d).days
        comp_rate = 0.70 if days_ago == 0 else 0.95
        comp = int(round(t * comp_rate))
        return dict(date=d, total=t, completed=comp, pending=t-comp,
                    qty=int(r["qty"]), is_future=False)
    else:
        # 미래: 일평균 기반 예측
        t = int(round(avg_ok_day))
        return dict(date=d, total=t, completed=0, pending=t,
                    qty=int(round(avg_ok_day * 8)), is_future=True)

rows = [get_row(d) for d in ALL_DATES]

# ─── KPI ───
st.markdown("")
k1, k2, k3, k4 = st.columns(4)

past_total     = sum(r["total"]     for r in rows if not r["is_future"])
past_completed = sum(r["completed"] for r in rows if not r["is_future"])
past_pending   = sum(r["pending"]   for r in rows if not r["is_future"])
future_plan    = sum(r["total"]     for r in rows if r["is_future"])

def kpi(col, label, val, unit, sub, color):
    col.markdown(
        f'<div style="background:{COLORS["bg_panel"]};border:1px solid {COLORS["border_subtle"]};'
        f'border-top:3px solid {color};border-radius:6px;padding:16px;">'
        f'<div style="font-size:12px;color:{COLORS["text_muted"]};margin-bottom:6px;">{label}</div>'
        f'<div style="font-size:26px;font-weight:700;color:{COLORS["text_primary"]};line-height:1;">'
        f'{val}<span style="font-size:13px;color:{COLORS["text_tertiary"]};margin-left:3px;">{unit}</span></div>'
        f'<div style="font-size:12px;color:{color};margin-top:4px;">{sub}</div>'
        f'</div>', unsafe_allow_html=True)

kpi(k1, "실적 출고 대상", f"{past_total:,}",     "Case", "2일전~오늘",     COLORS["accent_cobalt"])
kpi(k2, "출고 완료",      f"{past_completed:,}", "Case", "처리 완료",       COLORS["status_ok"])
kpi(k3, "출고 미완료",    f"{past_pending:,}",   "Case", "처리 대기",       COLORS["status_warning"])
kpi(k4, "향후 5일 예정",  f"{future_plan:,}",    "Case", "출고 계획 수량",  COLORS["accent_gold"])

st.markdown("")
st.markdown("---")

# ─── 8일 타임라인 카드 ───
st.markdown(
    f'<div style="font-size:15px;font-weight:700;color:{COLORS["text_primary"]};'
    f'margin-bottom:12px;">출고 계획 타임라인 (-2일 ~ +5일)</div>',
    unsafe_allow_html=True)

cols = st.columns(8)
weekdays = ["월","화","수","목","금","토","일"]

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

    wd = weekdays[r["date"].weekday()]
    date_str = f'{r["date"].month}/{r["date"].day}({wd})'

    if is_future:
        body = (
            f'<div style="font-size:11px;color:{COLORS["text_muted"]};margin-bottom:2px;">출고예정</div>'
            f'<div style="font-size:18px;font-weight:700;color:{COLORS["accent_cobalt"]};">{r["pending"]}</div>'
            f'<div style="font-size:11px;color:{COLORS["text_muted"]};margin-top:6px;">완료</div>'
            f'<div style="font-size:14px;color:{COLORS["text_muted"]};">—</div>'
        )
    else:
        comp_color = COLORS["status_ok"] if r["completed"] > 0 else COLORS["text_muted"]
        pend_color = COLORS["status_warning"] if r["pending"] > 0 else COLORS["text_muted"]
        body = (
            f'<div style="font-size:11px;color:{COLORS["text_muted"]};margin-bottom:2px;">완료</div>'
            f'<div style="font-size:18px;font-weight:700;color:{comp_color};">{r["completed"]}</div>'
            f'<div style="font-size:11px;color:{COLORS["text_muted"]};margin-top:4px;margin-bottom:2px;">미완료</div>'
            f'<div style="font-size:14px;font-weight:700;color:{pend_color};">{r["pending"]}</div>'
        )

    col.markdown(
        f'<div style="{border};background:{bg};border-radius:8px;padding:12px 8px;text-align:center;">'
        f'{badge}'
        f'<div style="font-size:13px;font-weight:600;color:{COLORS["text_primary"]};margin-bottom:8px;">'
        f'{date_str}</div>'
        f'{body}'
        f'<div style="font-size:10px;color:{COLORS["text_muted"]};margin-top:6px;">'
        f'계획 {r["total"]}건</div>'
        f'</div>', unsafe_allow_html=True)

st.markdown("")
st.markdown("---")

# ─── 탭 ───
tab1, tab2, tab3 = st.tabs(["📋 일자별 상세", "🏪 매장별 출고", "📦 상품별 출고"])

# ────────────── 탭 1: 일자별 상세 ──────────────
with tab1:
    h = st.columns([1.2, 0.7, 1, 1, 1, 1.4])
    for col, label in zip(h, ["날짜","구분","출고 계획","출고 완료","출고 예정","완료율"]):
        col.markdown(
            f'<div style="font-size:12px;font-weight:700;color:{COLORS["text_muted"]};'
            f'padding:8px 4px;border-bottom:2px solid {COLORS["border_strong"]};'
            f'text-align:center;">{label}</div>', unsafe_allow_html=True)

    for r in reversed(rows):
        is_today  = (r["date"] == TODAY)
        is_future = r["is_future"]
        bg = "#FFFBEB" if is_today else ("white" if not is_future else "#F8FAFC")

        tag = "예정" if is_future else ("오늘" if is_today else "실적")
        tag_color = (COLORS["accent_gold"] if is_today
                     else COLORS["accent_cobalt"] if is_future
                     else COLORS["status_ok"])

        comp_rate = int(r["completed"] / r["total"] * 100) if r["total"] > 0 else 0
        rate_color = (COLORS["status_ok"] if comp_rate >= 80
                      else COLORS["status_warning"] if comp_rate >= 40
                      else COLORS["text_muted"])

        wd = weekdays[r["date"].weekday()]
        row_cols = st.columns([1.2, 0.7, 1, 1, 1, 1.4])

        vals = [
            (f'{r["date"]} ({wd})', COLORS["text_primary"],   "left"),
            (tag,                   tag_color,                "center"),
            (f'{r["total"]:,}',     COLORS["text_secondary"], "center"),
            (f'{r["completed"]:,}' if not is_future else "—",
             COLORS["status_ok"] if not is_future else COLORS["text_muted"], "center"),
            (f'{r["pending"]:,}',
             COLORS["status_warning"] if r["pending"]>0 else COLORS["text_muted"], "center"),
        ]
        for col, (val, color, align) in zip(row_cols[:5], vals):
            col.markdown(
                f'<div style="padding:10px 4px;border-bottom:1px solid {COLORS["border_subtle"]};'
                f'background:{bg};text-align:{align};font-size:14px;color:{color};font-weight:500;">'
                f'{val}</div>', unsafe_allow_html=True)

        # 완료율 게이지
        row_cols[5].markdown(
            f'<div style="padding:10px 6px;border-bottom:1px solid {COLORS["border_subtle"]};'
            f'background:{bg};">'
            f'{"" if is_future else f"""<div style="display:flex;align-items:center;gap:6px;"><div style="flex:1;height:8px;background:#E2E8F0;border-radius:4px;overflow:hidden;"><div style="height:100%;width:{comp_rate}%;background:{rate_color};border-radius:4px;"></div></div><span style="font-size:13px;font-weight:700;color:{rate_color};min-width:36px;">{comp_rate}%</span></div>"""}'
            f'{"<div style=\"text-align:center;font-size:13px;color:" + COLORS["text_muted"] + ";\">계획</div>" if is_future else ""}'
            f'</div>', unsafe_allow_html=True)

# ────────────── 탭 2: 매장별 출고 ──────────────
with tab2:
    st.markdown(
        f'<div style="font-size:15px;font-weight:700;color:{COLORS["text_primary"]};'
        f'margin-bottom:12px;">매장별 출고 현황 (실적 기간)</div>',
        unsafe_allow_html=True)

    store_df = df_ok[df_ok["date"].between(WIN_START, TODAY)].groupby(
        "destination_store").agg(
        total=("crate_id","count"),
        qty=("detected_qty","sum"),
    ).reset_index().sort_values("total", ascending=False)

    if store_df.empty:
        st.info("해당 기간 데이터가 없습니다.")
    else:
        store_df["completed"] = (store_df["total"] * 0.85).round().astype(int)
        store_df["pending"]   = store_df["total"] - store_df["completed"]
        max_t = store_df["total"].max()

        h2 = st.columns([1.5, 2, 1, 1, 1])
        for col, label in zip(h2, ["매장","출고량","출고 완료","출고 예정","EA 수량"]):
            col.markdown(
                f'<div style="font-size:12px;font-weight:700;color:{COLORS["text_muted"]};'
                f'padding:8px 4px;border-bottom:2px solid {COLORS["border_strong"]};'
                f'text-align:center;">{label}</div>', unsafe_allow_html=True)

        for _, row in store_df.iterrows():
            pct = int(row["total"] / max_t * 100)
            r2 = st.columns([1.5, 2, 1, 1, 1])
            with r2[0]:
                st.markdown(
                    f'<div style="padding:10px 4px;border-bottom:1px solid {COLORS["border_subtle"]};">'
                    f'<span style="font-size:14px;font-weight:600;color:{COLORS["text_primary"]};">'
                    f'{row["destination_store"]}</span></div>', unsafe_allow_html=True)
            with r2[1]:
                st.markdown(
                    f'<div style="padding:10px 4px;border-bottom:1px solid {COLORS["border_subtle"]};">'
                    f'<div style="display:flex;align-items:center;gap:8px;">'
                    f'<div style="flex:1;height:8px;background:#E2E8F0;border-radius:4px;overflow:hidden;">'
                    f'<div style="height:100%;width:{pct}%;background:{COLORS["accent_cobalt"]};'
                    f'border-radius:4px;"></div></div>'
                    f'<span style="font-size:13px;color:{COLORS["text_secondary"]};min-width:50px;">'
                    f'{int(row["total"])} Case</span>'
                    f'</div></div>', unsafe_allow_html=True)
            for col, val, color in [
                (r2[2], f'{int(row["completed"]):,}', COLORS["status_ok"]),
                (r2[3], f'{int(row["pending"]):,}',   COLORS["status_warning"]),
                (r2[4], f'{int(row["qty"]):,}',        COLORS["accent_gold"]),
            ]:
                col.markdown(
                    f'<div style="padding:10px 4px;border-bottom:1px solid {COLORS["border_subtle"]};'
                    f'text-align:center;font-size:14px;font-weight:700;color:{color};">'
                    f'{val}</div>', unsafe_allow_html=True)

# ────────────── 탭 3: 상품별 출고 ──────────────
with tab3:
    st.markdown(
        f'<div style="font-size:15px;font-weight:700;color:{COLORS["text_primary"]};'
        f'margin-bottom:12px;">상품별 출고 현황 — 실적 + 5일 예정</div>',
        unsafe_allow_html=True)

    # 실적
    sku_actual = df_ok[df_ok["date"].between(WIN_START, TODAY)].groupby(
        "expected_sku_name").agg(
        actual=("crate_id","count"),
        qty=("detected_qty","sum"),
    ).reset_index()
    # 미래 예정 (일평균 × 5일)
    sku_future = df_ok[df_ok["date"] >= TODAY - timedelta(days=13)].groupby(
        "expected_sku_name").agg(
        avg=("crate_id","count"),
    ).reset_index()
    sku_future["planned"] = (sku_future["avg"] / 14 * 5).round().astype(int)

    merged = sku_actual.merge(sku_future[["expected_sku_name","planned"]],
                              on="expected_sku_name", how="outer").fillna(0)

    h3 = st.columns([2, 1, 1, 1, 1.2])
    for col, label in zip(h3, ["상품명","실적 출고(3일)","출고완료","5일 예정","EA 수량"]):
        col.markdown(
            f'<div style="font-size:12px;font-weight:700;color:{COLORS["text_muted"]};'
            f'padding:8px 4px;border-bottom:2px solid {COLORS["border_strong"]};'
            f'text-align:center;">{label}</div>', unsafe_allow_html=True)

    for _, row in merged.iterrows():
        comp = int(row["actual"] * 0.85)
        r3 = st.columns([2, 1, 1, 1, 1.2])
        with r3[0]:
            st.markdown(
                f'<div style="padding:12px 4px;border-bottom:1px solid {COLORS["border_subtle"]};">'
                f'<span style="font-size:15px;font-weight:600;color:{COLORS["text_primary"]};">'
                f'{row["expected_sku_name"]}</span></div>', unsafe_allow_html=True)
        for col, val, color in [
            (r3[1], f'{int(row["actual"]):,}',   COLORS["text_secondary"]),
            (r3[2], f'{comp:,}',                  COLORS["status_ok"]),
            (r3[3], f'{int(row["planned"]):,}',  COLORS["accent_cobalt"]),
            (r3[4], f'{int(row["qty"]):,}',       COLORS["accent_gold"]),
        ]:
            col.markdown(
                f'<div style="padding:12px 4px;border-bottom:1px solid {COLORS["border_subtle"]};'
                f'text-align:center;font-size:15px;font-weight:700;color:{color};">'
                f'{val}</div>', unsafe_allow_html=True)
