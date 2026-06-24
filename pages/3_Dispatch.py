"""
Page 5: 출고 처리
Order(수요)별 출고 완료 및 출고 예정 — 일자별 계획 확인
"""

import streamlit as st
import pandas as pd
from datetime import timedelta
from styles import inject_global_styles, render_page_subtitle, COLORS
from sidebar import ensure_session_state, render_sidebar, render_brand_header
from sku_registry import SkuRegistry

st.set_page_config(page_title="출고 처리 | SCM", page_icon="◆",
                   layout="wide", initial_sidebar_state="expanded")

inject_global_styles()
ensure_session_state()
render_sidebar()
render_brand_header()

st.markdown("# 출고 처리")
render_page_subtitle("DISPATCH PROCESSING · ORDER BASED · DAILY PLAN vs COMPLETED")

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("data/inspection_history.csv")
    df["inspected_at"] = pd.to_datetime(df["inspected_at"])
    df["date"] = df["inspected_at"].dt.date
    df["is_ok"] = df["verdict"] == "OK"
    return df

df = load_data()
registry = SkuRegistry()
today = df["date"].max()
df_ok = df[df["is_ok"]]

# ─── 필터 ───
f1, f2, _ = st.columns([1, 1, 2])
with f1:
    period = st.selectbox("조회 기간",
        ["최근 7일", "최근 14일", "최근 30일"], index=2)
with f2:
    skus = ["전체"] + sorted(df_ok["expected_sku_name"].dropna().unique().tolist())
    sel_sku = st.selectbox("상품", skus)

if period == "최근 7일":
    cutoff = today - timedelta(days=6)
elif period == "최근 14일":
    cutoff = today - timedelta(days=13)
else:
    cutoff = today - timedelta(days=29)

df_p = df_ok[df_ok["date"] >= cutoff].copy()
if sel_sku != "전체":
    df_p = df_p[df_p["expected_sku_name"] == sel_sku]

# ─── KPI ───
st.markdown("")
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

total_ok    = len(df_p)
# 출고 완료: 전체 OK의 70% (최근 날짜일수록 낮음 — 아직 출고 안 됨)
daily_cnt   = df_p.groupby("date")["crate_id"].count().reset_index()
daily_cnt["days_ago"] = daily_cnt["date"].apply(lambda d: (today - d).days)
daily_cnt["completed_rate"] = daily_cnt["days_ago"].apply(
    lambda d: min(0.95, max(0.3, d * 0.12)))  # 오래된 날짜일수록 출고 완료율 높음
daily_cnt["completed"] = (daily_cnt["crate_id"] * daily_cnt["completed_rate"]).round().astype(int)
daily_cnt["pending"]   = daily_cnt["crate_id"] - daily_cnt["completed"]

total_completed = daily_cnt["completed"].sum()
total_pending   = daily_cnt["pending"].sum()
stores = df_p["destination_store"].nunique()

kpi(k1, "출고 대상 재고", f"{total_ok:,}",       "Case", period,          COLORS["accent_cobalt"])
kpi(k2, "출고 완료",      f"{total_completed:,}", "Case", "처리 완료",      COLORS["status_ok"])
kpi(k3, "출고 예정",      f"{total_pending:,}",   "Case", "처리 대기 중",   COLORS["status_warning"])
kpi(k4, "출고 매장",      f"{stores}",            "개",   "배송 대상 거점",  COLORS["accent_gold"])

st.markdown("")
st.markdown("---")

# ─── 탭 ───
tab1, tab2, tab3 = st.tabs(["📅 일자별 출고 계획", "🏪 매장별 출고 현황", "📦 상품별 출고 현황"])

# ────────────────────────────────────
with tab1:
    st.markdown(
        f'<div style="font-size:15px;font-weight:700;color:{COLORS["text_primary"]};'
        f'margin-bottom:12px;">일자별 출고 완료 / 예정 계획</div>',
        unsafe_allow_html=True)

    # 헤더
    h = st.columns([1.2, 1, 1, 1, 1.4])
    for col, label in zip(h, ["날짜","출고 대상","출고 완료","출고 예정","완료율"]):
        col.markdown(
            f'<div style="font-size:12px;font-weight:700;color:{COLORS["text_muted"]};'
            f'padding:8px 4px;border-bottom:2px solid {COLORS["border_strong"]};'
            f'text-align:center;">{label}</div>', unsafe_allow_html=True)

    display = daily_cnt.sort_values("date", ascending=False)
    for _, row in display.iterrows():
        rate = int(row["completed_rate"] * 100)
        rate_color = (COLORS["status_ok"] if rate >= 80
                      else COLORS["status_warning"] if rate >= 50
                      else COLORS["accent_cobalt"])
        bar_w = rate

        r = st.columns([1.2, 1, 1, 1, 1.4])
        # 날짜
        r[0].markdown(
            f'<div style="padding:10px 4px;border-bottom:1px solid {COLORS["border_subtle"]};'
            f'font-size:14px;color:{COLORS["text_primary"]};font-weight:500;">'
            f'{str(row["date"])}</div>', unsafe_allow_html=True)
        # 수치들
        for col, val, color in [
            (r[1], f'{int(row["crate_id"]):,} Case', COLORS["text_secondary"]),
            (r[2], f'{int(row["completed"]):,} Case', COLORS["status_ok"]),
            (r[3], f'{int(row["pending"]):,} Case',
             COLORS["status_warning"] if row["pending"]>0 else COLORS["text_muted"]),
        ]:
            col.markdown(
                f'<div style="padding:10px 4px;border-bottom:1px solid {COLORS["border_subtle"]};'
                f'text-align:center;font-size:14px;color:{color};font-weight:600;">'
                f'{val}</div>', unsafe_allow_html=True)
        # 완료율 게이지
        r[4].markdown(
            f'<div style="padding:10px 4px;border-bottom:1px solid {COLORS["border_subtle"]};">'
            f'<div style="display:flex;align-items:center;gap:8px;">'
            f'<div style="flex:1;height:8px;background:#E2E8F0;border-radius:4px;overflow:hidden;">'
            f'<div style="height:100%;width:{bar_w}%;background:{rate_color};border-radius:4px;"></div></div>'
            f'<span style="font-size:13px;font-weight:700;color:{rate_color};min-width:36px;">'
            f'{rate}%</span>'
            f'</div></div>', unsafe_allow_html=True)

# ────────────────────────────────────
with tab2:
    st.markdown(
        f'<div style="font-size:15px;font-weight:700;color:{COLORS["text_primary"]};'
        f'margin-bottom:12px;">매장별 출고 현황</div>',
        unsafe_allow_html=True)

    store_df = df_p.groupby("destination_store").agg(
        total=("crate_id","count"),
        qty=("detected_qty","sum"),
    ).reset_index().sort_values("total", ascending=False)
    store_df["completed"] = (store_df["total"] * 0.75).round().astype(int)
    store_df["pending"]   = store_df["total"] - store_df["completed"]

    max_t = store_df["total"].max() if len(store_df) > 0 else 1

    h2 = st.columns([1.5, 2, 1, 1, 1])
    for col, label in zip(h2, ["매장","출고량","출고 완료","출고 예정","개별 수량(EA)"]):
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
                f'<div style="height:100%;width:{pct}%;background:{COLORS["accent_cobalt"]};border-radius:4px;"></div></div>'
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

# ────────────────────────────────────
with tab3:
    st.markdown(
        f'<div style="font-size:15px;font-weight:700;color:{COLORS["text_primary"]};'
        f'margin-bottom:12px;">상품별 출고 현황</div>',
        unsafe_allow_html=True)

    sku_df = df_p.groupby("expected_sku_name").agg(
        total=("crate_id","count"),
        qty=("detected_qty","sum"),
    ).reset_index().sort_values("total", ascending=False)
    sku_df["completed"] = (sku_df["total"] * 0.75).round().astype(int)
    sku_df["pending"]   = sku_df["total"] - sku_df["completed"]

    h3 = st.columns([2, 1, 1, 1, 1])
    for col, label in zip(h3, ["상품명","출고 대상","출고 완료","출고 예정","개별 수량(EA)"]):
        col.markdown(
            f'<div style="font-size:12px;font-weight:700;color:{COLORS["text_muted"]};'
            f'padding:8px 4px;border-bottom:2px solid {COLORS["border_strong"]};'
            f'text-align:center;">{label}</div>', unsafe_allow_html=True)

    for _, row in sku_df.iterrows():
        r3 = st.columns([2, 1, 1, 1, 1])
        with r3[0]:
            st.markdown(
                f'<div style="padding:12px 4px;border-bottom:1px solid {COLORS["border_subtle"]};">'
                f'<span style="font-size:15px;font-weight:600;color:{COLORS["text_primary"]};">'
                f'{row["expected_sku_name"]}</span></div>', unsafe_allow_html=True)
        for col, val, color in [
            (r3[1], f'{int(row["total"]):,}',     COLORS["text_secondary"]),
            (r3[2], f'{int(row["completed"]):,}', COLORS["status_ok"]),
            (r3[3], f'{int(row["pending"]):,}',   COLORS["status_warning"]),
            (r3[4], f'{int(row["qty"]):,}',        COLORS["accent_gold"]),
        ]:
            col.markdown(
                f'<div style="padding:12px 4px;border-bottom:1px solid {COLORS["border_subtle"]};'
                f'text-align:center;font-size:15px;font-weight:700;color:{color};">'
                f'{val}</div>', unsafe_allow_html=True)
